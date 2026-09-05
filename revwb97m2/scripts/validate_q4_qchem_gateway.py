#!/usr/bin/env python3
"""Aggregate validation for the six immutable Q4 integratedDV publications."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
ROOT = WORKSPACE / "revwb97m2"
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_feature_publisher import (  # noqa: E402
    MANIFEST_NAME,
    sha256,
    validate_published_artifact,
)


DEFAULT_CASE_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q3_native_v1"
)
DEFAULT_PUBLISHED_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q4_published_v1"
)
DEFAULT_OUTPUT = ROOT / "manifests/qchem_gateway/q4_validation_v1.json"
Q3_VALIDATION = ROOT / "manifests/qchem_gateway/q3_validation_v1.json"
CASES = (
    ("h2o_SW49", "closed_shell_singlet_uks"),
    ("12_NH2rad_HNBrBDE18", "open_shell_doublet_uks"),
)
GRIDS = ("250974", "99590", "75302")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-root", type=Path, default=DEFAULT_CASE_ROOT)
    parser.add_argument("--published-root", type=Path, default=DEFAULT_PUBLISHED_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    q3 = json.loads(Q3_VALIDATION.read_text(encoding="utf-8"))
    reports = []
    all_artifact_checks = True
    identities = set()
    for species, expected_role in CASES:
        for grid in GRIDS:
            case_root = (args.case_root / species / grid).resolve()
            output_dir = (args.published_root / species / grid).resolve()
            checks, details = validate_published_artifact(output_dir, case_root)
            passed = bool(checks) and all(checks.values())
            all_artifact_checks = all_artifact_checks and passed
            manifest = details.get("manifest", {})
            identity = (manifest.get("species"), manifest.get("role"), manifest.get("grid"))
            identities.add(identity)
            reports.append(
                {
                    "species": species,
                    "role": expected_role,
                    "grid": grid,
                    "case_root": str(case_root),
                    "published_root": str(output_dir),
                    "passed": passed,
                    "checks": checks,
                    "manifest_sha256": sha256(output_dir / MANIFEST_NAME)
                    if (output_dir / MANIFEST_NAME).is_file() else None,
                    "artifacts_sha256": manifest.get("artifacts_sha256", {}),
                    "complete_block_count": manifest.get("complete_block_count"),
                }
            )
    expected_identities = {
        (species, role, grid) for species, role in CASES for grid in GRIDS
    }
    q3_hashes = {
        (row["species"], row["grid"]): row["hashes"]["qchem_output"]
        for row in q3["case_reports"]
    }
    source_hashes_match_q3 = all(
        details_hash == q3_hashes[(report["species"], report["grid"])]
        for report in reports
        for details_hash in [
            json.loads((Path(report["published_root"]) / MANIFEST_NAME).read_text(encoding="utf-8"))
            .get("source", {}).get("qchem_output_sha256")
        ]
    )
    checks = {
        "q3_validation_passed": q3.get("passed") is True and q3.get("status") == "passed",
        "six_publications_present": len(reports) == 6,
        "all_publications_independently_validated": all_artifact_checks,
        "closed_and_open_shell_each_three_grids": identities == expected_identities,
        "source_qchem_outputs_match_q3": source_hashes_match_q3,
        "all_final_complete_blocks_recorded": all(report["complete_block_count"] >= 1 for report in reports),
        "all_artifact_sets_have_full_selected_and_flattened": all(
            set(report["artifacts_sha256"])
            == {"integrated_dv_180x96.npy", "selected_features_3x96.npy", "semilocal_features_288.npy"}
            for report in reports
        ),
    }
    payload = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "passed": all(checks.values()),
        "q3_validation": str(Q3_VALIDATION.resolve()),
        "q3_validation_sha256": sha256(Q3_VALIDATION),
        "publisher_module": str((ROOT / "qchem_feature_publisher.py").resolve()),
        "publisher_module_sha256": sha256(ROOT / "qchem_feature_publisher.py"),
        "checks": checks,
        "case_reports": reports,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if not args.check_only:
        output = args.output.resolve()
        if output.exists():
            raise FileExistsError(f"refusing to overwrite Q4 validation record: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.parent / f".{output.name}.tmp.{os.getpid()}"
        if temporary.exists():
            raise FileExistsError(f"refusing to reuse validation staging file: {temporary}")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.rename(output)
    print(rendered, end="")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
