"""Resource-aware but non-submitting Step-13 initial production planner."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from revwb97m2.production_generator import (
    DEFAULT_PRODUCTION_ROOT,
    canonical_sha256,
    sha256,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_INVENTORY = PROJECT_ROOT / "manifests/step12/step12_fitting_inventory_v1.csv"
Q4_VALIDATION = PROJECT_ROOT / "manifests/qchem_gateway/q4_validation_v1.json"
Q6_PILOT_MANIFEST = PROJECT_ROOT / "manifests/qchem_gateway/q6_resource_pilots_v1.yaml"
Q6_ACCOUNTING = PROJECT_ROOT / "manifests/qchem_gateway/q6_slurm_accounting_v1.json"
Q6_RESOURCE_GUIDANCE = PROJECT_ROOT / "manifests/qchem_gateway/q6_resource_guidance_v1.yaml"
STEP9_VALIDATION = PROJECT_ROOT / "manifests/scalar_features/step9_qchem_validation_v3.json"
QCHEM_STEP13_ADAPTER = PROJECT_ROOT / "qchem_step13_stages.py"
FRESH_SPECIES_VALIDATION = PROJECT_ROOT / "manifests/production_generator/step13_fresh_species_validation_v1.json"
QCHEM_BOUNDARIES = (
    {"name": "qchem_archive", "dependencies": []},
    *(
        {"name": f"integrated_dv_{grid}", "dependencies": ["qchem_archive"]}
        for grid in ("250974", "99590", "75302")
    ),
    {"name": "vv10", "dependencies": ["qchem_archive"]},
    {"name": "ri_mp2", "dependencies": ["qchem_archive"]},
    {"name": "d4_atm", "dependencies": []},
    {
        "name": "assembly",
        "dependencies": [
            "integrated_dv_250974", "integrated_dv_99590", "integrated_dv_75302",
            "vv10", "ri_mp2", "d4_atm",
        ],
    },
)
QCHEM_BOUNDARY_NAMES = tuple(row["name"] for row in QCHEM_BOUNDARIES)
PRESERVED_STOP_STATES = {
    "failed_preserved", "partial_preserved", "corrupt_preserved",
    "stale_authority_preserved",
}


def qchem_boundary_actions(states: dict[str, str]) -> dict[str, str]:
    """Resolve immutable-boundary restart actions without running or submitting."""

    if set(states) != set(QCHEM_BOUNDARY_NAMES):
        raise ValueError("Q-Chem boundary states must name all eight boundaries exactly")
    actions: dict[str, str] = {}
    for boundary in QCHEM_BOUNDARIES:
        name = boundary["name"]
        state = states[name]
        if state == "complete_validated":
            actions[name] = "reuse"
        elif state in PRESERVED_STOP_STATES:
            actions[name] = "stop_and_report_without_overwrite"
        elif state == "interrupted_temporary_present":
            actions[name] = "review_temporary_without_overwrite"
        elif state != "missing":
            raise ValueError(f"unknown Q-Chem boundary state for {name}: {state}")
        elif all(states[dependency] == "complete_validated" for dependency in boundary["dependencies"]):
            actions[name] = "eligible_bounded_execution_not_submission_authorized"
        elif any(states[dependency] in PRESERVED_STOP_STATES or states[dependency] == "interrupted_temporary_present" for dependency in boundary["dependencies"]):
            actions[name] = "blocked_by_preserved_dependency_review"
        else:
            actions[name] = "blocked_by_missing_dependencies"
    return actions


def load_initial_inventory(path: Path = DEFAULT_INVENTORY) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "scope", "species", "tier", "memory_class_mb", "requested_memory_gib",
        "qchem_mem_total_mb", "partition", "account", "qos", "wall_hours", "cpus",
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
                "qchem_mem_total_mb": int(row["qchem_mem_total_mb"]),
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
    authorities = {
        "inventory_sha256": sha256(DEFAULT_INVENTORY),
        "q4_validation_sha256": sha256(Q4_VALIDATION),
        "q6_pilot_manifest_sha256": sha256(Q6_PILOT_MANIFEST),
        "q6_slurm_accounting_sha256": sha256(Q6_ACCOUNTING),
        "q6_resource_guidance_sha256": sha256(Q6_RESOURCE_GUIDANCE),
        "step9_qchem_validation_sha256": sha256(STEP9_VALIDATION),
        "qchem_step13_adapter_sha256": sha256(QCHEM_STEP13_ADAPTER),
        "step13_fresh_species_validation_sha256": sha256(FRESH_SPECIES_VALIDATION),
        "planner_module_sha256": sha256(Path(__file__)),
    }
    identity = {
        "authorities": authorities,
        "boundaries": QCHEM_BOUNDARIES,
        "species": [(row["scope"], row["species"], row["source_record_sha256"]) for row in inventory],
    }
    return {
        "schema_version": 1,
        "status": "resource_specific_plan_not_submission_authorized",
        "purpose": "step13_initial_2799_species_qchem_archive_eight_boundary_plan",
        "inventory": str(DEFAULT_INVENTORY.relative_to(PROJECT_ROOT.parent)),
        "inventory_sha256": authorities["inventory_sha256"],
        "authorities": authorities,
        "production_root": str(production_root),
        "species_count": len(inventory),
        "boundaries": list(QCHEM_BOUNDARIES),
        "density_route": "reuse_validated_qchem_wb97m_v_archive_without_scf",
        "q4_feature_boundary": {
            "publisher": "revwb97m2/qchem_feature_publisher.py",
            "artifacts": [
                "integrated_dv_180x96.npy",
                "selected_features_3x96.npy",
                "semilocal_features_288.npy",
            ],
            "status": "implemented_and_validated",
        },
        "qchem_step13_adapter": {
            "path": "revwb97m2/qchem_step13_stages.py",
            "sha256": authorities["qchem_step13_adapter_sha256"],
            "active_feature_model": "R2_coachform_292",
            "status": "implemented_and_fresh_production_species_validated",
        },
        "fresh_species_execution": {
            "species": "11_H2O_TA13",
            "job_id": 25614541,
            "validation": "revwb97m2/manifests/production_generator/step13_fresh_species_validation_v1.json",
            "validation_sha256": authorities["step13_fresh_species_validation_sha256"],
            "status": "passed",
        },
        "restart_policy": {
            "complete_validated": "reuse_without_rewrite",
            "missing": "run_only_after_dependencies_and_separate_authorization",
            "failed_partial_corrupt_or_stale": "preserve_and_stop",
            "interrupted_temporary": "review_without_overwrite",
        },
        "empty_root_dependency_actions": qchem_boundary_actions(
            {name: "missing" for name in QCHEM_BOUNDARY_NAMES}
        ),
        "resource_calibration_status": "q6_complete_conservative_step12_assignments_retained",
        "q6_resource_guidance": {
            "path": str(Q6_RESOURCE_GUIDANCE.relative_to(PROJECT_ROOT.parent)),
            "sha256": authorities["q6_resource_guidance_sha256"],
            "decision": "retain_step12_inventory_assignments",
            "scope": "qchem_archive_and_integrated_dv_stages_only",
            "vv10_and_ri_mp2_resources": "step9_gateway_measured_production_retains_conservative_step12_assignment",
        },
        "boundary_implementation_status": {
            "qchem_archive": "fresh_production_species_implemented_and_validated",
            "integrated_dv_250974": "fresh_production_species_implemented_and_validated",
            "integrated_dv_99590": "fresh_production_species_implemented_and_validated",
            "integrated_dv_75302": "fresh_production_species_implemented_and_validated",
            "vv10": "step9_qchem_same_archive_implemented_and_validated",
            "ri_mp2": "step9_qchem_same_archive_implemented_and_validated",
            "d4_atm": "geometry_only_implementation_validated",
            "assembly": "qchem_r2_292_fresh_production_species_validated",
        },
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
