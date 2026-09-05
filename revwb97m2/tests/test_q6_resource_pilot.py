from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import yaml

from revwb97m2.scripts import run_q6_resource_pilot as q6


def test_q6_manifest_freezes_existing_step12_cases_and_safe_routes() -> None:
    path = Path("revwb97m2/manifests/qchem_gateway/q6_resource_pilots_v1.yaml")
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert manifest["status"] == "frozen_before_results"
    assert [(row["species"], row["size_role"]) for row in manifest["cases"]] == [
        ("3d4dIPSS_Ag_GS", "small"),
        ("TMB28_C1", "medium"),
        ("MOR32_pr24", "high"),
    ]
    assert [row["memory_class_mb"] for row in manifest["cases"]] == [3750, 30000, 300000]
    assert [row["resources"]["memory_gib"] for row in manifest["cases"]] == [14, 62, 557]
    assert all(row["resources"]["partition"] == "lr8" for row in manifest["cases"])
    assert manifest["runtime_contract"]["maximum_scf_cycles"] == 0
    assert manifest["runtime_contract"]["diagnostic_export"] == "disabled"


def test_q6_d4_uses_record_geometry_without_scf(monkeypatch) -> None:
    record = {
        "record_sha256": "a" * 64,
        "pyscf_molecule": {
            "unit": "Angstrom",
            "ghost_atom_count": 0,
            "real_atom_count": 3,
            "charge": 0,
            "atom": "H 0 0 0\nH 0 0 1\nH 0 1 0\n",
        },
    }
    monkeypatch.setattr(q6, "load_spec", lambda: {})
    monkeypatch.setattr(q6, "input_artifact_paths", lambda _spec: {"records": Path("unused")})
    monkeypatch.setattr(q6, "load_record", lambda _path, _species: (record, 1))
    energy, count = q6.d4_atm("fixture", "a" * 64)
    assert count == 3
    assert np.isfinite(energy)
    with pytest.raises(ValueError, match="source-record hash"):
        q6.d4_atm("fixture", "b" * 64)
