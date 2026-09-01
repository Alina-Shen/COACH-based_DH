"""Published omegaB97M(2) R0 coefficient algebra.

This module implements the semilocal feature definitions and component-level
linear assembly established by the omegaB97M-V and omegaB97M(2) papers and
their supporting information.  It remains isolated from the deliberately
different COACH-form R2 feature space, in particular its same-spin gamma.
"""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Mapping

import numpy as np
from scipy.special import erf


DOI = "10.1063/1.5025226"
PAPER_SHA256 = "c631e99b54e70859f55a159e783c2b7cc85a50e2d20d384480add5be52cc4642"
WB97M_V_PAPER_SHA256 = "50048825cb3dbf88f77b6281f032cfc370669a02a741fcc4d34d32c5bf3a1d07"
WB97M_V_SI_PDF_SHA256 = "bd9087133cbd8a11e8a9cc4c9f557dcaa3c424bd38907b80d139cbce2750cd35"
WB97M_V_SI_SOURCE_SHA256 = "08ddfba765d379d85a7fbcabc0ee2a98a73fd32551ddab1d4ec87dc666900908"

OMEGA = 0.3
GAMMA_X = 0.004
GAMMA_SS = 0.2
GAMMA_OS = 0.006
TOL = 1.0e-14

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


def _pw92_g(
    rs: np.ndarray,
    a_const: float,
    alpha_1: float,
    beta_1: float,
    beta_2: float,
    beta_3: float,
    beta_4: float,
) -> np.ndarray:
    inner = 2.0 * a_const * (
        (beta_1 + beta_3 * rs) * np.sqrt(rs) + (beta_2 + beta_4 * rs) * rs
    )
    return -2.0 * a_const * (1.0 + alpha_1 * rs) * np.log1p(1.0 / inner)


def _channel_term(name: str) -> tuple[int, int]:
    indices = name.rsplit("_", 1)[1]
    if len(indices) != 2 or not indices.isdigit():
        raise ValueError(f"invalid published coefficient name: {name}")
    return int(indices[0]), int(indices[1])


def published_semilocal_components_block(
    weights: np.ndarray,
    rho_a: np.ndarray,
    rho_b: np.ndarray,
    grad_a: np.ndarray,
    grad_b: np.ndarray,
    tau_a: np.ndarray,
    tau_b: np.ndarray,
) -> dict[str, float]:
    """Integrate the 13 selected published semilocal terms over one grid block.

    The implementation follows Eqs. (10)--(28) of the omegaB97M-V paper and
    Eqs. (5)--(7) plus Table II of the omegaB97M(2) paper. ``tau`` uses the
    Q-Chem convention ``sum_i |grad psi_i|^2``.
    """

    arrays = tuple(
        np.asarray(value, dtype=np.float64)
        for value in (weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b)
    )
    weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b = arrays
    npoint = weights.size
    if any(value.shape != (npoint,) for value in (rho_a, rho_b, tau_a, tau_b)):
        raise ValueError("weights, spin densities, and kinetic densities must be vectors")
    if grad_a.shape != (npoint, 3) or grad_b.shape != (npoint, 3):
        raise ValueError("spin-density gradients must have shape (npoint, 3)")
    if not all(np.isfinite(value).all() for value in arrays):
        raise ValueError("published semilocal inputs must all be finite")

    result = {name: 0.0 for name in SEMILOCAL_COEFFICIENTS}
    rho = (np.maximum(rho_a, 0.0), np.maximum(rho_b, 0.0))
    grad = (grad_a, grad_b)
    tau = (np.maximum(tau_a, 0.0), np.maximum(tau_b, 0.0))
    tau_ueg_coefficient = (3.0 / 5.0) * (6.0 * math.pi**2) ** (2.0 / 3.0)
    exchange_lda_coefficient = -(3.0 / 2.0) * (3.0 / (4.0 * math.pi)) ** (1.0 / 3.0)
    kf_coefficient = (6.0 * math.pi**2) ** (1.0 / 3.0)
    rs_coefficient = (0.75 / math.pi) ** (1.0 / 3.0)

    s2_spin = [np.zeros(npoint), np.zeros(npoint)]
    t_spin = [np.zeros(npoint), np.zeros(npoint)]
    eps_same_spin = [np.zeros(npoint), np.zeros(npoint)]
    for spin in (0, 1):
        r = rho[spin]
        kinetic = tau[spin]
        gradient_sq = np.einsum("ij,ij->i", grad[spin], grad[spin])
        mask = (r > TOL) & (kinetic > TOL)
        if not np.any(mask):
            continue
        r_m = r[mask]
        s2 = gradient_sq[mask] / r_m ** (8.0 / 3.0)
        tau_ueg = tau_ueg_coefficient * r_m ** (5.0 / 3.0)
        t_value = tau_ueg / kinetic[mask]
        w_value = (t_value - 1.0) / (t_value + 1.0)

        u_x = GAMMA_X * s2 / (1.0 + GAMMA_X * s2)
        a_value = OMEGA / (kf_coefficient * r_m ** (1.0 / 3.0))
        attenuation = 1.0 - (2.0 / 3.0) * a_value * (
            a_value**3
            - 3.0 * a_value
            + (2.0 * a_value - a_value**3) * np.exp(-(a_value**-2))
            + 2.0 * math.sqrt(math.pi) * erf(a_value**-1)
        )
        exchange_base = weights[mask] * exchange_lda_coefficient * r_m ** (4.0 / 3.0) * attenuation
        for name in (key for key in result if key.startswith("exchange_")):
            i_order, j_order = _channel_term(name)
            result[name] += float(np.sum(exchange_base * w_value**i_order * u_x**j_order))

        rs = rs_coefficient * r_m ** (-1.0 / 3.0)
        eps = _pw92_g(rs, 0.01554535, 0.20548, 14.1189, 6.1977, 3.3662, 0.62517)
        u_ss = GAMMA_SS * s2 / (1.0 + GAMMA_SS * s2)
        same_spin_base = weights[mask] * r_m * eps
        for name in (key for key in result if key.startswith("same_spin_")):
            i_order, j_order = _channel_term(name)
            result[name] += float(np.sum(same_spin_base * w_value**i_order * u_ss**j_order))
        s2_spin[spin][mask] = s2
        t_spin[spin][mask] = t_value
        eps_same_spin[spin][mask] = eps

    mask_ab = (rho[0] > TOL) & (rho[1] > TOL) & (tau[0] > TOL) & (tau[1] > TOL)
    if np.any(mask_ab):
        ra, rb = rho[0][mask_ab], rho[1][mask_ab]
        total = ra + rb
        rs = rs_coefficient * total ** (-1.0 / 3.0)
        zeta = (ra - rb) / total
        zeta[np.abs(zeta) < TOL] = 0.0
        pw0 = _pw92_g(rs, 0.0310907, 0.2137, 7.5957, 3.5876, 1.6382, 0.49294)
        pw1 = _pw92_g(rs, 0.01554535, 0.20548, 14.1189, 6.1977, 3.3662, 0.62517)
        alpha_c = _pw92_g(rs, 0.0168869, 0.11125, 10.357, 3.6231, 0.88026, 0.49671)
        fpol = (
            -2.0 + (1.0 - zeta) ** (4.0 / 3.0) + (1.0 + zeta) ** (4.0 / 3.0)
        ) / (-2.0 + 2.0 * 2.0 ** (1.0 / 3.0))
        fppz = 4.0 / (9.0 * (2.0 ** (1.0 / 3.0) - 1.0))
        eps_total = pw0 + fpol * (pw1 - pw0) * zeta**4 + fpol * alpha_c * (zeta**4 - 1.0) / fppz
        opposite_base = weights[mask_ab] * (
            eps_total * total
            - eps_same_spin[0][mask_ab] * ra
            - eps_same_spin[1][mask_ab] * rb
        )
        s2_average = 0.5 * (s2_spin[0][mask_ab] + s2_spin[1][mask_ab])
        t_average = 0.5 * (t_spin[0][mask_ab] + t_spin[1][mask_ab])
        u_os = GAMMA_OS * s2_average / (1.0 + GAMMA_OS * s2_average)
        w_os = (t_average - 1.0) / (t_average + 1.0)
        for name in (key for key in result if key.startswith("opposite_spin_")):
            i_order, j_order = _channel_term(name)
            result[name] += float(np.sum(opposite_base * w_os**i_order * u_os**j_order))

    if not all(math.isfinite(value) for value in result.values()):
        raise FloatingPointError("non-finite published semilocal component")
    return result


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
