#!/usr/bin/env python3
"""Build the exact two-tier Step-12 inventory for coefficient-fitting species."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROLES = ROOT / "manifests/data_roles/species_roles.csv"
DEFAULT_BRIDGE = ROOT / "manifests/basis_bridge/resolved_basis_records.csv"
DEFAULT_METADATA = ROOT / "manifests/data_roles/qchem_input_metadata.csv"
DEFAULT_QCHEM_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/qchem/gscdb137_v1"
)
DEFAULT_OUTPUT = ROOT / "manifests/step12/step12_fitting_inventory_v1.csv"
DEFAULT_SUMMARY = ROOT / "manifests/step12/step12_fitting_inventory_v1.json"
MEMORY_SAFETY_FACTOR = 1.25
PROCESS_OVERHEAD_MB = 4096
SBATCH_REQUEST_MULTIPLIER = 1.5
MHG_MAX_MEMORY_TOTAL_MB = 60000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_rem_memory(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    values: dict[str, int] = {}
    for key in ("MEM_TOTAL", "MEM_STATIC"):
        matches = re.findall(rf"(?im)^\s*{key}\s*(?:=\s*)?(\d+)\s*$", text)
        if not matches:
            raise ValueError(f"{path} has no unambiguous {key}")
        values[key] = int(matches[-1])
    return values["MEM_TOTAL"], values["MEM_STATIC"]


def requested_memory_gib(memory_total_mb: int) -> int:
    base_request_gib = max(
        8,
        math.ceil(
            (MEMORY_SAFETY_FACTOR * memory_total_mb + PROCESS_OVERHEAD_MB) / 1024
        ),
    )
    return math.ceil(SBATCH_REQUEST_MULTIPLIER * base_request_gib)


def atomic_write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with temporary.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roles", type=Path, default=DEFAULT_ROLES)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--qchem-root", type=Path, default=DEFAULT_QCHEM_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    fitting = {
        (row["scope"], row["species"])
        for row in read_csv(args.roles)
        if row["coefficient_fitting"].lower() == "true"
    }
    bridge = {
        (row["scope"], row["species"]): row for row in read_csv(args.bridge)
    }
    metadata = {
        (row["scope"], row["species"]): row for row in read_csv(args.metadata)
    }
    missing = sorted(fitting - bridge.keys()) + sorted(fitting - metadata.keys())
    if missing:
        raise ValueError(f"authority join failed: {missing[:5]}")

    rows: list[dict[str, object]] = []
    for scope, species in sorted(fitting):
        basis = bridge[(scope, species)]
        meta = metadata[(scope, species)]
        input_path = args.qchem_root / meta["snapshot_input"]
        if sha256(input_path) != meta["input_sha256"]:
            raise ValueError(f"Q-Chem input hash mismatch: {scope}/{species}")
        memory_total_mb, memory_static_mb = parse_rem_memory(input_path)
        memory_gib = requested_memory_gib(memory_total_mb)
        if memory_total_mb <= MHG_MAX_MEMORY_TOTAL_MB:
            tier = "small_mhg"
            partition, account, qos, wall_hours, cpus = (
                "mhg",
                "mhg",
                "normal",
                72,
                8,
            )
        else:
            tier = "large_lr8"
            partition, account, qos, wall_hours, cpus = (
                "lr8",
                "lr_mhg2",
                "mhg2_lr8_normal",
                336,
                16,
            )
        nao = int(basis["orbital_spherical_aos"])
        naux = int(basis["auxiliary_spherical_aos"])
        static_df_gib = naux * nao * (nao + 1) / 2 * 8 / 1024**3
        rows.append(
            {
                "scope": scope,
                "species": species,
                "tier": tier,
                "memory_class_mb": memory_total_mb,
                "qchem_mem_total_mb": memory_total_mb,
                "qchem_mem_static_mb": memory_static_mb,
                "requested_memory_gib": memory_gib,
                "pyscf_max_memory_mb": memory_total_mb,
                "partition": partition,
                "account": account,
                "qos": qos,
                "wall_hours": wall_hours,
                "cpus": cpus,
                "orbital_aos": nao,
                "auxiliary_aos": naux,
                "electron_count": int(basis["electron_count"]),
                "spin": int(basis["spin"]),
                "atom_count": int(meta["atom_count"]),
                "real_atom_count": int(meta["real_atom_count"]),
                "ghost_atom_count": int(meta["ghost_atom_count"]),
                "has_gen_basis": str(int(meta["basis_block_bytes"]) > 0).lower(),
                "has_ecp": str(bool(meta["qchem_rem_ecp"] or meta["ecp_block_sha256"])).lower(),
                "static_df_three_center_gib": f"{static_df_gib:.9f}",
                "source_record_sha256": basis["source_record_sha256"],
                "qchem_input_sha256": meta["input_sha256"],
                "qchem_input_path": str(input_path),
            }
        )
    if len(rows) != 2799:
        raise ValueError(f"expected 2799 fitting species, found {len(rows)}")

    atomic_write_csv(args.output, rows)
    tier_counts = Counter(str(row["tier"]) for row in rows)
    memory_counts = Counter(int(row["memory_class_mb"]) for row in rows)
    summary = {
        "schema_version": 1,
        "status": "two_tier_inventory_complete",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "population": "coefficient_fitting_only",
        "species_count": len(rows),
        "tier_predicate": {
            "small_mhg": f"Q-Chem MEM_TOTAL <= {MHG_MAX_MEMORY_TOTAL_MB} MB",
            "large_lr8": f"Q-Chem MEM_TOTAL > {MHG_MAX_MEMORY_TOTAL_MB} MB",
        },
        "tier_counts": dict(sorted(tier_counts.items())),
        "memory_class_counts": {
            str(key): memory_counts[key] for key in sorted(memory_counts)
        },
        "memory_rule": {
            "formula": "ceil(1.5 * max(8, ceil((1.25 * qchem_MEM_TOTAL_MB + 4096 MB) / 1024))) GiB",
            "base_minimum_gib": 8,
            "final_sbatch_multiplier": SBATCH_REQUEST_MULTIPLIER,
            "classes": {
                str(value): requested_memory_gib(value)
                for value in sorted(memory_counts)
            },
        },
        "routes": {
            "small_mhg": {
                "partition": "mhg",
                "account": "mhg",
                "qos": "normal",
                "wall_hours": 72,
                "cpus": 8,
                "array_concurrency": 16,
            },
            "large_lr8": {
                "partition": "lr8",
                "account": "lr_mhg2",
                "qos": "mhg2_lr8_normal",
                "wall_hours": 336,
                "cpus": 16,
                "array_concurrency": 1,
            },
        },
        "authority": {
            "roles_path": str(args.roles),
            "roles_sha256": sha256(args.roles),
            "bridge_path": str(args.bridge),
            "bridge_sha256": sha256(args.bridge),
            "metadata_path": str(args.metadata),
            "metadata_sha256": sha256(args.metadata),
        },
        "inventory_path": str(args.output),
        "inventory_sha256": sha256(args.output),
    }
    atomic_write_json(args.summary, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
