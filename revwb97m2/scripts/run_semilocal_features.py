#!/usr/bin/env python3
"""Run shared-density R1 and R2 features on the three frozen grids."""

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
from revwb97m2.semilocal_features import run_semilocal_stage  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--parent-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--stage", choices=("gateway", "pilot", "production"), default="gateway")
    parser.add_argument("--max-memory-mb", type=int, default=40000)
    parser.add_argument("--block-size", type=int, default=10000)
    args = parser.parse_args()
    parent_manifest = json.loads(
        (args.parent_dir / "parent_manifest.json").read_text(encoding="utf-8")
    )
    if parent_manifest["species"] != args.species:
        raise ValueError(
            f"requested species {args.species!r} does not match parent "
            f"{parent_manifest['species']!r}"
        )
    output_dir = args.output_dir
    if output_dir is None:
        root = Path(load_spec(args.spec)["orbital_source"]["checkpoint_root"])
        output_dir = root / "semilocal" / args.stage / args.species
    manifest = run_semilocal_stage(
        args.parent_dir,
        output_dir,
        args.spec,
        args.max_memory_mb,
        args.block_size,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
