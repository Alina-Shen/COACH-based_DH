#!/usr/bin/env python3
"""Independently validate every immutable-record byte offset used by Step 8."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "manifests" / "parent_scf" / "record_byte_offsets.csv"
SOURCE = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/pyscf/revwb97m2_all_uks_inputs_v1/pyscf_input_records.jsonl"
)
OUTPUT = ROOT / "manifests" / "parent_scf" / "record_index_validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    with INDEX.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    checks = {
        "count_17658": len(rows) == 17658,
        "species_sorted_unique": (
            [row["species"] for row in rows] == sorted(row["species"] for row in rows)
            and len({row["species"] for row in rows}) == len(rows)
        ),
    }
    every_offset = True
    observed_lines = set()
    with SOURCE.open("rb") as source:
        for row in rows:
            offset = int(row["byte_offset"])
            length = int(row["byte_length"])
            source.seek(offset)
            payload = source.read(length)
            try:
                record = json.loads(payload)
                every_offset = every_offset and (
                    record["identity"]["species"] == row["species"]
                    and record["record_sha256"] == row["record_sha256"]
                    and payload.endswith(b"\n")
                )
                observed_lines.add(int(row["line_number"]))
            except Exception:
                every_offset = False
    checks["every_offset_decodes_expected_record"] = every_offset
    checks["line_numbers_exact_1_through_17658"] = observed_lines == set(range(1, 17659))
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE),
        "source_sha256": sha256(SOURCE),
        "index": str(INDEX.relative_to(ROOT.parent)),
        "index_sha256": sha256(INDEX),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "passed":
        raise RuntimeError("parent record byte-offset index validation failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
