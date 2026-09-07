#!/usr/bin/env python3
"""Generate one Step-14 cohort species and its reaction-ready artifacts."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import yaml

from revwb97m2.qchem_scalar_features import derive_fixed_energy_input, parse_qchem_fixed_energy_output, sha256, tree_manifest
from revwb97m2.scripts.run_step13_fresh_species import main as run_step13_main, run_qchem


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/reaction_features/step14_real_reaction_cohort_v1.json"


def reaction_ready_valid(root: Path, species: str) -> bool:
    try:
        manifest_path = root / "reaction_ready_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return (
            manifest["status"] == "reaction_ready_species_complete_and_validated"
            and manifest["species"] == species
            and (root / "REACTION_READY_COMPLETE").is_file()
            and all((root / name).is_file() and sha256(root / name) == digest for name, digest in manifest["artifacts_sha256"].items())
        )
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-index", required=True, type=int)
    parser.add_argument("--cpus", required=True, type=int)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "frozen_before_results" or manifest.get("bulk_submission_authorized") is not False:
        raise ValueError("Step-14 cohort contract is not a frozen bounded smoke")
    authority_paths = {
        "cohort_runner_sha256": Path(__file__).resolve(),
        "cohort_slurm_sha256": ROOT / "slurm/run_step14_real_reaction_cohort_v1.sh",
        "qchem_scalar_features_sha256": ROOT / "qchem_scalar_features.py",
        "fixed_energy_validation_sha256": ROOT / "manifests/reaction_features/step14_fixed_energy_validation_v1.json",
        "dataset_eval_sha256": ROOT / "manifests/gscdb137/source/DatasetEval.csv",
        "training_entries_sha256": ROOT / "manifests/weights/coach_si_table2_final_cycle_entries.csv",
        "step12_inventory_sha256": ROOT / "manifests/step12/step12_fitting_inventory_v1.csv",
        "cohort_selector_sha256": ROOT / "scripts/freeze_step14_reaction_cohort.py",
    }
    observed_authorities = {name: sha256(path) for name, path in authority_paths.items()}
    if observed_authorities != manifest.get("step14_authorities"):
        raise ValueError(f"Step-14 cohort authority mismatch: {observed_authorities}")
    case = manifest["cases"][args.case_index]
    if args.cpus != int(case["resources"]["cpus"]):
        raise ValueError("allocated CPUs differ from frozen case")
    species = case["species"]
    species_root = Path(manifest["run_root"]) / case["scope"] / species
    marker = species_root / "FRESH_SPECIES_COMPLETE"
    step13_action = "reused"
    if not marker.is_file():
        if species_root.exists():
            raise RuntimeError(f"partial Step-13 root preserved for review: {species_root}")
        previous = sys.argv
        try:
            sys.argv = ["run_step13_fresh_species", "--species", species, "--cpus", str(args.cpus), "--manifest", str(manifest_path)]
            run_step13_main()
            step13_action = "published"
        finally:
            sys.argv = previous
    ready = species_root / "reaction_ready"
    if ready.exists():
        if not reaction_ready_valid(ready, species):
            raise RuntimeError(f"existing reaction-ready boundary is not reusable: {ready}")
        print(json.dumps({"species": species, "step13_action": step13_action, "reaction_ready_action": "reused"}, sort_keys=True))
        return 0

    work = species_root / "gateway_work/fixed_energy"
    if work.exists():
        raise RuntimeError(f"partial fixed-energy work preserved for review: {work}")
    work.mkdir(parents=True)
    source_input = Path(case["authoritative_input"])
    source_orbitals = Path(case["orbital_root"])
    scalar_root = species_root / "gateway_work/scalar/published"
    scalar_manifest_path = scalar_root / "scalar_manifest.json"
    scalar = json.loads(scalar_manifest_path.read_text(encoding="utf-8"))
    scratch = work / "qcscratch/fixed_energy"
    shutil.copytree(source_orbitals, scratch, copy_function=shutil.copy2)
    source_tree = tree_manifest(source_orbitals)
    if tree_manifest(scratch) != source_tree:
        raise ValueError("fixed-energy orbital copy differs from authority")
    derived, controls = derive_fixed_energy_input(source_input.read_text(encoding="utf-8"))
    shutil.copy2(source_input, work / "input.authoritative.in")
    (work / "input.fixed.in").write_text(derived, encoding="utf-8")
    (work / "PREPARED.json").write_text(json.dumps({"species": species, "source_tree": source_tree, "controls": controls, "derived_input_sha256": sha256(work / "input.fixed.in")}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fixed_seconds = run_qchem(work, "input.fixed.in", "qchem.out", "fixed_energy", args.cpus, False)
    fixed = parse_qchem_fixed_energy_output((work / "qchem.out").read_text(encoding="utf-8", errors="replace"), scalar["values_hartree"]["short_range_hf_hartree"])
    checks = {
        "normal_termination": fixed["normal_qchem_termination"] is True,
        "archive_read": int(fixed["archive_read_count"]) >= 2,
        "pure_hf_reconstruction": abs(float(fixed["pure_hf_reconstruction_error_hartree"])) <= 2.0e-8,
        "qarchive_unchanged": sha256(scratch / "qarchive.h5") == case["qarchive_sha256"],
        "source_tree_unchanged": tree_manifest(source_orbitals) == source_tree,
    }
    if not all(checks.values()):
        raise RuntimeError(f"fixed-energy checks failed: {checks}")
    temporary = ready.parent / f".{ready.name}.tmp.{os.getpid()}"
    temporary.mkdir()
    vector = np.load(species_root / "assembly/feature_vector_292.npy", allow_pickle=False)
    reference = np.load(species_root / "integrated_dv_250974/semilocal_features_288.npy", allow_pickle=False)
    np.save(temporary / "feature_vector_292.npy", vector, allow_pickle=False)
    for grid in ("99590", "75302"):
        comparison = np.load(species_root / f"integrated_dv_{grid}/semilocal_features_288.npy", allow_pickle=False)
        difference = np.concatenate((comparison - reference, np.zeros(4, dtype=np.float64)))
        np.save(temporary / f"grid_difference_{grid}_minus_250974.npy", difference, allow_pickle=False)
    fixed_payload = {"values": fixed, "checks": checks, "qchem_wall_seconds": fixed_seconds}
    (temporary / "fixed_energy.json").write_text(json.dumps(fixed_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifacts = {path.name: sha256(path) for path in temporary.iterdir() if path.is_file()}
    ready_manifest = {
        "schema_version": 1,
        "status": "reaction_ready_species_complete_and_validated",
        "scope": case["scope"],
        "species": species,
        "source_record_sha256": case["source_record_sha256"],
        "cohort_contract_sha256": sha256(manifest_path),
        "feature_model": "R2_coachform_292",
        "feature_count": 292,
        "fixed_energy_hartree": fixed["fixed_energy_hartree"],
        "grid_scalar_difference_policy": "zero_for_sr_hf_vv10_pt2_d4_because_only_semilocal_integratedDV_is_multi_grid",
        "artifacts_sha256": artifacts,
    }
    (temporary / "reaction_ready_manifest.json").write_text(json.dumps(ready_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (temporary / "REACTION_READY_COMPLETE").write_text("complete\n", encoding="utf-8")
    temporary.rename(ready)
    if not reaction_ready_valid(ready, species):
        raise RuntimeError("reaction-ready publication failed validation")
    print(json.dumps({"species": species, "step13_action": step13_action, "reaction_ready_action": "published", "fixed_qchem_seconds": fixed_seconds}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
