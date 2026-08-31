#!/usr/bin/env python3
"""Validate Step-10 matrix coverage, immutable metadata, and static preflight."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.parent_scf import (  # noqa: E402
    input_artifact_paths,
    load_bridge_row,
    load_record,
    load_spec,
    validate_record,
)
from revwb97m2.scripts.pyscf_basis_bridge import build_molecules  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=ROOT / "manifests" / "gateway_matrix" / "step10_gateway_matrix_v1.yaml",
    )
    args = parser.parse_args()
    matrix = yaml.safe_load(args.matrix.read_text(encoding="utf-8"))
    required = set(matrix["required_categories"])
    observed_categories: set[str] = set()
    species_reports = []
    names = [entry["name"] for entry in matrix["species"]]
    checks = {
        "species_count_5_to_10": 5 <= len(names) <= 10,
        "species_unique": len(names) == len(set(names)),
    }
    limits = matrix["preflight_stop_conditions"]
    execution = matrix["execution"]
    memory_by_species = {
        name: int(config["slurm"]["memory_gb"])
        for config in execution.values()
        for name in config["species"]
    }
    for entry in matrix["species"]:
        name = entry["name"]
        spec_path = WORKSPACE / entry["specification"]
        spec = load_spec(spec_path)
        record, line = load_record(input_artifact_paths(spec)["records"], name)
        bridge = load_bridge_row(spec, name)
        validate_record(record, bridge)
        mol, auxmol, resolved = build_molecules(record)
        molecule = record["pyscf_molecule"]
        actual = {
            "charge": mol.charge,
            "multiplicity": molecule["multiplicity"],
            "real_atoms": molecule["real_atom_count"],
            "ghost_atoms": molecule["ghost_atom_count"],
            "electrons": mol.nelectron,
            "orbital_aos": mol.nao_nr(),
            "auxiliary_aos": auxmol.nao_nr(),
        }
        observed_categories.update(entry["categories"])
        expected_match = actual == entry["expected"]
        resolution_match = all(
            resolved[key.removeprefix("expected_")] == value
            for key, value in entry.items()
            if key.startswith("expected_") and key != "expected"
        )
        nao = mol.nao_nr()
        naux = auxmol.nao_nr()
        df_3center_gib = naux * nao * (nao + 1) / 2 * 8 / 1024**3
        requested_gib = memory_by_species[name]
        preflight = (
            nao <= int(limits["maximum_orbital_aos"])
            and naux <= int(limits["maximum_auxiliary_aos"])
            and df_3center_gib
            <= float(limits["maximum_estimated_df_3center_gib_fraction_of_requested_memory"])
            * requested_gib
        )
        species_reports.append(
            {
                "species": name,
                "immutable_record_line": line,
                "categories": entry["categories"],
                "actual": actual,
                "orbital_resolution": resolved["orbital_resolution"],
                "ecp_resolution": resolved["ecp_resolution"],
                "auxiliary_resolution": resolved["auxiliary_resolution"],
                "estimated_df_3center_gib": df_3center_gib,
                "requested_memory_gib": requested_gib,
                "expected_metadata_match": expected_match,
                "expected_resolution_match": resolution_match,
                "preflight_pass": preflight,
            }
        )
    checks["all_required_categories_covered"] = required <= observed_categories
    checks["all_metadata_matches"] = all(r["expected_metadata_match"] for r in species_reports)
    checks["all_resolution_expectations_match"] = all(
        r["expected_resolution_match"] for r in species_reports
    )
    checks["all_static_preflights_pass"] = all(r["preflight_pass"] for r in species_reports)
    checks["execution_assigns_every_species_once"] = sorted(names) == sorted(
        name for config in execution.values() for name in config["species"]
    )
    report = {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "covered_categories": sorted(observed_categories),
        "species": species_reports,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
