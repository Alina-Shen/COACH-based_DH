"""Checkpoint-only scalar double-hybrid features for revwb97m2.

This stage consumes a validated Step-8 omegaB97M-V checkpoint.  It never
executes SCF and it keeps the fitted SR-HF, VV10, total RI-UMP2, and pure
three-body D4-ATM terms separate from the fixed energy partition.
"""

from __future__ import annotations

import json
import os
import resource
import socket
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np
from dftd4.interface import DampingParam, DispersionModel
from pyscf import dft, lib, mp
from pyscf.data import elements

from revwb97m2 import integrated_dv
from revwb97m2.parent_scf import (
    DEFAULT_SPEC,
    PROJECT_ROOT,
    array_sha256,
    git_commit,
    grid_policy,
    input_artifact_paths,
    load_bridge_row,
    load_checkpoint_parent,
    load_record,
    load_spec,
    sha256,
    sg1_prune_all_elements,
    software_versions,
    spin_density_matrices,
    utc_now,
    validate_input_authorities,
    validate_published_parent,
    validate_record,
)
from revwb97m2.scripts.pyscf_basis_bridge import build_molecules, canonical_hash


SCALAR_INDICES = {"short_range_hf": 288, "vv10": 289, "pt2": 290, "d4_atm": 291}
FEATURE_COUNT = 292
MODEL_FEATURE_COUNTS = {"R1": 79, "R2": 292}
MODEL_SEMILOCAL_COUNTS = {"R1": 75, "R2": 288}
MODEL_SCALAR_INDICES = {
    "R1": {"short_range_hf": 75, "vv10": 76, "pt2": 77, "d4_atm": 78},
    "R2": SCALAR_INDICES,
}
PT2_COMPONENT_TOLERANCE_HARTREE = 1.0e-12
IDENTITY_TOLERANCE_HARTREE = 1.0e-12


def _directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _max_rss_mb() -> float:
    # Linux reports ru_maxrss in KiB.
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def _configure_nlc_grid(mol: Any, policy: dict[str, Any]) -> Any:
    grids = dft.Grids(mol)
    grids.atom_grid = (int(policy["radial"]), int(policy["angular"]))
    grids.prune = sg1_prune_all_elements if policy["pruning"] == "SG-1" else None
    grids.radii_adjust = None
    grids.build(with_non0tab=True)
    return grids


def evaluate_vv10(
    mol: Any,
    dm_a: np.ndarray,
    dm_b: np.ndarray,
    grid: dict[str, Any],
    b: float,
    c: float,
    max_memory_mb: int,
) -> tuple[float, int]:
    """Evaluate VV10 once on the fixed parent total density and NLC grid."""

    nlc_grids = _configure_nlc_grid(mol, grid)
    numint = dft.numint.NumInt()
    numint.nlc_coeff = lambda _xc_code: (((b, c), 1.0),)
    _, energy, _ = numint.nr_nlc_vxc(
        mol,
        nlc_grids,
        "VV10",
        dm_a + dm_b,
        max_memory=max_memory_mb,
    )
    return float(energy), int(nlc_grids.weights.size)


def evaluate_ri_ump2(
    mf: Any,
    mol: Any,
    auxiliary_basis: dict[str, Any],
    scratch_dir: Path,
    max_memory_mb: int,
) -> tuple[dict[str, Any], int]:
    """Run canonical frozen-core DF-UMP2 on the checkpoint orbitals."""

    frozen = int(elements.chemcore(mol))
    calculation = mp.UMP2(mf, frozen=frozen).density_fit(auxbasis=auxiliary_basis)
    calculation.max_memory = max_memory_mb
    cderi = scratch_dir / "ri_3c.h5"
    calculation.with_df._cderi_to_save = str(cderi)
    # Production needs only the correlation energy and its SS/OS components.
    # Retaining the full O^2 V^2 amplitude tensors is unnecessary and can make
    # otherwise feasible species fail PySCF's pre-allocation memory check.
    correlation, amplitudes = calculation.kernel(with_t2=False)
    if amplitudes is not None:
        raise RuntimeError("energy-only DF-UMP2 unexpectedly retained amplitudes")
    result = {
        "method": type(calculation).__name__,
        "canonical_orbitals": True,
        "mp2_amplitudes_retained": False,
        "density_fitted": True,
        "frozen_core": True,
        "frozen_orbitals": frozen,
        "total_correlation_hartree": float(correlation),
        "same_spin_correlation_hartree": float(calculation.e_corr_ss),
        "opposite_spin_correlation_hartree": float(calculation.e_corr_os),
    }
    result["component_sum_error_hartree"] = float(
        result["total_correlation_hartree"]
        - result["same_spin_correlation_hartree"]
        - result["opposite_spin_correlation_hartree"]
    )
    return result, _directory_bytes(scratch_dir)


def evaluate_d4_atm(mol: Any, damping_parameters: dict[str, float]) -> float:
    """Evaluate the frozen COACH pure three-body D4-ATM feature."""

    model = DispersionModel(
        numbers=np.asarray(mol.atom_charges(), dtype=int),
        positions=np.asarray(mol.atom_coords(), dtype=float),
        charge=float(mol.charge),
    )
    parameters = DampingParam(**damping_parameters)
    return float(model.get_dispersion(parameters, grad=False)["energy"])


def fixed_energy_partition(parent_manifest: dict[str, Any]) -> dict[str, float]:
    components = parent_manifest["scf"]["components"]
    partition = {
        "nuclear_repulsion": float(components["nuclear_repulsion"]),
        "one_electron": float(components["one_electron"]),
        "coulomb": float(components["coulomb"]),
        "full_long_range_hf_exchange": float(
            components["unscaled_long_range_hf_exchange"]
        ),
    }
    partition["total_hartree"] = float(sum(partition.values()))
    return partition


def assemble_feature_vector(
    semilocal_features: np.ndarray,
    short_range_hf: float,
    vv10: float,
    pt2: float,
    d4_atm: float,
) -> np.ndarray:
    semilocal = np.asarray(semilocal_features, dtype=np.float64)
    if semilocal.shape != (3, integrated_dv.FEATURES_PER_CHANNEL):
        raise ValueError(f"expected selected semilocal shape (3, 96), got {semilocal.shape}")
    vector = np.empty(FEATURE_COUNT, dtype=np.float64)
    vector[:288] = semilocal.reshape(-1)
    vector[288:] = (short_range_hf, vv10, pt2, d4_atm)
    if not np.all(np.isfinite(vector)):
        raise FloatingPointError("assembled feature vector contains NaN or infinity")
    return vector


def assemble_r1_r2_feature_vectors(
    r1_semilocal_features: np.ndarray,
    r2_semilocal_features: np.ndarray,
    short_range_hf: float,
    vv10: float,
    pt2: float,
    d4_atm: float,
) -> dict[str, np.ndarray]:
    """Attach four shared scalar features to the production R1 and R2 spaces."""

    semilocal = {
        "R1": np.asarray(r1_semilocal_features, dtype=np.float64).reshape(-1),
        "R2": np.asarray(r2_semilocal_features, dtype=np.float64).reshape(-1),
    }
    scalars = np.asarray((short_range_hf, vv10, pt2, d4_atm), dtype=np.float64)
    if not np.all(np.isfinite(scalars)):
        raise FloatingPointError("shared scalar features contain NaN or infinity")
    vectors: dict[str, np.ndarray] = {}
    for space in ("R1", "R2"):
        expected = MODEL_SEMILOCAL_COUNTS[space]
        if semilocal[space].shape != (expected,):
            raise ValueError(
                f"expected {space} semilocal length {expected}, got {semilocal[space].shape}"
            )
        vector = np.concatenate((semilocal[space], scalars))
        if vector.shape != (MODEL_FEATURE_COUNTS[space],) or not np.all(
            np.isfinite(vector)
        ):
            raise FloatingPointError(f"invalid assembled {space} feature vector")
        vectors[space] = vector
    return vectors


def publish_r1_r2_assembly(
    semilocal_dir: Path,
    scalar_dir: Path,
    output_dir: Path,
    grid_id: str = "250974",
) -> dict[str, Any]:
    """Atomically publish final R1-79 and R2-292 vectors for one species.

    The semilocal arrays must come from the schema-2 shared-density evaluator;
    the four scalar features are loaded once and appended identically to both spaces.
    """

    semilocal_dir = semilocal_dir.resolve()
    scalar_dir = scalar_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing assembly artifact: {output_dir}")
    temp_dir = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temp_dir.exists():
        raise FileExistsError(f"refusing to reuse stale temporary directory: {temp_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir()
    try:
        semilocal_manifest_path = semilocal_dir / "semilocal_manifest.json"
        scalar_manifest_path = scalar_dir / "scalar_manifest.json"
        semilocal_manifest = json.loads(semilocal_manifest_path.read_text(encoding="utf-8"))
        scalar_manifest = json.loads(scalar_manifest_path.read_text(encoding="utf-8"))
        if semilocal_manifest.get("schema_version") != 2 or not semilocal_manifest.get(
            "shared_grid_density_evaluation"
        ):
            raise ValueError("R1/R2 assembly requires a shared-density schema-2 semilocal artifact")
        if semilocal_manifest.get("status") != (
            "three_grid_r1_r2_semilocal_features_complete_and_validated"
        ) or scalar_manifest.get("status") != "scalar_features_complete_and_validated":
            raise ValueError("semilocal or scalar input is not complete and validated")
        if semilocal_manifest["species"] != scalar_manifest["species"]:
            raise ValueError("semilocal and scalar artifacts belong to different species")
        r1_path = semilocal_dir / f"r1_semilocal_features_75_{grid_id}.npy"
        r2_path = semilocal_dir / f"r2_semilocal_features_288_{grid_id}.npy"
        scalars_path = scalar_dir / "scalar_features_288_291.npy"
        for path in (r1_path, r2_path, scalars_path):
            if not path.is_file():
                raise FileNotFoundError(path)
        for path, source_manifest in (
            (r1_path, semilocal_manifest),
            (r2_path, semilocal_manifest),
            (scalars_path, scalar_manifest),
        ):
            expected_hash = source_manifest.get("artifacts_sha256", {}).get(path.name)
            if expected_hash is None or sha256(path) != expected_hash:
                raise ValueError(f"input artifact hash mismatch or absent: {path}")
        scalars = np.load(scalars_path)
        if scalars.shape != (4,) or not np.all(np.isfinite(scalars)):
            raise ValueError(f"expected four finite scalar features, got {scalars.shape}")
        vectors = assemble_r1_r2_feature_vectors(
            np.load(r1_path), np.load(r2_path), *[float(value) for value in scalars]
        )
        filenames = {"R1": "feature_vector_79.npy", "R2": "feature_vector_292.npy"}
        for space, filename in filenames.items():
            np.save(temp_dir / filename, vectors[space])
        artifacts_sha256 = {
            filename: sha256(temp_dir / filename) for filename in filenames.values()
        }
        manifest = {
            "schema_version": 1,
            "status": "r1_r2_species_assembly_complete_and_validated",
            "created_utc": utc_now(),
            "species": semilocal_manifest["species"],
            "grid_id": grid_id,
            "shared_grid_density_evaluation": True,
            "shared_scalar_evaluation": True,
            "feature_vectors": {
                space: {
                    "length": MODEL_FEATURE_COUNTS[space],
                    "semilocal_count": MODEL_SEMILOCAL_COUNTS[space],
                    "scalar_indices": MODEL_SCALAR_INDICES[space],
                    "array_sha256": array_sha256(vectors[space]),
                    "filename": filenames[space],
                }
                for space in ("R1", "R2")
            },
            "inputs": {
                "semilocal_manifest": str(semilocal_manifest_path),
                "semilocal_manifest_sha256": sha256(semilocal_manifest_path),
                "scalar_manifest": str(scalar_manifest_path),
                "scalar_manifest_sha256": sha256(scalar_manifest_path),
            },
            "artifacts_sha256": artifacts_sha256,
        }
        (temp_dir / "assembly_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temp_dir / "ASSEMBLY_COMPLETE").write_text(utc_now() + "\n", encoding="utf-8")
        temp_dir.rename(output_dir)
        return manifest
    except BaseException:
        (temp_dir / "FAILURE.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "r1_r2_species_assembly_failed",
                    "created_utc": utc_now(),
                    "exception": traceback.format_exc(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        raise


def direct_energy_identity(
    fixed_energy: float,
    semilocal_features: np.ndarray,
    scalars: tuple[float, float, float, float],
) -> dict[str, Any]:
    """Compare named-channel assembly with a 292-vector dot product."""

    vector = assemble_feature_vector(semilocal_features, *scalars)
    coefficient_sets = {
        "dense_deterministic": np.linspace(-0.25, 0.25, FEATURE_COUNT),
        "scalar_and_channel_edges": np.zeros(FEATURE_COUNT, dtype=np.float64),
    }
    coefficient_sets["scalar_and_channel_edges"][[0, 95, 96, 191, 192, 287, 288, 289, 290, 291]] = (
        0.11,
        -0.07,
        0.05,
        -0.03,
        0.13,
        -0.17,
        0.41,
        0.73,
        0.29,
        0.37,
    )
    cases: dict[str, Any] = {}
    for name, coefficients in coefficient_sets.items():
        named = float(fixed_energy)
        named += float(np.dot(semilocal_features[0], coefficients[0:96]))
        named += float(np.dot(semilocal_features[1], coefficients[96:192]))
        named += float(np.dot(semilocal_features[2], coefficients[192:288]))
        named += float(scalars[0] * coefficients[288])
        named += float(scalars[1] * coefficients[289])
        named += float(scalars[2] * coefficients[290])
        named += float(scalars[3] * coefficients[291])
        vector_result = float(fixed_energy + np.dot(vector, coefficients))
        cases[name] = {
            "named_direct_energy_hartree": named,
            "vector_dot_energy_hartree": vector_result,
            "difference_hartree": float(named - vector_result),
            "coefficient_sha256": array_sha256(coefficients),
        }
    maximum = max(abs(case["difference_hartree"]) for case in cases.values())
    return {
        "passed": maximum <= IDENTITY_TOLERANCE_HARTREE,
        "tolerance_hartree": IDENTITY_TOLERANCE_HARTREE,
        "maximum_absolute_difference_hartree": maximum,
        "cases": cases,
    }


def run_scalar_stage(
    parent_dir: Path,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
) -> dict[str, Any]:
    """Compute and atomically publish scalar features from a Step-8 parent."""

    started = time.perf_counter()
    rss_start = _max_rss_mb()
    parent_dir = parent_dir.resolve()
    output_dir = output_dir.resolve()
    spec_path = spec_path.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing scalar artifact: {output_dir}")
    temp_dir = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temp_dir.exists():
        raise FileExistsError(f"refusing to reuse stale temporary directory: {temp_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir()
    scratch_dir = temp_dir / "scratch"
    scratch_dir.mkdir()
    try:
        spec = load_spec(spec_path)
        authority_hashes = validate_input_authorities(spec, spec_path)
        parent_checks, _ = validate_published_parent(parent_dir, spec_path)
        if not all(parent_checks.values()):
            failed = [name for name, passed in parent_checks.items() if not passed]
            raise ValueError(f"Step-8 parent validation failed: {failed}")

        parent_manifest_path = parent_dir / "parent_manifest.json"
        parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
        species = parent_manifest["species"]
        records = input_artifact_paths(spec)["records"]
        record, line_number = load_record(records, species)
        bridge_row = load_bridge_row(spec, species)
        validate_record(record, bridge_row)
        mol, auxmol, resolved = build_molecules(record)
        checkpoint = parent_dir / spec["orbital_source"]["checkpoint_name"]
        mf = load_checkpoint_parent(checkpoint, mol, record, spec, max_memory_mb)
        dm_a, dm_b = spin_density_matrices(mf)

        timings: dict[str, float] = {}
        mark = time.perf_counter()
        components = parent_manifest["scf"]["components"]
        short_range_hf = float(components["unscaled_short_range_hf_exchange"])
        timings["checkpoint_and_authority_validation_seconds"] = mark - started

        vv10_spec = spec["double_hybrid_energy"]["vv10"]
        nlc_grid = grid_policy(record, spec)["nonlocal"]
        vv10, nlc_points = evaluate_vv10(
            mol,
            dm_a,
            dm_b,
            nlc_grid,
            float(vv10_spec["b"]),
            float(vv10_spec["C"]),
            max_memory_mb,
        )
        timings["vv10_seconds"] = time.perf_counter() - mark

        mark = time.perf_counter()
        d4_spec = spec["double_hybrid_energy"]["dispersion_policy"]["d4_atm"]
        d4_parameters = {
            key: float(value) for key, value in d4_spec["damping_parameters"].items()
        }
        d4_atm = evaluate_d4_atm(mol, d4_parameters)
        timings["d4_atm_seconds"] = time.perf_counter() - mark

        mark = time.perf_counter()
        previous_tmpdir = lib.param.TMPDIR
        lib.param.TMPDIR = str(scratch_dir)
        try:
            pt2, scratch_peak_bytes = evaluate_ri_ump2(
                mf, mol, resolved["auxiliary_basis"], scratch_dir, max_memory_mb
            )
        finally:
            lib.param.TMPDIR = previous_tmpdir
        timings["ri_ump2_seconds"] = time.perf_counter() - mark
        if abs(pt2["component_sum_error_hartree"]) > PT2_COMPONENT_TOLERANCE_HARTREE:
            raise RuntimeError(f"RI-UMP2 spin-component identity failed: {pt2}")

        identity_grid = parent_manifest["checkpoint_roundtrip"]["feature_grid_id"]
        semilocal_path = parent_dir / f"checkpoint_identity_features_{identity_grid}.npy"
        semilocal = np.load(semilocal_path)
        vector = assemble_feature_vector(
            semilocal, short_range_hf, vv10, pt2["total_correlation_hartree"], d4_atm
        )
        np.save(temp_dir / "feature_vector_292.npy", vector)
        np.save(temp_dir / "scalar_features_288_291.npy", vector[288:])
        fixed = fixed_energy_partition(parent_manifest)
        identity = direct_energy_identity(
            fixed["total_hartree"], semilocal, tuple(float(x) for x in vector[288:])
        )
        if not identity["passed"]:
            raise RuntimeError(f"direct-energy identity failed: {identity}")

        for item in list(scratch_dir.iterdir()):
            if item.is_file():
                item.unlink()
        scratch_dir.rmdir()
        timings["total_seconds"] = time.perf_counter() - started
        artifact_names = ("feature_vector_292.npy", "scalar_features_288_291.npy")
        artifacts_sha256 = {name: sha256(temp_dir / name) for name in artifact_names}
        manifest = {
            "schema_version": 2,
            "status": "scalar_features_complete_and_validated",
            "created_utc": utc_now(),
            "species": species,
            "parent": {
                "directory": str(parent_dir),
                "manifest_sha256": sha256(parent_manifest_path),
                "checkpoint_sha256": sha256(checkpoint),
                "all_validation_checks_passed": True,
                "scf_rerun": False,
            },
            "immutable_record_line": line_number,
            "immutable_record_sha256": record["record_sha256"],
            "reference": {
                "scf_class": parent_manifest["reference"]["scf_class"],
                "post_scf_class": "UMP2",
                "charge": mol.charge,
                "spin": mol.spin,
                "electron_count": mol.nelectron,
            },
            "basis_bridge": {
                "auxiliary_resolution": resolved["auxiliary_resolution"],
                "auxiliary_definition_sha256": canonical_hash(resolved["auxiliary_basis"]),
                "auxiliary_spherical_aos": auxmol.nao_nr(),
            },
            "fixed_energy": fixed,
            "scalar_features": {
                "short_range_hf": {
                    "index": 288,
                    "energy_hartree": short_range_hf,
                    "coefficient_applied": False,
                },
                "vv10": {
                    "index": 289,
                    "energy_hartree": vv10,
                    "b": float(vv10_spec["b"]),
                    "C": float(vv10_spec["C"]),
                    "grid": nlc_grid,
                    "grid_points": nlc_points,
                    "evaluations": 1,
                    "coefficient_applied": False,
                },
                "pt2": {"index": 290, **pt2, "coefficient_applied": False},
                "d4_atm": {
                    "index": 291,
                    "energy_hartree": d4_atm,
                    "damping_parameters": d4_parameters,
                    "definition": d4_spec["definition"],
                    "coefficient_applied": False,
                },
            },
            "feature_vector": {
                "layout": SCALAR_INDICES,
                "length": FEATURE_COUNT,
                "semilocal_shape": list(semilocal.shape),
                "semilocal_rows": list(integrated_dv.SELECTED_ROWS),
                "semilocal_grid_id": identity_grid,
                "sha256": array_sha256(vector),
            },
            "grid_differences": {
                "zero_indices": [288, 289, 290, 291],
                "values_hartree": [0.0, 0.0, 0.0, 0.0],
                "reasons": {
                    "short_range_hf": "fixed parent density and orbitals; independent of semilocal feature grid",
                    "vv10": "evaluated once on the frozen nonlocal grid and reused for every semilocal grid",
                    "pt2": "fixed parent orbitals; independent of semilocal feature grid",
                    "d4_atm": "geometry/charge-only feature; independent of orbitals and grid",
                },
            },
            "direct_energy_identity": identity,
            "resource_usage": {
                "timings_seconds": timings,
                "max_rss_mb_start": rss_start,
                "max_rss_mb_end": _max_rss_mb(),
                "scratch_peak_bytes": scratch_peak_bytes,
                "scratch_retained_bytes": 0,
                "max_memory_setting_mb": max_memory_mb,
            },
            "provenance": {
                **authority_hashes,
                "scientific_specification_version": spec["scientific_specification"]["version"],
                "git_commit": git_commit(),
                "scalar_module_sha256": sha256(Path(__file__)),
                "parent_module_sha256": sha256(PROJECT_ROOT / "parent_scf.py"),
                "integrated_dv_module_sha256": sha256(PROJECT_ROOT / "integrated_dv.py"),
                "hostname": socket.gethostname(),
                "software_versions": software_versions(),
            },
            "qchem_orbitals_used": False,
            "qarchive_used": False,
            "artifacts_sha256": artifacts_sha256,
        }
        manifest_path = temp_dir / "scalar_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temp_dir / "SCALAR_COMPLETE").write_text(utc_now() + "\n", encoding="utf-8")
        temp_dir.rename(output_dir)
        return manifest
    except BaseException:
        failure = {
            "schema_version": 1,
            "status": "scalar_features_failed",
            "created_utc": utc_now(),
            "parent_dir": str(parent_dir),
            "exception": traceback.format_exc(),
        }
        (temp_dir / "FAILURE.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        raise


def validate_scalar_artifact(
    scalar_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
) -> tuple[dict[str, bool], dict[str, Any]]:
    """Independently validate a published scalar-feature artifact."""

    scalar_dir = scalar_dir.resolve()
    manifest_path = scalar_dir / "scalar_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    spec_path = spec_path.resolve()
    spec = load_spec(spec_path)
    authority_hashes = validate_input_authorities(spec, spec_path)
    parent_dir = Path(manifest["parent"]["directory"])
    parent_manifest_path = parent_dir / "parent_manifest.json"
    parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
    parent_checks, _ = validate_published_parent(parent_dir, spec_path)
    vector = np.load(scalar_dir / "feature_vector_292.npy")
    scalars = np.load(scalar_dir / "scalar_features_288_291.npy")
    fixed = fixed_energy_partition(parent_manifest)
    identity_grid = manifest["feature_vector"]["semilocal_grid_id"]
    semilocal = np.load(parent_dir / f"checkpoint_identity_features_{identity_grid}.npy")
    rebuilt = assemble_feature_vector(semilocal, *[float(x) for x in scalars])
    rebuilt_identity = direct_energy_identity(
        fixed["total_hartree"], semilocal, tuple(float(x) for x in scalars)
    )
    pt2 = manifest["scalar_features"]["pt2"]
    d4_atm = manifest["scalar_features"]["d4_atm"]
    checks = {
        "completion_marker": (scalar_dir / "SCALAR_COMPLETE").is_file(),
        "manifest_status": manifest["schema_version"] == 2
        and manifest["status"] == "scalar_features_complete_and_validated",
        "parent_validation": all(parent_checks.values()),
        "parent_manifest_hash": sha256(parent_manifest_path)
        == manifest["parent"]["manifest_sha256"],
        "parent_checkpoint_hash": sha256(
            parent_dir / spec["orbital_source"]["checkpoint_name"]
        )
        == manifest["parent"]["checkpoint_sha256"],
        "authority_hashes": all(
            manifest["provenance"][key] == value for key, value in authority_hashes.items()
        ),
        "artifact_hashes": all(
            (scalar_dir / name).is_file() and sha256(scalar_dir / name) == digest
            for name, digest in manifest["artifacts_sha256"].items()
        ),
        "feature_layout_and_values": vector.shape == (FEATURE_COUNT,)
        and scalars.shape == (4,)
        and np.array_equal(vector, rebuilt)
        and array_sha256(vector) == manifest["feature_vector"]["sha256"],
        "fixed_energy_partition": fixed == manifest["fixed_energy"],
        "pt2_spin_component_sum": abs(pt2["component_sum_error_hartree"])
        <= PT2_COMPONENT_TOLERANCE_HARTREE,
        "vv10_parameters": manifest["scalar_features"]["vv10"]["b"]
        == float(spec["double_hybrid_energy"]["vv10"]["b"])
        and manifest["scalar_features"]["vv10"]["C"]
        == float(spec["double_hybrid_energy"]["vv10"]["C"]),
        "d4_atm_definition": d4_atm["definition"]
        == spec["double_hybrid_energy"]["dispersion_policy"]["d4_atm"]["definition"]
        and d4_atm["damping_parameters"]
        == spec["double_hybrid_energy"]["dispersion_policy"]["d4_atm"]["damping_parameters"],
        "grid_difference_scalar_columns_zero": manifest["grid_differences"]["zero_indices"]
        == [288, 289, 290, 291]
        and manifest["grid_differences"]["values_hartree"] == [0.0, 0.0, 0.0, 0.0],
        "direct_energy_identity": rebuilt_identity["passed"]
        and manifest["direct_energy_identity"]["passed"],
        "checkpoint_only_no_qchem_orbitals": manifest["parent"]["scf_rerun"] is False
        and manifest["qchem_orbitals_used"] is False
        and manifest["qarchive_used"] is False,
    }
    return checks, {
        "species": manifest["species"],
        "scalar_dir": str(scalar_dir),
        "fixed_energy_hartree": fixed["total_hartree"],
        "scalar_features_hartree": {name: float(value) for name, value in zip(SCALAR_INDICES, scalars)},
        "resource_usage": manifest["resource_usage"],
        "direct_energy_identity": rebuilt_identity,
    }
