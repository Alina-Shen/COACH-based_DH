#!/usr/bin/env python3
"""Run one manifest-selected fixed omegaB97M-V parent calculation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.parent_scf import (  # noqa: E402
    DEFAULT_SPEC,
    load_spec,
    resume_interrupted_parent,
    run_parent,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--resume-interrupted-dir",
        type=Path,
        help="Validate and publish an already-converged temporary checkpoint without restarting SCF",
    )
    parser.add_argument("--stage", choices=("gateway", "pilot", "production"), default="gateway")
    parser.add_argument("--max-memory-mb", type=int, default=40000)
    parser.add_argument("--block-size", type=int, default=10000)
    parser.add_argument("--verbose", type=int, default=4)
    parser.add_argument("--identity-radial", type=int, default=75)
    parser.add_argument("--identity-angular", type=int, default=302)
    args = parser.parse_args()
    spec = load_spec(args.spec)
    output_dir = args.output_dir
    if output_dir is None:
        checkpoint_root = Path(spec["orbital_source"]["checkpoint_root"])
        output_dir = checkpoint_root / args.stage / args.species
    common = {
        "species": args.species,
        "output_dir": output_dir,
        "spec_path": args.spec,
        "max_memory_mb": args.max_memory_mb,
        "block_size": args.block_size,
        "identity_grid": (args.identity_radial, args.identity_angular),
    }
    if args.resume_interrupted_dir is None:
        manifest = run_parent(verbose=args.verbose, **common)
    else:
        manifest = resume_interrupted_parent(
            interrupted_dir=args.resume_interrupted_dir, **common
        )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
