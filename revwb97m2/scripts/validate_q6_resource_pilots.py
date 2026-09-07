#!/usr/bin/env python3
"""Validate frozen Q6 resource pilots and their Q-Chem Step-13 plan overlay."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

WORKSPACE = Path(__file__).resolve().parents[2]
ROOT = WORKSPACE / "revwb97m2"
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_feature_publisher import sha256, validate_published_artifact  # noqa: E402
from revwb97m2.step13_resource_plan import QCHEM_BOUNDARY_NAMES  # noqa: E402


DEFAULT_MANIFEST = ROOT / "manifests/qchem_gateway/q6_resource_pilots_v1.yaml"
DEFAULT_ACCOUNTING = ROOT / "manifests/qchem_gateway/q6_slurm_accounting_v1.json"
DEFAULT_GUIDANCE = ROOT / "manifests/qchem_gateway/q6_resource_guidance_v1.yaml"
DEFAULT_PLAN = ROOT / "manifests/production_generator/step13_qchem_initial_plan_v1.json"
DEFAULT_RUN_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q6_resource_pilots_v1"
)
DEFAULT_OUTPUT = ROOT / "manifests/qchem_gateway/q6_validation_v1.json"
D4_PARAMETERS = {"s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--accounting", type=Path, default=DEFAULT_ACCOUNTING)
    parser.add_argument("--guidance", type=Path, default=DEFAULT_GUIDANCE)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    accounting = json.loads(args.accounting.read_text(encoding="utf-8"))
    guidance = yaml.safe_load(args.guidance.read_text(encoding="utf-8"))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    accounting_by_species = {row["species"]: row for row in accounting["jobs"]}
    reports = []
    all_case_checks = True
    for case in manifest["cases"]:
        species = case["species"]
        species_root = args.run_root / species
        summary_path = species_root / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        measurement = summary["measurements"]
        grid_reports = measurement["grid_reports"]
        feature_checks = {}
        grid_report_by_id = {row["grid"]: row for row in grid_reports}
        for grid in manifest["grids"]:
            grid_id = str(grid["id"])
            expected_case_root = Path(
                grid_report_by_id[grid_id].get(
                    "case_root", species_root / "cases" / grid_id
                )
            )
            checks, _ = validate_published_artifact(
                species_root / "features" / grid_id,
                expected_case_root,
            )
            feature_checks[grid_id] = bool(checks) and all(checks.values())
        job = accounting_by_species[species]
        checks = {
            "completion_marker": (species_root / "Q6_PILOT_COMPLETE").is_file(),
            "summary_status": summary["status"] in {
                "q6_resource_pilot_complete_and_validated",
                "q6_resource_pilot_complete_and_validated_after_retry",
            },
            "manifest_pinned": summary["manifest_sha256"] == sha256(args.manifest),
            "size_and_resources_frozen": summary["size_role"] == case["size_role"]
            and summary["resources"] == case["resources"],
            "source_tree_reproduced": measurement["source_tree"] == case["source_tree"],
            "all_three_grids": [row["grid"] for row in grid_reports] == ["250974", "99590", "75302"],
            "all_qchem_runs_and_extractions_measured": all(
                row["isolated_copy_seconds"] > 0
                and row["qchem_wall_seconds"] > 0
                and row["qchem_output_bytes"] > 0
                and row["extraction_publication_seconds"] > 0
                and row["restart_revalidation_seconds"] > 0
                and row["complete_block_count"] >= 1
                for row in grid_reports
            ),
            "all_q4_boundaries_revalidated": all(feature_checks.values()),
            "diagnostic_export_disabled": not any((species_root / "cases" / row["grid"] / "integrated_dv_inputs.bin").exists() for row in grid_reports),
            "d4_finite_and_frozen": np.isfinite(measurement["d4_atm"]["energy_hartree"])
            and measurement["d4_atm"]["damping_parameters"] == D4_PARAMETERS
            and measurement["d4_atm"]["wall_seconds"] > 0,
            "total_measurements_positive": measurement["total_wall_seconds"] > 0
            and measurement["total_retained_bytes"] > 0,
            "slurm_complete_exit_zero": job["state"] == "COMPLETED"
            and job["exit_code"] == "0:0" and job["elapsed_seconds"] > 0,
            "slurm_resources_match_freeze": job["partition"] == case["resources"]["partition"]
            and job["requested_memory_gib"] == case["resources"]["memory_gib"]
            and job["cpus"] == case["resources"]["cpus"]
            and job["max_rss_mib"] > 0,
        }
        all_case_checks = all_case_checks and all(checks.values())
        reports.append(
            {
                "species": species,
                "size_role": case["size_role"],
                "checks": checks,
                "job": job,
                "measurements": measurement,
                "summary_sha256": sha256(summary_path),
                "feature_checks": feature_checks,
            }
        )
    peak_rss = {row["size_role"]: row["job"]["max_rss_mib"] for row in reports}
    suggested_memory = {
        role: max(4, math.ceil((mib / 1024.0) * 2.0 + 2.0))
        for role, mib in peak_rss.items()
    }
    plan_boundaries = tuple(row["name"] for row in plan["boundaries"])
    aggregate_checks = {
        "manifest_frozen_before_results": manifest["status"] == "frozen_before_results",
        "three_preselected_size_roles": [(row["species"], row["size_role"]) for row in reports]
        == [("3d4dIPSS_Ag_GS", "small"), ("TMB28_C1", "medium"), ("MOR32_pr24", "high")],
        "all_pilot_checks_pass": all_case_checks,
        "slurm_accounting_complete": set(accounting_by_species) == {row["species"] for row in manifest["cases"]},
        "step13_plan_not_authorized": plan["submission_authorized"] is False,
        "step13_plan_uses_qchem_archive_not_pyscf_parent": plan_boundaries == QCHEM_BOUNDARY_NAMES
        and "parent" not in plan_boundaries and "qchem_archive" in plan_boundaries,
        "step13_plan_connects_q4_three_grids": all(
            plan["boundary_implementation_status"][f"integrated_dv_{grid}"] == "q4_implemented_and_validated"
            for grid in ("250974", "99590", "75302")
        ),
        "step13_plan_preserves_step9_block": all(
            plan["boundary_implementation_status"][name].startswith("pending_step9")
            for name in ("vv10", "ri_mp2")
        ),
        "q6_resource_guidance_frozen_and_scoped": guidance["status"]
        == "frozen_after_terminal_pilots_before_aggregate_validation"
        and guidance["decision"]["production_assignment"]
        == "retain_step12_inventory_assignments"
        and guidance["scope"]["vv10_and_ri_mp2"] == "pending_step9_measurement",
        "step13_plan_pins_q6_resource_guidance": plan["resource_calibration_status"]
        == "q6_complete_conservative_step12_assignments_retained"
        and plan["authorities"]["q6_slurm_accounting_sha256"] == sha256(args.accounting)
        and plan["authorities"]["q6_resource_guidance_sha256"] == sha256(args.guidance)
        and plan["q6_resource_guidance"]["decision"]
        == "retain_step12_inventory_assignments",
        "step13_dependency_restart_policy_present": plan["restart_policy"]["complete_validated"] == "reuse_without_rewrite"
        and plan["restart_policy"]["failed_partial_corrupt_or_stale"] == "preserve_and_stop",
    }
    payload = {
        "schema_version": 1,
        "status": "passed" if all(aggregate_checks.values()) else "failed",
        "passed": all(aggregate_checks.values()),
        "checks": aggregate_checks,
        "manifest": str(args.manifest.resolve()),
        "manifest_sha256": sha256(args.manifest),
        "accounting": str(args.accounting.resolve()),
        "accounting_sha256": sha256(args.accounting),
        "resource_guidance": str(args.guidance.resolve()),
        "resource_guidance_sha256": sha256(args.guidance),
        "step13_plan": str(args.plan.resolve()),
        "step13_plan_sha256": sha256(args.plan),
        "case_reports": reports,
        "resource_observations": {
            "peak_rss_mib": peak_rss,
            "two_x_peak_plus_2_gib_suggested_qchem_stage_memory_gib": suggested_memory,
            "caution": "stage-specific Q-Chem observation only; VV10 and RI-MP2 remain separately gated",
        },
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if not args.check_only:
        if args.output.exists():
            raise FileExistsError(f"refusing to overwrite Q6 validation record: {args.output}")
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
