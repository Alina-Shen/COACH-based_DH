#!/usr/bin/env python3
"""Promote the frozen closed/open-shell Q-Chem gateways into Step-13."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from revwb97m2.production_generator import sha256
from revwb97m2.qchem_step13_stages import publish_species_from_validated_gateway


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
DEFAULT_OUTPUT = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step13/qchem_identity_smoke_v1")
Q4_ROOT = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q4_published_v1")
STEP9_ROOT = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/step9_same_archive_v3")
CASES = ("h2o_SW49", "12_NH2rad_HNBrBDE18")


def bridge_records() -> dict[str, dict[str, str]]:
    path = PROJECT / "manifests/basis_bridge/resolved_basis_records.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["species"]: row for row in csv.DictReader(handle) if row["species"] in CASES}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    records = bridge_records()
    authorities = {
        "scientific_specification_sha256": sha256(PROJECT / "configs/scientific_spec.yaml"),
        "basis_bridge_records_sha256": sha256(PROJECT / "manifests/basis_bridge/resolved_basis_records.csv"),
        "q4_validation_sha256": sha256(PROJECT / "manifests/qchem_gateway/q4_validation_v1.json"),
        "step9_validation_sha256": sha256(PROJECT / "manifests/scalar_features/step9_qchem_validation_v3.json"),
    }
    reports = []
    for species in CASES:
        row = records[species]
        identity = {"scope": row["scope"], "species": species, "source_record_sha256": row["source_record_sha256"]}
        reports.append(publish_species_from_validated_gateway(
            identity=identity,
            authorities=authorities,
            q4_dirs={grid: Q4_ROOT / species / grid for grid in ("250974", "99590", "75302")},
            scalar_dir=STEP9_ROOT / species / "published",
            species_root=args.output_root / row["scope"] / species,
        ))
    print(json.dumps({"status": "passed", "output_root": str(args.output_root), "cases": reports}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
