#!/usr/bin/env python3
"""Independently validate a completed Step-14 reaction assembly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml

from revwb97m2.qchem_scalar_features import sha256


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "manifests/reaction_features/step14_reaction_assembly_v1.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    cohort_path = Path(contract["cohort_contract"])
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    output = Path(contract["output_root"])
    manifest = json.loads((output / "assembly_manifest.json").read_text(encoding="utf-8"))
    names = json.loads((output / "reaction_names.json").read_text(encoding="utf-8"))
    feature = np.load(output / "feature_matrix_20x292.npy", allow_pickle=False)
    fixed = np.load(output / "fixed_energy_20.npy", allow_pickle=False)
    reference = np.load(output / "reference_energy_20.npy", allow_pickle=False)
    target = np.load(output / "target_reference_minus_fixed_20.npy", allow_pickle=False)
    weight = np.load(output / "objective_weight_20.npy", allow_pickle=False)
    differences = {
        grid: np.load(output / f"grid_difference_{grid}_minus_250974_20x292.npy", allow_pickle=False)
        for grid in contract["comparison_grid_ids"]
    }
    species_vectors = {}
    species_fixed = {}
    species_differences = {}
    species_artifacts_valid = True
    for case in cohort["cases"]:
        species = case["species"]
        ready = Path(cohort["run_root"]) / case["scope"] / species / "reaction_ready"
        ready_manifest = json.loads((ready / "reaction_ready_manifest.json").read_text(encoding="utf-8"))
        species_artifacts_valid &= (
            (ready / "REACTION_READY_COMPLETE").is_file()
            and ready_manifest["species"] == species
            and ready_manifest["cohort_contract_sha256"] == sha256(cohort_path)
            and all(sha256(ready / filename) == digest for filename, digest in ready_manifest["artifacts_sha256"].items())
        )
        species_vectors[species] = np.load(ready / "feature_vector_292.npy", allow_pickle=False)
        fixed_payload = json.loads((ready / "fixed_energy.json").read_text(encoding="utf-8"))
        species_fixed[species] = float(fixed_payload["values"]["fixed_energy_hartree"])
        species_differences[species] = {
            grid: np.load(ready / f"grid_difference_{grid}_minus_250974.npy", allow_pickle=False)
            for grid in contract["comparison_grid_ids"]
        }
    recomputed_feature = []
    recomputed_fixed = []
    recomputed_differences = {grid: [] for grid in contract["comparison_grid_ids"]}
    for reaction in cohort["reactions"]:
        row = np.zeros(292, dtype=np.float64)
        fixed_value = 0.0
        grid_rows = {grid: np.zeros(292, dtype=np.float64) for grid in contract["comparison_grid_ids"]}
        for term in reaction["stoichiometry"]:
            coefficient = float(term["coefficient"])
            species = term["species"]
            row += coefficient * species_vectors[species]
            fixed_value += coefficient * species_fixed[species]
            for grid in contract["comparison_grid_ids"]:
                grid_rows[grid] += coefficient * species_differences[species][grid]
        recomputed_feature.append(row)
        recomputed_fixed.append(fixed_value)
        for grid in contract["comparison_grid_ids"]:
            recomputed_differences[grid].append(grid_rows[grid])
    checks = {
        "completion_marker": (output / "ASSEMBLY_COMPLETE").read_text(encoding="utf-8") == "complete\n",
        "status": manifest["status"] == "step14_real_reaction_assembly_complete",
        "contract_hash": manifest["assembly_contract_sha256"] == sha256(contract_path),
        "cohort_hash": manifest["cohort_contract_sha256"] == sha256(cohort_path),
        "dimensions": feature.shape == (20, 292) and fixed.shape == reference.shape == target.shape == weight.shape == (20,),
        "grid_dimensions": all(array.shape == (20, 292) for array in differences.values()),
        "finite": all(np.isfinite(array).all() for array in (feature, fixed, reference, target, weight, *differences.values())),
        "positive_weights": bool(np.all(weight > 0.0)),
        "target_identity_exact": bool(np.array_equal(target, reference - fixed)),
        "reaction_order": names == [row["reaction"] for row in cohort["reactions"]],
        "reference_exact": bool(np.array_equal(reference, np.asarray([row["reference_hartree"] for row in cohort["reactions"]]))),
        "weight_exact": bool(np.array_equal(weight, np.asarray([row["objective_weight"] for row in cohort["reactions"]]))),
        "species_artifacts_valid": bool(species_artifacts_valid),
        "stoichiometric_feature_reassembly_exact": bool(np.array_equal(feature, np.stack(recomputed_feature))),
        "stoichiometric_fixed_reassembly_exact": bool(np.array_equal(fixed, np.asarray(recomputed_fixed))),
        "stoichiometric_grid_reassembly_exact": all(np.array_equal(differences[grid], np.stack(rows)) for grid, rows in recomputed_differences.items()),
        "artifact_hashes": all(sha256(output / filename) == digest for filename, digest in manifest["artifacts_sha256"].items()),
    }
    report = {"status": "passed" if all(checks.values()) else "failed", "checks": checks, "reaction_count": len(names), "species_count": cohort["species_count"]}
    print(json.dumps(report, indent=2, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
