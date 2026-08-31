#!/usr/bin/env python3
"""Independently recompute all three matrices in one semilocal artifact."""

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
from revwb97m2.semilocal_features import validate_semilocal_artifact  # noqa: E402


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semilocal-dir", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-memory-mb", type=int, default=40000)
    parser.add_argument("--block-size", type=int, default=10000)
    args = parser.parse_args()
    checks, details = validate_semilocal_artifact(
        args.semilocal_dir, args.spec, args.max_memory_mb, args.block_size
    )
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "validator": str(Path(__file__).relative_to(WORKSPACE)),
        "validator_sha256": file_sha256(Path(__file__)),
        "semilocal_module": "revwb97m2/semilocal_features.py",
        "semilocal_module_sha256": file_sha256(ROOT / "semilocal_features.py"),
        "checks": checks,
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "passed":
        failures = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"semilocal validation failed: {', '.join(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
