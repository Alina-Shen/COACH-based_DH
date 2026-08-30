#!/usr/bin/env python3
"""Generate one isolated R2/291-feature smoke artifact from fixed wb97M-V orbitals."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyscf
import yaml
from pyscf import dft, gto, mp
from pyscf.data import elements


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=root / "revwb97m2.yaml")
    parser.add_argument("--xyz", type=Path, default=root / "inputs" / "smoke_h2o.xyz")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-memory-mb", type=int, default=40000)
    parser.add_argument("--block-size", type=int, default=10000)
    parser.add_argument("--verbose", type=int, default=4)
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_coach_feature_module(code_root: Path):
    source = code_root / "1_data_generation" / "pyscf_integrated_dv.py"
    spec = importlib.util.spec_from_file_location("readonly_coach_integrated_dv", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load COACH feature implementation from {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, source


def load_xyz(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    natom = int(lines[0].strip())
    metadata = {}
    for field in lines[1].split(","):
        if "=" in field:
            key, value = field.split("=", 1)
            metadata[key.strip().lower()] = value.strip()
    atoms = [line.strip() for line in lines[2 : 2 + natom] if line.strip()]
    if len(atoms) != natom:
        raise ValueError(f"{path}: expected {natom} atoms, found {len(atoms)}")
    multiplicity = int(metadata.get("multiplicity", "1"))
    return {
        "name": metadata.get("name", path.stem),
        "atom": "\n".join(atoms),
        "charge": int(metadata.get("charge", "0")),
        "spin": multiplicity - 1,
        "multiplicity": multiplicity,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def spin_density_matrices(mf, dm: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if dm.ndim == 2:
        return 0.5 * dm, 0.5 * dm
    if dm.ndim == 3 and dm.shape[0] == 2:
        return dm[0], dm[1]
    raise ValueError(f"Unexpected density-matrix shape {dm.shape}")


def exchange_energy(dm: np.ndarray, vk: np.ndarray) -> float:
    return float(-0.5 * np.einsum("sij,sji->", dm, vk).real)


def build_sg1_grid(mol: gto.Mole):
    grid = dft.gen_grid.Grids(mol)
    grid.atom_grid = (50, 194)
    grid.prune = dft.gen_grid.sg1_prune
    grid.build(with_non0tab=False)
    return grid


def evaluate_vv10_b10(mol: gto.Mole, dm_total: np.ndarray, max_memory: int) -> float:
    numint = dft.numint.NumInt()
    numint.nlc_coeff = lambda xc_code: (((10.0, 0.01), 1.0),)
    grid = build_sg1_grid(mol)
    _, energy, _ = numint.nr_nlc_vxc(
        mol, grid, "VV10", dm_total, max_memory=max_memory
    )
    return float(energy)


def evaluate_parent_components(mf, dm_a: np.ndarray, dm_b: np.ndarray) -> dict:
    mol = mf.mol
    dm_spin = np.asarray([dm_a, dm_b])
    dm_total = dm_a + dm_b
    omega, alpha, hybrid = mf._numint.rsh_and_hybrid_coeff(mf.xc, spin=mol.spin)

    vk_full = mf.get_k(mol, dm_spin, hermi=1)
    vk_lr = mf.get_k(mol, dm_spin, hermi=1, omega=omega)
    x_full = exchange_energy(dm_spin, vk_full)
    x_lr = exchange_energy(dm_spin, vk_lr)
    x_sr = x_full - x_lr

    hcore = mf.get_hcore(mol)
    one_electron = float(np.einsum("ij,ji->", dm_total, hcore).real)
    vj = mf.get_j(mol, dm_total, hermi=1)
    coulomb = float(0.5 * np.einsum("ij,ji->", dm_total, vj).real)

    if dm_total.ndim != 2:
        raise ValueError("Total density matrix must be two-dimensional")
    if isinstance(mf, dft.rks.RKS):
        _, semilocal_xc, _ = mf._numint.nr_rks(
            mol, mf.grids, mf.xc, dm_total, max_memory=mf.max_memory
        )
    else:
        _, semilocal_xc, _ = mf._numint.nr_uks(
            mol, mf.grids, mf.xc, dm_spin, max_memory=mf.max_memory
        )

    native_nlc = 0.0
    if mf.do_nlc():
        xc_nlc = mf.xc if mf._numint.libxc.is_nlc(mf.xc) else mf.nlc
        _, native_nlc, _ = mf._numint.nr_nlc_vxc(
            mol, mf.nlcgrids, xc_nlc, dm_total, max_memory=mf.max_memory
        )

    reconstructed = (
        float(mol.energy_nuc())
        + one_electron
        + coulomb
        + float(semilocal_xc)
        + hybrid * x_sr
        + alpha * x_lr
        + float(native_nlc)
    )
    return {
        "omega_bohr_inverse": float(omega),
        "short_range_hf_fraction": float(hybrid),
        "long_range_hf_fraction": float(alpha),
        "nuclear_repulsion": float(mol.energy_nuc()),
        "one_electron": one_electron,
        "coulomb": coulomb,
        "semilocal_xc": float(semilocal_xc),
        "native_wb97m_v_nlc": float(native_nlc),
        "unscaled_full_hf_exchange": x_full,
        "unscaled_long_range_hf_exchange": x_lr,
        "unscaled_short_range_hf_exchange": x_sr,
        "reconstructed_parent_energy": float(reconstructed),
        "reported_parent_energy": float(mf.e_tot),
        "reconstruction_error_hartree": float(reconstructed - mf.e_tot),
    }


def run_pt2(mf, auxiliary_basis: str) -> dict:
    frozen = int(elements.chemcore(mf.mol))
    if isinstance(mf, dft.rks.RKS):
        calculation = mp.MP2(mf, frozen=frozen).density_fit(auxbasis=auxiliary_basis)
    else:
        calculation = mp.UMP2(mf, frozen=frozen).density_fit(auxbasis=auxiliary_basis)
    correlation, _ = calculation.kernel()
    if not np.isfinite(correlation):
        raise RuntimeError("RI-MP2 returned a non-finite correlation energy")
    return {
        "method": "RI-MP2",
        "auxiliary_basis": auxiliary_basis,
        "frozen_core_orbitals": frozen,
        "correlation_energy": float(correlation),
        "same_spin_energy": float(calculation.e_corr_ss),
        "opposite_spin_energy": float(calculation.e_corr_os),
    }


def generate_integrated_dv(
    helper,
    mol: gto.Mole,
    dm_a: np.ndarray,
    dm_b: np.ndarray,
    radial: int,
    angular: int,
    block_size: int,
) -> tuple[np.ndarray, int]:
    coords, weights, _ = helper.build_grid(mol, radial, angular)
    matrix = np.zeros((helper.NELE_SERIES, 180), dtype=np.float64)
    numint = dft.numint.NumInt()
    for start in range(0, weights.size, block_size):
        stop = min(start + block_size, weights.size)
        ao = numint.eval_ao(mol, coords[start:stop], deriv=1)
        rho_a_mgga = numint.eval_rho(mol, ao, dm_a, xctype="MGGA", with_lapl=False)
        rho_b_mgga = numint.eval_rho(mol, ao, dm_b, xctype="MGGA", with_lapl=False)
        rho_a, grad_a, tau_a = helper.unpack_mgga_rho(rho_a_mgga)
        rho_b, grad_b, tau_b = helper.unpack_mgga_rho(rho_b_mgga)
        helper.accumulate_integrated_dv_block(
            weights[start:stop], rho_a, rho_b, grad_a, grad_b, tau_a, tau_b, matrix
        )
        print(f"grid {radial},{angular}: {stop}/{weights.size} points", flush=True)
    if not np.isfinite(matrix).all():
        raise FloatingPointError(f"Non-finite integratedDV values on grid ({radial},{angular})")
    return matrix, int(weights.size)


def main() -> int:
    args = parse_args()
    config_path = args.config.resolve()
    xyz_path = args.xyz.resolve()
    output_dir = args.output_dir.resolve()
    config = load_yaml(config_path)
    if config["feature_models"]["active_for_first_fit"] != "R2_coach291":
        raise ValueError("Smoke driver requires active_for_first_fit=R2_coach291")

    data_root = Path(config["project"]["generated_data_root"]).resolve()
    output_dir.relative_to(data_root)
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    code_root = Path(config["project"]["code_root"]).resolve()
    helper, helper_source = load_coach_feature_module(code_root)
    job = load_xyz(xyz_path)
    orbital = config["orbital_calculation"]
    mol = gto.M(
        atom=job["atom"],
        basis=orbital["basis"],
        charge=job["charge"],
        spin=job["spin"],
        unit="Angstrom",
        verbose=args.verbose,
        max_memory=args.max_memory_mb,
    )
    restricted = job["spin"] == 0
    mf = dft.RKS(mol) if restricted else dft.UKS(mol)
    mf.xc = orbital["functional"]
    mf.conv_tol = float(orbital["convergence"]["energy_tolerance_hartree"])
    mf.max_cycle = int(orbital["convergence"]["maximum_cycles"])
    mf.max_memory = args.max_memory_mb
    parent_grid = config["published_reproduction_grids"]["semilocal_xc"]["default"]
    mf.grids.atom_grid = (parent_grid["radial"], parent_grid["angular"])
    mf.grids.prune = None
    mf.grids.radii_adjust = None
    mf.nlcgrids.atom_grid = (50, 194)
    mf.nlcgrids.prune = dft.gen_grid.sg1_prune
    mf.chkfile = str(temp_dir / "wb97m_v_scf.chk")

    print(f"Running {job['name']} with {mf.__class__.__name__}/{orbital['functional']}/{orbital['basis']}")
    parent_energy = mf.kernel()
    if not mf.converged:
        raise RuntimeError("wb97M-V SCF did not converge")
    dm = np.asarray(mf.make_rdm1())
    dm_a, dm_b = spin_density_matrices(mf, dm)
    gradient_norm = float(np.linalg.norm(mf.get_grad(mf.mo_coeff, mf.mo_occ)))

    stability = {"attempted": True, "stable": None, "error": None}
    try:
        stability_result = mf.stability(internal=True, external=False, return_status=True)
        stability["stable"] = bool(stability_result[2])
    except Exception as exc:  # Stability support varies by PySCF reference type.
        stability["error"] = f"{type(exc).__name__}: {exc}"

    components = evaluate_parent_components(mf, dm_a, dm_b)
    vv10_b10 = evaluate_vv10_b10(mol, dm_a + dm_b, args.max_memory_mb)
    pt2 = run_pt2(mf, "def2-qzvppd-ri")

    row_spec = config["feature_models"]["models"]["R2_coach291"]["integrated_dv_rows"]
    selected_rows = [row_spec["exchange"], row_spec["same_spin_correlation"], row_spec["opposite_spin_correlation"]]
    grid_config = config["coach_feature_grids"]
    grid_entries = {
        grid_config[name]["id"]: (grid_config[name]["radial"], grid_config[name]["angular"])
        for name in ("fitting_reference", "practical", "coarse_analysis")
    }
    matrices = {}
    grid_points = {}
    artifacts = {}
    for grid_id, (radial, angular) in grid_entries.items():
        matrix, point_count = generate_integrated_dv(
            helper, mol, dm_a, dm_b, radial, angular, args.block_size
        )
        matrices[grid_id] = matrix.T
        grid_points[grid_id] = point_count
        path = temp_dir / f"integrated_dv_{grid_id}.npy"
        np.save(path, matrices[grid_id])
        artifacts[path.name] = sha256(path)

    reference_id = grid_config["fitting_reference"]["id"]
    semilocal = matrices[reference_id][selected_rows].reshape(-1)
    feature_vector = np.concatenate(
        [
            semilocal,
            np.asarray(
                [
                    components["unscaled_short_range_hf_exchange"],
                    vv10_b10,
                    pt2["correlation_energy"],
                ]
            ),
        ]
    )
    feature_path = temp_dir / "r2_feature_vector_291.npy"
    np.save(feature_path, feature_vector)
    artifacts[feature_path.name] = sha256(feature_path)

    for grid_id in (grid_config["practical"]["id"], grid_config["coarse_analysis"]["id"]):
        semilocal_diff = (matrices[grid_id] - matrices[reference_id])[selected_rows].reshape(-1)
        diff = np.concatenate([semilocal_diff, np.zeros(3)])
        path = temp_dir / f"r2_grid_diff_{grid_id}_minus_{reference_id}.npy"
        np.save(path, diff)
        artifacts[path.name] = sha256(path)

    manifest = {
        "schema_version": 1,
        "status": "calculation_complete",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "pyscf_version": pyscf.__version__,
        "numpy_version": np.__version__,
        "git_commit": git_commit(Path(config["project"]["repository_root"])),
        "config": str(config_path),
        "config_sha256": sha256(config_path),
        "xyz": str(xyz_path),
        "xyz_sha256": sha256(xyz_path),
        "coach_feature_source": str(helper_source),
        "coach_feature_source_sha256": sha256(helper_source),
        "job": job,
        "reference": "RKS" if restricted else "UKS",
        "scf": {
            "converged": bool(mf.converged),
            "energy_hartree": float(parent_energy),
            "orbital_gradient_norm": gradient_norm,
            "stability": stability,
        },
        "parent_components": components,
        "vv10_b10_c001_hartree": vv10_b10,
        "pt2": pt2,
        "selected_integrated_dv_rows": selected_rows,
        "integrated_dv_shape": [180, 96],
        "grid_points": grid_points,
        "feature_layout": config["feature_models"]["models"]["R2_coach291"]["feature_layout"],
        "feature_vector_shape": list(feature_vector.shape),
        "artifacts_sha256": artifacts,
    }
    manifest_path = temp_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (temp_dir / "CALCULATION_COMPLETE").write_text(
        datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8"
    )
    temp_dir.rename(output_dir)
    print(f"Calculation artifacts written atomically to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
