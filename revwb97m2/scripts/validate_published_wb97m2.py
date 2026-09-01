#!/usr/bin/env python3
"""Validate the completed paper-backed Step-11 R0 record."""

from __future__ import annotations

import argparse
import hashlib
import json
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
        default=ROOT / "manifests/published_wb97m2/published_wb97m2_r0_v2.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "manifests/published_wb97m2/validation.json",
    )
    args = parser.parse_args()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    sources = manifest["sources"]
    paths = {
        "paper2": WORKSPACE / sources["omegaB97M2_paper"]["path"],
        "paperv": WORKSPACE / sources["omegaB97M_V_paper"]["path"],
        "si_pdf": WORKSPACE
        / sources["omegaB97M_V_supporting_information"]["pdf_path"],
        "si_src": WORKSPACE
        / sources["omegaB97M_V_supporting_information"]["source_path"],
    }
    molecular = json.loads(
        (WORKSPACE / manifest["validation"]["molecular"]["report"]).read_text()
    )
    reaction = json.loads(
        (WORKSPACE / manifest["validation"]["reaction"]["report"]).read_text()
    )
    comparison_path = WORKSPACE / manifest["comparison_schemas"]["path"]
    comparison = yaml.safe_load(comparison_path.read_text(encoding="utf-8"))
    expected_hashes = {
        "paper2": r0.PAPER_SHA256,
        "paperv": r0.WB97M_V_PAPER_SHA256,
        "si_pdf": r0.WB97M_V_SI_PDF_SHA256,
        "si_src": r0.WB97M_V_SI_SOURCE_SHA256,
    }
    checks = {
        "schema_version_2": manifest["schema_version"] == 2,
        "all_uploaded_authority_hashes_match": all(
            sha256(path) == expected_hashes[name] for name, path in paths.items()
        ),
        "nonlinear_parameters_match": manifest["published_conventions"]
        ["nonlinear_gamma"]
        == {
            "exchange": r0.GAMMA_X,
            "same_spin": r0.GAMMA_SS,
            "opposite_spin": r0.GAMMA_OS,
        },
        "semilocal_coefficients_match": dict(r0.SEMILOCAL_COEFFICIENTS)
        == manifest["table_II"]["semilocal"],
        "scalar_coefficients_match": dict(r0.SCALAR_COEFFICIENTS)
        == manifest["table_II"]["scalars"],
        "R0_is_unfitted_and_isolated": manifest["model_role"]["fit"] is False
        and manifest["model_role"]["may_seed_or_constrain_R1_or_R2"] is False
        and manifest["model_role"]["may_change_R2_feature_space"] is False,
        "comparison_schema_hash_matches": sha256(comparison_path)
        == manifest["comparison_schemas"]["sha256"],
        "R0_R1_R2_schemas_frozen": comparison["status"] == "frozen_before_fitting"
        and list(comparison["models"])
        == ["R0_published_wb97m2", "R1_coach_refit_original78", "R2_coach291"]
        and comparison["models"]["R1_coach_refit_original78"]
        ["total_candidate_feature_count"]
        == 78
        and comparison["models"]["R2_coach291"]["total_candidate_feature_count"]
        == 291
        and comparison["models"]["R2_coach291"]["semilocal_space"]
        ["selected_rows"]
        == [64, 154, 166],
        "density_evaluator_complete": manifest["implementation"]
        ["density_feature_definitions_complete"]
        is True,
        "molecular_report_passes": molecular["status"] == "passed",
        "reaction_report_passes": reaction["status"] == "passed",
        "molecular_tolerance_met": abs(
            molecular["local_minus_qchem_hartree"]["final_r0_energy_hartree"]
        )
        <= manifest["validation"]["molecular"]["tolerance_hartree"],
        "reaction_tolerance_met": abs(
            reaction["local_minus_qchem"]["dissociation_kcal_mol"]
        )
        <= manifest["validation"]["reaction"]["tolerance_kcal_mol"],
        "all_authority_requirements_resolved": len(
            manifest["resolved_authority_requirements"]
        )
        == 7,
        "step11_gate_complete": manifest["step11_gate"]["gate_complete"] is True
        and manifest["step11_gate"]
        ["no_unresolved_semantic_or_energy_definition_bug"]
        is True,
    }
    passed = all(checks.values())
    report = {
        "schema_version": 2,
        "status": "passed_step11_complete" if passed else "failed",
        "step11_gate_complete": passed,
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": str(args.manifest.relative_to(WORKSPACE)),
        "manifest_sha256": sha256(args.manifest),
        "module_sha256": sha256(ROOT / "published_wb97m2.py"),
        "checks": checks,
    }
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
