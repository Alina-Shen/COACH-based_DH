#!/usr/bin/env python3
"""Validate the project-owned revwb97m2 selected integratedDV kernel."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2 import integrated_dv as kernel  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_upstream_reference(path: Path):
    spec = importlib.util.spec_from_file_location("step7_upstream_reference", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load upstream reference {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def decode_row(row: int) -> dict[str, str | int]:
    families = (
        "exchange_mgga",
        "exchange_mgga_with_nonuniform_scaling",
        "range_separated_mgga",
        "range_separated_mgga_with_nonuniform_scaling",
        "pw92_same_spin",
        "pw92_same_spin_with_self_correlation_correction",
        "pw92_opposite_spin",
        "scan_alpha1_same_spin",
        "scan_alpha1_same_spin_with_self_correlation_correction",
        "scan_alpha1_opposite_spin",
    )
    polynomial = ("monomial", "legendre", "chebyshev")
    family_index, group = divmod(row, 18)
    basis_index = group % 9
    return {
        "row": row,
        "family": families[family_index],
        "u_polynomial": polynomial[basis_index // 3],
        "companion_variable": "w" if group < 9 else "beta_f",
        "companion_polynomial": polynomial[basis_index % 3],
    }


def independent_basis(u: float, companion: float, u_family: str) -> np.ndarray:
    if u_family == "monomial":
        u_values = u ** np.arange(8, dtype=np.float64)
    elif u_family == "legendre":
        u_values = np.polynomial.legendre.legvander(u, 7).reshape(-1)
    else:
        raise ValueError(u_family)
    companion_values = np.polynomial.legendre.legvander(companion, 11).reshape(-1)
    return np.outer(companion_values, u_values).reshape(-1)


def synthetic_inputs(npoint: int = 17) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(20260830)
    weights = rng.uniform(0.01, 0.8, npoint)
    rho_a = rng.uniform(0.02, 1.2, npoint)
    rho_b = rng.uniform(0.02, 1.0, npoint)
    grad_a = rng.normal(0.0, 0.16, (npoint, 3))
    grad_b = rng.normal(0.0, 0.13, (npoint, 3))
    tau_a = rng.uniform(0.08, 1.8, npoint)
    tau_b = rng.uniform(0.08, 1.6, npoint)
    return weights, rho_a, rho_b, grad_a, grad_b, tau_a, tau_b


def validate() -> tuple[dict[str, bool], dict[str, object]]:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    metadata = kernel.kernel_metadata()
    checks["frozen_parameters"] = metadata["parameters"] == {
        "omega": 0.3,
        "gamma_x": 0.004,
        "gamma_ss": 0.01,
        "gamma_os": 0.006,
    }
    checks["fit_target_not_coach_reproduction"] = (
        metadata["purpose"] == "fit_new_omegaB97M2_form_on_fixed_omegaB97M_V_density"
        and metadata["published_COACH_coefficients_used"] is False
    )
    expected_decoded = {
        64: {
            "row": 64,
            "family": "range_separated_mgga_with_nonuniform_scaling",
            "u_polynomial": "monomial",
            "companion_variable": "beta_f",
            "companion_polynomial": "legendre",
        },
        154: {
            "row": 154,
            "family": "scan_alpha1_same_spin_with_self_correlation_correction",
            "u_polynomial": "monomial",
            "companion_variable": "beta_f",
            "companion_polynomial": "legendre",
        },
        166: {
            "row": 166,
            "family": "scan_alpha1_opposite_spin",
            "u_polynomial": "legendre",
            "companion_variable": "w",
            "companion_polynomial": "legendre",
        },
    }
    decoded = {row: decode_row(row) for row in kernel.SELECTED_ROWS}
    checks["semantic_rows_64_154_166"] = decoded == expected_decoded
    checks["kernel_metadata_matches_independent_decoder"] = all(
        kernel.ROW_SEMANTICS[row] == {
            "channel": kernel.CHANNEL_NAMES[index],
            **{key: value for key, value in decoded[row].items() if key != "row"},
        }
        for index, row in enumerate(kernel.SELECTED_ROWS)
    )
    details["decoded_rows"] = decoded

    inputs = synthetic_inputs()
    features = kernel.selected_integrated_dv_block(*inputs)
    checks["shape_3_by_96"] = features.shape == (3, 96)
    checks["all_features_finite"] = bool(np.isfinite(features).all())

    split = 6
    partitioned = kernel.selected_integrated_dv_block(*(value[:split] for value in inputs))
    partitioned += kernel.selected_integrated_dv_block(*(value[split:] for value in inputs))
    checks["grid_block_partition_invariance"] = bool(
        np.allclose(features, partitioned, rtol=3.0e-15, atol=3.0e-15)
    )

    w, ra, rb, ga, gb, ta, tb = inputs
    spin_swapped = kernel.selected_integrated_dv_block(w, rb, ra, gb, ga, tb, ta)
    checks["alpha_beta_swap_invariance"] = bool(
        np.allclose(features, spin_swapped, rtol=2.0e-13, atol=2.0e-14)
    )

    legacy = kernel.KernelParameters(gamma_ss=0.2)
    legacy_features = kernel.selected_integrated_dv_block(*inputs, parameters=legacy)
    checks["gamma_ss_only_changes_same_spin_coordinate"] = bool(
        np.array_equal(features[0], legacy_features[0])
        and np.array_equal(features[2], legacy_features[2])
        and np.isclose(features[1, 0], legacy_features[1, 0], rtol=0.0, atol=1.0e-15)
    )
    same_spin_delta = float(np.max(np.abs(features[1] - legacy_features[1])))
    checks["legacy_gamma_ss_0p2_negative_regression"] = same_spin_delta > 1.0e-5
    details["legacy_gamma_ss_max_abs_same_spin_feature_delta"] = same_spin_delta

    one_weight = np.array([0.7])
    one_rho = np.array([0.43])
    one_grad = np.array([[0.18, -0.07, 0.11]])
    one_tau = np.array([0.61])
    symmetric = kernel.selected_integrated_dv_block(
        one_weight, one_rho, one_rho, one_grad, one_grad, one_tau, one_tau
    )
    s2 = float(np.dot(one_grad[0], one_grad[0]) / one_rho[0] ** (8.0 / 3.0))
    tau_ueg = float(
        (3.0 / 5.0)
        * (6.0 * np.pi * np.pi) ** (2.0 / 3.0)
        * one_rho[0] ** (5.0 / 3.0)
    )
    beta = float((one_tau[0] - np.dot(one_grad[0], one_grad[0]) / (4.0 * one_rho[0])) / (one_tau[0] + tau_ueg))
    beta_f = 2.0 * beta - 1.0
    tau_ratio = tau_ueg / one_tau[0]
    w_os = (tau_ratio - 1.0) / (tau_ratio + 1.0)
    u_x = 0.004 * s2 / (1.0 + 0.004 * s2)
    u_ss = 0.01 * s2 / (1.0 + 0.01 * s2)
    u_os = 0.006 * s2 / (1.0 + 0.006 * s2)
    expected_basis = (
        independent_basis(u_x, beta_f, "monomial"),
        independent_basis(u_ss, beta_f, "monomial"),
        independent_basis(u_os, w_os, "legendre"),
    )
    checks["independent_polynomial_coordinate_identity"] = all(
        np.allclose(symmetric[index] / symmetric[index, 0], expected_basis[index], rtol=2.0e-13, atol=2.0e-13)
        for index in range(3)
    )
    details["one_point_coordinates"] = {
        "s_squared": s2,
        "beta_f": beta_f,
        "w_os": w_os,
        "u_x": u_x,
        "u_ss": u_ss,
        "u_os": u_os,
    }

    upstream_path = WORKSPACE / "coach" / "1_data_generation" / "pyscf_integrated_dv.py"
    upstream = load_upstream_reference(upstream_path)
    upstream_matrix = np.zeros((96, 180), dtype=np.float64)
    upstream.accumulate_integrated_dv_block(*inputs, upstream_matrix)
    checks["upstream_protocol_exchange_row64_equivalence"] = bool(
        np.allclose(features[0], upstream_matrix[:, 64], rtol=2.0e-13, atol=2.0e-14)
    )
    checks["upstream_protocol_opposite_spin_row166_equivalence"] = bool(
        np.allclose(features[2], upstream_matrix[:, 166], rtol=2.0e-13, atol=2.0e-14)
    )
    checks["upstream_protocol_same_spin_equivalence_at_legacy_gamma"] = bool(
        np.allclose(
            legacy_features[1], upstream_matrix[:, 154], rtol=2.0e-13, atol=2.0e-14
        )
    )
    upstream_ss_delta = float(np.max(np.abs(features[1] - upstream_matrix[:, 154])))
    checks["upstream_legacy_same_spin_mismatch_detected"] = upstream_ss_delta > 1.0e-5
    details["upstream_legacy_row154_max_abs_delta"] = upstream_ss_delta

    zero = np.zeros(4)
    zero_grad = np.zeros((4, 3))
    zero_features = kernel.selected_integrated_dv_block(
        np.ones(4), zero, zero, zero_grad, zero_grad, zero, zero
    )
    checks["zero_density_safe_and_zero"] = bool(np.array_equal(zero_features, np.zeros((3, 96))))

    from pyscf import dft, gto

    mol = gto.M(atom="He 0 0 0", basis="sto-3g", spin=0, verbose=0)
    coords, grid_weights, grid_id = kernel.build_grid(mol, 10, 50)
    ao = dft.numint.eval_ao(mol, coords, deriv=1)
    spin_dm = 0.5 * np.eye(mol.nao_nr())
    rho_mgga = dft.numint.eval_rho(
        mol, ao, spin_dm, xctype="MGGA", with_lapl=False
    )
    rho_grid, grad_grid, tau_grid = kernel.unpack_mgga_rho(rho_mgga)
    pyscf_features = kernel.selected_integrated_dv_block(
        grid_weights,
        rho_grid,
        rho_grid,
        grad_grid,
        grad_grid,
        tau_grid,
        tau_grid,
    )
    checks["pyscf_grid_and_mgga_adapter"] = bool(
        grid_id == "10050"
        and coords.shape == (grid_weights.size, 3)
        and pyscf_features.shape == (3, 96)
        and np.isfinite(pyscf_features).all()
    )
    details["pyscf_adapter"] = {
        "molecule": "He/STO-3G synthetic spin density",
        "grid_id": grid_id,
        "grid_points": int(grid_weights.size),
    }
    return checks, details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "manifests" / "integrated_dv" / "validation.json",
    )
    args = parser.parse_args()
    checks, details = validate()
    passed = all(checks.values())
    source = ROOT / "integrated_dv.py"
    report = {
        "schema_version": 1,
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "target": "new omegaB97M(2)-form fit on fixed omegaB97M-V densities",
        "published_coach_coefficients_used": False,
        "kernel_source": str(source.relative_to(WORKSPACE)),
        "kernel_source_sha256": sha256(source),
        "checks": checks,
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not passed:
        failures = [name for name, value in checks.items() if not value]
        raise RuntimeError(f"integratedDV validation failed: {', '.join(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
