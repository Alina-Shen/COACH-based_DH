#!/usr/bin/env python3
"""Run Step 9 scalar features from an existing validated parent checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.parent_scf import DEFAULT_SPEC, load_spec  # noqa: E402
from revwb97m2.scalar_features import run_scalar_stage  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--parent-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--stage", choices=("gateway", "pilot", "production"), default="gateway")
    parser.add_argument("--max-memory-mb", type=int, default=40000)
    args = parser.parse_args()
    spec = load_spec(args.spec)
    output_dir = args.output_dir
    if output_dir is None:
        root = Path(spec["orbital_source"]["checkpoint_root"])
        output_dir = root / "scalar" / args.stage / args.species
    parent_manifest = json.loads(
        (args.parent_dir / "parent_manifest.json").read_text(encoding="utf-8")
    )
    if parent_manifest["species"] != args.species:
        raise ValueError(
            f"requested species {args.species!r} does not match parent "
            f"{parent_manifest['species']!r}"
        )
    manifest = run_scalar_stage(
        parent_dir=args.parent_dir,
        output_dir=output_dir,
        spec_path=args.spec,
        max_memory_mb=args.max_memory_mb,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
