#!/usr/bin/env python3
"""Validate the versioned Q-Chem orbital authority without reading archive payloads."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy",
        type=Path,
        default=root / "manifests/qchem_orbitals/qchem_orbital_authority_v1.yaml",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def archive_inventory(root: Path, species: list[str], archive_name: str) -> dict[str, object]:
    missing: list[str] = []
    empty: list[str] = []
    nonregular: list[str] = []
    for name in species:
        archive = root / name / archive_name
        if not archive.exists():
            missing.append(name)
        elif not archive.is_file():
            nonregular.append(name)
        elif archive.stat().st_size <= 0:
            empty.append(name)
    return {
        "expected": len(species),
        "present_regular_nonempty": len(species) - len(missing) - len(empty) - len(nonregular),
        "missing": missing,
        "empty": empty,
        "nonregular": nonregular,
    }


def validate(policy_path: Path) -> dict[str, object]:
    workspace = policy_path.resolve().parents[3]
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    checks["schema_v1_frozen"] = policy["schema_version"] == 1 and policy["status"] == "frozen"

    canonical = policy["canonical_gscdb"]
    canonical_manifest = workspace / canonical["species_manifest"]
    canonical_rows = load_rows(canonical_manifest)
    canonical_species = [row["species"] for row in canonical_rows]
    checks["canonical_manifest_hash"] = sha256(canonical_manifest) == canonical["species_manifest_sha256"]
    checks["canonical_count"] = len(canonical_species) == canonical["expected_species"] == 14006
    checks["canonical_unique"] = len(set(canonical_species)) == len(canonical_species)
    checks["canonical_scopes"] = Counter(row["scope"] for row in canonical_rows) == Counter(canonical["expected_scopes"])
    canonical_inventory = archive_inventory(
        Path(canonical["orbital_root"]), canonical_species, canonical["archive_filename"]
    )
    checks["canonical_archives_complete"] = canonical_inventory["present_regular_nonempty"] == 14006
    details["canonical_inventory"] = canonical_inventory

    bignc = policy["external_scopes"]["BigNC"]
    bignc_manifest = workspace / bignc["species_manifest"]
    bignc_rows = load_rows(bignc_manifest)
    bignc_species = [row["species"] for row in bignc_rows]
    checks["bignc_manifest_hash"] = sha256(bignc_manifest) == bignc["species_manifest_sha256"]
    checks["bignc_count_unique"] = (
        len(bignc_species) == bignc["expected_species"] == 75
        and len(set(bignc_species)) == len(bignc_species)
    )
    bignc_inventory = archive_inventory(
        Path(bignc["source_orbital_root"]), bignc_species, bignc["archive_filename"]
    )
    checks["bignc_source_archives_complete"] = bignc_inventory["present_regular_nonempty"] == 75
    checks["bignc_copy_required"] = bignc["require_project_owned_nonoverwriting_copy_before_execution"] is True
    details["bignc_inventory"] = bignc_inventory

    gdb = policy["external_scopes"]["GDB9_W1_F12"]
    checks["gdb_gap_explicit"] = (
        gdb["status"] == "blocked_no_validated_qchem_orbital_archive_authority"
        and gdb["expected_species"] == 3371
        and gdb["prohibit_silent_pyscf_regeneration"] is True
    )
    checks["opt_outside_fixed_geometry_workflow"] = (
        policy["external_scopes"]["OPT"]["status"]
        == "outside_fixed_geometry_energy_and_training_workflow"
    )

    safety = policy["execution_safety"]
    checks["nonmutating_archive_policy"] = all(
        safety[key] is True
        for key in (
            "authoritative_roots_are_read_only_inputs",
            "run_from_isolated_nonoverwriting_copy",
            "hash_source_archive_before_copy",
            "verify_copy_hash_before_qchem",
            "record_source_and_copy_hashes",
            "never_repair_or_replace_archive_in_place",
            "never_fall_back_to_new_scf_silently",
        )
    )

    report: dict[str, object] = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "passed": all(checks.values()),
        "policy": str(policy_path),
        "policy_sha256": sha256(policy_path),
        "checks": checks,
        "details": details,
    }
    return report


def main() -> int:
    args = parse_args()
    report = validate(args.policy)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
