from __future__ import annotations

import numpy as np
import pytest

from revwb97m2.scalar_features import (
    FEATURE_COUNT,
    assemble_feature_vector,
    direct_energy_identity,
    fixed_energy_partition,
)


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
