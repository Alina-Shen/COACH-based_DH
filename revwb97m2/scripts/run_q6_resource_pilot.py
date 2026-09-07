#!/usr/bin/env python3
"""Run one frozen Q6 Q-Chem archive/grid/extraction/D4 resource pilot."""

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

import numpy as np
import yaml
from dftd4.interface import DampingParam, DispersionModel
from pyscf.data import elements

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.parent_scf import input_artifact_paths, load_record, load_spec  # noqa: E402
from revwb97m2.qchem_feature_publisher import publish_or_resume, sha256  # noqa: E402
from revwb97m2.scripts.prepare_q3_qchem_gateway import derive_input, tree_manifest  # noqa: E402


DEFAULT_MANIFEST = ROOT / "manifests/qchem_gateway/q6_resource_pilots_v1.yaml"
DEFAULT_RUN_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q6_resource_pilots_v1"
)
QCHEM_ROOT = Path("/clusterfs/mhg-data/yaoshen/qchem/trunk")
RETRY_CONTROL_AMENDMENT = ROOT / "manifests/qchem_gateway/q6_retry2_control_amendment_v1.yaml"
QCAUX = "/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux"
BOHR_ANGSTROM = 0.529177210903
D4_PARAMETERS = {"s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0}


def canonical_tree_hash(records: list[dict[str, object]]) -> str:
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def child_max_rss_mb() -> float:
    return float(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss) / 1024.0


def d4_atm(species: str, expected_record_hash: str) -> tuple[float, int]:
    spec = load_spec()
    record, _ = load_record(input_artifact_paths(spec)["records"], species)
    if record["record_sha256"] != expected_record_hash:
        raise ValueError("Q6 pilot source-record hash mismatch")
    molecule = record["pyscf_molecule"]
    if molecule["unit"].lower() != "angstrom" or molecule["ghost_atom_count"] != 0:
        raise ValueError("Q6 D4 pilot requires a real-atom Angstrom geometry")
    numbers = []
    positions = []
    for line in molecule["atom"].splitlines():
        fields = line.split()
        if len(fields) != 4:
            raise ValueError(f"malformed atom line: {line}")
        numbers.append(elements.charge(fields[0]))
        positions.append([float(value) / BOHR_ANGSTROM for value in fields[1:]])
    if len(numbers) != molecule["real_atom_count"]:
        raise ValueError("Q6 D4 atom-count mismatch")
    model = DispersionModel(
        numbers=np.asarray(numbers, dtype=int),
        positions=np.asarray(positions, dtype=float),
        charge=float(molecule["charge"]),
    )
    energy = float(model.get_dispersion(DampingParam(**D4_PARAMETERS), grad=False)["energy"])
    if not np.isfinite(energy):
        raise FloatingPointError("non-finite Q6 D4-ATM energy")
    return energy, len(numbers)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--cpus", required=True, type=int)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if manifest["status"] != "frozen_before_results":
        raise ValueError("Q6 resource manifest must be frozen before results")
    matches = [row for row in manifest["cases"] if row["species"] == args.species]
    if len(matches) != 1:
        raise ValueError(f"expected one frozen Q6 case for {args.species}")
    case = matches[0]
    if args.cpus != int(case["resources"]["cpus"]):
        raise ValueError("allocated CPU count differs from frozen Q6 resources")
    run_root = args.run_root.resolve()
    species_root = run_root / args.species
    if species_root.exists():
        raise FileExistsError(f"refusing to overwrite Q6 pilot: {species_root}")
    species_root.mkdir(parents=True)
    started_total = time.perf_counter()
    try:
        source_root = Path(manifest["authorities"]["orbital_root"]) / args.species
        input_source = Path(manifest["authorities"]["authoritative_input_root"]) / args.species / "input0"
        if sha256(input_source) != case["authoritative_input_sha256"]:
            raise ValueError("Q6 authoritative input hash mismatch")
        hash_started = time.perf_counter()
        source_tree = tree_manifest(source_root)
        source_hash_seconds = time.perf_counter() - hash_started
        observed_tree = {
            "files": len(source_tree),
            "bytes": sum(int(row["bytes"]) for row in source_tree),
            "manifest_sha256": canonical_tree_hash(source_tree),
        }
        if observed_tree != case["source_tree"]:
            raise ValueError(f"Q6 authoritative orbital tree changed: {observed_tree}")

        staged_root = species_root / "staged_orbitals"
        copy_started = time.perf_counter()
        shutil.copytree(source_root, staged_root, copy_function=shutil.copy2)
        source_to_stage_seconds = time.perf_counter() - copy_started
        staged_tree = tree_manifest(staged_root)
        if staged_tree != source_tree:
            raise ValueError("Q6 staged orbital tree differs from authoritative source")

        grid_reports = []
        for grid in manifest["grids"]:
            grid_id = str(grid["id"])
            case_root = species_root / "cases" / grid_id
            scratch_root = case_root / "qcscratch" / "q6_gateway"
            case_root.mkdir(parents=True)
            shutil.copy2(input_source, case_root / "input.authoritative.in")
            (case_root / "input.q3.in").write_text(
                derive_input(
                    input_source.read_text(encoding="utf-8"),
                    str(grid["qchem_value"]),
                    skip_post_fock_diagonalization=True,
                ),
                encoding="utf-8",
            )
            grid_copy_started = time.perf_counter()
            shutil.copytree(staged_root, scratch_root, copy_function=shutil.copy2)
            grid_copy_seconds = time.perf_counter() - grid_copy_started
            copy_tree = tree_manifest(scratch_root)
            if copy_tree != source_tree:
                raise ValueError(f"Q6 isolated grid copy differs for {grid_id}")
            prepared = {
                "species": args.species,
                "role": case["size_role"],
                "grid": grid_id,
                "case_root": str(case_root.resolve()),
                "source_orbital_root": str(source_root.resolve()),
                "source_tree": source_tree,
                "copy_tree": copy_tree,
                "source_copy_tree_identity": True,
                "authoritative_input_sha256": sha256(input_source),
                "derived_input_sha256": sha256(case_root / "input.q3.in"),
                "mp2_restart_no_scf_required": True,
                "q6_control_amendment": str(RETRY_CONTROL_AMENDMENT),
                "q6_control_amendment_sha256": sha256(RETRY_CONTROL_AMENDMENT),
            }
            (case_root / "PREPARED.json").write_text(
                json.dumps(prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "QC": str(QCHEM_ROOT),
                    "QCPROG": str(QCHEM_ROOT / "exe/qcprog.exe"),
                    "QCAUX": QCAUX,
                    "QCSCRATCH": str(case_root / "qcscratch"),
                    "QCHEM_PRINT_INTEGRATED_DV": "1",
                }
            )
            environment.pop("QCLOCALSCR", None)
            environment.pop("QCHEM_DUMP_INTEGRATED_DV_INPUTS", None)
            qchem_started = time.perf_counter()
            with (case_root / "qchem.launch.stdout").open("wb") as stdout, (case_root / "qchem.launch.stderr").open("wb") as stderr:
                subprocess.run(
                    [str(QCHEM_ROOT / "bin/qchem"), "-save", "-nt", str(args.cpus),
                     str(case_root / "input.q3.in"), str(case_root / "qchem.out"), "q6_gateway"],
                    env=environment, stdout=stdout, stderr=stderr, check=True,
                )
            qchem_seconds = time.perf_counter() - qchem_started
            feature_root = species_root / "features" / grid_id
            extraction_started = time.perf_counter()
            action, feature_manifest = publish_or_resume(case_root, feature_root)
            extraction_seconds = time.perf_counter() - extraction_started
            if action != "published":
                raise RuntimeError("fresh Q6 feature boundary was unexpectedly reused")
            restart_started = time.perf_counter()
            restart_action, _ = publish_or_resume(case_root, feature_root)
            restart_seconds = time.perf_counter() - restart_started
            if restart_action != "reused":
                raise RuntimeError("Q6 restart did not reuse the validated feature boundary")
            grid_reports.append(
                {
                    "grid": grid_id,
                    "isolated_copy_seconds": grid_copy_seconds,
                    "isolated_copy_bytes": observed_tree["bytes"],
                    "qchem_wall_seconds": qchem_seconds,
                    "qchem_output_bytes": (case_root / "qchem.out").stat().st_size,
                    "extraction_publication_seconds": extraction_seconds,
                    "restart_revalidation_seconds": restart_seconds,
                    "complete_block_count": feature_manifest["complete_block_count"],
                    "feature_artifact_bytes": directory_bytes(feature_root),
                    "feature_manifest_sha256": sha256(feature_root / "qchem_integrated_dv_manifest.json"),
                    "child_max_rss_mb_after_grid": child_max_rss_mb(),
                }
            )

        d4_started = time.perf_counter()
        d4_energy, atom_count = d4_atm(args.species, case["source_record_sha256"])
        d4_seconds = time.perf_counter() - d4_started
        d4_root = species_root / "d4_atm"
        d4_root.mkdir()
        d4_payload = {
            "definition": "pure_three_body_coach_d4_atm",
            "damping_parameters": D4_PARAMETERS,
            "energy_hartree": d4_energy,
            "atom_count": atom_count,
            "wall_seconds": d4_seconds,
            "source_record_sha256": case["source_record_sha256"],
        }
        (d4_root / "d4_atm.json").write_text(json.dumps(d4_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary = {
            "schema_version": 1,
            "status": "q6_resource_pilot_complete_and_validated",
            "species": args.species,
            "size_role": case["size_role"],
            "manifest": str(manifest_path),
            "manifest_sha256": sha256(manifest_path),
            "resources": case["resources"],
            "measurements": {
                "authoritative_tree_hash_seconds": source_hash_seconds,
                "source_to_stage_copy_seconds": source_to_stage_seconds,
                "source_tree": observed_tree,
                "grid_reports": grid_reports,
                "d4_atm": d4_payload,
                "total_wall_seconds": time.perf_counter() - started_total,
                "child_max_rss_mb": child_max_rss_mb(),
            },
        }
        (species_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (species_root / "Q6_PILOT_COMPLETE").write_text("complete\n", encoding="utf-8")
        summary["measurements"]["total_retained_bytes"] = directory_bytes(species_root)
        (species_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except BaseException:
        (species_root / "FAILURE.json").write_text(
            json.dumps(
                {"schema_version": 1, "status": "q6_resource_pilot_failed", "species": args.species,
                 "exception": traceback.format_exc()},
                indent=2, sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
