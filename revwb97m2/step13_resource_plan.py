"""Resource-aware but non-submitting Step-13 initial production planner."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from revwb97m2.production_generator import (
    BOUNDARIES,
    DEFAULT_PRODUCTION_ROOT,
    canonical_sha256,
    sha256,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_INVENTORY = PROJECT_ROOT / "manifests/step12/step12_fitting_inventory_v1.csv"


def load_initial_inventory(path: Path = DEFAULT_INVENTORY) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "scope", "species", "tier", "memory_class_mb", "requested_memory_gib",
        "pyscf_max_memory_mb", "partition", "account", "qos", "wall_hours", "cpus",
        "source_record_sha256",
    }
    if not rows or required - set(rows[0]):
        raise ValueError("Step-12 inventory lacks required production resource columns")
    seen = set()
    plan_rows = []
    for row in rows:
        key = (row["scope"], row["species"])
        if key in seen:
            raise ValueError(f"duplicate Step-12 production identity: {key}")
        seen.add(key)
        plan_rows.append(
            {
                "scope": row["scope"],
                "species": row["species"],
                "tier": row["tier"],
                "memory_class_mb": int(row["memory_class_mb"]),
                "requested_memory_gib": int(row["requested_memory_gib"]),
                "pyscf_max_memory_mb": int(row["pyscf_max_memory_mb"]),
                "partition": row["partition"],
                "account": row["account"],
                "qos": row["qos"],
                "wall_hours": int(row["wall_hours"]),
                "cpus": int(row["cpus"]),
                "source_record_sha256": row["source_record_sha256"],
            }
        )
    if len(plan_rows) != 2799:
        raise ValueError(f"expected 2799 initial fitting species, got {len(plan_rows)}")
    return sorted(plan_rows, key=lambda row: (row["tier"], row["memory_class_mb"], row["scope"], row["species"]))


def build_initial_resource_plan(
    inventory: list[dict[str, Any]],
    production_root: Path = DEFAULT_PRODUCTION_ROOT,
) -> dict[str, Any]:
    classes: dict[str, list[dict[str, Any]]] = {}
    for row in inventory:
        key = f"{row['tier']}_{row['memory_class_mb']}"
        classes.setdefault(key, []).append(row)
    class_summaries = []
    for key, rows in sorted(classes.items()):
        first = rows[0]
        concurrency = 16 if first["tier"] == "small_mhg" else 1
        class_summaries.append(
            {
                "class_key": key,
                "species_count": len(rows),
                "tier": first["tier"],
                "memory_class_mb": first["memory_class_mb"],
                "partition": first["partition"],
                "account": first["account"],
                "qos": first["qos"],
                "cpus": first["cpus"],
                "requested_memory_gib": first["requested_memory_gib"],
                "wall_hours": first["wall_hours"],
                "maximum_array_concurrency": concurrency,
            }
        )
    identity = [(row["scope"], row["species"], row["source_record_sha256"]) for row in inventory]
    return {
        "schema_version": 1,
        "status": "resource_specific_plan_not_submission_authorized",
        "purpose": "step13_initial_2799_species_seven_boundary_execution",
        "inventory": str(DEFAULT_INVENTORY.relative_to(PROJECT_ROOT.parent)),
        "inventory_sha256": sha256(DEFAULT_INVENTORY),
        "production_root": str(production_root),
        "species_count": len(inventory),
        "boundaries": [boundary.name for boundary in BOUNDARIES],
        "retry_policy": "inherit_step12_failure_ledger_and_one_engineered_resubmission_maximum",
        "submission_authorized": False,
        "class_summaries": class_summaries,
        "plan_id": canonical_sha256(identity)[:16],
        "species": inventory,
    }


def write_plan_atomic(plan: dict[str, Any], output: Path) -> None:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite Step-13 plan: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.parent / f".{output.name}.tmp"
    if temporary.exists():
        raise FileExistsError(f"temporary Step-13 plan exists: {temporary}")
    temporary.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.rename(output)
