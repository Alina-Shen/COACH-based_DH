#!/usr/bin/env python3
"""Validate committed GSCDB137 manifest artifacts without scratch access."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "gscdb137"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str, failures: list[str]) -> None:
    print(("PASS" if condition else "FAIL") + f": {message}")
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    species = rows(MANIFEST / "species_manifest.csv")
    datasets = rows(MANIFEST / "dataset_manifest.csv")
    auxiliary = rows(MANIFEST / "auxiliary_dataset_groups.csv")
    bignc = rows(MANIFEST / "bignc_species_manifest.csv")
    weights = rows(ROOT / "manifests" / "weights" / "coach_si_table2_first_cycle.csv")
    provenance = json.loads((MANIFEST / "source_provenance.json").read_text())

    check(len(species) == 14006, "14,006 molecular records", failures)
    check(len({row["species"] for row in species}) == len(species), "unique species IDs", failures)
    scopes = Counter(row["scope"] for row in species)
    check(scopes == {"gscdb137": 13907, "auxiliary_only": 99}, "13,907 core plus 99 auxiliary-only species", failures)
    check(len(datasets) == 137, "137 dataset rows", failures)
    check(sum(int(row["reaction_count"]) for row in datasets) == 8377, "8,377 core reactions", failures)
    check({row["dataset_group"] for row in auxiliary} == {"OEEFD", "SC74"}, "only OEEFD and SC74 are auxiliary", failures)
    check(sum(int(row["reaction_count"]) for row in auxiliary) == 71, "71 auxiliary reaction rows", failures)
    check(len(bignc) == 75, "75 BigNC species", failures)
    check({name for row in bignc for name in row["datasets"].split(";")} == {"L14", "vL11"}, "BigNC is L14 plus vL11", failures)
    check(len(weights) == 46, "46 published first-cycle COACH weight rows", failures)
    check(provenance["commit"] == "f62f5d844d64b4ff451cbfc9320a39d830857099", "pinned GSCDB commit", failures)
    for record in provenance["source_files"]:
        source = ROOT / Path(record["vendored_path"]).relative_to("revwb97m2")
        check(source.is_file(), f"vendored source exists: {source.name}", failures)
        check(sha256(source) == record["sha256"], f"source hash: {source.name}", failures)

    if failures:
        raise SystemExit(f"{len(failures)} validation checks failed")
    print("All GSCDB137 manifest validation checks passed.")


if __name__ == "__main__":
    main()
