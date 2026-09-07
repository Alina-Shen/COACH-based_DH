import numpy as np
import pytest

from revwb97m2.reaction_assembly import FEATURE_COUNT, assemble_reaction_arrays


def fixtures():
    reactions = [{
        "reaction": "test_rxn",
        "reference_hartree": -0.25,
        "objective_weight": 2.0,
        "stoichiometry": [
            {"coefficient": -1.0, "species": "a"},
            {"coefficient": 2.0, "species": "b"},
        ],
    }]
    vectors = {"a": np.ones(FEATURE_COUNT), "b": np.arange(FEATURE_COUNT, dtype=float)}
    fixed = {"a": -3.0, "b": -1.0}
    differences = {
        "a": {"99590": np.full(FEATURE_COUNT, 0.5)},
        "b": {"99590": np.full(FEATURE_COUNT, -0.25)},
    }
    return reactions, vectors, fixed, differences


def test_exact_stoichiometric_assembly_and_target_identity():
    reactions, vectors, fixed, differences = fixtures()
    result = assemble_reaction_arrays(reactions, vectors, fixed, differences, ["99590"])
    np.testing.assert_array_equal(result["feature_matrix"][0], -vectors["a"] + 2 * vectors["b"])
    np.testing.assert_array_equal(result["grid_differences"]["99590"][0], -differences["a"]["99590"] + 2 * differences["b"]["99590"])
    np.testing.assert_array_equal(result["target"], result["reference_energy"] - result["fixed_energy"])
    assert result["fixed_energy"].tolist() == [1.0]
    assert result["objective_weight"].tolist() == [2.0]


def test_missing_species_is_rejected():
    reactions, vectors, fixed, differences = fixtures()
    del vectors["b"]
    with pytest.raises(KeyError, match="missing species artifact"):
        assemble_reaction_arrays(reactions, vectors, fixed, differences, ["99590"])


def test_wrong_shape_and_nonpositive_weight_are_rejected():
    reactions, vectors, fixed, differences = fixtures()
    vectors["a"] = np.ones(FEATURE_COUNT - 1)
    with pytest.raises(ValueError, match="invalid 292-feature"):
        assemble_reaction_arrays(reactions, vectors, fixed, differences, ["99590"])
    reactions, vectors, fixed, differences = fixtures()
    reactions[0]["objective_weight"] = 0.0
    with pytest.raises(ValueError, match="invalid reference or objective weight"):
        assemble_reaction_arrays(reactions, vectors, fixed, differences, ["99590"])
