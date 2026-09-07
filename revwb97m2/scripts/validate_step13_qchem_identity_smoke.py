#!/usr/bin/env python3
"""Independently validate the closed/open-shell Step-13 Q-Chem smoke."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np

from revwb97m2.production_generator import sha256
from revwb97m2.qchem_step13_stages import BOUNDARY_CONTRACTS, authority_fingerprint, validate_boundary


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "revwb97m2"
DEFAULT_SMOKE = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step13/qchem_identity_smoke_v1")
DEFAULT_OUTPUT = PROJECT / "manifests/production_generator/step13_qchem_identity_smoke_validation_v1.json"
Q4_ROOT = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q4_published_v1")
STEP9_ROOT = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/step9_same_archive_v3")
CASES = ("h2o_SW49", "12_NH2rad_HNBrBDE18")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-root", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    bridge_path = PROJECT / "manifests/basis_bridge/resolved_basis_records.csv"
    with bridge_path.open(newline="", encoding="utf-8") as handle:
        records = {row["species"]: row for row in csv.DictReader(handle) if row["species"] in CASES}
    authorities = {
        "scientific_specification_sha256": sha256(PROJECT / "configs/scientific_spec.yaml"),
        "basis_bridge_records_sha256": sha256(bridge_path),
        "q4_validation_sha256": sha256(PROJECT / "manifests/qchem_gateway/q4_validation_v1.json"),
        "step9_validation_sha256": sha256(PROJECT / "manifests/scalar_features/step9_qchem_validation_v3.json"),
    }
    cases = []
    for species in CASES:
        row = records[species]
        identity = {"scope": row["scope"], "species": species, "source_record_sha256": row["source_record_sha256"]}
        fingerprint = authority_fingerprint(identity, authorities)
        species_root = args.smoke_root / row["scope"] / species
        boundary_checks = {
            name: validate_boundary(species_root / name, name, identity, fingerprint)["passed"]
            for name in BOUNDARY_CONTRACTS
        }
        vector = np.load(species_root / "assembly/feature_vector_292.npy", allow_pickle=False)
        semilocal = np.load(Q4_ROOT / species / "250974/semilocal_features_288.npy", allow_pickle=False)
        scalar = json.loads((STEP9_ROOT / species / "published/scalar_manifest.json").read_text(encoding="utf-8"))
        values = scalar["values_hartree"]
        expected_tail = np.asarray([values["short_range_hf_hartree"], values["vv10_hartree"], values["pt2_total_hartree"], values["d4_atm_hartree"]])
        checks = {
            "all_eight_boundaries_valid": all(boundary_checks.values()),
            "feature_vector_shape_finite": vector.shape == (292,) and bool(np.isfinite(vector).all()),
            "q4_semilocal_prefix_exact": bool(np.array_equal(vector[:288], semilocal)),
            "step9_scalar_tail_exact": bool(np.array_equal(vector[288:], expected_tail)),
        }
        cases.append({"species": species, "role": "closed_shell_singlet_uks" if species == "h2o_SW49" else "open_shell_doublet_uks", "passed": all(checks.values()), "checks": checks, "boundary_checks": boundary_checks, "feature_vector_sha256": sha256(species_root / "assembly/feature_vector_292.npy")})
    report = {
        "schema_version": 1,
        "status": "passed" if all(case["passed"] for case in cases) else "failed",
        "step": 13,
        "purpose": "qchem_closed_open_shell_eight_boundary_r2_292_identity_smoke",
        "smoke_root": str(args.smoke_root),
        "authorities": authorities,
        "cases": cases,
        "bulk_submission_authorized": False,
    }
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite validation report: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.parent / f".{args.output.name}.tmp.{os.getpid()}"
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.rename(args.output)
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
