"""Project-owned semilocal feature kernel for the revwb97m2 fit.

The kernel follows the COACH integratedDV construction protocol on fixed
omegaB97M-V spin densities, but it does not contain or evaluate the published
COACH coefficients.  It generates only the three frozen 96-feature rows used
by the new 291-parameter omegaB97M(2)-form fit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np
from scipy.special import erf


FEATURES_PER_CHANNEL = 96
SELECTED_ROWS = (64, 154, 166)
CHANNEL_NAMES = ("exchange", "same_spin_correlation", "opposite_spin_correlation")
TOL = 1.0e-14


@dataclass(frozen=True)
class KernelParameters:
    """Nonlinear coordinates frozen by scientific specification version 3."""

    omega: float = 0.3
    gamma_x: float = 0.004
    gamma_ss: float = 0.01
    gamma_os: float = 0.006

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


FROZEN_PARAMETERS = KernelParameters()


ROW_SEMANTICS: dict[int, dict[str, str | int]] = {
    64: {
        "channel": "exchange",
        "family": "range_separated_mgga_with_nonuniform_scaling",
        "u_polynomial": "monomial",
        "companion_variable": "beta_f",
        "companion_polynomial": "legendre",
    },
    154: {
        "channel": "same_spin_correlation",
        "family": "scan_alpha1_same_spin_with_self_correlation_correction",
        "u_polynomial": "monomial",
        "companion_variable": "beta_f",
        "companion_polynomial": "legendre",
    },
    166: {
        "channel": "opposite_spin_correlation",
        "family": "scan_alpha1_opposite_spin",
        "u_polynomial": "legendre",
        "companion_variable": "w",
        "companion_polynomial": "legendre",
    },
}


def kernel_metadata(parameters: KernelParameters = FROZEN_PARAMETERS) -> dict[str, Any]:
    """Return serializable provenance for every generated feature artifact."""

    return {
        "schema_version": 1,
        "purpose": "fit_new_omegaB97M2_form_on_fixed_omegaB97M_V_density",
        "protocol": "COACH_integratedDV_feature_construction",
        "published_COACH_coefficients_used": False,
        "parameters": parameters.as_dict(),
        "selected_rows": list(SELECTED_ROWS),
        "row_semantics": {str(row): value for row, value in ROW_SEMANTICS.items()},
        "shape": [len(SELECTED_ROWS), FEATURES_PER_CHANNEL],
    }


def _series(x: np.ndarray, size: int, family: str) -> np.ndarray:
    out = np.empty((x.size, size), dtype=np.float64)
    out[:, 0] = 1.0
    if size == 1:
        return out
    out[:, 1] = x
    if family == "monomial":
        for order in range(2, size):
            out[:, order] = out[:, order - 1] * x
    elif family == "legendre":
        for order in range(2, size):
            degree = float(order)
            out[:, order] = (
                (2.0 * degree - 1.0) * x * out[:, order - 1]
                - (degree - 1.0) * out[:, order - 2]
            ) / degree
    elif family == "chebyshev":
        for order in range(2, size):
            out[:, order] = 2.0 * x * out[:, order - 1] - out[:, order - 2]
    else:
        raise ValueError(f"Unsupported polynomial family: {family}")
    return out


def _basis(
    u: np.ndarray,
    companion: np.ndarray,
    u_family: str,
    companion_family: str,
) -> np.ndarray:
    """Return 96 columns ordered companion degree first, then u degree."""

    u_values = _series(u, 8, u_family)
    companion_values = _series(companion, 12, companion_family)
    return (companion_values[:, :, None] * u_values[:, None, :]).reshape(u.size, -1)


def _g_pw92(
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


def _scan_h1(rs: np.ndarray, s2: np.ndarray, zeta: np.ndarray, e_lda: np.ndarray) -> np.ndarray:
    phi = ((1.0 - zeta) ** (2.0 / 3.0) + (1.0 + zeta) ** (2.0 / 3.0)) / 2.0
    correlation_gamma = (1.0 - math.log(2.0)) / (math.pi * math.pi)
    gamma_phi3 = correlation_gamma * phi**3
    beta_rs = 0.066725 * (1.0 + 0.1 * rs) / (1.0 + 0.1778 * rs)
    w1 = np.expm1(np.clip(-e_lda / gamma_phi3, -700.0, 700.0))
    a_const = beta_rs / (w1 * correlation_gamma)
    t2 = s2 / (16.0 * 4.0 ** (1.0 / 3.0) * rs * phi**2)
    g_at2 = (1.0 + 4.0 * a_const * t2) ** (-0.25)
    return gamma_phi3 * np.log1p(w1 * (1.0 - g_at2))


def _validate_inputs(*arrays: np.ndarray) -> tuple[np.ndarray, ...]:
    converted = tuple(np.asarray(value, dtype=np.float64) for value in arrays)
    npoint = converted[0].shape[0]
    scalar_names = ("weights", "rho_a", "rho_b", "tau_a", "tau_b")
    for name, value in zip(scalar_names, converted[:3] + converted[5:]):
        if value.shape != (npoint,):
            raise ValueError(f"{name} must have shape ({npoint},), got {value.shape}")
    for name, value in (("grad_a", converted[3]), ("grad_b", converted[4])):
        if value.shape != (npoint, 3):
            raise ValueError(f"{name} must have shape ({npoint}, 3), got {value.shape}")
    if not all(np.isfinite(value).all() for value in converted):
        raise ValueError("Kernel inputs must all be finite")
    return converted


def selected_integrated_dv_block(
    weights: np.ndarray,
    rho_a: np.ndarray,
    rho_b: np.ndarray,
    grad_a: np.ndarray,
    grad_b: np.ndarray,
    tau_a: np.ndarray,
    tau_b: np.ndarray,
    parameters: KernelParameters = FROZEN_PARAMETERS,
) -> np.ndarray:
    """Integrate rows 64, 154, and 166 over one numerical-grid block.

    Returns a ``(3, 96)`` matrix in exchange, same-spin correlation, and
    opposite-spin correlation order.  Inputs use the Q-Chem/COACH kinetic
    energy convention ``tau = sum_i |grad psi_i|^2``.
    """

    weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b = _validate_inputs(
        weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b
    )
    result = np.zeros((3, FEATURES_PER_CHANNEL), dtype=np.float64)
    rho = (np.maximum(rho_a, 0.0), np.maximum(rho_b, 0.0))
    grad = (grad_a, grad_b)
    tau = (np.maximum(tau_a, 0.0), np.maximum(tau_b, 0.0))

    tau_ueg_spin_coeff = (3.0 / 5.0) * (6.0 * math.pi * math.pi) ** (2.0 / 3.0)
    exchange_lda_coeff = -(3.0 / 2.0) * (3.0 / (4.0 * math.pi)) ** (1.0 / 3.0)
    kf_coeff = (6.0 * math.pi * math.pi) ** (1.0 / 3.0)
    rs_coeff = (0.75 / math.pi) ** (1.0 / 3.0)

    scan_same_spin = [np.zeros_like(weights), np.zeros_like(weights)]
    s2_spin = [np.zeros_like(weights), np.zeros_like(weights)]
    tau_ratio_spin = [np.zeros_like(weights), np.zeros_like(weights)]

    for spin in (0, 1):
        r = rho[spin]
        t = tau[spin]
        gradient_sq = np.einsum("ij,ij->i", grad[spin], grad[spin])
        mask = (r > TOL) & (t > TOL)
        if not np.any(mask):
            continue
        r_m, t_m = r[mask], t[mask]
        g_m, wt_m = gradient_sq[mask], weights[mask]
        s2 = g_m / r_m ** (8.0 / 3.0)
        tau_ueg = tau_ueg_spin_coeff * r_m ** (5.0 / 3.0)
        tau_ratio = tau_ueg / t_m
        tau_w = g_m / (4.0 * r_m)
        beta = (t_m - tau_w) / (t_m + tau_ueg)
        beta_f = 2.0 * beta - 1.0

        u_x = parameters.gamma_x * s2 / (1.0 + parameters.gamma_x * s2)
        exchange_basis = _basis(u_x, beta_f, "monomial", "legendre")
        ex_ueg = exchange_lda_coeff * r_m ** (4.0 / 3.0)
        a_value = parameters.omega / (kf_coeff * r_m ** (1.0 / 3.0))
        attenuation = 1.0 - (2.0 / 3.0) * a_value * (
            a_value**3
            - 3.0 * a_value
            + (2.0 * a_value - a_value**3) * np.exp(-(a_value**-2))
            + 2.0 * math.sqrt(math.pi) * erf(a_value**-1)
        )
        nonuniform = np.ones_like(s2)
        positive_s2 = s2 > 0.0
        nonuniform[positive_s2] = 1.0 - np.exp(-13.815 / s2[positive_s2] ** 0.25)
        result[0] += np.einsum(
            "p,pk->k", wt_m * ex_ueg * attenuation * nonuniform, exchange_basis
        )

        rs = rs_coeff * r_m ** (-1.0 / 3.0)
        eps_pw = _g_pw92(rs, 0.01554535, 0.20548, 14.1189, 6.1977, 3.3662, 0.62517)
        zeta = np.ones_like(rs) if spin == 0 else -np.ones_like(rs)
        eps_scan = eps_pw + _scan_h1(rs, s2, zeta, eps_pw)
        u_ss = parameters.gamma_ss * s2 / (1.0 + parameters.gamma_ss * s2)
        same_spin_basis = _basis(u_ss, beta_f, "monomial", "legendre")
        result[1] += np.einsum(
            "p,pk->k", wt_m * r_m * eps_scan * (2.0 * beta), same_spin_basis
        )
        scan_same_spin[spin][mask] = eps_scan
        s2_spin[spin][mask] = s2
        tau_ratio_spin[spin][mask] = tau_ratio

    mask_ab = (rho[0] > TOL) & (rho[1] > TOL) & (tau[0] > TOL) & (tau[1] > TOL)
    if np.any(mask_ab):
        ra, rb = rho[0][mask_ab], rho[1][mask_ab]
        r_total = ra + rb
        grad_total = grad[0][mask_ab] + grad[1][mask_ab]
        gradient_total_sq = np.einsum("ij,ij->i", grad_total, grad_total)
        s2_total = gradient_total_sq / r_total ** (8.0 / 3.0)
        rs = rs_coeff * r_total ** (-1.0 / 3.0)
        alpha_c = _g_pw92(rs, 0.0168869, 0.11125, 10.357, 3.6231, 0.88026, 0.49671)
        pw0 = _g_pw92(rs, 0.0310907, 0.2137, 7.5957, 3.5876, 1.6382, 0.49294)
        pw1 = _g_pw92(rs, 0.01554535, 0.20548, 14.1189, 6.1977, 3.3662, 0.62517)
        zeta = (ra - rb) / r_total
        zeta[np.abs(zeta) < TOL] = 0.0
        fpol = (
            -2.0 + (1.0 - zeta) ** (4.0 / 3.0) + (1.0 + zeta) ** (4.0 / 3.0)
        ) / (-2.0 + 2.0 * 2.0 ** (1.0 / 3.0))
        zeta4 = zeta**4
        fppz = 4.0 / (9.0 * (2.0 ** (1.0 / 3.0) - 1.0))
        eps_pw = pw0 + fpol * alpha_c * (zeta4 - 1.0) / fppz + fpol * (pw1 - pw0) * zeta4
        eps_scan = eps_pw + _scan_h1(rs, s2_total, zeta, eps_pw)
        base_os = (
            eps_scan * r_total
            - scan_same_spin[0][mask_ab] * ra
            - scan_same_spin[1][mask_ab] * rb
        )
        s2_average = 0.5 * (s2_spin[0][mask_ab] + s2_spin[1][mask_ab])
        u_os = parameters.gamma_os * s2_average / (1.0 + parameters.gamma_os * s2_average)
        tau_ratio = 0.5 * (
            tau_ratio_spin[0][mask_ab] + tau_ratio_spin[1][mask_ab]
        )
        w_os = (tau_ratio - 1.0) / (tau_ratio + 1.0)
        opposite_spin_basis = _basis(u_os, w_os, "legendre", "legendre")
        result[2] += np.einsum(
            "p,pk->k", weights[mask_ab] * base_os, opposite_spin_basis
        )

    if not np.isfinite(result).all():
        raise FloatingPointError("Non-finite selected integratedDV features")
    return result


def accumulate_selected_integrated_dv_block(
    destination: np.ndarray,
    weights: np.ndarray,
    rho_a: np.ndarray,
    rho_b: np.ndarray,
    grad_a: np.ndarray,
    grad_b: np.ndarray,
    tau_a: np.ndarray,
    tau_b: np.ndarray,
    parameters: KernelParameters = FROZEN_PARAMETERS,
) -> None:
    """Add one block to an existing ``(3, 96)`` feature matrix."""

    if destination.shape != (3, FEATURES_PER_CHANNEL):
        raise ValueError(f"destination must have shape (3, 96), got {destination.shape}")
    destination += selected_integrated_dv_block(
        weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b, parameters
    )


def build_grid(mol: Any, radial: int, angular: int) -> tuple[np.ndarray, np.ndarray, str]:
    """Build the unpruned, unadjusted PySCF grid required by the protocol."""

    from pyscf import dft

    grids = dft.gen_grid.Grids(mol)
    grids.atom_grid = (radial, angular)
    grids.prune = None
    grids.radii_adjust = None
    grids.build(with_non0tab=False)
    return grids.coords, grids.weights, f"{radial}{angular:03d}"


def unpack_mgga_rho(rho_mgga: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert a PySCF MGGA density tensor to the kernel's tau convention."""

    rho_mgga = np.asarray(rho_mgga, dtype=np.float64)
    if rho_mgga.ndim != 2 or rho_mgga.shape[0] < 5:
        raise ValueError(f"Unexpected MGGA rho shape: {rho_mgga.shape}")
    gradient = np.column_stack((rho_mgga[1], rho_mgga[2], rho_mgga[3]))
    tau_index = 5 if rho_mgga.shape[0] >= 6 else 4
    return rho_mgga[0], gradient, 2.0 * rho_mgga[tau_index]
