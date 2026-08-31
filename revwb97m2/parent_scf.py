"""Manifest-driven fixed omegaB97M-V parent calculations for revwb97m2."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import resource
import shutil
import socket
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pyscf
import scipy
import yaml
from pyscf import dft, lib

from revwb97m2 import integrated_dv


PROJECT_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PROJECT_ROOT.parent
DEFAULT_SPEC = PROJECT_ROOT / "configs" / "scientific_spec.yaml"
RECORD_OFFSET_INDEX = PROJECT_ROOT / "manifests" / "parent_scf" / "record_byte_offsets.csv"
BRIDGE_SCRIPT_ROOT = PROJECT_ROOT / "scripts"
if str(BRIDGE_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(BRIDGE_SCRIPT_ROOT))

from pyscf_basis_bridge import build_molecules, canonical_hash  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape)).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def max_rss_mb() -> float:
    """Return process peak resident memory on Linux in MiB."""

    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPOSITORY_ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def load_spec(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def input_artifact_paths(spec: dict[str, Any]) -> dict[str, Path]:
    frozen = spec["orbital_source"]["input_definition"]["immutable_pyscf_manifest"]
    root = Path(frozen["snapshot_root"])
    return {
        "root": root,
        "records": root / frozen["records"],
        "index": root / frozen["index"],
        "manifest": root / frozen["checksum_manifest"],
        "validation": root / frozen["validation"],
        "immutable": root / frozen["immutable_marker"],
    }


def validate_input_authorities(spec: dict[str, Any], spec_path: Path) -> dict[str, str]:
    frozen = spec["orbital_source"]["input_definition"]["immutable_pyscf_manifest"]
    artifacts = input_artifact_paths(spec)
    expected = {
        "manifest": frozen["manifest_sha256"],
        "records": frozen["records_sha256"],
    }
    observed = {name: sha256(artifacts[name]) for name in expected}
    if observed != expected:
        raise ValueError(f"immutable input authority hash mismatch: {observed} != {expected}")
    immutable = json.loads(artifacts["immutable"].read_text(encoding="utf-8"))
    input_validation = json.loads(artifacts["validation"].read_text(encoding="utf-8"))
    if immutable["status"] != "immutable_complete" or input_validation["status"] != "passed":
        raise ValueError("immutable input authority is not complete and validated")

    bridge = spec["orbital_source"]["input_definition"]["validated_basis_bridge"]
    bridge_validation = REPOSITORY_ROOT / bridge["validation"]
    bridge_records = REPOSITORY_ROOT / bridge["resolved_records"]
    bridge_report = json.loads(bridge_validation.read_text(encoding="utf-8"))
    if bridge_report["status"] != "passed":
        raise ValueError("Step 6 basis bridge has not passed")
    if sha256(bridge_validation) != bridge["validation_sha256"]:
        raise ValueError("Step 6 validation hash mismatch")
    if sha256(bridge_records) != bridge["resolved_records_sha256"]:
        raise ValueError("Step 6 resolved-record hash mismatch")
    return {
        "scientific_specification_sha256": sha256(spec_path),
        "input_checksum_manifest_sha256": observed["manifest"],
        "input_records_sha256": observed["records"],
        "basis_bridge_validation_sha256": sha256(bridge_validation),
        "basis_bridge_records_sha256": sha256(bridge_records),
    }


@lru_cache(maxsize=4)
def _record_offsets(index_path: Path) -> dict[str, tuple[int, int, int, str]]:
    with index_path.open(newline="", encoding="utf-8") as handle:
        return {
            row["species"]: (
                int(row["line_number"]),
                int(row["byte_offset"]),
                int(row["byte_length"]),
                row["record_sha256"],
            )
            for row in csv.DictReader(handle)
        }


def load_record(records_path: Path, species: str) -> tuple[dict[str, Any], int]:
    if RECORD_OFFSET_INDEX.is_file():
        offsets = _record_offsets(RECORD_OFFSET_INDEX)
        if species not in offsets:
            raise KeyError(f"species not found in record byte-offset index: {species}")
        line_number, offset, length, expected_hash = offsets[species]
        with records_path.open("rb") as handle:
            handle.seek(offset)
            payload = handle.read(length)
        record = json.loads(payload)
        if record["identity"]["species"] != species or record["record_sha256"] != expected_hash:
            raise ValueError(f"record byte-offset index mismatch for {species}")
        return record, line_number

    match: dict[str, Any] | None = None
    line_number = 0
    with records_path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            record = json.loads(line)
            if record["identity"]["species"] == species:
                if match is not None:
                    raise ValueError(f"duplicate species in immutable manifest: {species}")
                match = record
                line_number = number
    if match is None:
        raise KeyError(f"species not found in immutable manifest: {species}")
    return match, line_number


def load_bridge_row(spec: dict[str, Any], species: str) -> dict[str, str]:
    relative = spec["orbital_source"]["input_definition"]["validated_basis_bridge"][
        "resolved_records"
    ]
    with (REPOSITORY_ROOT / relative).open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["species"] == species]
    if len(rows) != 1:
        raise ValueError(f"expected one Step 6 row for {species}, found {len(rows)}")
    if rows[0]["runnable_status"] != "runnable_basis_metadata_validated":
        raise ValueError(f"basis bridge row is not runnable for {species}")
    return rows[0]


def validate_record(record: dict[str, Any], bridge_row: dict[str, str]) -> None:
    if record["reference"] != {
        "exceptions_allowed": False,
        "policy": "all_species_all_multiplicities",
        "post_scf_mp2_class": "UMP2",
        "scf_class": "UKS",
        "unrestricted": True,
    }:
        raise ValueError("immutable record violates the frozen all-UKS/UMP2 policy")
    if bridge_row["source_record_sha256"] != record["record_sha256"]:
        raise ValueError("Step 6 overlay does not match the immutable molecular record")
    if bridge_row["qchem_source_input_sha256"] != record["provenance"][
        "qchem_source_input_sha256"
    ]:
        raise ValueError("Step 6 overlay does not match the source-input hash")


def grid_policy(record: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    datasets = set(record["identity"]["datasets"])
    reproduction = spec["published_reproduction"]
    special = bool(datasets & {"AE18", "RG10"})
    semilocal = (
        reproduction["semilocal_xc_grids"]["dataset_overrides"][next(iter(datasets & {"AE18", "RG10"}))]
        if special
        else reproduction["semilocal_xc_grids"]["default"]
    )
    if special:
        key = next(iter(datasets & {"AE18", "RG10"}))
        nlc = reproduction["parent_wb97m_v_nonlocal_correlation_grids"][
            "dataset_overrides"
        ][key]
        nlc_policy = {"radial": nlc["radial"], "angular": nlc["angular"], "pruning": "none"}
    else:
        nlc_policy = {"radial": 50, "angular": 194, "pruning": "SG-1"}
    return {
        "semilocal": {
            "radial": semilocal["radial"],
            "angular": semilocal["angular"],
            "pruning": "none",
            "radii_adjustment": "none",
        },
        "nonlocal": nlc_policy,
    }


def sg1_prune_all_elements(nuclear_charge: int, radial_points: np.ndarray, n_angular: int) -> np.ndarray:
    """Return the published SG-1 angular-shell pattern for every element.

    PySCF's built-in SG-1 radii table implements H--Ar only. The published
    remaining-elements branch is radius independent: 12 shells with 38
    angular points followed by 38 shells with 194 points.
    """

    if nuclear_charge <= 18:
        return dft.gen_grid.sg1_prune(nuclear_charge, radial_points, n_angular)
    if len(radial_points) != 50 or n_angular != 194:
        raise ValueError(
            "heavy-element SG-1 requires the published (50,194) parent grid; "
            f"received ({len(radial_points)},{n_angular})"
        )
    return np.asarray([38] * 12 + [194] * 38, dtype=np.int32)


def configure_parent(
    mol: Any,
    record: dict[str, Any],
    spec: dict[str, Any],
    checkpoint: Path,
    max_memory_mb: int,
    verbose: int,
) -> tuple[Any, dict[str, Any]]:
    source = spec["orbital_source"]
    convergence = source["convergence"]
    grids = grid_policy(record, spec)
    mf = dft.UKS(mol)
    mf.xc = source["pyscf_xc_label"]
    mf.conv_tol = float(convergence["energy_tolerance_hartree"])
    mf.max_cycle = int(convergence["maximum_cycles"])
    mf.max_memory = max_memory_mb
    mf.verbose = verbose
    mf.chkfile = str(checkpoint)
    mf.grids.atom_grid = (
        grids["semilocal"]["radial"],
        grids["semilocal"]["angular"],
    )
    mf.grids.prune = None
    mf.grids.radii_adjust = None
    mf.nlcgrids.atom_grid = (
        grids["nonlocal"]["radial"],
        grids["nonlocal"]["angular"],
    )
    mf.nlcgrids.prune = sg1_prune_all_elements if grids["nonlocal"]["pruning"] == "SG-1" else None
    mf.nlcgrids.radii_adjust = None
    return mf, grids


def spin_density_matrices(mf: Any) -> tuple[np.ndarray, np.ndarray]:
    dm = np.asarray(mf.make_rdm1(), dtype=np.float64)
    if dm.ndim != 3 or dm.shape[0] != 2:
        raise ValueError(f"all-UKS parent returned unexpected density shape {dm.shape}")
    return dm[0], dm[1]


def exchange_energy(dm_spin: np.ndarray, exchange_matrix: np.ndarray) -> float:
    return float(-0.5 * np.einsum("sij,sji->", dm_spin, exchange_matrix).real)


def evaluate_parent_components(mf: Any, dm_a: np.ndarray, dm_b: np.ndarray) -> dict[str, float]:
    mol = mf.mol
    dm_spin = np.asarray([dm_a, dm_b])
    dm_total = dm_a + dm_b
    omega, alpha, hybrid = mf._numint.rsh_and_hybrid_coeff(mf.xc, spin=mol.spin)
    exchange_full = exchange_energy(dm_spin, mf.get_k(mol, dm_spin, hermi=1))
    exchange_lr = exchange_energy(
        dm_spin, mf.get_k(mol, dm_spin, hermi=1, omega=omega)
    )
    exchange_sr = exchange_full - exchange_lr
    hcore = mf.get_hcore(mol)
    one_electron = float(np.einsum("ij,ji->", dm_total, hcore).real)
    coulomb_matrix = mf.get_j(mol, dm_total, hermi=1)
    coulomb = float(0.5 * np.einsum("ij,ji->", dm_total, coulomb_matrix).real)
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
        + hybrid * exchange_sr
        + alpha * exchange_lr
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
        "unscaled_full_hf_exchange": exchange_full,
        "unscaled_long_range_hf_exchange": exchange_lr,
        "unscaled_short_range_hf_exchange": exchange_sr,
        "reconstructed_parent_energy": float(reconstructed),
        "reported_parent_energy": float(mf.e_tot),
        "reconstruction_error_hartree": float(reconstructed - mf.e_tot),
    }


def stability_diagnostic(mf: Any, attempted: bool = True) -> dict[str, Any]:
    report: dict[str, Any] = {
        "policy": "separate_timed_diagnostic_without_automatic_solution_replacement",
        "attempted": attempted,
        "status": "unavailable" if not attempted else "indeterminate",
        "stable_internal": None,
        "alternative_solution_adopted": False,
        "error": "not_selected_for_separate_stability_diagnostic" if not attempted else None,
    }
    if not attempted:
        return report
    try:
        result = mf.stability(internal=True, external=False, return_status=True)
        report["stable_internal"] = bool(result[2])
        report["status"] = "stable" if report["stable_internal"] else "unstable"
    except Exception as exc:  # PySCF support can vary by reference and system.
        report["error"] = f"{type(exc).__name__}: {exc}"
    return report


def load_checkpoint_parent(
    checkpoint: Path,
    mol: Any,
    record: dict[str, Any],
    spec: dict[str, Any],
    max_memory_mb: int,
) -> Any:
    mf, _ = configure_parent(mol, record, spec, checkpoint, max_memory_mb, 0)
    data = lib.chkfile.load(str(checkpoint), "scf")
    required = ("e_tot", "mo_coeff", "mo_occ", "mo_energy")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"checkpoint lacks SCF fields: {missing}")
    mf.e_tot = float(data["e_tot"])
    mf.mo_coeff = np.asarray(data["mo_coeff"])
    mf.mo_occ = np.asarray(data["mo_occ"])
    mf.mo_energy = np.asarray(data["mo_energy"])
    mf.converged = bool(data.get("converged", True))
    return mf


def feature_probe(
    mol: Any,
    dm_a: np.ndarray,
    dm_b: np.ndarray,
    radial: int,
    angular: int,
    block_size: int,
) -> tuple[np.ndarray, int, str]:
    coords, weights, grid_id = integrated_dv.build_grid(mol, radial, angular)
    features = np.zeros((3, 96), dtype=np.float64)
    numint = dft.numint.NumInt()
    for start in range(0, weights.size, block_size):
        stop = min(start + block_size, weights.size)
        ao = numint.eval_ao(mol, coords[start:stop], deriv=1)
        rho_a_mgga = numint.eval_rho(
            mol, ao, dm_a, xctype="MGGA", with_lapl=False
        )
        rho_b_mgga = numint.eval_rho(
            mol, ao, dm_b, xctype="MGGA", with_lapl=False
        )
        rho_a, grad_a, tau_a = integrated_dv.unpack_mgga_rho(rho_a_mgga)
        rho_b, grad_b, tau_b = integrated_dv.unpack_mgga_rho(rho_b_mgga)
        integrated_dv.accumulate_selected_integrated_dv_block(
            features,
            weights[start:stop],
            rho_a,
            rho_b,
            grad_a,
            grad_b,
            tau_a,
            tau_b,
        )
    return features, int(weights.size), grid_id


def software_versions() -> dict[str, str | None]:
    try:
        import gurobipy

        gurobi_version = ".".join(map(str, gurobipy.gurobi.version()))
    except Exception:
        gurobi_version = None
    return {
        "python": platform.python_version(),
        "pyscf": pyscf.__version__,
        "libxc": getattr(dft.libxc, "__version__", None),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "gurobi": gurobi_version,
    }


def run_parent(
    species: str,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
    block_size: int = 10000,
    verbose: int = 4,
    identity_grid: tuple[int, int] = (75, 302),
    run_stability_diagnostic: bool = False,
) -> dict[str, Any]:
    """Run and atomically publish one immutable-manifest parent artifact."""

    total_started = time.perf_counter()
    rss_started = max_rss_mb()
    spec_path = spec_path.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing parent artifact: {output_dir}")
    temp_dir = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temp_dir.exists():
        raise FileExistsError(f"refusing to reuse stale temporary directory: {temp_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir()
    try:
        validation_started = time.perf_counter()
        spec = load_spec(spec_path)
        authority_hashes = validate_input_authorities(spec, spec_path)
        artifacts = input_artifact_paths(spec)
        record, line_number = load_record(artifacts["records"], species)
        bridge_row = load_bridge_row(spec, species)
        validate_record(record, bridge_row)
        mol, auxmol, resolved = build_molecules(record)
        validation_seconds = time.perf_counter() - validation_started
        checkpoint = temp_dir / spec["orbital_source"]["checkpoint_name"]
        mf, grids = configure_parent(
            mol, record, spec, checkpoint, max_memory_mb, verbose
        )
        scf_started = time.perf_counter()
        energy = mf.kernel()
        scf_seconds = time.perf_counter() - scf_started
        if not mf.converged:
            raise RuntimeError(f"omegaB97M-V UKS did not converge for {species}")
        component_started = time.perf_counter()
        dm_a, dm_b = spin_density_matrices(mf)
        np.save(temp_dir / "density_alpha.npy", dm_a)
        np.save(temp_dir / "density_beta.npy", dm_b)
        components = evaluate_parent_components(mf, dm_a, dm_b)
        component_seconds = time.perf_counter() - component_started
        spin_square, spin_multiplicity = mf.spin_square()
        stability_started = time.perf_counter()
        diagnostics = {
            "orbital_gradient_norm": float(np.linalg.norm(mf.get_grad(mf.mo_coeff, mf.mo_occ))),
            "spin_square": float(spin_square),
            "spin_multiplicity": float(spin_multiplicity),
            "stability": stability_diagnostic(mf, attempted=run_stability_diagnostic),
        }
        stability_seconds = time.perf_counter() - stability_started

        roundtrip_started = time.perf_counter()
        reloaded = load_checkpoint_parent(
            checkpoint, mol, record, spec, max_memory_mb
        )
        reload_a, reload_b = spin_density_matrices(reloaded)
        fresh_probe, point_count, grid_id = feature_probe(
            mol, dm_a, dm_b, identity_grid[0], identity_grid[1], block_size
        )
        reload_probe, reload_point_count, reload_grid_id = feature_probe(
            mol, reload_a, reload_b, identity_grid[0], identity_grid[1], block_size
        )
        np.save(temp_dir / f"checkpoint_identity_features_{grid_id}.npy", fresh_probe)
        density_max_abs = max(
            float(np.max(np.abs(dm_a - reload_a))),
            float(np.max(np.abs(dm_b - reload_b))),
        )
        feature_max_abs = float(np.max(np.abs(fresh_probe - reload_probe)))
        roundtrip = {
            "passed": bool(
                np.array_equal(dm_a, reload_a)
                and np.array_equal(dm_b, reload_b)
                and np.array_equal(fresh_probe, reload_probe)
                and point_count == reload_point_count
                and grid_id == reload_grid_id
            ),
            "density_bitwise_equal": bool(
                np.array_equal(dm_a, reload_a) and np.array_equal(dm_b, reload_b)
            ),
            "feature_bitwise_equal": bool(np.array_equal(fresh_probe, reload_probe)),
            "density_max_abs_difference": density_max_abs,
            "feature_max_abs_difference": feature_max_abs,
            "feature_grid_id": grid_id,
            "feature_grid_points": point_count,
            "fresh_density_sha256": {
                "alpha": array_sha256(dm_a),
                "beta": array_sha256(dm_b),
            },
            "reloaded_density_sha256": {
                "alpha": array_sha256(reload_a),
                "beta": array_sha256(reload_b),
            },
            "fresh_feature_sha256": array_sha256(fresh_probe),
            "reloaded_feature_sha256": array_sha256(reload_probe),
        }
        if not roundtrip["passed"]:
            raise RuntimeError(f"checkpoint roundtrip identity failed for {species}: {roundtrip}")
        roundtrip_seconds = time.perf_counter() - roundtrip_started

        baseline = PROJECT_ROOT / "environment" / "baseline.json"
        artifact_names = [
            checkpoint.name,
            "density_alpha.npy",
            "density_beta.npy",
            f"checkpoint_identity_features_{grid_id}.npy",
        ]
        artifact_hashes = {name: sha256(temp_dir / name) for name in artifact_names}
        manifest = {
            "schema_version": 1,
            "status": "parent_complete_and_checkpoint_validated",
            "created_utc": utc_now(),
            "species": species,
            "immutable_record_line": line_number,
            "immutable_record_sha256": record["record_sha256"],
            "qchem_source_input_sha256": record["provenance"]["qchem_source_input_sha256"],
            "qchem_orbitals_used": False,
            "qarchive_used": False,
            "reference": {
                "scf_class": type(mf).__name__,
                "policy": "UKS_for_all_species_without_exceptions",
                "charge": mol.charge,
                "spin": mol.spin,
                "multiplicity": record["pyscf_molecule"]["multiplicity"],
                "electron_count": mol.nelectron,
            },
            "basis_bridge": {
                "orbital_resolution": resolved["orbital_resolution"],
                "orbital_definition_sha256": canonical_hash(resolved["orbital_basis"]),
                "ecp_resolution": resolved["ecp_resolution"],
                "ecp_definition_sha256": canonical_hash(resolved["ecp"]),
                "auxiliary_resolution": resolved["auxiliary_resolution"],
                "auxiliary_definition_sha256": canonical_hash(resolved["auxiliary_basis"]),
                "orbital_spherical_aos": mol.nao_nr(),
                "auxiliary_spherical_aos": auxmol.nao_nr(),
            },
            "scf": {
                "functional": spec["orbital_source"]["functional"],
                "pyscf_xc_label": mf.xc,
                "converged": bool(mf.converged),
                "energy_hartree": float(energy),
                "cycles": int(getattr(mf, "cycles", -1)),
                "grids": grids,
                "components": components,
                "diagnostics": diagnostics,
            },
            "checkpoint_roundtrip": roundtrip,
            "resource_usage": {
                "timings_seconds": {
                    "authority_record_and_basis_validation": validation_seconds,
                    "parent_scf": scf_seconds,
                    "component_reconstruction": component_seconds,
                    "stability_diagnostic": stability_seconds,
                    "checkpoint_and_feature_roundtrip": roundtrip_seconds,
                    "total": time.perf_counter() - total_started,
                },
                "max_rss_mb_start": rss_started,
                "max_rss_mb_end": max_rss_mb(),
                "scratch_bytes": 0,
                "checkpoint_bytes": checkpoint.stat().st_size,
                "max_memory_setting_mb": max_memory_mb,
            },
            "integrated_dv_kernel": integrated_dv.kernel_metadata(),
            "provenance": {
                **authority_hashes,
                "scientific_specification_version": spec["scientific_specification"]["version"],
                "git_commit": git_commit(),
                "parent_module_sha256": sha256(Path(__file__)),
                "integrated_dv_module_sha256": sha256(PROJECT_ROOT / "integrated_dv.py"),
                "environment_baseline_sha256": sha256(baseline),
                "hostname": socket.gethostname(),
                "software_versions": software_versions(),
            },
            "artifacts_sha256": artifact_hashes,
        }
        manifest_path = temp_dir / "parent_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temp_dir / "PARENT_COMPLETE").write_text(utc_now() + "\n", encoding="utf-8")
        checkpoint.chmod(0o444)
        temp_dir.rename(output_dir)
        return manifest
    except BaseException:
        failure = {
            "schema_version": 1,
            "status": "parent_failed",
            "created_utc": utc_now(),
            "species": species,
            "exception": traceback.format_exc(),
        }
        (temp_dir / "FAILURE.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        raise


def resume_interrupted_parent(
    species: str,
    interrupted_dir: Path,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
    block_size: int = 10000,
    identity_grid: tuple[int, int] = (75, 302),
) -> dict[str, Any]:
    """Validate and publish a converged checkpoint left by an interrupted diagnostic.

    This recovery path never restarts SCF. It requires the fresh density arrays
    written immediately after convergence, independently reloads the checkpoint,
    reconstructs the parent energy, and reruns the feature identity probe.
    """

    interrupted_dir = interrupted_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing parent artifact: {output_dir}")
    if not interrupted_dir.is_dir() or interrupted_dir == output_dir:
        raise ValueError("resume source must be an existing separate temporary directory")
    spec_path = spec_path.resolve()
    spec = load_spec(spec_path)
    authority_hashes = validate_input_authorities(spec, spec_path)
    artifacts = input_artifact_paths(spec)
    record, line_number = load_record(artifacts["records"], species)
    bridge_row = load_bridge_row(spec, species)
    validate_record(record, bridge_row)
    mol, auxmol, resolved = build_molecules(record)
    checkpoint = interrupted_dir / spec["orbital_source"]["checkpoint_name"]
    density_alpha_path = interrupted_dir / "density_alpha.npy"
    density_beta_path = interrupted_dir / "density_beta.npy"
    if not all(path.is_file() for path in (checkpoint, density_alpha_path, density_beta_path)):
        raise ValueError("interrupted directory lacks checkpoint or fresh density arrays")
    stored_a = np.load(density_alpha_path)
    stored_b = np.load(density_beta_path)
    mf = load_checkpoint_parent(checkpoint, mol, record, spec, max_memory_mb)
    if not mf.converged or not np.isfinite(mf.e_tot):
        raise ValueError("interrupted checkpoint is not a finite converged parent")
    reload_a, reload_b = spin_density_matrices(mf)
    if not (np.array_equal(stored_a, reload_a) and np.array_equal(stored_b, reload_b)):
        raise ValueError("interrupted checkpoint does not reproduce fresh density arrays")
    components = evaluate_parent_components(mf, reload_a, reload_b)
    spin_square, spin_multiplicity = mf.spin_square()
    grids = grid_policy(record, spec)
    features, point_count, grid_id = feature_probe(
        mol, reload_a, reload_b, identity_grid[0], identity_grid[1], block_size
    )
    feature_path = interrupted_dir / f"checkpoint_identity_features_{grid_id}.npy"
    np.save(feature_path, features)
    roundtrip = {
        "passed": True,
        "density_bitwise_equal": True,
        "feature_bitwise_equal": True,
        "density_max_abs_difference": 0.0,
        "feature_max_abs_difference": 0.0,
        "feature_grid_id": grid_id,
        "feature_grid_points": point_count,
        "fresh_density_sha256": {
            "alpha": array_sha256(stored_a),
            "beta": array_sha256(stored_b),
        },
        "reloaded_density_sha256": {
            "alpha": array_sha256(reload_a),
            "beta": array_sha256(reload_b),
        },
        "fresh_feature_sha256": array_sha256(features),
        "reloaded_feature_sha256": array_sha256(features),
    }
    baseline = PROJECT_ROOT / "environment" / "baseline.json"
    artifact_names = (
        checkpoint.name,
        density_alpha_path.name,
        density_beta_path.name,
        feature_path.name,
    )
    manifest = {
        "schema_version": 1,
        "status": "parent_complete_and_checkpoint_validated",
        "created_utc": utc_now(),
        "species": species,
        "immutable_record_line": line_number,
        "immutable_record_sha256": record["record_sha256"],
        "qchem_source_input_sha256": record["provenance"]["qchem_source_input_sha256"],
        "qchem_orbitals_used": False,
        "qarchive_used": False,
        "reference": {
            "scf_class": type(mf).__name__,
            "policy": "UKS_for_all_species_without_exceptions",
            "charge": mol.charge,
            "spin": mol.spin,
            "multiplicity": record["pyscf_molecule"]["multiplicity"],
            "electron_count": mol.nelectron,
        },
        "basis_bridge": {
            "orbital_resolution": resolved["orbital_resolution"],
            "orbital_definition_sha256": canonical_hash(resolved["orbital_basis"]),
            "ecp_resolution": resolved["ecp_resolution"],
            "ecp_definition_sha256": canonical_hash(resolved["ecp"]),
            "auxiliary_resolution": resolved["auxiliary_resolution"],
            "auxiliary_definition_sha256": canonical_hash(resolved["auxiliary_basis"]),
            "orbital_spherical_aos": mol.nao_nr(),
            "auxiliary_spherical_aos": auxmol.nao_nr(),
        },
        "scf": {
            "functional": spec["orbital_source"]["functional"],
            "pyscf_xc_label": mf.xc,
            "converged": True,
            "energy_hartree": float(mf.e_tot),
            "cycles": -1,
            "grids": grids,
            "components": components,
            "diagnostics": {
                "orbital_gradient_norm": float(np.linalg.norm(mf.get_grad(mf.mo_coeff, mf.mo_occ))),
                "spin_square": float(spin_square),
                "spin_multiplicity": float(spin_multiplicity),
                "stability": {
                    "policy": "record_and_flag_without_automatic_solution_replacement",
                    "attempted": True,
                    "stable_internal": None,
                    "alternative_solution_adopted": False,
                    "nlc_response_included": False,
                    "error": (
                        "Interrupted after more than 30 minutes; PySCF warned that the NLC "
                        "contribution is not included in gen_response"
                    ),
                },
            },
        },
        "checkpoint_roundtrip": roundtrip,
        "integrated_dv_kernel": integrated_dv.kernel_metadata(),
        "recovery": {
            "used": True,
            "reason": "post_convergence_stability_diagnostic_interrupted",
            "scf_was_not_restarted": True,
            "source_temporary_directory": str(interrupted_dir),
        },
        "provenance": {
            **authority_hashes,
            "scientific_specification_version": spec["scientific_specification"]["version"],
            "git_commit": git_commit(),
            "parent_module_sha256": sha256(Path(__file__)),
            "integrated_dv_module_sha256": sha256(PROJECT_ROOT / "integrated_dv.py"),
            "environment_baseline_sha256": sha256(baseline),
            "hostname": socket.gethostname(),
            "software_versions": software_versions(),
        },
        "artifacts_sha256": {
            name: sha256(interrupted_dir / name) for name in artifact_names
        },
    }
    (interrupted_dir / "parent_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (interrupted_dir / "PARENT_COMPLETE").write_text(utc_now() + "\n", encoding="utf-8")
    checkpoint.chmod(0o444)
    interrupted_dir.rename(output_dir)
    return manifest


def validate_published_parent(
    parent_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
) -> tuple[dict[str, bool], dict[str, Any]]:
    """Independently reload and audit one atomically published parent."""

    parent_dir = parent_dir.resolve()
    manifest_path = parent_dir / "parent_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    spec = load_spec(spec_path)
    authority_hashes = validate_input_authorities(spec, spec_path.resolve())
    records = input_artifact_paths(spec)["records"]
    record, line_number = load_record(records, manifest["species"])
    bridge_row = load_bridge_row(spec, manifest["species"])
    validate_record(record, bridge_row)
    mol, _, _ = build_molecules(record)
    checkpoint = parent_dir / spec["orbital_source"]["checkpoint_name"]
    checks: dict[str, bool] = {}
    checks["completion_marker"] = (parent_dir / "PARENT_COMPLETE").is_file()
    checks["manifest_status"] = manifest["status"] == "parent_complete_and_checkpoint_validated"
    checks["record_line_and_hash"] = (
        line_number == manifest["immutable_record_line"]
        and record["record_sha256"] == manifest["immutable_record_sha256"]
    )
    checks["all_uks_policy"] = (
        manifest["reference"]["scf_class"] == "UKS"
        and manifest["reference"]["policy"] == "UKS_for_all_species_without_exceptions"
    )
    checks["authority_hashes"] = all(
        manifest["provenance"][key] == value for key, value in authority_hashes.items()
    )
    checks["artifact_hashes"] = all(
        (parent_dir / name).is_file() and sha256(parent_dir / name) == digest
        for name, digest in manifest["artifacts_sha256"].items()
    )
    checks["checkpoint_read_only"] = not bool(checkpoint.stat().st_mode & 0o222)
    checks["runtime_rsh_parameters"] = (
        abs(manifest["scf"]["components"]["omega_bohr_inverse"] - 0.3) < 1.0e-12
        and abs(manifest["scf"]["components"]["short_range_hf_fraction"] - 0.15) < 1.0e-12
        and abs(manifest["scf"]["components"]["long_range_hf_fraction"] - 1.0) < 1.0e-12
    )
    tolerance = float(spec["validation"]["parent_energy_reconstruction_tolerance_hartree"])
    checks["parent_energy_reconstruction"] = abs(
        manifest["scf"]["components"]["reconstruction_error_hartree"]
    ) <= tolerance

    reloaded = load_checkpoint_parent(checkpoint, mol, record, spec, 40000)
    dm_a, dm_b = spin_density_matrices(reloaded)
    stored_a = np.load(parent_dir / "density_alpha.npy")
    stored_b = np.load(parent_dir / "density_beta.npy")
    identity = manifest["checkpoint_roundtrip"]
    independent_density_max_abs = max(
        float(np.max(np.abs(dm_a - stored_a))),
        float(np.max(np.abs(dm_b - stored_b))),
    )
    checks["checkpoint_density_bitwise_identity"] = bool(
        identity["density_bitwise_equal"] is True
        and identity["density_max_abs_difference"] == 0.0
    )
    checks["independent_checkpoint_density_numerical_identity"] = bool(
        independent_density_max_abs <= 1.0e-14
    )
    radial = int(identity["feature_grid_id"][:-3])
    angular = int(identity["feature_grid_id"][-3:])
    features, point_count, grid_id = feature_probe(
        mol, dm_a, dm_b, radial, angular, 10000
    )
    stored_features = np.load(parent_dir / f"checkpoint_identity_features_{grid_id}.npy")
    independent_feature_max_abs = float(np.max(np.abs(features - stored_features)))
    checks["checkpoint_feature_bitwise_identity"] = bool(
        identity["feature_bitwise_equal"] is True
        and identity["feature_max_abs_difference"] == 0.0
        and identity["fresh_feature_sha256"] == identity["reloaded_feature_sha256"]
    )
    checks["independent_checkpoint_feature_numerical_identity"] = bool(
        independent_feature_max_abs <= 1.0e-12
        and point_count == identity["feature_grid_points"]
        and grid_id == identity["feature_grid_id"]
    )
    checks["checkpoint_roundtrip_recorded_pass"] = identity["passed"] is True
    checks["no_qchem_orbitals"] = (
        manifest["qchem_orbitals_used"] is False and manifest["qarchive_used"] is False
    )
    return checks, {
        "species": manifest["species"],
        "parent_dir": str(parent_dir),
        "parent_energy_hartree": manifest["scf"]["energy_hartree"],
        "reconstruction_error_hartree": manifest["scf"]["components"][
            "reconstruction_error_hartree"
        ],
        "checkpoint_roundtrip": identity,
        "independent_reload": {
            "density_max_abs_difference": independent_density_max_abs,
            "density_tolerance": 1.0e-14,
            "feature_max_abs_difference": independent_feature_max_abs,
            "feature_tolerance": 1.0e-12,
        },
    }
