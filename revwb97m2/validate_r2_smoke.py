#!/usr/bin/env python3
"""Validate one generated revwb97m2 R2 smoke directory."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    run_dir = args.run_dir.resolve()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    checks = {}

    checks["scf_converged"] = manifest["scf"]["converged"] is True
    checks["rsh_omega"] = abs(manifest["parent_components"]["omega_bohr_inverse"] - 0.3) < 1.0e-12
    checks["rsh_lr_hf"] = abs(manifest["parent_components"]["long_range_hf_fraction"] - 1.0) < 1.0e-12
    checks["rsh_sr_hf"] = abs(manifest["parent_components"]["short_range_hf_fraction"] - 0.15) < 1.0e-12
    checks["parent_reconstruction"] = abs(
        manifest["parent_components"]["reconstruction_error_hartree"]
    ) <= float(config["validation"]["parent_energy_reconstruction_tolerance_hartree"])
    checks["pt2_finite"] = np.isfinite(manifest["pt2"]["correlation_energy"])
    checks["pt2_spin_sum"] = abs(
        manifest["pt2"]["same_spin_energy"]
        + manifest["pt2"]["opposite_spin_energy"]
        - manifest["pt2"]["correlation_energy"]
    ) < 1.0e-10

    feature = np.load(run_dir / "r2_feature_vector_291.npy")
    checks["feature_shape_291"] = feature.shape == (291,)
    checks["feature_finite"] = bool(np.isfinite(feature).all())
    checks["feature_sr_hf_matches"] = abs(
        feature[288] - manifest["parent_components"]["unscaled_short_range_hf_exchange"]
    ) < 1.0e-12
    checks["feature_vv10_matches"] = abs(feature[289] - manifest["vv10_b10_c001_hartree"]) < 1.0e-12
    checks["feature_pt2_matches"] = abs(feature[290] - manifest["pt2"]["correlation_energy"]) < 1.0e-12

    for grid_id in ("250974", "99590", "75302"):
        matrix = np.load(run_dir / f"integrated_dv_{grid_id}.npy")
        checks[f"matrix_{grid_id}_shape"] = matrix.shape == (180, 96)
        checks[f"matrix_{grid_id}_finite"] = bool(np.isfinite(matrix).all())
    for grid_id in ("99590", "75302"):
        diff = np.load(run_dir / f"r2_grid_diff_{grid_id}_minus_250974.npy")
        checks[f"diff_{grid_id}_shape"] = diff.shape == (291,)
        checks[f"diff_{grid_id}_finite"] = bool(np.isfinite(diff).all())
        checks[f"diff_{grid_id}_nongrid_zero"] = bool(np.array_equal(diff[288:], np.zeros(3)))

    checks = {name: bool(result) for name, result in checks.items()}
    passed = all(checks.values())
    report = {
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "checks": checks,
    }
    (run_dir / "validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not passed:
        failures = [name for name, result in checks.items() if not result]
        raise RuntimeError(f"Smoke validation failed: {', '.join(failures)}")
    (run_dir / "SMOKE_PASS").write_text(
        datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
