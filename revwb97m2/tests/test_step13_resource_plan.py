from __future__ import annotations

import pytest

from revwb97m2.step13_resource_plan import build_initial_resource_plan, load_initial_inventory, write_plan_atomic


def test_initial_resource_plan_is_exact_and_not_authorized(tmp_path) -> None:
    inventory = load_initial_inventory()
    plan = build_initial_resource_plan(inventory, tmp_path / "production")
    assert plan["species_count"] == 2799
    assert plan["submission_authorized"] is False
    assert plan["boundaries"] == ["parent", "semilocal_250974", "semilocal_99590", "semilocal_75302", "vv10", "ri_mp2", "assembly"]
    counts = {row["memory_class_mb"]: row["species_count"] for row in plan["class_summaries"]}
    assert counts == {3750: 2145, 7500: 298, 15000: 186, 30000: 107, 60000: 29, 120000: 26, 300000: 8}
    output = tmp_path / "plan.json"
    write_plan_atomic(plan, output)
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        write_plan_atomic(plan, output)
