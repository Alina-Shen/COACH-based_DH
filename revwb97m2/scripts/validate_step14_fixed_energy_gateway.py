#!/usr/bin/env python3
"""Independently validate the frozen Step-14 fixed-energy gateway."""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml

from revwb97m2.qchem_scalar_features import parse_qchem_fixed_energy_output, sha256, tree_manifest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "manifests/reaction_features/step14_fixed_energy_gateway_v1.yaml"
OUTPUT = ROOT / "manifests/reaction_features/step14_fixed_energy_validation_v1.json"


def main() -> int:
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    reports = []
    for case in contract["cases"]:
        root = Path(contract["run_root"]) / case["species"]
        published = json.loads((root / "fixed_energy.json").read_text(encoding="utf-8"))
        scalar = json.loads((Path(case["scalar_artifact"]) / "scalar_manifest.json").read_text(encoding="utf-8"))
        parsed = parse_qchem_fixed_energy_output((root / "qchem.out").read_text(encoding="utf-8", errors="replace"), scalar["values_hartree"]["short_range_hf_hartree"])
        checks = {
            "completion_marker": (root / "FIXED_ENERGY_COMPLETE").is_file(),
            "no_failure_record": not (root / "FAILURE.json").exists(),
            "published_values_reproduced": parsed == published["values"],
            "published_checks_pass": all(published["checks"].values()),
            "authoritative_input_unchanged": sha256(Path(case["authoritative_input"])) == case["authoritative_input_sha256"],
            "source_tree_unchanged": tree_manifest(Path(case["orbital_root"])) == json.loads((root / "PREPARED.json").read_text(encoding="utf-8"))["source_tree"],
        }
        reports.append({"species": case["species"], "passed": all(checks.values()), "checks": checks, "values": parsed, "cross_code_absolute_errors_hartree": published["cross_code_absolute_errors_hartree"]})
    report = {
        "schema_version": 1,
        "status": "passed" if all(row["passed"] for row in reports) else "failed",
        "step": 14,
        "jobs": {"array_job_id": 25615292, "states": ["COMPLETED", "COMPLETED"], "elapsed_seconds": [15, 13], "max_rss_kib": [725092, 894132]},
        "contract": str(CONTRACT),
        "contract_sha256": sha256(CONTRACT),
        "cases": reports,
        "bulk_submission_authorized": False,
    }
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite {OUTPUT}")
    temporary = OUTPUT.parent / f".{OUTPUT.name}.tmp.{os.getpid()}"
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.rename(OUTPUT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
