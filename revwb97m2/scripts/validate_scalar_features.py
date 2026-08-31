#!/usr/bin/env python3
"""Independently validate one published Step-9 scalar artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.parent_scf import DEFAULT_SPEC  # noqa: E402
from revwb97m2.scalar_features import validate_scalar_artifact  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scalar-dir", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checks, details = validate_scalar_artifact(args.scalar_dir, args.spec)
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "validator": str(Path(__file__).relative_to(WORKSPACE)),
        "validator_sha256": sha256(Path(__file__)),
        "scalar_module": "revwb97m2/scalar_features.py",
        "scalar_module_sha256": sha256(ROOT / "scalar_features.py"),
        "checks": checks,
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "passed":
        failures = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"scalar-feature validation failed: {', '.join(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
