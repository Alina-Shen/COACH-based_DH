from __future__ import annotations

import pytest
import yaml

from revwb97m2.scripts.run_step13_fresh_species import canonical_tree_hash, load_frozen_case


def test_canonical_tree_hash_is_stable() -> None:
    records = [{"path": "a", "bytes": 1, "sha256": "b"}]
    assert canonical_tree_hash(records) == canonical_tree_hash(records)


def test_fresh_contract_requires_frozen_identity_and_resources(tmp_path) -> None:
    path = tmp_path / "contract.yaml"
    payload = {"status": "frozen_before_results", "cases": [{"species": "x", "resources": {"cpus": 8}}]}
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    _, case = load_frozen_case(path, "x", 8)
    assert case["species"] == "x"
    with pytest.raises(ValueError, match="CPU"):
        load_frozen_case(path, "x", 4)
    payload["status"] = "draft"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="frozen"):
        load_frozen_case(path, "x", 8)
