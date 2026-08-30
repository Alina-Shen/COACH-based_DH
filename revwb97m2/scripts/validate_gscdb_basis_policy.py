#!/usr/bin/env python3
"""Validate GSCDB per-species orbital and RI auxiliary bases against Q-Chem inputs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "manifests" / "gscdb137" / "species_manifest.csv",
    )
    parser.add_argument(
        "--scratch-root",
        type=Path,
        default=Path("/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2"),
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def rem_values(text: str) -> dict[str, str]:
    match = re.search(r"(?ims)^\s*\$rem\s*$\n(.*?)^\s*\$end\s*$", text)
    if not match:
        raise ValueError("missing $rem block")
    values: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("!", "#")):
            continue
        fields = line.replace("=", " ").split()
        if len(fields) >= 2:
            values[fields[0].upper()] = fields[1]
    return values


def normalized(value: str) -> str:
    return value.strip().upper()


GENERATED_BASIS_TOKENS = {"GEN", "GENERAL"}


def main() -> int:
    args = parse_args()
    with args.manifest.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["scope"] == "gscdb137"]

    missing_inputs: list[str] = []
    parse_failures: dict[str, str] = {}
    basis_mismatches: dict[str, dict[str, str]] = {}
    auxiliary_mismatches: dict[str, dict[str, str]] = {}
    advisory_omissions: dict[str, str] = {}
    missing_generated_sections: list[str] = []
    generated_basis_realizations: list[str] = []
    observed_basis: Counter[str] = Counter()
    observed_auxiliary: Counter[str] = Counter()

    for row in rows:
        species = row["species"]
        input_path = args.scratch_root / species / "input0"
        if not input_path.is_file():
            missing_inputs.append(species)
            continue
        text = input_path.read_text(encoding="utf-8", errors="replace")
        try:
            rem = rem_values(text)
        except ValueError as exc:
            parse_failures[species] = str(exc)
            continue
        input_basis = rem.get("BASIS", "")
        input_auxiliary = rem.get("AUX_BASIS_CORR", "")
        observed_basis[input_basis] += 1
        observed_auxiliary[input_auxiliary] += 1
        has_generated_basis = bool(re.search(r"(?im)^\s*\$basis\s*$", text))
        if normalized(input_basis) in GENERATED_BASIS_TOKENS and has_generated_basis:
            generated_basis_realizations.append(species)
        elif normalized(input_basis) != normalized(row["basis"]):
            basis_mismatches[species] = {"manifest": row["basis"], "qchem": input_basis}
        manifest_auxiliary = row["aux_basis_corr"]
        if manifest_auxiliary:
            if normalized(input_auxiliary) != normalized(manifest_auxiliary):
                auxiliary_mismatches[species] = {
                    "manifest": manifest_auxiliary,
                    "qchem": input_auxiliary,
                }
        elif input_auxiliary:
            advisory_omissions[species] = input_auxiliary
        if normalized(input_basis) in GENERATED_BASIS_TOKENS and not has_generated_basis:
            missing_generated_sections.append(f"{species}:$basis")
        if normalized(input_auxiliary) == "GEN" and not re.search(r"(?im)^\s*\$aux_basis\s*$", text):
            missing_generated_sections.append(f"{species}:$aux_basis")

    expected_advisory_omissions = {"AE11_Yb": "GEN"}
    checks = {
        "core_species_13907": len(rows) == 13907,
        "all_input0_present": not missing_inputs,
        "all_rem_blocks_parse": not parse_failures,
        "all_orbital_basis_semantics_match": not basis_mismatches,
        "all_nonblank_auxiliary_labels_match": not auxiliary_mismatches,
        "known_allmols_auxiliary_omission_only": advisory_omissions == expected_advisory_omissions,
        "generated_basis_sections_present": not missing_generated_sections,
    }
    report = {
        "passed": all(checks.values()),
        "checks": checks,
        "counts": {
            "core_species": len(rows),
            "orbital_basis_labels": dict(observed_basis),
            "auxiliary_basis_labels": dict(observed_auxiliary),
            "generated_orbital_basis_realizations": len(generated_basis_realizations),
        },
        "details": {
            "missing_inputs": missing_inputs,
            "parse_failures": parse_failures,
            "basis_mismatches": basis_mismatches,
            "auxiliary_mismatches": auxiliary_mismatches,
            "advisory_omissions": advisory_omissions,
            "missing_generated_sections": missing_generated_sections,
        },
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for name, passed in checks.items():
            print(f"{'PASS' if passed else 'FAIL'} {name}")
        print(f"\nBasis policy: {'PASS' if report['passed'] else 'FAIL'}")
        print(f"Manifest: {args.manifest.resolve()}")
        print(f"Scratch: {args.scratch_root.resolve()}")
        if not report["passed"]:
            print(json.dumps(report["details"], indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
