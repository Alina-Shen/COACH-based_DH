from __future__ import annotations

import math

import pytest

from revwb97m2.published_wb97m2 import (
    ALL_REQUIRED_COMPONENTS,
    SCALAR_COEFFICIENTS,
    SEMILOCAL_COEFFICIENTS,
    evaluate_r0_components,
    independent_parameter_count,
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
