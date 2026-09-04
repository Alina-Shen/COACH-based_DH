#!/usr/bin/env python3
"""Validate the non-authorizing Step-12 sign-off candidate."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
POLICY = ROOT / "manifests/step12/step12_resource_signoff_candidate_v1.yaml"
OUTPUT = ROOT / "manifests/step12/step12_resource_signoff_candidate_validation.json"


def main() -> int:
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    inventory_path = WORKSPACE / policy["D12_2_population"]["inventory"]
    with inventory_path.open(newline="", encoding="utf-8") as handle:
        inventory = list(csv.DictReader(handle))
    tier_counts = {
        tier: sum(row["tier"] == tier for row in inventory)
        for tier in ("small_mhg", "large_lr8")
    }
    scripts = [WORKSPACE / path for path in policy["pilot_scripts"]["memory_classes"]]
    headers = "\n".join(path.read_text(encoding="utf-8") for path in scripts)
    scalar_source = (ROOT / "scalar_features.py").read_text(encoding="utf-8")
    checks = {
        "candidate_not_authorized": policy["production_submission_authorized"] is False,
        "exact_population": len(inventory) == policy["D12_2_population"]["species_count"] == 2799,
        "two_tier_counts": tier_counts == {"small_mhg": 2765, "large_lr8": 34},
        "mandatory_seven_boundaries": len(policy["D12_3_mandatory_stage_work"]["stages"]) == 7,
        "mhg_72h": "#SBATCH --partition=mhg" in headers
        and headers.count("#SBATCH --time=72:00:00") == 5,
        "lr8_336h": "#SBATCH --partition=lr8" in headers
        and headers.count("#SBATCH --time=336:00:00") == 2,
        "memory_classes_exact": sorted(
            int(match) for match in re.findall(r"STEP12_MEMORY_CLASS_MB=(\d+)", headers)
        )
        == [3750, 7500, 15000, 30000, 60000, 120000, 300000],
        "sbatch_memory_requests_are_1p5x": sorted(
            int(match) for match in re.findall(r"#SBATCH --mem=(\d+)G", headers)
        )
        == [14, 21, 35, 62, 117, 227, 557],
        "all_requests_strictly_fit_snapshot": 117 * 1024
        < policy["D12_4_two_tier_routes"]["live_partition_snapshot_2026_09_01"]["mhg"]
        ["minimum_physical_memory_mb"]
        and 557 * 1024
        < policy["D12_4_two_tier_routes"]["live_partition_snapshot_2026_09_01"]["lr8"]
        ["physical_memory_mb"],
        "identical_timeout_retry_forbidden": policy["D12_6_retry_policy"]
        ["identical_timeout_automatic_retry"]
        == "forbidden",
        "other_failures_require_user": policy["D12_6_retry_policy"]
        ["other_failure_or_failed_resubmission"]["action"]
        == "append_failure_ledger_and_ask_user",
        "energy_only_dfump2_does_not_retain_t2": "kernel(with_t2=False)"
        in scalar_source
        and '"mp2_amplitudes_retained": False' in scalar_source,
        "D12_9_still_pending": policy["D12_9_signoff_gate"]["status"]
        == "pending_energy_only_pt2_real_validation"
        and policy["D12_9_signoff_gate"]["sbatch_test_only_complete"] is True
        and policy["D12_9_signoff_gate"]["small_real_array_submitted"] is True
        and policy["D12_9_signoff_gate"]["small_real_array_complete"] is False
        and policy["D12_9_signoff_gate"]["real_retry_submission_approved"] is False
        and policy["D12_9_signoff_gate"]["production_submission_authorized"] is False,
        "scripts_exist": all(path.is_file() for path in scripts)
        and (WORKSPACE / policy["pilot_scripts"]["common"]).is_file(),
    }
    passed = all(checks.values())
    report = {
        "schema_version": 1,
        "status": "passed_candidate_pilots_pending" if passed else "failed",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "species_count": len(inventory),
        "tier_counts": tier_counts,
        "production_submission_authorized": False,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
