#!/usr/bin/env python3
"""Assemble production R1-78 and R2-291 vectors from validated stage artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.scalar_features import publish_r1_r2_assembly  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semilocal-dir", type=Path, required=True)
    parser.add_argument("--scalar-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--grid-id", default="250974")
    args = parser.parse_args()
    manifest = publish_r1_r2_assembly(
        args.semilocal_dir, args.scalar_dir, args.output_dir, args.grid_id
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
