#!/usr/bin/env python3
"""Publish, resume, or inspect a Q-Chem integratedDV feature boundary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_feature_publisher import (  # noqa: E402
    publish_integrated_dv,
    publish_or_resume,
    validate_published_artifact,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("publish", "publish-or-resume", "inspect"))
    parser.add_argument("case_root", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    if args.action == "publish":
        payload = {"action": "published", "manifest": publish_integrated_dv(args.case_root, args.output_dir)}
    elif args.action == "publish-or-resume":
        action, manifest = publish_or_resume(args.case_root, args.output_dir)
        payload = {"action": action, "manifest": manifest}
    else:
        checks, details = validate_published_artifact(args.output_dir, args.case_root)
        payload = {"action": "inspected", "passed": bool(checks) and all(checks.values()), "checks": checks, "details": details}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
