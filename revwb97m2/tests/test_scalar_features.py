from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

from revwb97m2.scalar_features import (
    FEATURE_COUNT,
    MODEL_FEATURE_COUNTS,
    assemble_feature_vector,
    assemble_r1_r2_feature_vectors,
    direct_energy_identity,
    evaluate_ri_ump2,
    fixed_energy_partition,
    publish_r1_r2_assembly,
)


def test_ri_ump2_uses_energy_only_kernel_without_retaining_t2(
    tmp_path, monkeypatch
) -> None:
    calls = {}

    class FakeDF:
        _cderi_to_save = None

    class FakeUMP2:
        e_corr_ss = -0.1
        e_corr_os = -0.2
        with_df = FakeDF()

        def __init__(self, _mf, frozen):
            calls["frozen"] = frozen

        def density_fit(self, auxbasis):
            calls["auxbasis"] = auxbasis
            return self

        def kernel(self, *, with_t2):
            calls["with_t2"] = with_t2
            return -0.3, None

    monkeypatch.setattr("revwb97m2.scalar_features.elements.chemcore", lambda _mol: 2)
    monkeypatch.setattr("revwb97m2.scalar_features.mp.UMP2", FakeUMP2)
    result, scratch_bytes = evaluate_ri_ump2(
        object(), object(), {"H": "aux"}, tmp_path, 3750
    )
    assert calls == {
        "frozen": 2,
        "auxbasis": {"H": "aux"},
        "with_t2": False,
    }
    assert result["canonical_orbitals"] is True
    assert result["mp2_amplitudes_retained"] is False
    assert result["total_correlation_hartree"] == pytest.approx(-0.3)
    assert result["component_sum_error_hartree"] == pytest.approx(0.0)
    assert scratch_bytes == 0


def test_feature_layout_and_scalar_indices() -> None:
    semilocal = np.arange(288, dtype=np.float64).reshape(3, 96)
    vector = assemble_feature_vector(semilocal, -1.25, 0.02, -0.31)
    assert vector.shape == (FEATURE_COUNT,)
    assert np.array_equal(vector[:288], semilocal.reshape(-1))
    assert np.array_equal(vector[288:], np.asarray([-1.25, 0.02, -0.31]))


def test_feature_layout_rejects_wrong_selected_shape() -> None:
    with pytest.raises(ValueError, match="expected selected semilocal shape"):
        assemble_feature_vector(np.zeros((180, 96)), -1.0, 0.0, -0.1)


def test_named_direct_energy_matches_vector_dot() -> None:
    semilocal = np.linspace(-0.8, 0.9, 288).reshape(3, 96)
    report = direct_energy_identity(-7.5, semilocal, (-1.2, 0.03, -0.4))
    assert report["passed"]
    assert report["maximum_absolute_difference_hartree"] <= 1.0e-12


def test_fixed_energy_partition_uses_full_unscaled_lr_hf() -> None:
    parent = {
        "scf": {
            "components": {
                "nuclear_repulsion": 1.0,
                "one_electron": -10.0,
                "coulomb": 3.0,
                "unscaled_long_range_hf_exchange": -0.75,
                "unscaled_short_range_hf_exchange": -2.0,
            }
        }
    }
    result = fixed_energy_partition(parent)
    assert result == {
        "nuclear_repulsion": 1.0,
        "one_electron": -10.0,
        "coulomb": 3.0,
        "full_long_range_hf_exchange": -0.75,
        "total_hartree": -6.75,
    }


def test_shared_scalars_assemble_r1_78_and_r2_291() -> None:
    r1 = np.arange(75, dtype=np.float64)
    r2 = np.arange(288, dtype=np.float64) + 100.0
    vectors = assemble_r1_r2_feature_vectors(r1, r2, -1.25, 0.02, -0.31)
    assert vectors["R1"].shape == (MODEL_FEATURE_COUNTS["R1"],)
    assert vectors["R2"].shape == (MODEL_FEATURE_COUNTS["R2"],)
    assert np.array_equal(vectors["R1"][:75], r1)
    assert np.array_equal(vectors["R2"][:288], r2)
    assert np.array_equal(vectors["R1"][-3:], vectors["R2"][-3:])


def test_shared_assembly_rejects_wrong_semilocal_length() -> None:
    with pytest.raises(ValueError, match="R1 semilocal length 75"):
        assemble_r1_r2_feature_vectors(np.zeros(74), np.zeros(288), -1.0, 0.0, -0.2)


def test_atomic_r1_r2_artifact_uses_one_semilocal_and_scalar_source(tmp_path) -> None:
    semilocal = tmp_path / "semilocal"
    scalar = tmp_path / "scalar"
    output = tmp_path / "assembly"
    semilocal.mkdir()
    scalar.mkdir()
    r1_path = semilocal / "r1_semilocal_features_75_250974.npy"
    r2_path = semilocal / "r2_semilocal_features_288_250974.npy"
    scalars_path = scalar / "scalar_features_288_290.npy"
    np.save(r1_path, np.arange(75.0))
    np.save(r2_path, np.arange(288.0))
    np.save(scalars_path, np.asarray([-1.2, 0.03, -0.4]))
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    (semilocal / "semilocal_manifest.json").write_text(
        json.dumps({
            "schema_version": 2,
            "status": "three_grid_r1_r2_semilocal_features_complete_and_validated",
            "species": "fixture",
            "shared_grid_density_evaluation": True,
            "artifacts_sha256": {r1_path.name: digest(r1_path), r2_path.name: digest(r2_path)},
        }), encoding="utf-8"
    )
    (scalar / "scalar_manifest.json").write_text(
        json.dumps({
            "schema_version": 1,
            "status": "scalar_features_complete_and_validated",
            "species": "fixture",
            "artifacts_sha256": {scalars_path.name: digest(scalars_path)},
        }), encoding="utf-8"
    )
    manifest = publish_r1_r2_assembly(semilocal, scalar, output)
    assert manifest["shared_grid_density_evaluation"] is True
    assert manifest["shared_scalar_evaluation"] is True
    assert np.load(output / "feature_vector_78.npy").shape == (78,)
    assert np.load(output / "feature_vector_291.npy").shape == (291,)
    assert (output / "ASSEMBLY_COMPLETE").is_file()
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        publish_r1_r2_assembly(semilocal, scalar, output)
