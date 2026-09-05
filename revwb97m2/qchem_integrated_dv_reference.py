"""Independent NumPy reference for Q-Chem's complete 96x180 COACH matrix."""

from __future__ import annotations

import math

import numpy as np
from scipy.special import erf

from .integrated_dv import FROZEN_PARAMETERS, TOL, _g_pw92, _scan_h1, _series


NROW = 96
NGROUP = 18


def _basis(u: np.ndarray, w: np.ndarray, beta_f: np.ndarray) -> np.ndarray:
    """Return the 96x18 basis for every point in the native column order."""
    result = np.empty((u.size, NROW, NGROUP), dtype=np.float64)
    u_series = [_series(u, 8, family) for family in ("monomial", "legendre", "chebyshev")]
    w_series = [_series(w, 12, family) for family in ("monomial", "legendre", "chebyshev")]
    beta_series = [_series(beta_f, 12, family) for family in ("monomial", "legendre", "chebyshev")]
    group = 0
    for u_values in u_series:
        for companion in w_series:
            result[:, :, group] = (companion[:, :, None] * u_values[:, None, :]).reshape(u.size, NROW)
            group += 1
    for u_values in u_series:
        for companion in beta_series:
            result[:, :, group] = (companion[:, :, None] * u_values[:, None, :]).reshape(u.size, NROW)
            group += 1
    return result


def _add(destination: np.ndarray, coefficients: np.ndarray, basis: np.ndarray) -> None:
    destination += np.tensordot(coefficients, basis, axes=(0, 0))


def _exchange(weights: np.ndarray, rho: np.ndarray, gradient: np.ndarray, tau: np.ndarray) -> np.ndarray:
    result = np.zeros((NROW, 72), dtype=np.float64)
    rho = np.maximum(rho, 0.0)
    tau = np.maximum(tau, 0.0)
    gradient_sq = np.einsum("ij,ij->i", gradient, gradient)
    mask = (rho > TOL) & (tau > TOL)
    if not np.any(mask):
        return result
    r, t, g, wt = rho[mask], tau[mask], gradient_sq[mask], weights[mask]
    s2 = g / r ** (8.0 / 3.0)
    tau_ueg = (3.0 / 5.0) * (6.0 * math.pi * math.pi) ** (2.0 / 3.0) * r ** (5.0 / 3.0)
    beta_f = 2.0 * (t - g / (4.0 * r)) / (t + tau_ueg) - 1.0
    tau_ratio = tau_ueg / t
    w = (tau_ratio - 1.0) / (tau_ratio + 1.0)
    u = FROZEN_PARAMETERS.gamma_x * s2 / (1.0 + FROZEN_PARAMETERS.gamma_x * s2)
    basis = _basis(u, w, beta_f)
    ex_ueg = -(3.0 / 2.0) * (3.0 / (4.0 * math.pi)) ** (1.0 / 3.0) * r ** (4.0 / 3.0)
    a = FROZEN_PARAMETERS.omega / ((6.0 * math.pi * math.pi) ** (1.0 / 3.0) * r ** (1.0 / 3.0))
    attenuation = 1.0 - (2.0 / 3.0) * a * (
        a**3 - 3.0 * a + (2.0 * a - a**3) * np.exp(-(a**-2))
        + 2.0 * math.sqrt(math.pi) * erf(a**-1)
    )
    nonuniform = np.ones_like(s2)
    positive = s2 > 0.0
    nonuniform[positive] = 1.0 - np.exp(-13.815 / s2[positive] ** 0.25)
    base = wt * ex_ueg
    _add(result[:, 0:18], base, basis)
    _add(result[:, 18:36], nonuniform * base, basis)
    _add(result[:, 36:54], attenuation * base, basis)
    _add(result[:, 54:72], nonuniform * attenuation * base, basis)
    return result


def _correlation(
    weights: np.ndarray,
    rho_a: np.ndarray,
    rho_b: np.ndarray,
    grad_a: np.ndarray,
    grad_b: np.ndarray,
    tau_a: np.ndarray,
    tau_b: np.ndarray,
) -> np.ndarray:
    result = np.zeros((NROW, 108), dtype=np.float64)
    rho = (np.maximum(rho_a, 0.0), np.maximum(rho_b, 0.0))
    grad = (grad_a, grad_b)
    tau = (np.maximum(tau_a, 0.0), np.maximum(tau_b, 0.0))
    eps_pw = [np.zeros_like(weights), np.zeros_like(weights)]
    eps_scan = [np.zeros_like(weights), np.zeros_like(weights)]
    s2_spin = [np.zeros_like(weights), np.zeros_like(weights)]
    tau_ratio_spin = [np.zeros_like(weights), np.zeros_like(weights)]
    rs_coefficient = (0.75 / math.pi) ** (1.0 / 3.0)
    tau_coefficient = (3.0 / 5.0) * (6.0 * math.pi * math.pi) ** (2.0 / 3.0)

    for spin in (0, 1):
        r_all, t_all = rho[spin], tau[spin]
        gradient_sq = np.einsum("ij,ij->i", grad[spin], grad[spin])
        mask = (r_all > TOL) & (t_all > TOL)
        if not np.any(mask):
            continue
        r, t, g, wt = r_all[mask], t_all[mask], gradient_sq[mask], weights[mask]
        rs = rs_coefficient * r ** (-1.0 / 3.0)
        pw = _g_pw92(rs, 0.01554535, 0.20548, 14.1189, 6.1977, 3.3662, 0.62517)
        s2 = g / r ** (8.0 / 3.0)
        scan = pw + _scan_h1(rs, s2, 1.0 if spin == 0 else -1.0, pw)
        tau_ueg = tau_coefficient * r ** (5.0 / 3.0)
        tau_ratio = tau_ueg / t
        w = (tau_ratio - 1.0) / (tau_ratio + 1.0)
        beta = (t - g / (4.0 * r)) / (t + tau_ueg)
        beta_f = 2.0 * beta - 1.0
        u = FROZEN_PARAMETERS.gamma_ss * s2 / (1.0 + FROZEN_PARAMETERS.gamma_ss * s2)
        basis = _basis(u, w, beta_f)
        weighted_pw = wt * r * pw
        weighted_scan = wt * r * scan
        _add(result[:, 0:18], weighted_pw, basis)
        _add(result[:, 18:36], 2.0 * beta * weighted_pw, basis)
        _add(result[:, 54:72], weighted_scan, basis)
        _add(result[:, 72:90], 2.0 * beta * weighted_scan, basis)
        eps_pw[spin][mask] = pw
        eps_scan[spin][mask] = scan
        s2_spin[spin][mask] = s2
        tau_ratio_spin[spin][mask] = tau_ratio

    mask = (rho[0] > TOL) & (rho[1] > TOL) & (tau[0] > TOL) & (tau[1] > TOL)
    if not np.any(mask):
        return result
    ra, rb = rho[0][mask], rho[1][mask]
    total_rho = ra + rb
    total_gradient = grad[0][mask] + grad[1][mask]
    total_gradient_sq = np.einsum("ij,ij->i", total_gradient, total_gradient)
    rs = rs_coefficient * total_rho ** (-1.0 / 3.0)
    alpha_c = _g_pw92(rs, 0.0168869, 0.11125, 10.357, 3.6231, 0.88026, 0.49671)
    pw0 = _g_pw92(rs, 0.0310907, 0.2137, 7.5957, 3.5876, 1.6382, 0.49294)
    pw1 = _g_pw92(rs, 0.01554535, 0.20548, 14.1189, 6.1977, 3.3662, 0.62517)
    zeta = (ra - rb) / total_rho
    zeta[np.abs(zeta) < TOL] = 0.0
    fpol = (-2.0 + (1.0 - zeta) ** (4.0 / 3.0) + (1.0 + zeta) ** (4.0 / 3.0)) / (
        -2.0 + 2.0 * 2.0 ** (1.0 / 3.0)
    )
    zeta4 = zeta**4
    fppz = 4.0 / (9.0 * (2.0 ** (1.0 / 3.0) - 1.0))
    total_pw = pw0 + fpol * alpha_c * (zeta4 - 1.0) / fppz + fpol * (pw1 - pw0) * zeta4
    s2_total = total_gradient_sq / total_rho ** (8.0 / 3.0)
    total_scan = total_pw + _scan_h1(rs, s2_total, zeta, total_pw)
    weighted_pw = weights[mask] * (total_pw * total_rho - eps_pw[0][mask] * ra - eps_pw[1][mask] * rb)
    weighted_scan = weights[mask] * (
        total_scan * total_rho - eps_scan[0][mask] * ra - eps_scan[1][mask] * rb
    )
    s2_average = 0.5 * (s2_spin[0][mask] + s2_spin[1][mask])
    u = FROZEN_PARAMETERS.gamma_os * s2_average / (1.0 + FROZEN_PARAMETERS.gamma_os * s2_average)
    tau_ratio = 0.5 * (tau_ratio_spin[0][mask] + tau_ratio_spin[1][mask])
    w = (tau_ratio - 1.0) / (tau_ratio + 1.0)
    total_tau = tau[0][mask] + tau[1][mask]
    total_tau_ueg = (3.0 / 5.0) * (3.0 * math.pi * math.pi) ** (2.0 / 3.0) * total_rho ** (5.0 / 3.0)
    beta_f = 2.0 * (total_tau - total_gradient_sq / (4.0 * total_rho)) / (
        total_tau + total_tau_ueg
    ) - 1.0
    basis = _basis(u, w, beta_f)
    _add(result[:, 36:54], weighted_pw, basis)
    _add(result[:, 90:108], weighted_scan, basis)
    return result


def full_integrated_dv_block(
    weights: np.ndarray,
    rho_a: np.ndarray,
    rho_b: np.ndarray,
    grad_a: np.ndarray,
    grad_b: np.ndarray,
    tau_a: np.ndarray,
    tau_b: np.ndarray,
) -> np.ndarray:
    """Independently evaluate one native diagnostic block."""
    arrays = tuple(np.asarray(value, dtype=np.float64) for value in (
        weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b
    ))
    if not all(np.isfinite(value).all() for value in arrays):
        raise ValueError("diagnostic grid inputs must be finite")
    result = np.zeros((NROW, 180), dtype=np.float64)
    result[:, :72] = _exchange(arrays[0], arrays[1], arrays[3], arrays[5])
    result[:, :72] += _exchange(arrays[0], arrays[2], arrays[4], arrays[6])
    result[:, 72:] = _correlation(*arrays)
    if not np.isfinite(result).all():
        raise FloatingPointError("non-finite full integratedDV reference")
    return result
