from __future__ import annotations

import json

import numpy as np
import pytest

from revwb97m2.production_generator import BOUNDARY_BY_NAME, inspect_boundary
from revwb97m2.step13_stages import publish_assembly


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

    output = root / "assembly"
    manifest = publish_assembly(root, output)
    assert manifest["status"] == "species_assembly_complete_and_validated"
    assert np.load(output / "feature_vector_78.npy").shape == (78,)
    assert np.load(output / "feature_vector_291.npy").shape == (291,)
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
