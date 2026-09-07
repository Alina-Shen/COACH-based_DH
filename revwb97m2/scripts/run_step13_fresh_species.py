#!/usr/bin/env python3
"""Run one frozen production-style Q-Chem species through Step 13."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_feature_publisher import publish_or_resume, sha256  # noqa: E402
from revwb97m2.qchem_scalar_features import (  # noqa: E402
    derive_pt2_input,
    derive_scalar_input,
    publish_scalar_case,
    tree_manifest,
)
from revwb97m2.qchem_step13_stages import publish_species_from_validated_gateway  # noqa: E402
from revwb97m2.scripts.prepare_q3_qchem_gateway import derive_input  # noqa: E402


DEFAULT_MANIFEST = ROOT / "manifests/production_generator/step13_fresh_species_smoke_v1.yaml"
QCHEM_ROOT = Path("/clusterfs/mhg-data/yaoshen/qchem/trunk")
QCAUX = "/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux"
CONTROL_AMENDMENT = ROOT / "manifests/qchem_gateway/q6_retry2_control_amendment_v1.yaml"


def canonical_tree_hash(records: list[dict[str, object]]) -> str:
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def load_frozen_case(manifest_path: Path, species: str, cpus: int) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "frozen_before_results":
        raise ValueError("fresh-species contract must be frozen before results")
    matches = [row for row in manifest["cases"] if row["species"] == species]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one frozen case for {species}")
    case = matches[0]
    if cpus != int(case["resources"]["cpus"]):
        raise ValueError("allocated CPU count differs from frozen contract")
    return manifest, case


def validate_frozen_authorities(manifest: dict[str, Any]) -> None:
    paths = {
        "scientific_specification_sha256": ROOT / "configs/scientific_spec.yaml",
        "basis_bridge_records_sha256": ROOT / "manifests/basis_bridge/resolved_basis_records.csv",
        "q4_validation_sha256": ROOT / "manifests/qchem_gateway/q4_validation_v1.json",
        "step9_validation_sha256": ROOT / "manifests/scalar_features/step9_qchem_validation_v3.json",
        "qchem_step13_adapter_sha256": ROOT / "qchem_step13_stages.py",
        "runner_sha256": Path(__file__).resolve(),
        "slurm_script_sha256": ROOT / "slurm/run_step13_fresh_species_smoke_v1.sh",
        "fixed_orbital_control_amendment_sha256": CONTROL_AMENDMENT,
    }
    observed = {name: sha256(path) for name, path in paths.items()}
    if observed != manifest.get("authorities"):
        raise ValueError(f"fresh-species authority hash mismatch: {observed}")
    build = manifest["qchem_build"]
    if sha256(QCHEM_ROOT / "bin/qchem") != build["qchem_launcher_sha256"]:
        raise ValueError("Q-Chem launcher differs from frozen contract")
    if sha256(QCHEM_ROOT / "exe/qcprog.exe") != build["qcprog_executable_sha256"]:
        raise ValueError("Q-Chem executable differs from frozen contract")


def qchem_environment(scratch_parent: Path, print_integrated_dv: bool) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update({
        "QC": str(QCHEM_ROOT),
        "QCPROG": str(QCHEM_ROOT / "exe/qcprog.exe"),
        "QCAUX": QCAUX,
        "QCSCRATCH": str(scratch_parent),
    })
    environment.pop("QCLOCALSCR", None)
    environment.pop("QCHEM_DUMP_INTEGRATED_DV_INPUTS", None)
    if print_integrated_dv:
        environment["QCHEM_PRINT_INTEGRATED_DV"] = "1"
    else:
        environment.pop("QCHEM_PRINT_INTEGRATED_DV", None)
    return environment


def run_qchem(case_root: Path, input_name: str, output_name: str, save_name: str, cpus: int, print_integrated_dv: bool) -> float:
    started = time.perf_counter()
    with (case_root / f"{output_name}.launch.stdout").open("wb") as stdout, (case_root / f"{output_name}.launch.stderr").open("wb") as stderr:
        subprocess.run(
            [str(QCHEM_ROOT / "bin/qchem"), "-save", "-nt", str(cpus), str(case_root / input_name), str(case_root / output_name), save_name],
            env=qchem_environment(case_root / "qcscratch", print_integrated_dv),
            stdout=stdout,
            stderr=stderr,
            check=True,
        )
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--cpus", required=True, type=int)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest, case = load_frozen_case(manifest_path, args.species, args.cpus)
    validate_frozen_authorities(manifest)
    species_root = Path(manifest["run_root"]).resolve() / case["scope"] / args.species
    if species_root.exists():
        raise FileExistsError(f"refusing to overwrite fresh Step-13 species root: {species_root}")
    species_root.mkdir(parents=True)
    work_root = species_root / "gateway_work"
    work_root.mkdir()
    started = time.perf_counter()
    timings: dict[str, Any] = {}
    try:
        input_source = Path(case["authoritative_input"])
        orbital_source = Path(case["orbital_root"])
        if sha256(input_source) != case["authoritative_input_sha256"]:
            raise ValueError("authoritative Q-Chem input hash mismatch")
        if sha256(orbital_source / "qarchive.h5") != case["qarchive_sha256"]:
            raise ValueError("authoritative qarchive hash mismatch")
        tree_started = time.perf_counter()
        source_tree = tree_manifest(orbital_source)
        observed_tree = {"files": len(source_tree), "bytes": sum(int(row["bytes"]) for row in source_tree), "manifest_sha256": canonical_tree_hash(source_tree)}
        timings["authoritative_tree_hash_seconds"] = time.perf_counter() - tree_started
        if observed_tree != case["source_tree"]:
            raise ValueError(f"authoritative orbital tree changed: {observed_tree}")

        staged = work_root / "staged_orbitals"
        copy_started = time.perf_counter()
        shutil.copytree(orbital_source, staged, copy_function=shutil.copy2)
        timings["archive_copy_seconds"] = time.perf_counter() - copy_started
        if tree_manifest(staged) != source_tree:
            raise ValueError("staged orbital tree differs from authoritative source")

        q4_dirs: dict[str, Path] = {}
        grid_timings = {}
        for grid in manifest["grids"]:
            grid_id = str(grid["id"])
            grid_root = work_root / "grids" / grid_id
            scratch = grid_root / "qcscratch" / "step13_grid"
            grid_root.mkdir(parents=True)
            shutil.copy2(input_source, grid_root / "input.authoritative.in")
            (grid_root / "input.q3.in").write_text(
                derive_input(input_source.read_text(encoding="utf-8"), str(grid["qchem_value"]), skip_post_fock_diagonalization=True),
                encoding="utf-8",
            )
            shutil.copytree(staged, scratch, copy_function=shutil.copy2)
            copy_tree = tree_manifest(scratch)
            if copy_tree != source_tree:
                raise ValueError(f"isolated grid copy differs for {grid_id}")
            prepared = {
                "species": args.species,
                "role": case["role"],
                "grid": grid_id,
                "case_root": str(grid_root.resolve()),
                "source_orbital_root": str(orbital_source.resolve()),
                "source_tree": source_tree,
                "copy_tree": copy_tree,
                "source_copy_tree_identity": True,
                "authoritative_input_sha256": sha256(input_source),
                "derived_input_sha256": sha256(grid_root / "input.q3.in"),
                "mp2_restart_no_scf_required": True,
                "q6_control_amendment": str(CONTROL_AMENDMENT.resolve()),
                "q6_control_amendment_sha256": sha256(CONTROL_AMENDMENT),
            }
            (grid_root / "PREPARED.json").write_text(json.dumps(prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            qchem_seconds = run_qchem(grid_root, "input.q3.in", "qchem.out", "step13_grid", args.cpus, True)
            q4_dir = work_root / "q4" / grid_id
            action, _ = publish_or_resume(grid_root, q4_dir)
            if action != "published":
                raise RuntimeError("fresh integratedDV source was unexpectedly reused")
            q4_dirs[grid_id] = q4_dir
            grid_timings[grid_id] = {"qchem_seconds": qchem_seconds}
        timings["grids"] = grid_timings

        scalar_root = work_root / "scalar"
        scalar_scratch = scalar_root / "qcscratch" / "step9_scalar"
        scalar_root.mkdir(parents=True)
        shutil.copy2(input_source, scalar_root / "input.authoritative.in")
        source_text = input_source.read_text(encoding="utf-8")
        scalar_input, scalar_controls = derive_scalar_input(source_text)
        pt2_input, pt2_controls = derive_pt2_input(source_text)
        (scalar_root / "input.step9.in").write_text(scalar_input, encoding="utf-8")
        (scalar_root / "input.step9.pt2.in").write_text(pt2_input, encoding="utf-8")
        shutil.copytree(staged, scalar_scratch, copy_function=shutil.copy2)
        scalar_copy_tree = tree_manifest(scalar_scratch)
        if scalar_copy_tree != source_tree:
            raise ValueError("isolated scalar copy differs from authoritative source")
        scalar_prepared = {
            "species": args.species,
            "role": case["role"],
            "authoritative_input": str(input_source.resolve()),
            "authoritative_input_sha256": sha256(input_source),
            "source_orbital_root": str(orbital_source.resolve()),
            "source_tree": source_tree,
            "copy_tree": scalar_copy_tree,
            "controls": scalar_controls,
            "pt2_controls": pt2_controls,
        }
        (scalar_root / "PREPARED.json").write_text(json.dumps(scalar_prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        timings["scalar_sr_vv10_qchem_seconds"] = run_qchem(scalar_root, "input.step9.in", "qchem.out", "step9_scalar", args.cpus, False)
        timings["scalar_pt2_qchem_seconds"] = run_qchem(scalar_root, "input.step9.pt2.in", "qchem.pt2.out", "step9_scalar", args.cpus, False)
        (scalar_root / "QCHEM_COMPLETE").write_text("complete\n", encoding="utf-8")
        publish_scalar_case(scalar_root)

        authorities = dict(manifest["authorities"])
        authorities["fresh_species_contract_sha256"] = sha256(manifest_path)
        report = publish_species_from_validated_gateway(
            identity={"scope": case["scope"], "species": args.species, "source_record_sha256": case["source_record_sha256"]},
            authorities=authorities,
            q4_dirs=q4_dirs,
            scalar_dir=scalar_root / "published",
            species_root=species_root,
        )
        summary = {
            "schema_version": 1,
            "status": "fresh_step13_species_complete_and_validated",
            "species": args.species,
            "scope": case["scope"],
            "manifest": str(manifest_path),
            "manifest_sha256": sha256(manifest_path),
            "timings": timings,
            "total_wall_seconds": time.perf_counter() - started,
            "child_max_rss_mb": float(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss) / 1024.0,
            "boundary_actions": {name: boundary["action"] for name, boundary in report["boundaries"].items()},
            "feature_vector_sha256": sha256(species_root / "assembly/feature_vector_292.npy"),
            "bulk_submission_authorized": False,
        }
        (species_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (species_root / "FRESH_SPECIES_COMPLETE").write_text("complete\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except BaseException:
        (species_root / "FAILURE.json").write_text(json.dumps({"schema_version": 1, "status": "fresh_step13_species_failed", "species": args.species, "exception": traceback.format_exc()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
