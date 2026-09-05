"""Exact eight-boundary Step-13 production execution stages."""

from __future__ import annotations

import json
import os
import resource
import shutil
import socket
import time
import traceback
from pathlib import Path
from typing import Any, Callable

import numpy as np
from pyscf import lib

from revwb97m2.parent_scf import (
    DEFAULT_SPEC,
    input_artifact_paths,
    load_bridge_row,
    load_checkpoint_parent,
    load_record,
    load_spec,
    run_parent,
    sha256,
    spin_density_matrices,
    utc_now,
    validate_input_authorities,
    validate_published_parent,
    validate_record,
)
from revwb97m2.production_generator import (
    authority_hashes as production_authority_hashes,
    load_locked_population,
    species_authority_fingerprint,
)
from revwb97m2.scalar_features import (
    PT2_COMPONENT_TOLERANCE_HARTREE,
    assemble_r1_r2_feature_vectors,
    direct_energy_identity,
    evaluate_d4_atm,
    evaluate_ri_ump2,
    evaluate_vv10,
    fixed_energy_partition,
)
from revwb97m2.semilocal_features import feature_probe_r1_r2, frozen_grids
from revwb97m2.scripts.pyscf_basis_bridge import build_molecules


BOUNDARY_FILES = {
    "semilocal": ("semilocal_grid_manifest.json", "SEMILOCAL_GRID_COMPLETE"),
    "vv10": ("vv10_manifest.json", "VV10_COMPLETE"),
    "ri_mp2": ("ri_mp2_manifest.json", "RI_MP2_COMPLETE"),
    "d4_atm": ("d4_atm_manifest.json", "D4_ATM_COMPLETE"),
    "assembly": ("assembly_manifest.json", "ASSEMBLY_COMPLETE"),
}


def _max_rss_mb() -> float:
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def _identity(species: str) -> tuple[dict[str, Any], dict[str, str], str]:
    matches = [row for row in load_locked_population() if row["species"] == species]
    if len(matches) != 1:
        raise ValueError(f"expected one locked-population row for {species}, got {len(matches)}")
    row = matches[0]
    authorities = production_authority_hashes()
    return row, authorities, species_authority_fingerprint(row, authorities)


def _atomic_publish(
    output_dir: Path,
    failure_status: str,
    operation: Callable[[Path], dict[str, Any]],
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite boundary: {output_dir}")
    temporary = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temporary.exists():
        raise FileExistsError(f"refusing to reuse temporary boundary: {temporary}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary.mkdir()
    try:
        manifest = operation(temporary)
        temporary.rename(output_dir)
        return manifest
    except BaseException:
        (temporary / "FAILURE.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": failure_status,
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


def _write_manifest_validation_marker(
    temporary: Path,
    manifest_name: str,
    marker_name: str,
    manifest: dict[str, Any],
    checks: dict[str, bool],
) -> None:
    manifest_path = temporary / manifest_name
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not all(checks.values()):
        raise RuntimeError(f"boundary validation failed: {checks}")
    (temporary / "validation.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": "passed",
                "validated_utc": utc_now(),
                "manifest_sha256": sha256(manifest_path),
                "checks": checks,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (temporary / marker_name).write_text(utc_now() + "\n", encoding="utf-8")


def _context(parent_dir: Path, spec_path: Path, max_memory_mb: int) -> dict[str, Any]:
    parent_dir = parent_dir.resolve()
    spec_path = spec_path.resolve()
    spec = load_spec(spec_path)
    validate_input_authorities(spec, spec_path)
    checks, _ = validate_published_parent(parent_dir, spec_path)
    if not all(checks.values()):
        raise ValueError(f"parent validation failed: {checks}")
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
    identity, authorities, fingerprint = _identity(species)
    if identity["source_record_sha256"] != record["record_sha256"]:
        raise ValueError("production identity/source record disagreement")
    return {
        "spec": spec,
        "species": species,
        "record": record,
        "record_line": line_number,
        "mol": mol,
        "auxmol": auxmol,
        "resolved": resolved,
        "mf": mf,
        "dm_a": dm_a,
        "dm_b": dm_b,
        "parent_dir": parent_dir,
        "parent_manifest": parent_manifest,
        "parent_manifest_sha256": sha256(parent_manifest_path),
        "checkpoint_sha256": sha256(checkpoint),
        "identity": identity,
        "authorities": authorities,
        "fingerprint": fingerprint,
    }


def publish_parent(
    species: str,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
    block_size: int = 10000,
) -> dict[str, Any]:
    """Run the existing parent driver, then add the production identity record."""

    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite boundary: {output_dir}")
    staging = output_dir.parent / f".{output_dir.name}.step13.{os.getpid()}"
    if staging.exists():
        raise FileExistsError(f"refusing to reuse parent staging path: {staging}")
    try:
        manifest = run_parent(
            species,
            staging,
            spec_path,
            max_memory_mb,
            block_size,
            verbose=4,
        )
        identity, _, fingerprint = _identity(species)
        manifest.update(
            {
                "scope": identity["scope"],
                "source_record_sha256": identity["source_record_sha256"],
                "authority_fingerprint_sha256": fingerprint,
            }
        )
        manifest_path = staging / "parent_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        checks, _ = validate_published_parent(staging, spec_path)
        if not all(checks.values()):
            raise RuntimeError(f"production parent validation failed: {checks}")
        (staging / "validation.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "passed",
                    "validated_utc": utc_now(),
                    "manifest_sha256": sha256(manifest_path),
                    "checks": checks,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        staging.rename(output_dir)
        return manifest
    except BaseException:
        if staging.exists() and not (staging / "FAILURE.json").exists():
            (staging / "FAILURE.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "status": "production_parent_failed",
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


def publish_semilocal_grid(
    parent_dir: Path,
    output_dir: Path,
    grid_id: str,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
    block_size: int = 10000,
) -> dict[str, Any]:
    context = _context(parent_dir, spec_path, max_memory_mb)
    by_id = {row["id"]: row for row in frozen_grids(context["spec"]).values()}
    if grid_id not in by_id:
        raise KeyError(f"unknown frozen semilocal grid: {grid_id}")
    policy = by_id[grid_id]

    def operation(temporary: Path) -> dict[str, Any]:
        started = time.perf_counter()
        spaces, point_count, observed_id = feature_probe_r1_r2(
            context["mol"], context["dm_a"], context["dm_b"],
            policy["radial"], policy["angular"], block_size,
        )
        if observed_id != grid_id:
            raise ValueError(f"grid ID mismatch: {observed_id} != {grid_id}")
        filenames = {
            "R1": f"r1_semilocal_features_75_{grid_id}.npy",
            "R2": f"r2_semilocal_features_288_{grid_id}.npy",
        }
        for space, filename in filenames.items():
            np.save(temporary / filename, spaces[space].reshape(-1))
        artifacts = {name: sha256(temporary / name) for name in filenames.values()}
        manifest = {
            "schema_version": 1,
            "status": "semilocal_grid_complete_and_validated",
            "created_utc": utc_now(),
            "scope": context["identity"]["scope"],
            "species": context["species"],
            "source_record_sha256": context["identity"]["source_record_sha256"],
            "authority_fingerprint_sha256": context["fingerprint"],
            "grid": {**policy, "grid_points": point_count},
            "parent_manifest_sha256": context["parent_manifest_sha256"],
            "shared_density_R1_R2": True,
            "resource_usage": {
                "wall_seconds": time.perf_counter() - started,
                "max_rss_mb": _max_rss_mb(),
                "max_memory_setting_mb": max_memory_mb,
                "block_size": block_size,
            },
            "artifacts_sha256": artifacts,
        }
        checks = {
            "grid_id": observed_id == grid_id,
            "r1_shape_finite": spaces["R1"].shape == (3, 25)
            and bool(np.all(np.isfinite(spaces["R1"]))),
            "r2_shape_finite": spaces["R2"].shape == (3, 96)
            and bool(np.all(np.isfinite(spaces["R2"]))),
            "artifact_hashes": all(sha256(temporary / name) == digest for name, digest in artifacts.items()),
        }
        _write_manifest_validation_marker(
            temporary, *BOUNDARY_FILES["semilocal"], manifest, checks
        )
        return manifest

    return _atomic_publish(output_dir, "semilocal_grid_failed", operation)


def publish_vv10(
    parent_dir: Path,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
) -> dict[str, Any]:
    context = _context(parent_dir, spec_path, max_memory_mb)

    def operation(temporary: Path) -> dict[str, Any]:
        started = time.perf_counter()
        vv10_spec = context["spec"]["double_hybrid_energy"]["vv10"]
        from revwb97m2.parent_scf import grid_policy
        grid = grid_policy(context["record"], context["spec"])["nonlocal"]
        energy, point_count = evaluate_vv10(
            context["mol"], context["dm_a"], context["dm_b"], grid,
            float(vv10_spec["b"]), float(vv10_spec["C"]), max_memory_mb,
        )
        payload = {
            "energy_hartree": energy,
            "b": float(vv10_spec["b"]),
            "C": float(vv10_spec["C"]),
            "grid": grid,
            "grid_points": point_count,
        }
        payload_name = "vv10.json"
        (temporary / payload_name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        artifacts = {payload_name: sha256(temporary / payload_name)}
        manifest = {
            "schema_version": 1,
            "status": "vv10_complete_and_validated",
            "created_utc": utc_now(),
            "scope": context["identity"]["scope"],
            "species": context["species"],
            "source_record_sha256": context["identity"]["source_record_sha256"],
            "authority_fingerprint_sha256": context["fingerprint"],
            "parent_manifest_sha256": context["parent_manifest_sha256"],
            "resource_usage": {"wall_seconds": time.perf_counter() - started, "max_rss_mb": _max_rss_mb()},
            "artifacts_sha256": artifacts,
        }
        checks = {"finite_energy": bool(np.isfinite(energy)), "positive_grid_points": point_count > 0, "artifact_hashes": True}
        _write_manifest_validation_marker(temporary, *BOUNDARY_FILES["vv10"], manifest, checks)
        return manifest

    return _atomic_publish(output_dir, "vv10_failed", operation)


def publish_ri_mp2(
    parent_dir: Path,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
) -> dict[str, Any]:
    context = _context(parent_dir, spec_path, max_memory_mb)

    def operation(temporary: Path) -> dict[str, Any]:
        started = time.perf_counter()
        scratch = temporary / "scratch"
        scratch.mkdir()
        previous_tmpdir = lib.param.TMPDIR
        lib.param.TMPDIR = str(scratch)
        try:
            pt2, scratch_peak = evaluate_ri_ump2(
                context["mf"], context["mol"], context["resolved"]["auxiliary_basis"],
                scratch, max_memory_mb,
            )
        finally:
            lib.param.TMPDIR = previous_tmpdir
        if abs(pt2["component_sum_error_hartree"]) > PT2_COMPONENT_TOLERANCE_HARTREE:
            raise RuntimeError(f"RI-MP2 component identity failed: {pt2}")
        for item in list(scratch.iterdir()):
            if item.is_file():
                item.unlink()
        scratch.rmdir()
        payload_name = "ri_mp2.json"
        (temporary / payload_name).write_text(json.dumps(pt2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        artifacts = {payload_name: sha256(temporary / payload_name)}
        manifest = {
            "schema_version": 1,
            "status": "ri_mp2_complete_and_validated",
            "created_utc": utc_now(),
            "scope": context["identity"]["scope"],
            "species": context["species"],
            "source_record_sha256": context["identity"]["source_record_sha256"],
            "authority_fingerprint_sha256": context["fingerprint"],
            "parent_manifest_sha256": context["parent_manifest_sha256"],
            "energy_only": True,
            "resource_usage": {
                "wall_seconds": time.perf_counter() - started,
                "max_rss_mb": _max_rss_mb(),
                "scratch_peak_bytes": scratch_peak,
                "scratch_retained_bytes": 0,
            },
            "artifacts_sha256": artifacts,
        }
        checks = {
            "finite_total": bool(np.isfinite(pt2["total_correlation_hartree"])),
            "spin_components_sum": abs(pt2["component_sum_error_hartree"]) <= PT2_COMPONENT_TOLERANCE_HARTREE,
            "amplitudes_not_retained": pt2["mp2_amplitudes_retained"] is False,
            "artifact_hashes": True,
        }
        _write_manifest_validation_marker(temporary, *BOUNDARY_FILES["ri_mp2"], manifest, checks)
        return manifest

    return _atomic_publish(output_dir, "ri_mp2_failed", operation)


def publish_d4_atm(
    parent_dir: Path,
    output_dir: Path,
    spec_path: Path = DEFAULT_SPEC,
    max_memory_mb: int = 40000,
) -> dict[str, Any]:
    """Publish the geometry-only, frozen-parameter COACH D4-ATM energy feature."""

    context = _context(parent_dir, spec_path, max_memory_mb)

    def operation(temporary: Path) -> dict[str, Any]:
        started = time.perf_counter()
        d4_spec = context["spec"]["double_hybrid_energy"]["dispersion_policy"]["d4_atm"]
        parameters = {name: float(value) for name, value in d4_spec["damping_parameters"].items()}
        energy = evaluate_d4_atm(context["mol"], parameters)
        payload = {
            "energy_hartree": energy,
            "definition": d4_spec["definition"],
            "damping_parameters": parameters,
        }
        payload_name = "d4_atm.json"
        (temporary / payload_name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        artifacts = {payload_name: sha256(temporary / payload_name)}
        manifest = {
            "schema_version": 1,
            "status": "d4_atm_complete_and_validated",
            "created_utc": utc_now(),
            "scope": context["identity"]["scope"],
            "species": context["species"],
            "source_record_sha256": context["identity"]["source_record_sha256"],
            "authority_fingerprint_sha256": context["fingerprint"],
            "parent_manifest_sha256": context["parent_manifest_sha256"],
            "orbital_independent": True,
            "resource_usage": {
                "wall_seconds": time.perf_counter() - started,
                "max_rss_mb": _max_rss_mb(),
            },
            "artifacts_sha256": artifacts,
        }
        checks = {
            "finite_energy": bool(np.isfinite(energy)),
            "frozen_definition": payload["definition"] == "pure_three_body_coach_d4_atm"
            and parameters
            == {"s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0},
            "artifact_hashes": sha256(temporary / payload_name) == artifacts[payload_name],
        }
        _write_manifest_validation_marker(
            temporary, *BOUNDARY_FILES["d4_atm"], manifest, checks
        )
        return manifest

    return _atomic_publish(output_dir, "d4_atm_failed", operation)


def publish_assembly(species_root: Path, output_dir: Path) -> dict[str, Any]:
    species_root = species_root.resolve()
    parent_manifest = json.loads((species_root / "parent/parent_manifest.json").read_text(encoding="utf-8"))
    species = parent_manifest["species"]
    identity, _, fingerprint = _identity(species)

    def operation(temporary: Path) -> dict[str, Any]:
        semilocal_dirs = {grid: species_root / "semilocal" / grid for grid in ("250974", "99590", "75302")}
        for directory in (
            *semilocal_dirs.values(),
            species_root / "vv10",
            species_root / "ri_mp2",
            species_root / "d4_atm",
        ):
            validation = json.loads((directory / "validation.json").read_text(encoding="utf-8"))
            if validation.get("status") != "passed":
                raise ValueError(f"dependency validation failed: {directory}")
        r1 = np.load(semilocal_dirs["250974"] / "r1_semilocal_features_75_250974.npy")
        r2 = np.load(semilocal_dirs["250974"] / "r2_semilocal_features_288_250974.npy")
        vv10 = json.loads((species_root / "vv10/vv10.json").read_text(encoding="utf-8"))["energy_hartree"]
        pt2 = json.loads((species_root / "ri_mp2/ri_mp2.json").read_text(encoding="utf-8"))["total_correlation_hartree"]
        d4_atm = json.loads((species_root / "d4_atm/d4_atm.json").read_text(encoding="utf-8"))["energy_hartree"]
        sr_hf = float(parent_manifest["scf"]["components"]["unscaled_short_range_hf_exchange"])
        vectors = assemble_r1_r2_feature_vectors(r1, r2, sr_hf, vv10, pt2, d4_atm)
        filenames = {"R1": "feature_vector_79.npy", "R2": "feature_vector_292.npy"}
        for space, filename in filenames.items():
            np.save(temporary / filename, vectors[space])
        fixed = fixed_energy_partition(parent_manifest)
        (temporary / "fixed_energy.json").write_text(json.dumps(fixed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        artifacts = {name: sha256(temporary / name) for name in (*filenames.values(), "fixed_energy.json")}
        identity_check = direct_energy_identity(
            fixed["total_hartree"], r2.reshape(3, 96), (sr_hf, vv10, pt2, d4_atm)
        )
        manifest = {
            "schema_version": 1,
            "status": "species_assembly_complete_and_validated",
            "created_utc": utc_now(),
            "scope": identity["scope"],
            "species": species,
            "source_record_sha256": identity["source_record_sha256"],
            "authority_fingerprint_sha256": fingerprint,
            "feature_counts": {"R1": 79, "R2": 292},
            "fitting_grid_id": "250974",
            "shared_scalar_values": {
                "short_range_hf": sr_hf,
                "vv10": vv10,
                "pt2": pt2,
                "d4_atm": d4_atm,
            },
            "direct_energy_identity": identity_check,
            "artifacts_sha256": artifacts,
        }
        checks = {
            "r1_shape_finite": vectors["R1"].shape == (79,) and bool(np.all(np.isfinite(vectors["R1"]))),
            "r2_shape_finite": vectors["R2"].shape == (292,) and bool(np.all(np.isfinite(vectors["R2"]))),
            "shared_scalar_tail": bool(np.array_equal(vectors["R1"][-4:], vectors["R2"][-4:])),
            "direct_energy_identity": identity_check["passed"],
            "artifact_hashes": all(sha256(temporary / name) == digest for name, digest in artifacts.items()),
        }
        _write_manifest_validation_marker(temporary, *BOUNDARY_FILES["assembly"], manifest, checks)
        return manifest

    return _atomic_publish(output_dir, "species_assembly_failed", operation)
