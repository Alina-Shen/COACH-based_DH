#!/usr/bin/env python3
"""Run one frozen pure-HF fixed-energy partition gateway."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import traceback
from pathlib import Path

import yaml

from revwb97m2.qchem_scalar_features import (
    derive_fixed_energy_input,
    parse_qchem_fixed_energy_output,
    sha256,
    tree_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/reaction_features/step14_fixed_energy_gateway_v1.yaml"
QCHEM_ROOT = Path("/clusterfs/mhg-data/yaoshen/qchem/trunk")
QCAUX = "/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-index", type=int, required=True)
    parser.add_argument("--cpus", type=int, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "frozen_before_results":
        raise ValueError("fixed-energy gateway must be frozen before results")
    observed_authorities = {
        "qchem_scalar_features_sha256": sha256(ROOT / "qchem_scalar_features.py"),
        "runner_sha256": sha256(Path(__file__).resolve()),
        "slurm_script_sha256": sha256(ROOT / "slurm/run_step14_fixed_energy_gateway_v1.sh"),
        "qcprog_executable_sha256": sha256(QCHEM_ROOT / "exe/qcprog.exe"),
    }
    if observed_authorities != manifest.get("authorities"):
        raise ValueError(f"fixed-energy gateway authority mismatch: {observed_authorities}")
    case = manifest["cases"][args.case_index]
    if args.cpus != int(case["resources"]["cpus"]):
        raise ValueError("allocated CPUs differ from frozen gateway contract")
    output_dir = Path(manifest["run_root"]) / case["species"]
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite fixed-energy gateway: {output_dir}")
    output_dir.mkdir(parents=True)
    try:
        source_input = Path(case["authoritative_input"])
        source_orbitals = Path(case["orbital_root"])
        scalar_dir = Path(case["scalar_artifact"])
        scalar_manifest_path = scalar_dir / "scalar_manifest.json"
        scalar = json.loads(scalar_manifest_path.read_text(encoding="utf-8"))
        if sha256(source_input) != case["authoritative_input_sha256"]:
            raise ValueError("authoritative input changed")
        if sha256(source_orbitals / "qarchive.h5") != case["qarchive_sha256"]:
            raise ValueError("authoritative qarchive changed")
        if sha256(scalar_manifest_path) != case["scalar_manifest_sha256"]:
            raise ValueError("Step-9 scalar authority changed")
        if scalar["species"] != case["species"] or not all(scalar["checks"].values()):
            raise ValueError("Step-9 scalar identity or validation mismatch")
        source_tree = tree_manifest(source_orbitals)
        scratch = output_dir / "qcscratch" / "fixed_energy"
        shutil.copytree(source_orbitals, scratch, copy_function=shutil.copy2)
        copy_tree = tree_manifest(scratch)
        if copy_tree != source_tree:
            raise ValueError("isolated fixed-energy orbital copy differs")
        derived, controls = derive_fixed_energy_input(source_input.read_text(encoding="utf-8"))
        shutil.copy2(source_input, output_dir / "input.authoritative.in")
        (output_dir / "input.fixed.in").write_text(derived, encoding="utf-8")
        prepared = {
            "species": case["species"],
            "authoritative_input_sha256": sha256(source_input),
            "source_tree": source_tree,
            "copy_tree": copy_tree,
            "derived_input_sha256": sha256(output_dir / "input.fixed.in"),
            "scalar_manifest_sha256": sha256(scalar_manifest_path),
            "controls": controls,
        }
        (output_dir / "PREPARED.json").write_text(json.dumps(prepared, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        environment = os.environ.copy()
        environment.update({"QC": str(QCHEM_ROOT), "QCPROG": str(QCHEM_ROOT / "exe/qcprog.exe"), "QCAUX": QCAUX, "QCSCRATCH": str(output_dir / "qcscratch")})
        for name in ("QCLOCALSCR", "QCHEM_PRINT_INTEGRATED_DV", "QCHEM_DUMP_INTEGRATED_DV_INPUTS"):
            environment.pop(name, None)
        with (output_dir / "qchem.launch.stdout").open("wb") as stdout, (output_dir / "qchem.launch.stderr").open("wb") as stderr:
            subprocess.run([str(QCHEM_ROOT / "bin/qchem"), "-save", "-nt", str(args.cpus), str(output_dir / "input.fixed.in"), str(output_dir / "qchem.out"), "fixed_energy"], env=environment, stdout=stdout, stderr=stderr, check=True)
        parsed = parse_qchem_fixed_energy_output((output_dir / "qchem.out").read_text(encoding="utf-8", errors="replace"), scalar["values_hartree"]["short_range_hf_hartree"])
        checks = {
            "normal_qchem_termination": parsed["normal_qchem_termination"] is True,
            "archive_read": int(parsed["archive_read_count"]) >= 2,
            "pure_hf_reconstruction": abs(float(parsed["pure_hf_reconstruction_error_hartree"])) <= float(manifest["tolerances_hartree"]["pure_hf_reconstruction"]),
            "post_run_qarchive_identity": sha256(scratch / "qarchive.h5") == case["qarchive_sha256"],
            "source_tree_unchanged": tree_manifest(source_orbitals) == source_tree,
        }
        expected = case.get("cross_code_reference")
        errors = {}
        if expected:
            for name, reference in expected["values_hartree"].items():
                errors[name] = abs(float(parsed[name]) - float(reference))
            checks["cross_code_components"] = all(error <= float(manifest["tolerances_hartree"]["cross_code_component"]) for error in errors.values())
        report = {
            "schema_version": 1,
            "status": "qchem_fixed_energy_complete_and_validated",
            "species": case["species"],
            "contract_sha256": sha256(manifest_path),
            "scalar_manifest_sha256": sha256(scalar_manifest_path),
            "values": parsed,
            "cross_code_absolute_errors_hartree": errors,
            "checks": checks,
        }
        if not all(checks.values()):
            raise RuntimeError(f"fixed-energy validation failed: {checks}")
        (output_dir / "fixed_energy.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (output_dir / "FIXED_ENERGY_COMPLETE").write_text("complete\n", encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except BaseException:
        (output_dir / "FAILURE.json").write_text(json.dumps({"status": "qchem_fixed_energy_failed", "species": case["species"], "exception": traceback.format_exc()}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
