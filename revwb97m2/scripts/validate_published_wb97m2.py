#!/usr/bin/env python3
"""Validate the paper-backed Step-11 R0 source and algebra scaffold."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2 import published_wb97m2 as r0  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT
        / "manifests"
        / "published_wb97m2"
        / "published_wb97m2_r0_v1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "manifests" / "published_wb97m2" / "validation.json",
    )
    args = parser.parse_args()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    source = WORKSPACE / manifest["source"]["path"]
    table = manifest["table_II"]
    unresolved = manifest["unresolved_authority_requirements"]

    checks = {
        "schema_version_1": manifest["schema_version"] == 1,
        "status_marks_density_kernel_blocked": manifest["status"]
        == "source_audit_complete_r0_density_kernel_blocked",
        "paper_exists": source.is_file(),
        "paper_hash_matches": source.is_file()
        and sha256(source) == manifest["source"]["sha256"] == r0.PAPER_SHA256,
        "doi_matches_module": manifest["source"]["doi"] == r0.DOI,
        "paper_authority_scope_is_limited": manifest["source"]["authority_scope"]
        == "paper_only_at_displayed_precision",
        "semilocal_coefficients_match_module": dict(r0.SEMILOCAL_COEFFICIENTS)
        == table["semilocal"],
        "scalar_coefficients_match_module": dict(r0.SCALAR_COEFFICIENTS)
        == table["scalars"],
        "displayed_nonzero_count_16": table["displayed_nonzero_coefficients"]
        == len(r0.SEMILOCAL_COEFFICIENTS) + len(r0.SCALAR_COEFFICIENTS)
        == 16,
        "independent_parameter_count_14": table[
            "independent_parameters_after_two_constraints"
        ]
        == r0.independent_parameter_count()
        == 14,
        "exchange_constraint_at_printed_precision": math.isclose(
            table["semilocal"]["exchange_00"] + table["scalars"]["short_range_hf"],
            1.0,
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        "nonlocal_constraint_at_printed_precision": math.isclose(
            table["scalars"]["vv10"] + table["scalars"]["pt2"],
            1.0,
            rel_tol=0.0,
            abs_tol=1e-15,
        ),
        "R0_is_unfitted_and_isolated_from_R2": manifest["model_role"]["fit"]
        is False
        and manifest["model_role"]["may_seed_or_constrain_R1_or_R2"] is False
        and manifest["model_role"]["may_change_R2_feature_space"] is False,
        "no_density_generator_claim": manifest["implemented_now"][
            "generates_density_features"
        ]
        is False,
        "no_trusted_fixture_claim": manifest["implemented_now"][
            "trusted_molecular_or_reaction_fixture"
        ]
        is False,
        "unresolved_authorities_are_explicit": len(unresolved) == 7
        and len({entry["id"] for entry in unresolved}) == 7,
        "gate_remains_open": manifest["step11_gate"]["gate_complete"] is False
        and manifest["step11_gate"]["full_R0_evaluator_ready"] is False
        and manifest["step11_gate"]["trusted_fixture_validation_complete"] is False,
    }
    report = {
        "schema_version": 1,
        "status": "passed_source_and_algebra_scaffold"
        if all(checks.values())
        else "failed",
        "step11_gate_complete": False,
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "validator": str(Path(__file__).relative_to(WORKSPACE)),
        "validator_sha256": sha256(Path(__file__)),
        "manifest": str(args.manifest.relative_to(WORKSPACE)),
        "manifest_sha256": sha256(args.manifest),
        "paper_sha256": sha256(source) if source.is_file() else None,
        "module": "revwb97m2/published_wb97m2.py",
        "module_sha256": sha256(ROOT / "published_wb97m2.py"),
        "checks": checks,
        "unresolved_authority_ids": [entry["id"] for entry in unresolved],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed_source_and_algebra_scaffold" else 1


if __name__ == "__main__":
    raise SystemExit(main())
