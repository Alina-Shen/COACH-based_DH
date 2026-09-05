from __future__ import annotations

import json

import numpy as np
import pytest

from revwb97m2.production_generator import BOUNDARY_BY_NAME, inspect_boundary
from revwb97m2.step13_stages import publish_assembly, publish_d4_atm


def test_d4_atm_boundary_publishes_frozen_coach_feature(tmp_path, monkeypatch) -> None:
    parameters = {"s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0}
    monkeypatch.setattr(
        "revwb97m2.step13_stages._context",
        lambda *_args: {
            "spec": {
                "double_hybrid_energy": {
                    "dispersion_policy": {
                        "d4_atm": {
                            "definition": "pure_three_body_coach_d4_atm",
                            "damping_parameters": parameters,
                        }
                    }
                }
            },
            "mol": object(),
            "identity": {"scope": "gscdb137", "source_record_sha256": "a" * 64},
            "species": "fixture",
            "fingerprint": "b" * 64,
            "parent_manifest_sha256": "c" * 64,
        },
    )
    monkeypatch.setattr(
        "revwb97m2.step13_stages.evaluate_d4_atm",
        lambda _mol, observed: -0.005 if observed == parameters else float("nan"),
    )
    output = tmp_path / "d4_atm"
    manifest = publish_d4_atm(tmp_path / "parent", output)
    assert manifest["status"] == "d4_atm_complete_and_validated"
    assert json.loads((output / "d4_atm.json").read_text())["energy_hartree"] == pytest.approx(-0.005)
    assert (output / "D4_ATM_COMPLETE").is_file()
    assert json.loads((output / "validation.json").read_text())["status"] == "passed"


def test_split_assembly_publishes_contract_complete_boundary(tmp_path, monkeypatch) -> None:
    identity = {
        "scope": "gscdb137",
        "species": "fixture",
        "source_record_sha256": "a" * 64,
    }
    fingerprint = "b" * 64
    monkeypatch.setattr(
        "revwb97m2.step13_stages._identity",
        lambda _species: (identity, {}, fingerprint),
    )
    root = tmp_path / "gscdb137/fixture"
    (root / "parent").mkdir(parents=True)
    (root / "parent/parent_manifest.json").write_text(
        json.dumps(
            {
                "species": "fixture",
                "scf": {
                    "components": {
                        "nuclear_repulsion": 1.0,
                        "one_electron": -10.0,
                        "coulomb": 3.0,
                        "unscaled_long_range_hf_exchange": -0.7,
                        "unscaled_short_range_hf_exchange": -1.2,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    for grid in ("250974", "99590", "75302"):
        directory = root / "semilocal" / grid
        directory.mkdir(parents=True)
        np.save(directory / f"r1_semilocal_features_75_{grid}.npy", np.arange(75.0))
        np.save(directory / f"r2_semilocal_features_288_{grid}.npy", np.arange(288.0))
        (directory / "validation.json").write_text(
            json.dumps({"status": "passed"}), encoding="utf-8"
        )
    (root / "vv10").mkdir()
    (root / "vv10/vv10.json").write_text(
        json.dumps({"energy_hartree": 0.03}), encoding="utf-8"
    )
    (root / "vv10/validation.json").write_text(
        json.dumps({"status": "passed"}), encoding="utf-8"
    )
    (root / "ri_mp2").mkdir()
    (root / "ri_mp2/ri_mp2.json").write_text(
        json.dumps({"total_correlation_hartree": -0.4}), encoding="utf-8"
    )
    (root / "ri_mp2/validation.json").write_text(
        json.dumps({"status": "passed"}), encoding="utf-8"
    )
    (root / "d4_atm").mkdir()
    (root / "d4_atm/d4_atm.json").write_text(
        json.dumps({"energy_hartree": -0.005}), encoding="utf-8"
    )
    (root / "d4_atm/validation.json").write_text(
        json.dumps({"status": "passed"}), encoding="utf-8"
    )

    output = root / "assembly"
    manifest = publish_assembly(root, output)
    assert manifest["status"] == "species_assembly_complete_and_validated"
    assert np.load(output / "feature_vector_79.npy").shape == (79,)
    assert np.load(output / "feature_vector_292.npy").shape == (292,)
    assert manifest["shared_scalar_values"]["d4_atm"] == pytest.approx(-0.005)
    report = inspect_boundary(
        output,
        BOUNDARY_BY_NAME["assembly"],
        "gscdb137",
        "fixture",
        "a" * 64,
        fingerprint,
    )
    assert report["state"] == "complete_validated"
    assert report["reusable"] is True
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        publish_assembly(root, output)
