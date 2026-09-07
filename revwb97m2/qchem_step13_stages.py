"""Immutable Step-13 boundaries backed by validated Q-Chem gateway artifacts.

This adapter does not run an SCF calculation or Q-Chem.  It promotes already
validated Q4 integratedDV and Step-9 scalar artifacts into the eight-boundary
Step-13 layout and assembles the active 292-feature R2 vector.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

from revwb97m2.qchem_feature_publisher import (
    ARTIFACTS as Q4_ARTIFACTS,
    MANIFEST_NAME as Q4_MANIFEST,
    validate_published_artifact,
)


GRIDS = ("250974", "99590", "75302")
BOUNDARY_CONTRACTS = {
    "qchem_archive": ("qchem_archive_manifest.json", "QCHEM_ARCHIVE_COMPLETE", "qchem_archive_complete_and_validated"),
    **{
        f"integrated_dv_{grid}": ("integrated_dv_manifest.json", "INTEGRATED_DV_COMPLETE", "integrated_dv_complete_and_validated")
        for grid in GRIDS
    },
    "vv10": ("vv10_manifest.json", "VV10_COMPLETE", "vv10_complete_and_validated"),
    "ri_mp2": ("ri_mp2_manifest.json", "RI_MP2_COMPLETE", "ri_mp2_complete_and_validated"),
    "d4_atm": ("d4_atm_manifest.json", "D4_ATM_COMPLETE", "d4_atm_complete_and_validated"),
    "assembly": ("assembly_manifest.json", "ASSEMBLY_COMPLETE", "species_assembly_complete_and_validated"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def authority_fingerprint(identity: dict[str, str], authorities: dict[str, str]) -> str:
    return canonical_sha256({"identity": identity, "authorities": authorities})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _publish(
    output_dir: Path,
    boundary: str,
    identity: dict[str, str],
    fingerprint: str,
    operation: Callable[[Path], tuple[dict[str, Any], dict[str, bool]]],
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        report = validate_boundary(output_dir, boundary, identity, fingerprint)
        if report["passed"]:
            return {"action": "reused", **report["manifest"]}
        raise RuntimeError(f"existing Step-13 boundary is not reusable: {output_dir}: {report['checks']}")
    temporary = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temporary.exists():
        raise FileExistsError(f"interrupted temporary boundary requires review: {temporary}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary.mkdir()
    manifest_name, marker_name, status = BOUNDARY_CONTRACTS[boundary]
    try:
        body, checks = operation(temporary)
        artifacts = {
            str(path.relative_to(temporary)): sha256(path)
            for path in sorted(temporary.rglob("*"))
            if path.is_file()
        }
        manifest = {
            "schema_version": 1,
            "status": status,
            "created_utc": utc_now(),
            **identity,
            "authority_fingerprint_sha256": fingerprint,
            **body,
            "artifacts_sha256": artifacts,
        }
        manifest_path = temporary / manifest_name
        _write_json(manifest_path, manifest)
        validation = {
            "schema_version": 1,
            "status": "passed" if checks and all(checks.values()) else "failed",
            "validated_utc": utc_now(),
            "manifest_sha256": sha256(manifest_path),
            "checks": checks,
        }
        _write_json(temporary / "validation.json", validation)
        if validation["status"] != "passed":
            raise RuntimeError(f"staged {boundary} validation failed: {checks}")
        (temporary / marker_name).write_text(utc_now() + "\n", encoding="utf-8")
        temporary.rename(output_dir)
        report = validate_boundary(output_dir, boundary, identity, fingerprint)
        if not report["passed"]:
            raise RuntimeError(f"published {boundary} failed independent validation: {report['checks']}")
        return {"action": "published", **manifest}
    except BaseException:
        if temporary.is_dir():
            _write_json(temporary / "FAILURE.json", {"status": f"{boundary}_failed", "created_utc": utc_now()})
        raise


def validate_boundary(
    output_dir: Path,
    boundary: str,
    identity: dict[str, str],
    fingerprint: str,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    manifest_name, marker_name, status = BOUNDARY_CONTRACTS[boundary]
    manifest_path = output_dir / manifest_name
    validation_path = output_dir / "validation.json"
    checks = {
        "directory": output_dir.is_dir(),
        "manifest": manifest_path.is_file(),
        "validation": validation_path.is_file(),
        "marker": (output_dir / marker_name).is_file(),
    }
    if not all(checks.values()):
        return {"passed": False, "checks": checks, "manifest": {}}
    try:
        manifest = _load_json(manifest_path)
        validation = _load_json(validation_path)
        checks.update({
            "status": manifest.get("status") == status,
            "identity": all(manifest.get(key) == value for key, value in identity.items()),
            "authority": manifest.get("authority_fingerprint_sha256") == fingerprint,
            "manifest_hash": validation.get("status") == "passed" and validation.get("manifest_sha256") == sha256(manifest_path),
            "artifact_hashes": bool(manifest.get("artifacts_sha256")) and all(
                (output_dir / name).is_file() and sha256(output_dir / name) == digest
                for name, digest in manifest.get("artifacts_sha256", {}).items()
            ),
        })
    except Exception:
        checks["load"] = False
        manifest = {}
    return {"passed": all(checks.values()), "checks": checks, "manifest": manifest}


def _validated_sources(q4_dirs: dict[str, Path], scalar_dir: Path, species: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if set(q4_dirs) != set(GRIDS):
        raise ValueError(f"Q4 sources must contain exactly {GRIDS}")
    q4 = {}
    for grid, directory in q4_dirs.items():
        checks, details = validate_published_artifact(directory)
        if not checks or not all(checks.values()):
            raise RuntimeError(f"Q4 source failed validation for {species}/{grid}: {checks}")
        manifest = details["manifest"]
        if manifest["species"] != species or manifest["grid"] != grid:
            raise ValueError(f"Q4 source identity mismatch for {species}/{grid}")
        q4[grid] = manifest
    scalar = _load_json(scalar_dir / "scalar_manifest.json")
    if scalar.get("status") != "qchem_same_archive_scalar_features_complete_and_validated" or scalar.get("species") != species:
        raise ValueError(f"Step-9 scalar source identity/status mismatch for {species}")
    if not (scalar_dir / "SCALAR_COMPLETE").is_file():
        raise FileNotFoundError(f"Step-9 scalar completion marker missing: {scalar_dir}")
    input_hashes = {
        _load_json(Path(manifest["source"]["prepared_path"]))["authoritative_input_sha256"]
        for manifest in q4.values()
    }
    input_hashes.add(scalar["source"]["authoritative_input_sha256"])
    archive_hashes = {manifest["source"]["qarchive_sha256"] for manifest in q4.values()}
    archive_hashes.add(scalar["source"]["qarchive_sha256"])
    if len(input_hashes) != 1 or len(archive_hashes) != 1:
        raise ValueError(f"Q4/Step-9 sources do not share input/archive identity for {species}")
    return q4, scalar


def publish_species_from_validated_gateway(
    *,
    identity: dict[str, str],
    authorities: dict[str, str],
    q4_dirs: dict[str, Path],
    scalar_dir: Path,
    species_root: Path,
) -> dict[str, Any]:
    """Promote one validated Q4+Step-9 case through all eight boundaries."""

    species = identity["species"]
    q4, scalar = _validated_sources(q4_dirs, scalar_dir, species)
    fingerprint = authority_fingerprint(identity, authorities)
    results: dict[str, Any] = {}
    archive_hash = scalar["source"]["qarchive_sha256"]
    input_hash = scalar["source"]["authoritative_input_sha256"]

    def archive_operation(temp: Path) -> tuple[dict[str, Any], dict[str, bool]]:
        payload = {
            "qarchive_sha256": archive_hash,
            "authoritative_input_sha256": input_hash,
            "q4_manifest_sha256_by_grid": {grid: sha256(q4_dirs[grid] / Q4_MANIFEST) for grid in GRIDS},
            "step9_scalar_manifest_sha256": sha256(scalar_dir / "scalar_manifest.json"),
        }
        _write_json(temp / "archive_identity.json", payload)
        return ({"archive_identity": payload, "promotion_only_no_qchem_execution": True}, {"shared_input": True, "shared_qarchive": True})

    results["qchem_archive"] = _publish(species_root / "qchem_archive", "qchem_archive", identity, fingerprint, archive_operation)

    for grid in GRIDS:
        boundary = f"integrated_dv_{grid}"

        def grid_operation(temp: Path, grid: str = grid) -> tuple[dict[str, Any], dict[str, bool]]:
            for filename in Q4_ARTIFACTS.values():
                shutil.copy2(q4_dirs[grid] / filename, temp / filename)
            vector = np.load(temp / Q4_ARTIFACTS["flattened"], allow_pickle=False)
            return ({
                "grid": grid,
                "qchem_archive_manifest_sha256": sha256(species_root / "qchem_archive/qchem_archive_manifest.json"),
                "source_q4_manifest_sha256": sha256(q4_dirs[grid] / Q4_MANIFEST),
                "qarchive_sha256": archive_hash,
            }, {"shape_288": vector.shape == (288,), "finite": bool(np.isfinite(vector).all())})

        results[boundary] = _publish(species_root / boundary, boundary, identity, fingerprint, grid_operation)

    values = scalar["values_hartree"]
    scalar_specs = {
        "vv10": ("vv10.json", {"energy_hartree": values["vv10_hartree"], "short_range_hf_hartree": values["short_range_hf_hartree"]}),
        "ri_mp2": ("ri_mp2.json", {"total_correlation_hartree": values["pt2_total_hartree"], "same_spin_hartree": values["pt2_same_spin_hartree"], "opposite_spin_hartree": values["pt2_opposite_spin_hartree"]}),
        "d4_atm": ("d4_atm.json", {"energy_hartree": values["d4_atm_hartree"], "definition": "pure_three_body_coach_d4_atm"}),
    }
    for boundary, (filename, payload) in scalar_specs.items():

        def scalar_operation(temp: Path, filename: str = filename, payload: dict[str, Any] = payload) -> tuple[dict[str, Any], dict[str, bool]]:
            _write_json(temp / filename, payload)
            finite = all(np.isfinite(value) for value in payload.values() if isinstance(value, float))
            component = payload.get("total_correlation_hartree", 0.0) - payload.get("same_spin_hartree", 0.0) - payload.get("opposite_spin_hartree", 0.0)
            return ({"source_step9_scalar_manifest_sha256": sha256(scalar_dir / "scalar_manifest.json"), "qarchive_sha256": archive_hash}, {"finite": finite, "pt2_component_sum": abs(component) <= 1.0e-10})

        results[boundary] = _publish(species_root / boundary, boundary, identity, fingerprint, scalar_operation)

    def assembly_operation(temp: Path) -> tuple[dict[str, Any], dict[str, bool]]:
        grids = {
            grid: np.load(species_root / f"integrated_dv_{grid}" / Q4_ARTIFACTS["flattened"], allow_pickle=False)
            for grid in GRIDS
        }
        vv10 = _load_json(species_root / "vv10/vv10.json")
        pt2 = _load_json(species_root / "ri_mp2/ri_mp2.json")
        d4 = _load_json(species_root / "d4_atm/d4_atm.json")
        tail = np.asarray([vv10["short_range_hf_hartree"], vv10["energy_hartree"], pt2["total_correlation_hartree"], d4["energy_hartree"]], dtype=np.float64)
        vector = np.concatenate((grids["250974"], tail))
        np.save(temp / "feature_vector_292.npy", vector, allow_pickle=False)
        deltas = {
            grid: {"max_abs_hartree": float(np.max(np.abs(grids[grid] - grids["250974"]))), "l2_hartree": float(np.linalg.norm(grids[grid] - grids["250974"]))}
            for grid in ("99590", "75302")
        }
        _write_json(temp / "grid_differences.json", deltas)
        dependencies = {name: sha256(species_root / name / BOUNDARY_CONTRACTS[name][0]) for name in BOUNDARY_CONTRACTS if name != "assembly"}
        return ({
            "model": "R2_coachform_292",
            "feature_count": 292,
            "fitting_grid": "250974",
            "shared_scalar_values": {"short_range_hf": float(tail[0]), "vv10": float(tail[1]), "pt2": float(tail[2]), "d4_atm": float(tail[3])},
            "dependency_manifest_sha256": dependencies,
        }, {"shape_292": vector.shape == (292,), "finite": bool(np.isfinite(vector).all()), "semilocal_prefix": bool(np.array_equal(vector[:288], grids["250974"])), "scalar_tail": bool(np.array_equal(vector[288:], tail))})

    results["assembly"] = _publish(species_root / "assembly", "assembly", identity, fingerprint, assembly_operation)
    return {"species": species, "authority_fingerprint_sha256": fingerprint, "boundaries": results}
