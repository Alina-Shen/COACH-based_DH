from __future__ import annotations

import json
from pathlib import Path

import pytest

from revwb97m2.production_generator import (
    BOUNDARIES,
    BOUNDARY_BY_NAME,
    boundary_directory,
    build_dry_run_plan,
    canonical_sha256,
    inspect_boundary,
    load_locked_population,
    plan_species,
    sha256,
    species_authority_fingerprint,
    write_plan_atomic,
)


AUTHORITIES = {
    "species_roles_sha256": "1" * 64,
    "basis_bridge_records_sha256": "2" * 64,
    "record_index_sha256": "3" * 64,
    "scientific_specification_sha256": "4" * 64,
    "production_generator_module_sha256": "5" * 64,
}
SPECIES = {
    "scope": "gscdb137",
    "species": "fixture_H2O",
    "roles": ["coefficient_fitting"],
    "source_record_sha256": "a" * 64,
    "record_line_number": 7,
    "orbital_spherical_aos": 12,
    "auxiliary_spherical_aos": 24,
    "electron_count": 10,
    "spin": 0,
    "orbital_definition_sha256": "b" * 64,
    "auxiliary_definition_sha256": "c" * 64,
    "ecp_definition_sha256": "d" * 64,
}


def publish_complete_boundary(
    path: Path,
    boundary_name: str,
    species: dict = SPECIES,
    authorities: dict = AUTHORITIES,
) -> None:
    contract = BOUNDARY_BY_NAME[boundary_name]
    path.mkdir(parents=True)
    artifact = path / "payload.bin"
    artifact.write_bytes(b"validated fixture")
    manifest = {
        "schema_version": 1,
        "status": contract.complete_status,
        "scope": species["scope"],
        "species": species["species"],
        "source_record_sha256": species["source_record_sha256"],
        "authority_fingerprint_sha256": species_authority_fingerprint(
            species, authorities
        ),
        "artifacts_sha256": {"payload.bin": sha256(artifact)},
    }
    manifest_path = path / contract.manifest_name
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (path / contract.marker_name).write_text("complete\n", encoding="utf-8")
    (path / contract.validation_name).write_text(
        json.dumps({"status": "passed", "manifest_sha256": sha256(manifest_path)}),
        encoding="utf-8",
    )


def inspect(path: Path, boundary_name: str = "parent") -> dict:
    return inspect_boundary(
        path,
        BOUNDARY_BY_NAME[boundary_name],
        SPECIES["scope"],
        SPECIES["species"],
        SPECIES["source_record_sha256"],
        species_authority_fingerprint(SPECIES, AUTHORITIES),
    )


def test_locked_population_is_exact_role_minimal_union() -> None:
    population = load_locked_population()
    assert len(population) == 17452
    assert all(row["roles"] for row in population)
    assert len({(row["scope"], row["species"]) for row in population}) == 17452


def test_boundary_layout_has_seven_independent_restart_points(tmp_path: Path) -> None:
    root = tmp_path / "scope" / "species"
    assert [boundary.name for boundary in BOUNDARIES] == [
        "parent",
        "semilocal_250974",
        "semilocal_99590",
        "semilocal_75302",
        "vv10",
        "ri_mp2",
        "assembly",
    ]
    assert boundary_directory(root, "parent") == root / "parent"
    assert boundary_directory(root, "semilocal_99590") == root / "semilocal/99590"
    assert boundary_directory(root, "ri_mp2") == root / "ri_mp2"


def test_complete_boundary_is_reused_only_after_all_hash_checks(tmp_path: Path) -> None:
    path = tmp_path / "parent"
    publish_complete_boundary(path, "parent")
    report = inspect(path)
    assert report["state"] == "complete_validated"
    assert report["reusable"] is True

    (path / "payload.bin").write_bytes(b"corrupted")
    report = inspect(path)
    assert report["state"] == "corrupt_preserved"
    assert report["reusable"] is False


def test_failed_partial_stale_and_interrupted_states_are_preserved(
    tmp_path: Path,
) -> None:
    failed = tmp_path / "failed"
    failed.mkdir()
    (failed / "FAILURE.json").write_text("{}", encoding="utf-8")
    assert inspect(failed)["state"] == "failed_preserved"

    partial = tmp_path / "partial"
    partial.mkdir()
    assert inspect(partial)["state"] == "partial_preserved"

    stale = tmp_path / "stale"
    publish_complete_boundary(stale, "parent")
    manifest_path = stale / "parent_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source_record_sha256"] = "f" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (stale / "validation.json").write_text(
        json.dumps({"status": "passed", "manifest_sha256": sha256(manifest_path)}),
        encoding="utf-8",
    )
    assert inspect(stale)["state"] == "stale_authority_preserved"

    expected = tmp_path / "missing"
    (tmp_path / ".missing.tmp.123").mkdir()
    assert inspect(expected)["state"] == "interrupted_temporary_present"


def test_species_plan_is_dependency_aware_and_resource_gated(tmp_path: Path) -> None:
    plan = plan_species(SPECIES, tmp_path, AUTHORITIES)
    assert plan["submission_authorized"] is False
    assert plan["resource_tier"] is None
    assert plan["stages"]["parent"]["action"] == (
        "eligible_pending_step12_resources"
    )
    assert plan["stages"]["semilocal_250974"]["action"] == (
        "eligible_after_dependencies_pending_step12_resources"
    )
    assert plan["stages"]["assembly"]["dependencies"] == [
        "semilocal_250974",
        "semilocal_99590",
        "semilocal_75302",
        "vv10",
        "ri_mp2",
    ]

    parent_path = Path(plan["stages"]["parent"]["path"])
    publish_complete_boundary(parent_path, "parent")
    refreshed = plan_species(SPECIES, tmp_path, AUTHORITIES)
    assert refreshed["stages"]["parent"]["action"] == "reuse"
    assert refreshed["stages"]["vv10"]["action"] == (
        "eligible_pending_step12_resources"
    )


def test_plan_identity_and_atomic_non_overwriting_output(tmp_path: Path) -> None:
    first = build_dry_run_plan([SPECIES], tmp_path / "production", AUTHORITIES)
    second = build_dry_run_plan([SPECIES], tmp_path / "production", AUTHORITIES)
    assert first["plan_id"] == second["plan_id"]
    assert first["plan_id"] == canonical_sha256(
        {
            "authorities": AUTHORITIES,
            "population": [
                (
                    SPECIES["scope"],
                    SPECIES["species"],
                    SPECIES["source_record_sha256"],
                )
            ],
            "boundaries": [boundary.name for boundary in BOUNDARIES],
        }
    )[:16]
    output = tmp_path / "plan.json"
    write_plan_atomic(first, output)
    assert json.loads(output.read_text(encoding="utf-8"))["plan_id"] == first[
        "plan_id"
    ]
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        write_plan_atomic(first, output)
