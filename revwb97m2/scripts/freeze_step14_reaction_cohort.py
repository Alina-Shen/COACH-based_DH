#!/usr/bin/env python3
"""Freeze the deterministic seven-class Step-14 real-reaction cohort."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

import yaml

from revwb97m2.qchem_scalar_features import sha256, tree_manifest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "manifests/reaction_features/step14_real_reaction_cohort_v1.json"
QUOTAS = {"BH": 3, "EF": 3, "ISO": 3, "INC": 2, "NC": 4, "TC": 3, "TM": 2}


def parse_stoichiometry(text: str) -> list[tuple[float, str]]:
    fields = text.split(",")
    if len(fields) % 2:
        raise ValueError(f"odd stoichiometry: {text}")
    return [(float(fields[index]), fields[index + 1]) for index in range(0, len(fields), 2)]


def canonical_tree_summary(root: Path) -> dict[str, object]:
    records = tree_manifest(root)
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    return {"files": len(records), "bytes": sum(int(row["bytes"]) for row in records), "manifest_sha256": hashlib.sha256(payload).hexdigest()}


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    inventory_path = ROOT / "manifests/step12/step12_fitting_inventory_v1.csv"
    dataset_path = ROOT / "manifests/gscdb137/source/DatasetEval.csv"
    entries_path = ROOT / "manifests/weights/coach_si_table2_final_cycle_entries.csv"
    inventory = {row["species"]: row for row in csv.DictReader(inventory_path.open(encoding="utf-8"))}
    dataset = {row["Reaction"]: row for row in csv.DictReader(dataset_path.open(encoding="utf-8"))}
    entries = list(csv.DictReader(entries_path.open(encoding="utf-8")))
    candidates: dict[str, list[tuple[int, int, dict[str, str], dict[str, str], list[tuple[float, str]]]]] = defaultdict(list)
    for entry in entries:
        reaction = dataset[entry["reaction"]]
        stoichiometry = parse_stoichiometry(reaction["Stoichiometry"])
        if len(stoichiometry) != 2:
            continue
        if not all(species in inventory and inventory[species]["tier"] == "small_mhg" and int(inventory[species]["memory_class_mb"]) <= 7500 for _, species in stoichiometry):
            continue
        cost = sum(int(inventory[species]["orbital_aos"]) for _, species in stoichiometry)
        candidates[entry["property_class"]].append((cost, int(entry["global_index"]), entry, reaction, stoichiometry))
    chosen = []
    for property_class, count in QUOTAS.items():
        rows = sorted(candidates[property_class])[:count]
        if len(rows) != count:
            raise RuntimeError(f"insufficient candidates for {property_class}")
        chosen.extend(rows)
    chosen.sort(key=lambda row: row[1])
    reactions = []
    species_names = set()
    for cost, global_index, entry, reaction, stoichiometry in chosen:
        species_names.update(species for _, species in stoichiometry)
        reactions.append({
            "reaction": entry["reaction"],
            "dataset": entry["dataset_eval_dataset"],
            "property_class": entry["property_class"],
            "training_global_index": global_index,
            "objective_weight": float(entry["objective_weight"]),
            "reference_hartree": float(reaction["Reference"]),
            "orbital_ao_cost_proxy": cost,
            "stoichiometry": [{"coefficient": coefficient, "species": species} for coefficient, species in stoichiometry],
        })
    cases = []
    for species in sorted(species_names):
        row = inventory[species]
        orbital_root = Path("/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2") / species
        input_path = Path(row["qchem_input_path"])
        cases.append({
            "species": species,
            "scope": row["scope"],
            "role": "step14_real_reaction_cohort_species",
            "source_record_sha256": row["source_record_sha256"],
            "authoritative_input": str(input_path),
            "authoritative_input_sha256": row["qchem_input_sha256"],
            "orbital_root": str(orbital_root),
            "qarchive_sha256": sha256(orbital_root / "qarchive.h5"),
            "source_tree": canonical_tree_summary(orbital_root),
            "resources": {"partition": row["partition"], "account": row["account"], "qos": row["qos"], "cpus": int(row["cpus"]), "memory_class_mb": int(row["memory_class_mb"]), "requested_memory_gib": int(row["requested_memory_gib"]), "wall_hours": 4},
        })
    fresh_contract = yaml.safe_load((ROOT / "manifests/production_generator/step13_fresh_species_smoke_v1.yaml").read_text(encoding="utf-8"))
    step14_paths = {
        "cohort_runner_sha256": ROOT / "scripts/run_step14_cohort_species.py",
        "cohort_slurm_sha256": ROOT / "slurm/run_step14_real_reaction_cohort_v1.sh",
        "qchem_scalar_features_sha256": ROOT / "qchem_scalar_features.py",
        "fixed_energy_validation_sha256": ROOT / "manifests/reaction_features/step14_fixed_energy_validation_v1.json",
        "dataset_eval_sha256": dataset_path,
        "training_entries_sha256": entries_path,
        "step12_inventory_sha256": inventory_path,
        "cohort_selector_sha256": Path(__file__).resolve(),
    }
    contract = {
        "schema_version": 1,
        "status": "frozen_before_results",
        "step": 14,
        "purpose": "seven_property_class_real_reaction_292_feature_smoke",
        "frozen_local_date": "2026-09-05",
        "run_root": "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/real_reaction_cohort_v1/species",
        "reaction_output_root": "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/real_reaction_cohort_v1/reactions",
        "selection_policy": {"property_class_quotas": QUOTAS, "required_stoichiometric_species_count": 2, "allowed_tiers": ["small_mhg"], "maximum_memory_class_mb": 7500, "ranking": ["ascending_sum_orbital_aos", "ascending_training_global_index"], "performance_assessment": False},
        "reaction_count": len(reactions),
        "species_count": len(cases),
        "reactions": reactions,
        "cases": cases,
        "grids": fresh_contract["grids"],
        "qchem_build": fresh_contract["qchem_build"],
        "authorities": fresh_contract["authorities"],
        "step14_authorities": {name: sha256(path) for name, path in step14_paths.items()},
        "bulk_submission_authorized": False,
    }
    if len(reactions) != 20 or len(cases) != 38:
        raise RuntimeError(f"unexpected cohort size: {len(reactions)} reactions, {len(cases)} species")
    temporary = OUTPUT.parent / f".{OUTPUT.name}.tmp.{os.getpid()}"
    temporary.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.rename(OUTPUT)
    print(json.dumps({"output": str(OUTPUT), "reaction_count": len(reactions), "species_count": len(cases), "property_class_quotas": QUOTAS}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
