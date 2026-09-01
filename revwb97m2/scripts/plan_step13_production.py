#!/usr/bin/env python3
"""Create a non-overwriting, resource-neutral Step-13 production dry run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.production_generator import (  # noqa: E402
    DEFAULT_BRIDGE,
    DEFAULT_PRODUCTION_ROOT,
    DEFAULT_RECORD_INDEX,
    DEFAULT_ROLES,
    DEFAULT_SPEC,
    authority_hashes,
    build_dry_run_plan,
    load_locked_population,
    write_plan_atomic,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--production-root", type=Path, default=DEFAULT_PRODUCTION_ROOT)
    parser.add_argument("--roles", type=Path, default=DEFAULT_ROLES)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--record-index", type=Path, default=DEFAULT_RECORD_INDEX)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument(
        "--species",
        action="append",
        default=[],
        help="Restrict to a species name; repeat for multiple species",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Deterministic test-only prefix after optional species filtering",
    )
    args = parser.parse_args()
    population = load_locked_population(args.roles, args.bridge, args.record_index)
    if args.species:
        requested = set(args.species)
        population = [row for row in population if row["species"] in requested]
        missing = requested - {row["species"] for row in population}
        if missing:
            raise KeyError(f"requested species absent from locked population: {sorted(missing)}")
    if args.limit is not None:
        if args.limit <= 0:
            raise ValueError("--limit must be positive")
        population = population[: args.limit]
    authorities = authority_hashes(
        args.roles, args.bridge, args.record_index, args.spec
    )
    plan = build_dry_run_plan(population, args.production_root, authorities)
    write_plan_atomic(plan, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "plan_id": plan["plan_id"],
                "population_count": plan["population_count"],
                "summary": plan["summary"],
                "submission_authorized": plan["submission_authorized"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
