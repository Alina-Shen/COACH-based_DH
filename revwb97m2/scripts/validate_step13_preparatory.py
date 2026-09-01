#!/usr/bin/env python3
"""Validate the resource-neutral Step-13 production-generator contract."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.production_generator import (  # noqa: E402
    BOUNDARIES,
    DEFAULT_BRIDGE,
    DEFAULT_RECORD_INDEX,
    DEFAULT_ROLES,
    DEFAULT_SPEC,
    authority_hashes,
    build_dry_run_plan,
    load_locked_population,
    sha256,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy",
        type=Path,
        default=ROOT
        / "manifests/production_generator/step13_preparatory_v1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "manifests/production_generator/validation.json",
    )
    parser.add_argument(
        "--inspection-root",
        type=Path,
        default=Path("/tmp/revwb97m2-step13-validation-empty-root"),
        help="Must not exist; keeps validation independent of live production state",
    )
    args = parser.parse_args()
    if args.inspection_root.exists():
        raise FileExistsError(
            f"validation inspection root must not exist: {args.inspection_root}"
        )
    policy = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    population = load_locked_population()
    authorities = authority_hashes()
    plan = build_dry_run_plan(population, args.inspection_root, authorities)
    declared = policy["locked_population"]
    boundary_rows = policy["boundaries"]
    expected_boundaries = [boundary.name for boundary in BOUNDARIES]
    declared_boundaries = [row["name"] for row in boundary_rows]
    resource_gate = policy["resource_gate"]
    expected_boundary_total = len(population) * len(BOUNDARIES)
    checks = {
        "schema_version_1": policy["schema_version"] == 1,
        "preparatory_status": policy["status"]
        == "preparatory_implementation_in_progress_step12_resources_pending",
        "authority_hashes_match": authorities["species_roles_sha256"]
        == declared["roles_sha256"]
        and authorities["basis_bridge_records_sha256"]
        == declared["basis_bridge_sha256"]
        and authorities["record_index_sha256"]
        == declared["record_index_sha256"]
        and authorities["scientific_specification_sha256"]
        == declared["scientific_specification_sha256"],
        "exact_role_minimal_population": len(population)
        == declared["expected_species_count"]
        == 17452,
        "boundary_names_and_order_match": declared_boundaries
        == expected_boundaries,
        "boundary_dependencies_match": all(
            boundary_rows[index]["dependencies"] == list(boundary.dependencies)
            for index, boundary in enumerate(BOUNDARIES)
        ),
        "seven_boundaries_per_species": len(BOUNDARIES) == 7
        and plan["boundary_count_per_species"] == 7,
        "full_dry_run_population": plan["population_count"] == 17452,
        "all_empty_root_boundaries_missing": plan["summary"]["boundary_states"]
        == {"missing": expected_boundary_total},
        "parent_actions_resource_gated": plan["summary"]["planned_actions"].get(
            "eligible_pending_step12_resources"
        )
        == 17452,
        "dependent_actions_resource_gated": plan["summary"]["planned_actions"].get(
            "eligible_after_dependencies_pending_step12_resources"
        )
        == 17452 * 6,
        "submission_globally_forbidden": plan["submission_authorized"] is False
        and all(row["submission_authorized"] is False for row in plan["species"]),
        "step12_fields_unset": resource_gate["step12_signoff_required"] is True
        and resource_gate["submission_authorized"] is False
        and all(
            resource_gate[key] is None
            for key in (
                "production_subset",
                "size_tiers",
                "partition_account_qos",
                "cpu_memory_walltime",
                "array_concurrency",
                "retry_limits",
                "direct_or_out_of_core_routes",
                "quantitative_ao_stops",
            )
        ),
        "planner_and_cli_exist": (WORKSPACE / policy["implementation"]["planner_module"]).is_file()
        and (WORKSPACE / policy["implementation"]["planner_cli"]).is_file(),
    }
    passed = all(checks.values())
    report = {
        "schema_version": 1,
        "status": "passed" if passed else "failed",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "policy": str(args.policy.relative_to(WORKSPACE)),
        "policy_sha256": sha256(args.policy),
        "checks": checks,
        "dry_run_summary": plan["summary"],
        "population_count": len(population),
        "boundary_count_per_species": len(BOUNDARIES),
        "submission_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
