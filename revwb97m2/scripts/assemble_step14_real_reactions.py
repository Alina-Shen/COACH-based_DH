#!/usr/bin/env python3
"""Assemble the frozen Step-14 species artifacts into real reactions."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import yaml

from revwb97m2.qchem_scalar_features import sha256
from revwb97m2.reaction_assembly import FEATURE_COUNT, assemble_reaction_arrays


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "manifests/reaction_features/step14_reaction_assembly_v1.yaml"


def load_species(cohort: dict) -> tuple[dict, dict, dict]:
    vectors: dict[str, np.ndarray] = {}
    fixed: dict[str, float] = {}
    differences: dict[str, dict[str, np.ndarray]] = {}
    cohort_sha = sha256(Path(cohort["contract_path"]))
    for case in cohort["cases"]:
        species = case["species"]
        ready = Path(cohort["run_root"]) / case["scope"] / species / "reaction_ready"
        marker = ready / "REACTION_READY_COMPLETE"
        manifest_path = ready / "reaction_ready_manifest.json"
        if not marker.is_file() or not manifest_path.is_file():
            raise FileNotFoundError(f"species is not reaction-ready: {species}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "reaction_ready_species_complete_and_validated" or manifest.get("species") != species or manifest.get("cohort_contract_sha256") != cohort_sha:
            raise ValueError(f"invalid reaction-ready manifest for {species}")
        for filename, digest in manifest["artifacts_sha256"].items():
            if sha256(ready / filename) != digest:
                raise ValueError(f"reaction-ready artifact hash mismatch for {species}: {filename}")
        vectors[species] = np.load(ready / "feature_vector_292.npy", allow_pickle=False)
        fixed_payload = json.loads((ready / "fixed_energy.json").read_text(encoding="utf-8"))
        fixed[species] = float(fixed_payload["values"]["fixed_energy_hartree"])
        differences[species] = {
            grid: np.load(ready / f"grid_difference_{grid}_minus_250974.npy", allow_pickle=False)
            for grid in cohort["comparison_grid_ids"]
        }
    return vectors, fixed, differences


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if contract.get("status") != "frozen_before_results" or contract.get("bulk_submission_authorized") is not False:
        raise ValueError("assembly contract is not a frozen bounded smoke")
    authority_paths = {
        "assembler_sha256": Path(__file__).resolve(),
        "validator_sha256": ROOT / "scripts/validate_step14_real_reactions.py",
        "reaction_assembly_module_sha256": ROOT / "reaction_assembly.py",
        "cohort_contract_sha256": Path(contract["cohort_contract"]),
    }
    observed = {key: sha256(path) for key, path in authority_paths.items()}
    if observed != contract["authorities"]:
        raise ValueError(f"assembly authority mismatch: {observed}")
    cohort = json.loads(Path(contract["cohort_contract"]).read_text(encoding="utf-8"))
    cohort["contract_path"] = contract["cohort_contract"]
    cohort["comparison_grid_ids"] = contract["comparison_grid_ids"]
    if len(cohort["reactions"]) != contract["expected_reaction_count"] or len(cohort["cases"]) != contract["expected_species_count"]:
        raise ValueError("cohort dimensions differ from frozen assembly contract")
    output = Path(contract["output_root"])
    if output.exists():
        raise FileExistsError(f"refusing to overwrite {output}")
    vectors, fixed, differences = load_species(cohort)
    assembled = assemble_reaction_arrays(cohort["reactions"], vectors, fixed, differences, contract["comparison_grid_ids"])
    temporary = output.parent / f".{output.name}.tmp.{os.getpid()}"
    temporary.mkdir(parents=True)
    artifacts: dict[str, str] = {}
    arrays = {
        "feature_matrix_20x292.npy": assembled["feature_matrix"],
        "fixed_energy_20.npy": assembled["fixed_energy"],
        "reference_energy_20.npy": assembled["reference_energy"],
        "target_reference_minus_fixed_20.npy": assembled["target"],
        "objective_weight_20.npy": assembled["objective_weight"],
    }
    for grid, array in assembled["grid_differences"].items():
        arrays[f"grid_difference_{grid}_minus_250974_20x292.npy"] = array
    for filename, array in arrays.items():
        np.save(temporary / filename, array, allow_pickle=False)
        artifacts[filename] = sha256(temporary / filename)
    names_path = temporary / "reaction_names.json"
    names_path.write_text(json.dumps(assembled["reaction_names"], indent=2) + "\n", encoding="utf-8")
    artifacts[names_path.name] = sha256(names_path)
    manifest = {
        "schema_version": 1,
        "status": "step14_real_reaction_assembly_complete",
        "assembly_contract_sha256": sha256(contract_path),
        "cohort_contract_sha256": sha256(Path(contract["cohort_contract"])),
        "reaction_count": len(assembled["reaction_names"]),
        "species_count": len(cohort["cases"]),
        "feature_count": FEATURE_COUNT,
        "target_identity": "reference_energy_hartree - fixed_energy_hartree",
        "stoichiometry_policy": "exact_frozen_benchmark_coefficients; charge_balance_not_required_for_charge-changing_energy_differences",
        "artifacts_sha256": artifacts,
    }
    (temporary / "assembly_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (temporary / "ASSEMBLY_COMPLETE").write_text("complete\n", encoding="utf-8")
    temporary.rename(output)
    print(json.dumps({"output": str(output), "reaction_count": manifest["reaction_count"], "species_count": manifest["species_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
