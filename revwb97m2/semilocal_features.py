"""Three-grid selected semilocal features from validated parent checkpoints."""

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

from revwb97m2 import integrated_dv
from revwb97m2.parent_scf import (
    DEFAULT_SPEC,
    PROJECT_ROOT,
    array_sha256,
    git_commit,
    input_artifact_paths,
    load_bridge_row,
    load_checkpoint_parent,
    load_record,
    load_spec,
    sha256,
    software_versions,
    spin_density_matrices,
    utc_now,
    validate_input_authorities,
    validate_published_parent,
    validate_record,
    feature_probe,
)
from revwb97m2.scripts.pyscf_basis_bridge import build_molecules, canonical_hash


GRID_ORDER = ("fitting_reference", "practical", "coarse_analysis")
INDEPENDENT_FEATURE_TOLERANCE = 1.0e-12


def _max_rss_mb() -> float:
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def frozen_grids(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    policy = spec["coach_feature_grids"]
    grids: dict[str, dict[str, Any]] = {}
    for name in GRID_ORDER:
        entry = policy[name]
        grids[name] = {
            "id": str(entry["id"]),
            "radial": int(entry["radial"]),
            "angular": int(entry["angular"]),
            "pruning": policy["pruning"],
            "radii_adjustment": policy["radii_adjustment"],
        }
    return grids


def evaluate_three_grids(
    mol: Any,
    dm_a: np.ndarray,
    dm_b: np.ndarray,
    grids: dict[str, dict[str, Any]],
    block_size: int,
) -> tuple[dict[str, np.ndarray], dict[str, dict[str, Any]]]:
    matrices: dict[str, np.ndarray] = {}
    measurements: dict[str, dict[str, Any]] = {}
    for name in GRID_ORDER:
        policy = grids[name]
        started = time.perf_counter()
        rss_before = _max_rss_mb()
        matrix, point_count, grid_id = feature_probe(
            mol,
            dm_a,
            dm_b,
            policy["radial"],
            policy["angular"],
            block_size,
        )
        if grid_id != policy["id"]:
            raise ValueError(f"grid ID mismatch for {name}: {grid_id} != {policy['id']}")
        if matrix.shape != (3, 96) or not np.all(np.isfinite(matrix)):
            raise FloatingPointError(f"invalid selected feature matrix on grid {name}")
        matrices[name] = matrix
        measurements[name] = {
            **policy,
            "grid_points": point_count,
            "wall_seconds": time.perf_counter() - started,
            "max_rss_mb_before": rss_before,
            "max_rss_mb_after": _max_rss_mb(),
            "array_sha256": array_sha256(matrix),
        }
    return matrices, measurements


def grid_differences(matrices: dict[str, np.ndarray]) -> dict[str, Any]:
    reference = matrices["fitting_reference"]
    comparisons: dict[str, Any] = {}
    for name in ("practical", "coarse_analysis"):
        difference = matrices[name] - reference
        comparisons[name] = {
            "comparison_minus_reference_max_abs_hartree": float(np.max(np.abs(difference))),
            "comparison_minus_reference_l1_hartree": float(np.sum(np.abs(difference))),
            "comparison_minus_reference_array_sha256": array_sha256(difference),
        }
    return comparisons


def run_semilocal_stage(
    parent_dir: Path,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
    block_size: int = 10000,
) -> dict[str, Any]:
    """Evaluate and atomically publish all three selected COACH feature grids."""

    total_started = time.perf_counter()
    parent_dir = parent_dir.resolve()
    output_dir = output_dir.resolve()
    spec_path = spec_path.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing semilocal artifact: {output_dir}")
    temp_dir = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temp_dir.exists():
        raise FileExistsError(f"refusing to reuse stale temporary directory: {temp_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir()
    try:
        validation_started = time.perf_counter()
        spec = load_spec(spec_path)
        authority_hashes = validate_input_authorities(spec, spec_path)
        parent_checks, _ = validate_published_parent(parent_dir, spec_path)
        if not all(parent_checks.values()):
            failed = [name for name, passed in parent_checks.items() if not passed]
            raise ValueError(f"Step-8 parent validation failed: {failed}")
        parent_manifest_path = parent_dir / "parent_manifest.json"
        parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
        species = parent_manifest["species"]
        record, line_number = load_record(input_artifact_paths(spec)["records"], species)
        bridge_row = load_bridge_row(spec, species)
        validate_record(record, bridge_row)
        mol, auxmol, resolved = build_molecules(record)
        checkpoint = parent_dir / spec["orbital_source"]["checkpoint_name"]
        mf = load_checkpoint_parent(checkpoint, mol, record, spec, max_memory_mb)
        dm_a, dm_b = spin_density_matrices(mf)
        validation_seconds = time.perf_counter() - validation_started

        grids = frozen_grids(spec)
        matrices, measurements = evaluate_three_grids(
            mol, dm_a, dm_b, grids, block_size
        )
        artifact_names: list[str] = []
        for name in GRID_ORDER:
            filename = f"selected_features_{grids[name]['id']}.npy"
            np.save(temp_dir / filename, matrices[name])
            artifact_names.append(filename)
        artifacts_sha256 = {name: sha256(temp_dir / name) for name in artifact_names}
        manifest = {
            "schema_version": 1,
            "status": "three_grid_semilocal_features_complete_and_validated",
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
            "reference": parent_manifest["reference"],
            "basis_bridge": {
                "orbital_definition_sha256": canonical_hash(resolved["orbital_basis"]),
                "ecp_definition_sha256": canonical_hash(resolved["ecp"]),
                "auxiliary_definition_sha256": canonical_hash(resolved["auxiliary_basis"]),
                "orbital_spherical_aos": mol.nao_nr(),
                "auxiliary_spherical_aos": auxmol.nao_nr(),
            },
            "kernel": integrated_dv.kernel_metadata(),
            "selected_rows": list(integrated_dv.SELECTED_ROWS),
            "matrix_shape_per_grid": [3, 96],
            "grids": measurements,
            "grid_differences": grid_differences(matrices),
            "resource_usage": {
                "authority_and_parent_validation_seconds": validation_seconds,
                "total_seconds": time.perf_counter() - total_started,
                "max_rss_mb": _max_rss_mb(),
                "scratch_bytes": 0,
                "max_memory_setting_mb": max_memory_mb,
                "block_size": block_size,
            },
            "provenance": {
                **authority_hashes,
                "scientific_specification_version": spec["scientific_specification"]["version"],
                "git_commit": git_commit(),
                "semilocal_module_sha256": sha256(Path(__file__)),
                "parent_module_sha256": sha256(PROJECT_ROOT / "parent_scf.py"),
                "integrated_dv_module_sha256": sha256(PROJECT_ROOT / "integrated_dv.py"),
                "hostname": socket.gethostname(),
                "software_versions": software_versions(),
            },
            "qchem_orbitals_used": False,
            "qarchive_used": False,
            "artifacts_sha256": artifacts_sha256,
        }
        (temp_dir / "semilocal_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temp_dir / "SEMILOCAL_COMPLETE").write_text(utc_now() + "\n", encoding="utf-8")
        temp_dir.rename(output_dir)
        return manifest
    except BaseException:
        failure = {
            "schema_version": 1,
            "status": "three_grid_semilocal_features_failed",
            "created_utc": utc_now(),
            "parent_dir": str(parent_dir),
            "exception": traceback.format_exc(),
        }
        (temp_dir / "FAILURE.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        raise


def validate_semilocal_artifact(
    semilocal_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
    block_size: int = 10000,
) -> tuple[dict[str, bool], dict[str, Any]]:
    """Independently recompute and validate all three selected matrices."""

    semilocal_dir = semilocal_dir.resolve()
    spec_path = spec_path.resolve()
    manifest = json.loads((semilocal_dir / "semilocal_manifest.json").read_text(encoding="utf-8"))
    spec = load_spec(spec_path)
    authority_hashes = validate_input_authorities(spec, spec_path)
    parent_dir = Path(manifest["parent"]["directory"])
    parent_manifest_path = parent_dir / "parent_manifest.json"
    parent_manifest = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
    parent_checks, _ = validate_published_parent(parent_dir, spec_path)
    record, _ = load_record(input_artifact_paths(spec)["records"], manifest["species"])
    bridge_row = load_bridge_row(spec, manifest["species"])
    validate_record(record, bridge_row)
    mol, _, _ = build_molecules(record)
    checkpoint = parent_dir / spec["orbital_source"]["checkpoint_name"]
    mf = load_checkpoint_parent(checkpoint, mol, record, spec, max_memory_mb)
    dm_a, dm_b = spin_density_matrices(mf)
    grids = frozen_grids(spec)
    recomputed, measurements = evaluate_three_grids(
        mol, dm_a, dm_b, grids, block_size
    )
    maximum_differences: dict[str, float] = {}
    arrays_match = True
    for name in GRID_ORDER:
        stored = np.load(semilocal_dir / f"selected_features_{grids[name]['id']}.npy")
        difference = float(np.max(np.abs(stored - recomputed[name])))
        maximum_differences[name] = difference
        arrays_match = arrays_match and difference <= INDEPENDENT_FEATURE_TOLERANCE
    checks = {
        "completion_marker": (semilocal_dir / "SEMILOCAL_COMPLETE").is_file(),
        "manifest_status": manifest["status"]
        == "three_grid_semilocal_features_complete_and_validated",
        "parent_validation": all(parent_checks.values()),
        "parent_hashes": sha256(parent_manifest_path) == manifest["parent"]["manifest_sha256"]
        and sha256(checkpoint) == manifest["parent"]["checkpoint_sha256"],
        "authority_hashes": all(
            manifest["provenance"][key] == value for key, value in authority_hashes.items()
        ),
        "artifact_hashes": all(
            (semilocal_dir / name).is_file() and sha256(semilocal_dir / name) == digest
            for name, digest in manifest["artifacts_sha256"].items()
        ),
        "selected_rows_and_shape": manifest["selected_rows"] == [64, 154, 166]
        and manifest["matrix_shape_per_grid"] == [3, 96],
        "all_three_grid_policies": all(
            all(manifest["grids"][name][key] == value for key, value in grids[name].items())
            for name in GRID_ORDER
        ),
        "all_three_matrices_independently_reproduced": arrays_match,
        "grid_point_counts_reproduced": all(
            measurements[name]["grid_points"] == manifest["grids"][name]["grid_points"]
            for name in GRID_ORDER
        ),
        "checkpoint_only_no_qchem_orbitals": manifest["parent"]["scf_rerun"] is False
        and manifest["qchem_orbitals_used"] is False
        and manifest["qarchive_used"] is False,
    }
    return checks, {
        "species": manifest["species"],
        "semilocal_dir": str(semilocal_dir),
        "maximum_absolute_differences": maximum_differences,
        "independent_tolerance": INDEPENDENT_FEATURE_TOLERANCE,
        "grid_points": {name: measurements[name]["grid_points"] for name in GRID_ORDER},
        "resource_usage": manifest["resource_usage"],
    }
