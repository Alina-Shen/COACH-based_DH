#!/usr/bin/env python3
"""Execute or reuse the exact eight Step-13 boundaries for one species."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.parent_scf import DEFAULT_SPEC  # noqa: E402
from revwb97m2.production_generator import (  # noqa: E402
    BOUNDARIES,
    authority_hashes,
    inspect_boundary,
    load_locked_population,
    species_authority_fingerprint,
)
from revwb97m2.step13_stages import (  # noqa: E402
    publish_assembly,
    publish_d4_atm,
    publish_parent,
    publish_ri_mp2,
    publish_semilocal_grid,
    publish_vv10,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--max-memory-mb", type=int, required=True)
    parser.add_argument("--block-size", type=int, required=True)
    args = parser.parse_args()
    matches = [row for row in load_locked_population() if row["species"] == args.species]
    if len(matches) != 1:
        raise ValueError(f"expected one locked population row, got {len(matches)}")
    identity = matches[0]
    authorities = authority_hashes()
    fingerprint = species_authority_fingerprint(identity, authorities)
    species_root = (args.output_root / identity["scope"] / args.species).resolve()
    paths = {
        "parent": species_root / "parent",
        "semilocal_250974": species_root / "semilocal/250974",
        "semilocal_99590": species_root / "semilocal/99590",
        "semilocal_75302": species_root / "semilocal/75302",
        "vv10": species_root / "vv10",
        "ri_mp2": species_root / "ri_mp2",
        "d4_atm": species_root / "d4_atm",
        "assembly": species_root / "assembly",
    }
    actions = []
    for contract in BOUNDARIES:
        report = inspect_boundary(
            paths[contract.name], contract, identity["scope"], args.species,
            identity["source_record_sha256"], fingerprint,
        )
        if report["state"] == "complete_validated":
            actions.append({"boundary": contract.name, "action": "reuse"})
            continue
        if report["state"] != "missing":
            raise RuntimeError(f"boundary requires review: {contract.name}: {report}")
        if contract.name == "parent":
            publish_parent(args.species, paths[contract.name], args.spec, args.max_memory_mb, args.block_size)
        elif contract.name.startswith("semilocal_"):
            publish_semilocal_grid(
                paths["parent"], paths[contract.name], contract.name.removeprefix("semilocal_"),
                args.spec, args.max_memory_mb, args.block_size,
            )
        elif contract.name == "vv10":
            publish_vv10(paths["parent"], paths[contract.name], args.spec, args.max_memory_mb)
        elif contract.name == "ri_mp2":
            publish_ri_mp2(paths["parent"], paths[contract.name], args.spec, args.max_memory_mb)
        elif contract.name == "d4_atm":
            publish_d4_atm(paths["parent"], paths[contract.name], args.spec, args.max_memory_mb)
        else:
            publish_assembly(species_root, paths[contract.name])
        actions.append({"boundary": contract.name, "action": "publish"})
    print(json.dumps({"status": "complete", "species": args.species, "species_root": str(species_root), "actions": actions}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
