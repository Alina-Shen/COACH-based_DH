from __future__ import annotations

import math

import numpy as np
import pytest

from revwb97m2.published_wb97m2 import (
    ALL_REQUIRED_COMPONENTS,
    SCALAR_COEFFICIENTS,
    SEMILOCAL_COEFFICIENTS,
    evaluate_r0_components,
    independent_parameter_count,
    published_semilocal_components_block,
    r1_candidate_semilocal_block,
)


def test_printed_coefficients_and_constraints() -> None:
    assert len(SEMILOCAL_COEFFICIENTS) == 13
    assert len(SCALAR_COEFFICIENTS) == 3
    assert independent_parameter_count() == 14
    assert SEMILOCAL_COEFFICIENTS["exchange_30"] == -0.21886
    assert SEMILOCAL_COEFFICIENTS["same_spin_20"] == -3.67267
    assert SEMILOCAL_COEFFICIENTS["opposite_spin_22"] == -2.26280
    assert SEMILOCAL_COEFFICIENTS["exchange_00"] + SCALAR_COEFFICIENTS[
        "short_range_hf"
    ] == 1.0
    assert SCALAR_COEFFICIENTS["vv10"] + SCALAR_COEFFICIENTS["pt2"] == 1.0


def test_component_assembly_matches_independent_sum() -> None:
    components = {name: (index - 8.0) / 13.0 for index, name in enumerate(ALL_REQUIRED_COMPONENTS)}
    result = evaluate_r0_components(components)
    expected = math.fsum(components[name] for name in ALL_REQUIRED_COMPONENTS[:4])
    expected += math.fsum(
        coefficient * components[name]
        for name, coefficient in SEMILOCAL_COEFFICIENTS.items()
    )
    expected += math.fsum(
        coefficient * components[name] for name, coefficient in SCALAR_COEFFICIENTS.items()
    )
    assert result["total_energy_hartree"] == pytest.approx(expected, abs=1e-15)


def test_component_assembly_refuses_missing_or_nonfinite_values() -> None:
    components = {name: 0.0 for name in ALL_REQUIRED_COMPONENTS}
    missing = dict(components)
    missing.pop("same_spin_10")
    with pytest.raises(ValueError, match="missing published"):
        evaluate_r0_components(missing)
    components["pt2"] = float("nan")
    with pytest.raises(ValueError, match="non-finite"):
        evaluate_r0_components(components)


def test_uniform_reference_point_selects_only_00_terms() -> None:
    rho = np.asarray([0.2])
    tau_ueg = (3.0 / 5.0) * (6.0 * math.pi**2) ** (2.0 / 3.0) * rho ** (5.0 / 3.0)
    values = published_semilocal_components_block(
        np.ones(1),
        rho,
        rho,
        np.zeros((1, 3)),
        np.zeros((1, 3)),
        tau_ueg,
        tau_ueg,
    )
    assert values["exchange_00"] < 0.0
    assert values["same_spin_00"] < 0.0
    assert values["opposite_spin_00"] < 0.0
    assert all(value == 0.0 for name, value in values.items() if not name.endswith("_00"))


def test_semilocal_block_is_additive_and_refuses_bad_shapes() -> None:
    weights = np.asarray([0.4, 0.6])
    rho_a = np.asarray([0.2, 0.15])
    rho_b = np.asarray([0.18, 0.12])
    grad_a = np.asarray([[0.03, -0.01, 0.02], [0.01, 0.04, -0.02]])
    grad_b = np.asarray([[0.02, 0.01, -0.01], [-0.02, 0.03, 0.01]])
    tau_a = np.asarray([0.3, 0.22])
    tau_b = np.asarray([0.28, 0.19])
    combined = published_semilocal_components_block(
        weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b
    )
    split = {name: 0.0 for name in combined}
    for index in range(2):
        part = published_semilocal_components_block(
            weights[index : index + 1],
            rho_a[index : index + 1],
            rho_b[index : index + 1],
            grad_a[index : index + 1],
            grad_b[index : index + 1],
            tau_a[index : index + 1],
            tau_b[index : index + 1],
        )
        for name, value in part.items():
            split[name] += value
    assert combined == pytest.approx(split, abs=1.0e-15)
    with pytest.raises(ValueError, match="gradients"):
        published_semilocal_components_block(
            weights, rho_a, rho_b, np.zeros((2, 2)), grad_b, tau_a, tau_b
        )


def test_r1_candidate_space_contains_published_terms_with_frozen_order() -> None:
    weights = np.asarray([0.4, 0.6])
    rho_a = np.asarray([0.2, 0.15])
    rho_b = np.asarray([0.18, 0.12])
    grad_a = np.asarray([[0.03, -0.01, 0.02], [0.01, 0.04, -0.02]])
    grad_b = np.asarray([[0.02, 0.01, -0.01], [-0.02, 0.03, 0.01]])
    tau_a = np.asarray([0.3, 0.22])
    tau_b = np.asarray([0.28, 0.19])
    matrix = r1_candidate_semilocal_block(
        weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b
    )
    selected = published_semilocal_components_block(
        weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b
    )
    channel_rows = {"exchange": 0, "same_spin": 1, "opposite_spin": 2}
    assert matrix.shape == (3, 25)
    for name, value in selected.items():
        channel, indices = name.rsplit("_", 1)
        index = 5 * int(indices[0]) + int(indices[1])
        assert matrix[channel_rows[channel], index] == pytest.approx(value, abs=1.0e-15)
