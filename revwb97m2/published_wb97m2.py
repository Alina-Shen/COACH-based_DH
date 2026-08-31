"""Published omegaB97M(2) R0 coefficient algebra.

This module implements only the component-level linear assembly established by
Eqs. (3)--(8) and Table II of Mardirossian and Head-Gordon, J. Chem. Phys.
148, 241736 (2018).  It deliberately does not generate the published
semi-local density features: the uploaded paper delegates their detailed base
definitions to Sec. V of Ref. 31, which is not yet an authority in this
project.  Keeping that boundary explicit prevents the COACH-form R2 kernel
from being silently substituted for the distinct published R0 model.
"""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Mapping


DOI = "10.1063/1.5025226"
PAPER_SHA256 = "c631e99b54e70859f55a159e783c2b7cc85a50e2d20d384480add5be52cc4642"

# Table II values at the five-decimal precision printed in the paper.  The
# names preserve the paper's channel and (i,j) polynomial indices.
SEMILOCAL_COEFFICIENTS = MappingProxyType(
    {
        "exchange_00": 0.37806,
        "exchange_20": 0.28193,
        "exchange_30": -0.21886,
        "exchange_01": 0.13642,
        "exchange_41": 0.70767,
        "same_spin_00": 0.54846,
        "same_spin_10": -1.17724,
        "same_spin_20": -3.67267,
        "opposite_spin_00": 0.46152,
        "opposite_spin_20": 2.30490,
        "opposite_spin_01": -1.94794,
        "opposite_spin_02": 3.24910,
        "opposite_spin_22": -2.26280,
    }
)
SCALAR_COEFFICIENTS = MappingProxyType(
    {
        "short_range_hf": 0.62194,
        "vv10": 0.65904,
        "pt2": 0.34096,
    }
)
FIXED_COMPONENTS = (
    "nuclear_repulsion",
    "one_electron",
    "coulomb",
    "full_long_range_hf_exchange",
)
ALL_REQUIRED_COMPONENTS = FIXED_COMPONENTS + tuple(SEMILOCAL_COEFFICIENTS) + tuple(
    SCALAR_COEFFICIENTS
)


def independent_parameter_count() -> int:
    """Return the published count after its two exact linear constraints."""

    displayed_nonzero = len(SEMILOCAL_COEFFICIENTS) + len(SCALAR_COEFFICIENTS)
    return displayed_nonzero - 2


def evaluate_r0_components(components: Mapping[str, float]) -> dict[str, object]:
    """Assemble R0 from already evaluated *published-definition* components.

    This function cannot turn R2/COACH features into R0 features.  Callers must
    supply each named semi-local component evaluated with the original
    omegaB97M(2) density definitions once those definitions are authoritative.
    """

    missing = [name for name in ALL_REQUIRED_COMPONENTS if name not in components]
    if missing:
        raise ValueError(f"missing published omegaB97M(2) components: {missing}")
    values = {name: float(components[name]) for name in ALL_REQUIRED_COMPONENTS}
    nonfinite = [name for name, value in values.items() if not math.isfinite(value)]
    if nonfinite:
        raise ValueError(f"non-finite published omegaB97M(2) components: {nonfinite}")

    fixed_terms = {name: values[name] for name in FIXED_COMPONENTS}
    weighted_semilocal = {
        name: SEMILOCAL_COEFFICIENTS[name] * values[name]
        for name in SEMILOCAL_COEFFICIENTS
    }
    weighted_scalars = {
        name: SCALAR_COEFFICIENTS[name] * values[name]
        for name in SCALAR_COEFFICIENTS
    }
    fixed_energy = math.fsum(fixed_terms.values())
    fitted_energy = math.fsum((*weighted_semilocal.values(), *weighted_scalars.values()))
    return {
        "fixed_terms_hartree": fixed_terms,
        "weighted_semilocal_hartree": weighted_semilocal,
        "weighted_scalars_hartree": weighted_scalars,
        "fixed_energy_hartree": fixed_energy,
        "fitted_energy_hartree": fitted_energy,
        "total_energy_hartree": fixed_energy + fitted_energy,
    }
