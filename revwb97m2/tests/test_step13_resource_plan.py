from __future__ import annotations

import pytest

from revwb97m2.step13_resource_plan import (
    QCHEM_BOUNDARY_NAMES,
    build_initial_resource_plan,
    load_initial_inventory,
    qchem_boundary_actions,
    write_plan_atomic,
)


def test_initial_resource_plan_is_exact_and_not_authorized(tmp_path) -> None:
    inventory = load_initial_inventory()
    plan = build_initial_resource_plan(inventory, tmp_path / "production")
    assert plan["species_count"] == 2799
    assert plan["submission_authorized"] is False
    assert [row["name"] for row in plan["boundaries"]] == [
        "qchem_archive",
        "integrated_dv_250974",
        "integrated_dv_99590",
        "integrated_dv_75302",
        "vv10", "ri_mp2", "d4_atm", "assembly",
    ]
    assert plan["density_route"] == "reuse_validated_qchem_wb97m_v_archive_without_scf"
    assert plan["q4_feature_boundary"]["status"] == "implemented_and_validated"
    assert set(plan["authorities"]) == {
        "inventory_sha256", "q4_validation_sha256", "q6_pilot_manifest_sha256",
        "planner_module_sha256",
    }
    assert plan["boundary_implementation_status"]["vv10"].startswith("pending_step9")
    assert all("pyscf_max_memory_mb" not in row for row in plan["species"])
    assert plan["empty_root_dependency_actions"]["qchem_archive"].startswith("eligible")
    assert plan["empty_root_dependency_actions"]["d4_atm"].startswith("eligible")
    assert plan["empty_root_dependency_actions"]["integrated_dv_250974"] == "blocked_by_missing_dependencies"
    assert plan["empty_root_dependency_actions"]["vv10"].startswith("blocked_pending_step9")
    counts = {row["memory_class_mb"]: row["species_count"] for row in plan["class_summaries"]}
    assert counts == {3750: 2145, 7500: 298, 15000: 186, 30000: 107, 60000: 29, 120000: 26, 300000: 8}
    output = tmp_path / "plan.json"
    write_plan_atomic(plan, output)
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        write_plan_atomic(plan, output)


def test_qchem_boundary_restart_and_dependency_actions() -> None:
    states = {name: "missing" for name in QCHEM_BOUNDARY_NAMES}
    states["qchem_archive"] = "complete_validated"
    actions = qchem_boundary_actions(states)
    assert actions["qchem_archive"] == "reuse"
    assert actions["integrated_dv_99590"].startswith("eligible_bounded")
    assert actions["vv10"] == "blocked_pending_step9_same_archive_implementation"
    assert actions["assembly"] == "blocked_by_missing_dependencies"

    states["qchem_archive"] = "corrupt_preserved"
    actions = qchem_boundary_actions(states)
    assert actions["qchem_archive"] == "stop_and_report_without_overwrite"
    assert actions["integrated_dv_99590"] == "blocked_by_preserved_dependency_review"

    states = {name: "complete_validated" for name in QCHEM_BOUNDARY_NAMES}
    assert set(qchem_boundary_actions(states).values()) == {"reuse"}
