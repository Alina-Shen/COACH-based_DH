#!/usr/bin/env python3
"""Aggregate and independently validate all six frozen Q3 gateway reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/qchem_gateway/q3_native_gateway_v1.yaml"
DEFAULT_BUILD = ROOT / "manifests/qchem_gateway/q3_diagnostic_build_v1.yaml"
DEFAULT_RUN_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q3_native_v1"
)
DEFAULT_OUTPUT = ROOT / "manifests/qchem_gateway/q3_validation_v1.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--build", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    build = yaml.safe_load(args.build.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "manifest_frozen_before_results": manifest["status"] == "frozen_before_results",
        "user_approved_uks_interpretation": manifest["interpretation"]["user_approved"] is True,
        "tolerances_frozen": manifest["comparison_contract"]["relative_tolerance"] == 2.0e-12
        and manifest["comparison_contract"]["absolute_tolerance_hartree"] == 2.0e-12,
        "diagnostic_build_record_complete": build["status"] == "complete",
    }
    executable = Path(build["build"]["executable"])
    libks = Path(build["build"]["installed_libks"])
    checks["executable_hash_pinned"] = executable.is_file() and sha256(executable) == build["build"]["executable_sha256"]
    checks["installed_libks_hash_pinned"] = libks.is_file() and sha256(libks) == build["build"]["installed_libks_sha256"]
    try:
        diff = subprocess.check_output(["svn", "diff", build["source"]["libks_root"]])
        checks["live_libks_diff_pinned"] = hashlib.sha256(diff).hexdigest() == build["source"]["libks_diff_sha256"]
    except (OSError, subprocess.CalledProcessError):
        checks["live_libks_diff_pinned"] = False

    expected = {(case["species"], grid["id"]): case for case in manifest["cases"] for grid in manifest["grids"]}
    reports = []
    for (species, grid), case in expected.items():
        case_root = args.run_root / species / grid
        report_path = case_root / "validation.json"
        marker_path = case_root / "Q3_CASE_PASS"
        key = f"case_{species}_{grid}"
        if not report_path.is_file():
            checks[key] = False
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        checks[key] = (
            report["passed"] is True
            and marker_path.is_file()
            and report["species"] == species
            and report["grid"] == grid
            and report["role"] == case["role"]
            and report["tolerances_frozen_before_results"] == {"rtol": 2.0e-12, "atol_hartree": 2.0e-12}
            and all(report["checks"].values())
        )
        reports.append({
            "species": species,
            "role": report["role"],
            "grid": grid,
            "passed": report["passed"],
            "metrics": report["metrics"],
            "hashes": report["hashes"],
            "heavy_validation_report": str(report_path),
            "heavy_validation_report_sha256": sha256(report_path),
        })
    checks["six_case_reports_present"] = len(reports) == 6
    checks["closed_and_open_shell_each_three_grids"] = (
        sum(report["role"] == "closed_shell_singlet_uks" for report in reports) == 3
        and sum(report["role"] == "open_shell_doublet_uks" for report in reports) == 3
    )
    checks["authoritative_inputs_unchanged"] = all(
        sha256(Path(case["authoritative_input"])) == case["authoritative_input_sha256"]
        for case in manifest["cases"]
    )
    checks["authoritative_qarchives_unchanged"] = all(
        sha256(Path(case["orbital_root"]) / "qarchive.h5") == case["qarchive_sha256"]
        for case in manifest["cases"]
    )
    passed = all(checks.values())
    result = {
        "schema_version": 1,
        "status": "passed" if passed else "failed",
        "passed": passed,
        "checks": checks,
        "manifest": str(args.manifest.resolve()),
        "manifest_sha256": sha256(args.manifest),
        "diagnostic_build_manifest": str(args.build.resolve()),
        "diagnostic_build_manifest_sha256": sha256(args.build),
        "case_reports": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
