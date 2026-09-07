#!/usr/bin/env python3
"""Aggregate the frozen Step 9 same-archive scalar gateway."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_scalar_features import sha256  # noqa: E402

DEFAULT_MANIFEST = ROOT / "manifests/scalar_features/step9_qchem_same_archive_v3.yaml"
DEFAULT_RUN_ROOT = Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/step9_same_archive_v3")
BUILD_MANIFEST = ROOT / "manifests/qchem_gateway/q3_diagnostic_build_v1.yaml"


def validate(manifest_path: Path, run_root: Path) -> dict[str, object]:
    contract = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    build = yaml.safe_load(BUILD_MANIFEST.read_text(encoding="utf-8"))
    tolerances = contract["validation"]["cross_engine_reference_tolerances"]
    case_reports = []
    for case in contract["cases"]:
        published = run_root / case["species"] / "published"
        scalar_manifest_path = published / "scalar_manifest.json"
        scalar = json.loads(scalar_manifest_path.read_text(encoding="utf-8"))
        values = scalar["values_hartree"]
        reference = case["fallback_reference"]
        errors = {
            name: abs(float(values[name]) - float(reference[name]))
            for name in ("short_range_hf_hartree", "vv10_hartree", "pt2_total_hartree")
        }
        vector = np.load(published / "scalar_features_288_291.npy")
        checks = {
            "published_status": scalar["status"] == "qchem_same_archive_scalar_features_complete_and_validated",
            "internal_checks": all(scalar["checks"].values()),
            "qarchive_hash": scalar["source"]["qarchive_sha256"] == case["qarchive_sha256"]
            and scalar["source"]["copied_qarchive_sha256"] == case["qarchive_sha256"],
            "feature_vector_shape_finite": vector.shape == (4,) and bool(np.isfinite(vector).all()),
            "feature_vector_identity": bool(np.array_equal(vector, np.asarray([
                values["short_range_hf_hartree"], values["vv10_hartree"],
                values["pt2_total_hartree"], values["d4_atm_hartree"],
            ], dtype=np.float64))),
            "d4_atm_finite": bool(np.isfinite(values["d4_atm_hartree"])),
            "sr_hf_cross_engine": errors["short_range_hf_hartree"] <= tolerances["short_range_hf_hartree"],
            "vv10_cross_engine": errors["vv10_hartree"] <= tolerances["vv10_hartree"],
            "pt2_cross_engine": errors["pt2_total_hartree"] <= tolerances["pt2_total_hartree"],
        }
        case_reports.append({
            "species": case["species"],
            "role": case["role"],
            "passed": all(checks.values()),
            "checks": checks,
            "values_hartree": values,
            "absolute_errors_hartree": errors,
            "scalar_manifest_sha256": sha256(scalar_manifest_path),
        })
    executable = Path(build["build"]["executable"])
    global_checks = {
        "contract_frozen_before_results": contract["status"] == "frozen_before_results",
        "diagnostic_predecessor_rejected": json.loads(
            (ROOT / "manifests/scalar_features/step9_qchem_same_archive_v2_diagnostic.json").read_text(encoding="utf-8")
        )["status"] == "rejected_diagnostic_not_published",
        "qchem_executable_hash": sha256(executable) == build["build"]["executable_sha256"],
        "closed_and_open_shell_gateways": {row["role"] for row in case_reports}
        == {"closed_shell_singlet_uks", "open_shell_doublet_uks"},
        "all_cases_pass": all(row["passed"] for row in case_reports),
    }
    return {
        "schema_version": 1,
        "status": "passed" if all(global_checks.values()) else "failed",
        "step": 9,
        "slurm": {
            "rejected_diagnostic_job": 25612738,
            "completed_gateway_job": 25613167,
            "partition": "mhg",
        },
        "contract": str(manifest_path.resolve()),
        "contract_sha256": sha256(manifest_path),
        "qchem_build": {
            "main_svn_revision": build["source"]["qchem_svn_revision"],
            "libks_svn_revision": build["source"]["libks_svn_revision"],
            "executable_sha256": build["build"]["executable_sha256"],
        },
        "tolerances": tolerances,
        "global_checks": global_checks,
        "cases": case_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    args = parser.parse_args()
    report = validate(args.manifest, args.run_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
