#!/usr/bin/env python3
"""Build the lightweight byte-offset index for immutable molecular records."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/pyscf/revwb97m2_all_uks_inputs_v1/pyscf_input_records.jsonl"
)
OUTPUT = ROOT / "manifests" / "parent_scf" / "record_byte_offsets.csv"


def main() -> int:
    rows = []
    with SOURCE.open("rb") as handle:
        line_number = 0
        while True:
            offset = handle.tell()
            payload = handle.readline()
            if not payload:
                break
            line_number += 1
            record = json.loads(payload)
            rows.append(
                {
                    "species": record["identity"]["species"],
                    "line_number": line_number,
                    "byte_offset": offset,
                    "byte_length": len(payload),
                    "record_sha256": record["record_sha256"],
                }
            )
    if len(rows) != 17658 or len({row["species"] for row in rows}) != len(rows):
        raise ValueError("immutable record index must contain 17,658 unique species")
    rows.sort(key=lambda row: row["species"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("species", "line_number", "byte_offset", "byte_length", "record_sha256"),
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} byte offsets to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
