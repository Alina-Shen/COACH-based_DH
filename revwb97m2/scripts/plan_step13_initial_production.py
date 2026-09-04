#!/usr/bin/env python3
"""Write a non-overwriting resource-specific Step-13 initial production plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.step13_resource_plan import (  # noqa: E402
    build_initial_resource_plan,
    load_initial_inventory,
    write_plan_atomic,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--production-root", type=Path)
    args = parser.parse_args()
    inventory = load_initial_inventory()
    kwargs = {} if args.production_root is None else {"production_root": args.production_root}
    plan = build_initial_resource_plan(inventory, **kwargs)
    write_plan_atomic(plan, args.output)
    print(json.dumps({"output": str(args.output.resolve()), "plan_id": plan["plan_id"], "species_count": plan["species_count"], "class_summaries": plan["class_summaries"], "submission_authorized": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
