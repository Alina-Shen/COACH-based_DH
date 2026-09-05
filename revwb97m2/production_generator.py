"""Resource-neutral Step-13 production inventory and resumability planner.

This module never runs chemistry, selects Slurm resources, or submits jobs.
It joins the locked fixed-geometry role population to the validated basis and
record authorities, inspects non-overwriting stage directories, and emits a
dry-run dependency plan whose resource fields remain blocked on Step 12.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PROJECT_ROOT.parent
DEFAULT_POLICY = (
    PROJECT_ROOT
    / "manifests"
    / "production_generator"
    / "step13_preparatory_v2.yaml"
)
DEFAULT_ROLES = PROJECT_ROOT / "manifests/data_roles/species_roles.csv"
DEFAULT_BRIDGE = PROJECT_ROOT / "manifests/basis_bridge/resolved_basis_records.csv"
DEFAULT_RECORD_INDEX = PROJECT_ROOT / "manifests/parent_scf/record_byte_offsets.csv"
DEFAULT_SPEC = PROJECT_ROOT / "configs/scientific_spec.yaml"
DEFAULT_PRODUCTION_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/production"
)
ENERGY_ROLE_COLUMNS = (
    "coefficient_fitting",
    "model_selection",
    "overfitting_diagnostic",
    "final_assessment",
)
GRID_IDS = ("250974", "99590", "75302")


@dataclass(frozen=True)
class BoundaryContract:
    name: str
    manifest_name: str
    marker_name: str
    validation_name: str
    complete_status: str
    dependencies: tuple[str, ...]


BOUNDARIES = (
    BoundaryContract(
        "parent",
        "parent_manifest.json",
        "PARENT_COMPLETE",
        "validation.json",
        "parent_complete_and_checkpoint_validated",
        (),
    ),
    *(
        BoundaryContract(
            f"semilocal_{grid_id}",
            "semilocal_grid_manifest.json",
            "SEMILOCAL_GRID_COMPLETE",
            "validation.json",
            "semilocal_grid_complete_and_validated",
            ("parent",),
        )
        for grid_id in GRID_IDS
    ),
    BoundaryContract(
        "vv10",
        "vv10_manifest.json",
        "VV10_COMPLETE",
        "validation.json",
        "vv10_complete_and_validated",
        ("parent",),
    ),
    BoundaryContract(
        "ri_mp2",
        "ri_mp2_manifest.json",
        "RI_MP2_COMPLETE",
        "validation.json",
        "ri_mp2_complete_and_validated",
        ("parent",),
    ),
    BoundaryContract(
        "d4_atm",
        "d4_atm_manifest.json",
        "D4_ATM_COMPLETE",
        "validation.json",
        "d4_atm_complete_and_validated",
        ("parent",),
    ),
    BoundaryContract(
        "assembly",
        "assembly_manifest.json",
        "ASSEMBLY_COMPLETE",
        "validation.json",
        "species_assembly_complete_and_validated",
        tuple(f"semilocal_{grid_id}" for grid_id in GRID_IDS)
        + ("vv10", "ri_mp2", "d4_atm"),
    ),
)
BOUNDARY_BY_NAME = {boundary.name: boundary for boundary in BOUNDARIES}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _true(value: str) -> bool:
    return value.strip().lower() == "true"


def _safe_component(value: str, label: str) -> str:
    if not value or value in {".", ".."} or "/" in value or "\0" in value:
        raise ValueError(f"unsafe {label} path component: {value!r}")
    return value


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_locked_population(
    roles_path: Path = DEFAULT_ROLES,
    bridge_path: Path = DEFAULT_BRIDGE,
    record_index_path: Path = DEFAULT_RECORD_INDEX,
) -> list[dict[str, Any]]:
    """Join and validate the role-minimal fixed-geometry species population."""

    roles_rows = [
        row
        for row in _read_csv(roles_path)
        if any(_true(row[column]) for column in ENERGY_ROLE_COLUMNS)
    ]
    bridge_rows = {
        (row["scope"], row["species"]): row for row in _read_csv(bridge_path)
    }
    record_rows = {row["species"]: row for row in _read_csv(record_index_path)}
    role_keys = [(row["scope"], row["species"]) for row in roles_rows]
    if len(role_keys) != len(set(role_keys)):
        raise ValueError("duplicate scope/species identity in locked role population")
    missing_bridge = sorted(set(role_keys) - set(bridge_rows))
    missing_records = sorted(
        species for _scope, species in role_keys if species not in record_rows
    )
    if missing_bridge or missing_records:
        raise ValueError(
            "locked population authority join failed: "
            f"missing_bridge={missing_bridge[:5]}, missing_records={missing_records[:5]}"
        )

    population: list[dict[str, Any]] = []
    for role in roles_rows:
        scope = _safe_component(role["scope"], "scope")
        species = _safe_component(role["species"], "species")
        bridge = bridge_rows[(scope, species)]
        record = record_rows[species]
        source_hash = bridge["source_record_sha256"]
        if source_hash != record["record_sha256"]:
            raise ValueError(f"record hash disagreement for {scope}/{species}")
        if not _true(bridge["required_for_energy_roles"]):
            raise ValueError(f"energy-role bridge row is not required: {scope}/{species}")
        if bridge["runnable_status"] != "runnable_basis_metadata_validated":
            raise ValueError(f"basis bridge is not runnable: {scope}/{species}")
        active_roles = [column for column in ENERGY_ROLE_COLUMNS if _true(role[column])]
        population.append(
            {
                "scope": scope,
                "species": species,
                "roles": active_roles,
                "source_record_sha256": source_hash,
                "record_line_number": int(record["line_number"]),
                "orbital_spherical_aos": int(bridge["orbital_spherical_aos"]),
                "auxiliary_spherical_aos": int(bridge["auxiliary_spherical_aos"]),
                "electron_count": int(bridge["electron_count"]),
                "spin": int(bridge["spin"]),
                "orbital_definition_sha256": bridge["orbital_definition_sha256"],
                "auxiliary_definition_sha256": bridge[
                    "auxiliary_definition_sha256"
                ],
                "ecp_definition_sha256": bridge["ecp_definition_sha256"],
            }
        )
    return sorted(population, key=lambda row: (row["scope"], row["species"]))


def authority_hashes(
    roles_path: Path = DEFAULT_ROLES,
    bridge_path: Path = DEFAULT_BRIDGE,
    record_index_path: Path = DEFAULT_RECORD_INDEX,
    spec_path: Path = DEFAULT_SPEC,
) -> dict[str, str]:
    return {
        "species_roles_sha256": sha256(roles_path),
        "basis_bridge_records_sha256": sha256(bridge_path),
        "record_index_sha256": sha256(record_index_path),
        "scientific_specification_sha256": sha256(spec_path),
        "production_generator_module_sha256": sha256(Path(__file__)),
    }


def species_authority_fingerprint(
    species: Mapping[str, Any], authorities: Mapping[str, str]
) -> str:
    payload = {
        "authorities": dict(authorities),
        "scope": species["scope"],
        "species": species["species"],
        "source_record_sha256": species["source_record_sha256"],
        "orbital_definition_sha256": species["orbital_definition_sha256"],
        "auxiliary_definition_sha256": species["auxiliary_definition_sha256"],
        "ecp_definition_sha256": species["ecp_definition_sha256"],
    }
    return canonical_sha256(payload)


def boundary_directory(species_root: Path, boundary_name: str) -> Path:
    if boundary_name == "parent":
        return species_root / "parent"
    if boundary_name.startswith("semilocal_"):
        return species_root / "semilocal" / boundary_name.removeprefix("semilocal_")
    return species_root / boundary_name


def _temporary_directories(path: Path) -> list[str]:
    if not path.parent.is_dir():
        return []
    return sorted(str(candidate) for candidate in path.parent.glob(f".{path.name}.tmp.*"))


def inspect_boundary(
    path: Path,
    contract: BoundaryContract,
    scope: str,
    species: str,
    source_record_sha256: str,
    authority_fingerprint_sha256: str,
) -> dict[str, Any]:
    """Classify one immutable boundary without modifying any artifact."""

    temporary = _temporary_directories(path)
    base = {"path": str(path), "temporary_directories": temporary}
    if not path.exists():
        state = "interrupted_temporary_present" if temporary else "missing"
        return {**base, "state": state, "reusable": False}
    if path.is_symlink() or not path.is_dir():
        return {**base, "state": "corrupt_preserved", "reusable": False}

    marker = path / contract.marker_name
    manifest_path = path / contract.manifest_name
    validation_path = path / contract.validation_name
    failure_path = path / "FAILURE.json"
    if failure_path.is_file() and not marker.is_file():
        return {**base, "state": "failed_preserved", "reusable": False}
    if not marker.is_file() or not manifest_path.is_file() or not validation_path.is_file():
        return {**base, "state": "partial_preserved", "reusable": False}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {**base, "state": "corrupt_preserved", "reusable": False}

    identity_matches = (
        manifest.get("scope") == scope
        and manifest.get("species") == species
        and manifest.get("status") == contract.complete_status
    )
    authority_matches = (
        manifest.get("source_record_sha256") == source_record_sha256
        and manifest.get("authority_fingerprint_sha256")
        == authority_fingerprint_sha256
    )
    if not identity_matches:
        return {**base, "state": "corrupt_preserved", "reusable": False}
    if not authority_matches:
        return {**base, "state": "stale_authority_preserved", "reusable": False}
    if validation.get("status") != "passed" or validation.get(
        "manifest_sha256"
    ) != sha256(manifest_path):
        return {**base, "state": "corrupt_preserved", "reusable": False}

    artifacts = manifest.get("artifacts_sha256")
    if not isinstance(artifacts, dict) or not artifacts:
        return {**base, "state": "corrupt_preserved", "reusable": False}
    for relative_name, expected_hash in artifacts.items():
        if not isinstance(relative_name, str) or not isinstance(expected_hash, str):
            return {**base, "state": "corrupt_preserved", "reusable": False}
        artifact = path / relative_name
        try:
            artifact.relative_to(path)
        except ValueError:
            return {**base, "state": "corrupt_preserved", "reusable": False}
        if (
            Path(relative_name).is_absolute()
            or ".." in Path(relative_name).parts
            or artifact.is_symlink()
            or not artifact.is_file()
            or sha256(artifact) != expected_hash
        ):
            return {**base, "state": "corrupt_preserved", "reusable": False}
    return {
        **base,
        "state": "complete_validated",
        "reusable": True,
        "manifest_sha256": sha256(manifest_path),
    }


def _action(state: str, dependency_states: Iterable[str]) -> str:
    if state == "complete_validated":
        return "reuse"
    if state in {
        "failed_preserved",
        "partial_preserved",
        "corrupt_preserved",
        "stale_authority_preserved",
    }:
        return "stop_and_report"
    if state == "interrupted_temporary_present":
        return "review_or_resume_without_overwrite"
    dependencies = tuple(dependency_states)
    if not dependencies or all(value == "complete_validated" for value in dependencies):
        return "eligible_pending_step12_resources"
    if any(
        value
        in {
            "failed_preserved",
            "partial_preserved",
            "corrupt_preserved",
            "stale_authority_preserved",
            "interrupted_temporary_present",
        }
        for value in dependencies
    ):
        return "blocked_by_artifact_review"
    return "eligible_after_dependencies_pending_step12_resources"


def plan_species(
    species: Mapping[str, Any],
    production_root: Path,
    authorities: Mapping[str, str],
) -> dict[str, Any]:
    species_root = production_root / species["scope"] / species["species"]
    fingerprint = species_authority_fingerprint(species, authorities)
    stages: dict[str, Any] = {}
    for contract in BOUNDARIES:
        path = boundary_directory(species_root, contract.name)
        report = inspect_boundary(
            path,
            contract,
            species["scope"],
            species["species"],
            species["source_record_sha256"],
            fingerprint,
        )
        report["dependencies"] = list(contract.dependencies)
        report["action"] = _action(
            report["state"],
            (stages[name]["state"] for name in contract.dependencies),
        )
        stages[contract.name] = report
    return {
        **dict(species),
        "species_root": str(species_root),
        "authority_fingerprint_sha256": fingerprint,
        "resource_tier": None,
        "resource_assignment_status": "pending_step12_signoff",
        "submission_authorized": False,
        "stages": stages,
    }


def build_dry_run_plan(
    population: list[dict[str, Any]],
    production_root: Path = DEFAULT_PRODUCTION_ROOT,
    authorities: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    active_authorities = dict(authorities or authority_hashes())
    species_plans = [
        plan_species(species, production_root, active_authorities)
        for species in population
    ]
    states: dict[str, int] = {}
    actions: dict[str, int] = {}
    for species in species_plans:
        for stage in species["stages"].values():
            states[stage["state"]] = states.get(stage["state"], 0) + 1
            actions[stage["action"]] = actions.get(stage["action"], 0) + 1
    identity = {
        "authorities": active_authorities,
        "population": [
            (row["scope"], row["species"], row["source_record_sha256"])
            for row in population
        ],
        "boundaries": [boundary.name for boundary in BOUNDARIES],
    }
    return {
        "schema_version": 1,
        "status": "dry_run_only_step12_resources_pending",
        "created_utc": utc_now(),
        "plan_id": canonical_sha256(identity)[:16],
        "production_root": str(production_root),
        "submission_authorized": False,
        "step12_resource_signoff_required": True,
        "resource_fields_intentionally_unset": [
            "partition",
            "account",
            "qos",
            "cpus",
            "memory",
            "walltime",
            "array_concurrency",
            "retry_limit",
            "size_tier",
            "direct_or_out_of_core_route",
        ],
        "authorities": active_authorities,
        "population_count": len(species_plans),
        "boundary_count_per_species": len(BOUNDARIES),
        "summary": {
            "boundary_states": dict(sorted(states.items())),
            "planned_actions": dict(sorted(actions.items())),
        },
        "species": species_plans,
    }


def write_plan_atomic(plan: Mapping[str, Any], output: Path) -> None:
    """Publish a dry-run plan atomically and refuse all overwrites."""

    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing dry-run plan: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.parent / f".{output.name}.tmp.{os.getpid()}"
    if temporary.exists():
        raise FileExistsError(f"refusing to reuse temporary plan path: {temporary}")
    temporary.write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.rename(output)
