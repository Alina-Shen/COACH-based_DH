"""Strict extraction and immutable publication of Q-Chem integratedDV features."""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


PRINTED_SHAPE = (96, 180)
STORED_SHAPE = (180, 96)
SELECTED_ROWS = (64, 154, 166)
SELECTED_SHAPE = (3, 96)
BEGIN_PATTERN = re.compile(r"COACH integratedDV begin rows=(\d+) cols=(\d+)")
BEGIN_TOKEN = "COACH integratedDV begin"
END_TOKEN = "COACH integratedDV end"
NORMAL_TERMINATION = "Thank you very much for using Q-Chem"
ARCHIVE_READ = "Reading MOs from coefficient file"
GRID_VALUES = {
    "250974": "000250000974",
    "99590": "000099000590",
    "75302": "000075000302",
}
ARTIFACTS = {
    "full": "integrated_dv_180x96.npy",
    "selected": "selected_features_3x96.npy",
    "flattened": "semilocal_features_288.npy",
}
MANIFEST_NAME = "qchem_integrated_dv_manifest.json"
VALIDATION_NAME = "validation.json"
COMPLETION_MARKER = "QCHEM_INTEGRATED_DV_COMPLETE"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_regular_nonempty(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"{label} must be a regular nonempty file: {path}")


def _tree_hash(records: list[dict[str, Any]], relative: str, label: str) -> str:
    matches = [row for row in records if row.get("path") == relative]
    if len(matches) != 1 or not re.fullmatch(r"[0-9a-f]{64}", str(matches[0].get("sha256", ""))):
        raise ValueError(f"{label} must contain exactly one hash-pinned {relative}")
    return str(matches[0]["sha256"])


def parse_integrated_dv_output(path: Path) -> tuple[np.ndarray, int]:
    """Return the final valid complete 96x180 block and total complete count.

    Any malformed, nested, unmatched, non-finite, or truncated marked block is
    rejected. Unmarked Q-Chem text is ignored.
    """

    _require_regular_nonempty(path, "Q-Chem output")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks: list[np.ndarray] = []
    body: list[str] | None = None
    for line_number, line in enumerate(lines, start=1):
        if BEGIN_TOKEN in line:
            if body is not None:
                raise ValueError(f"nested integratedDV begin marker at line {line_number}")
            match = BEGIN_PATTERN.search(line)
            if match is None:
                raise ValueError(f"malformed integratedDV begin marker at line {line_number}")
            declared = (int(match.group(1)), int(match.group(2)))
            if declared != PRINTED_SHAPE:
                raise ValueError(f"wrong declared integratedDV shape {declared} at line {line_number}")
            body = []
            continue
        if END_TOKEN in line:
            if body is None:
                raise ValueError(f"unmatched integratedDV end marker at line {line_number}")
            if not body or body[0].strip() != "integratedDV":
                raise ValueError("integratedDV block has missing or wrong label")
            rows = body[1:]
            if len(rows) != PRINTED_SHAPE[0]:
                raise ValueError(f"wrong integratedDV row count: {len(rows)}")
            try:
                values = [[float(value) for value in row.split()] for row in rows]
            except ValueError as exc:
                raise ValueError("integratedDV block contains a nonnumeric value") from exc
            if any(len(row) != PRINTED_SHAPE[1] for row in values):
                raise ValueError("integratedDV block has a wrong column count")
            matrix = np.asarray(values, dtype=np.float64)
            if matrix.shape != PRINTED_SHAPE:
                raise ValueError(f"wrong integratedDV matrix shape: {matrix.shape}")
            if not np.isfinite(matrix).all():
                raise FloatingPointError("integratedDV block contains non-finite values")
            blocks.append(matrix)
            body = None
            continue
        if body is not None:
            body.append(line)
    if body is not None:
        raise ValueError("truncated integratedDV block: begin marker has no end marker")
    if not blocks:
        raise ValueError("no complete integratedDV block")
    return blocks[-1], len(blocks)


def _required_rem_control(text: str, key: str, expected: str) -> bool:
    pattern = re.compile(rf"(?im)^\s*{re.escape(key)}\s*(?:=\s*)?{re.escape(expected)}\s*$")
    return len(pattern.findall(text)) == 1


def validate_case_source(case_root: Path) -> dict[str, Any]:
    """Validate the immutable input/archive and completed Q-Chem source run."""

    case_root = case_root.resolve()
    prepared_path = case_root / "PREPARED.json"
    input_path = case_root / "input.q3.in"
    authoritative_copy = case_root / "input.authoritative.in"
    output_path = case_root / "qchem.out"
    for path, label in (
        (prepared_path, "preparation record"),
        (input_path, "derived Q-Chem input"),
        (authoritative_copy, "authoritative input copy"),
        (output_path, "Q-Chem output"),
    ):
        _require_regular_nonempty(path, label)
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    required_keys = {
        "species", "role", "grid", "source_orbital_root", "source_tree",
        "copy_tree", "source_copy_tree_identity", "authoritative_input_sha256",
        "derived_input_sha256",
    }
    missing = sorted(required_keys - prepared.keys())
    if missing:
        raise ValueError(f"PREPARED.json is missing keys: {missing}")
    if prepared["source_copy_tree_identity"] is not True:
        raise ValueError("preparation did not establish source/copy tree identity")
    if Path(prepared.get("case_root", "")).resolve() != case_root:
        raise ValueError("PREPARED.json case_root does not match requested case")
    grid = str(prepared["grid"])
    if grid not in GRID_VALUES:
        raise ValueError(f"unsupported integratedDV grid: {grid}")

    source_qarchive = Path(prepared["source_orbital_root"]).resolve() / "qarchive.h5"
    copied_archives = sorted((case_root / "qcscratch").glob("*/qarchive.h5"))
    if len(copied_archives) != 1:
        raise ValueError(f"expected one isolated copied qarchive.h5, found {len(copied_archives)}")
    copied_qarchive = copied_archives[0]
    _require_regular_nonempty(source_qarchive, "authoritative qarchive")
    _require_regular_nonempty(copied_qarchive, "isolated copied qarchive")
    source_record_hash = _tree_hash(prepared["source_tree"], "qarchive.h5", "source_tree")
    copy_record_hash = _tree_hash(prepared["copy_tree"], "qarchive.h5", "copy_tree")
    source_hash = sha256(source_qarchive)
    copy_hash = sha256(copied_qarchive)
    if len({source_record_hash, copy_record_hash, source_hash, copy_hash}) != 1:
        raise ValueError("authoritative or copied qarchive hash changed")
    if sha256(authoritative_copy) != prepared["authoritative_input_sha256"]:
        raise ValueError("authoritative input copy hash changed")
    if sha256(input_path) != prepared["derived_input_sha256"]:
        raise ValueError("derived Q-Chem input hash changed")

    input_text = input_path.read_text(encoding="utf-8", errors="strict")
    controls = {
        "method_wb97m_v": _required_rem_control(input_text, "METHOD", "wB97M-V"),
        "unrestricted_true": _required_rem_control(input_text, "UNRESTRICTED", "TRUE"),
        "scf_guess_read": _required_rem_control(input_text, "SCF_GUESS", "READ"),
        "maximum_scf_cycles_zero": _required_rem_control(input_text, "MAX_SCF_CYCLES", "0"),
        "gen_scfman_false": _required_rem_control(input_text, "GEN_SCFMAN", "FALSE"),
        "xc_fxc_libks": _required_rem_control(input_text, "XC_FXC", "3"),
        "grid_matches_record": _required_rem_control(input_text, "XC_GRID", GRID_VALUES[grid]),
    }
    if not all(controls.values()):
        raise ValueError(f"derived Q-Chem input control check failed: {controls}")
    output_text = output_path.read_text(encoding="utf-8", errors="replace")
    if output_text.count(ARCHIVE_READ) < 2:
        raise ValueError("Q-Chem output lacks alpha/beta MO archive-read evidence")
    if NORMAL_TERMINATION not in output_text:
        raise ValueError("Q-Chem output lacks normal termination")
    return {
        "case_root": str(case_root),
        "species": str(prepared["species"]),
        "role": str(prepared["role"]),
        "grid": grid,
        "prepared_path": str(prepared_path),
        "prepared_sha256": sha256(prepared_path),
        "derived_input_path": str(input_path),
        "derived_input_sha256": sha256(input_path),
        "qchem_output_path": str(output_path),
        "qchem_output_sha256": sha256(output_path),
        "source_qarchive_path": str(source_qarchive),
        "copied_qarchive_path": str(copied_qarchive),
        "qarchive_sha256": source_hash,
        "archive_read_message_count": output_text.count(ARCHIVE_READ),
        "normal_qchem_termination": True,
        "input_controls": controls,
    }


def validate_published_artifact(
    output_dir: Path, expected_case_root: Path | None = None
) -> tuple[dict[str, bool], dict[str, Any]]:
    """Independently validate a published Q-Chem integratedDV boundary."""

    output_dir = output_dir.resolve()
    manifest_path = output_dir / MANIFEST_NAME
    validation_path = output_dir / VALIDATION_NAME
    marker_path = output_dir / COMPLETION_MARKER
    checks: dict[str, bool] = {
        "output_directory": output_dir.is_dir(),
        "manifest_present": manifest_path.is_file(),
        "validation_present": validation_path.is_file(),
        "completion_marker": marker_path.is_file(),
    }
    details: dict[str, Any] = {"output_dir": str(output_dir)}
    if not all(checks.values()):
        return checks, details
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        full = np.load(output_dir / ARTIFACTS["full"], allow_pickle=False)
        selected = np.load(output_dir / ARTIFACTS["selected"], allow_pickle=False)
        flattened = np.load(output_dir / ARTIFACTS["flattened"], allow_pickle=False)
        checks.update(
            {
                "manifest_schema": manifest.get("schema_version") == 1
                and manifest.get("status") == "qchem_integrated_dv_complete_and_validated",
                "validation_status": validation.get("schema_version") == 1
                and validation.get("status") == "passed",
                "manifest_hash": validation.get("manifest_sha256") == sha256(manifest_path),
                "artifact_hashes": all(
                    (output_dir / name).is_file()
                    and sha256(output_dir / name) == digest
                    for name, digest in manifest.get("artifacts_sha256", {}).items()
                )
                and set(manifest.get("artifacts_sha256", {})) == set(ARTIFACTS.values()),
                "full_shape_finite": full.shape == STORED_SHAPE and bool(np.isfinite(full).all()),
                "selected_shape_finite": selected.shape == SELECTED_SHAPE and bool(np.isfinite(selected).all()),
                "flattened_shape_finite": flattened.shape == (288,) and bool(np.isfinite(flattened).all()),
                "selection_identity": bool(np.array_equal(selected, full[list(SELECTED_ROWS)])),
                "flattening_identity": bool(np.array_equal(flattened, selected.reshape(-1))),
                "layout_manifest": manifest.get("printed_shape") == list(PRINTED_SHAPE)
                and manifest.get("stored_shape") == list(STORED_SHAPE)
                and manifest.get("selected_rows") == list(SELECTED_ROWS)
                and manifest.get("selected_shape") == list(SELECTED_SHAPE)
                and manifest.get("flattened_shape") == [288],
                "complete_block_count_positive": int(manifest.get("complete_block_count", 0)) >= 1,
            }
        )
        case_root = Path(manifest["source"]["case_root"])
        source = validate_case_source(case_root)
        native, count = parse_integrated_dv_output(Path(source["qchem_output_path"]))
        checks.update(
            {
                "source_hashes": source["prepared_sha256"] == manifest["source"]["prepared_sha256"]
                and source["derived_input_sha256"] == manifest["source"]["derived_input_sha256"]
                and source["qchem_output_sha256"] == manifest["source"]["qchem_output_sha256"]
                and source["qarchive_sha256"] == manifest["source"]["qarchive_sha256"],
                "source_identity": source["species"] == manifest["species"]
                and source["role"] == manifest["role"] and source["grid"] == manifest["grid"],
                "source_matrix_identity": bool(np.array_equal(full, native.T)),
                "complete_block_count_reproduced": count == manifest["complete_block_count"],
                "expected_case_root": expected_case_root is None
                or case_root.resolve() == expected_case_root.resolve(),
            }
        )
        details.update({"manifest": manifest, "source": source})
    except Exception as exc:
        checks["load_and_revalidate"] = False
        details["exception"] = f"{type(exc).__name__}: {exc}"
    return checks, details


def publish_integrated_dv(case_root: Path, output_dir: Path) -> dict[str, Any]:
    """Extract, validate, and atomically publish one immutable feature boundary."""

    case_root = case_root.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite Q-Chem feature boundary: {output_dir}")
    temporary = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temporary.exists():
        raise FileExistsError(f"refusing to reuse temporary feature boundary: {temporary}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary.mkdir()
    try:
        source = validate_case_source(case_root)
        native, block_count = parse_integrated_dv_output(Path(source["qchem_output_path"]))
        full = np.ascontiguousarray(native.T)
        selected = np.ascontiguousarray(full[list(SELECTED_ROWS)])
        flattened = np.ascontiguousarray(selected.reshape(-1))
        arrays = {"full": full, "selected": selected, "flattened": flattened}
        for key, array in arrays.items():
            np.save(temporary / ARTIFACTS[key], array, allow_pickle=False)
        artifacts_sha256 = {
            name: sha256(temporary / name) for name in ARTIFACTS.values()
        }
        manifest = {
            "schema_version": 1,
            "status": "qchem_integrated_dv_complete_and_validated",
            "created_utc": utc_now(),
            "species": source["species"],
            "role": source["role"],
            "grid": source["grid"],
            "complete_block_policy": "retain_final_complete_block_and_record_count",
            "complete_block_count": block_count,
            "selected_complete_block_ordinal": block_count,
            "printed_shape": list(PRINTED_SHAPE),
            "stored_shape": list(STORED_SHAPE),
            "selected_rows": list(SELECTED_ROWS),
            "selected_shape": list(SELECTED_SHAPE),
            "flattened_shape": [288],
            "source": source,
            "artifacts_sha256": artifacts_sha256,
            "provenance": {
                "publisher_sha256": sha256(Path(__file__).resolve()),
                "hostname": socket.gethostname(),
                "numpy_version": np.__version__,
            },
        }
        manifest_path = temporary / MANIFEST_NAME
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validation = {
            "schema_version": 1,
            "status": "passed",
            "validated_utc": utc_now(),
            "manifest_sha256": sha256(manifest_path),
            "checks": {
                "source_preflight": True,
                "final_complete_block_selected": block_count >= 1,
                "printed_shape_finite": native.shape == PRINTED_SHAPE and bool(np.isfinite(native).all()),
                "transpose_shape_finite": full.shape == STORED_SHAPE and bool(np.isfinite(full).all()),
                "selected_rows_identity": bool(np.array_equal(selected, full[list(SELECTED_ROWS)])),
                "flattened_identity": bool(np.array_equal(flattened, selected.reshape(-1))),
                "artifact_hashes": all(sha256(temporary / name) == digest for name, digest in artifacts_sha256.items()),
            },
        }
        (temporary / VALIDATION_NAME).write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temporary / COMPLETION_MARKER).write_text(utc_now() + "\n", encoding="utf-8")
        checks, _ = validate_published_artifact(temporary, expected_case_root=case_root)
        if not all(checks.values()):
            raise RuntimeError(f"staged Q-Chem feature validation failed: {checks}")
        temporary.rename(output_dir)
        return manifest
    except BaseException:
        (temporary / "FAILURE.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "qchem_integrated_dv_publication_failed",
                    "created_utc": utc_now(),
                    "case_root": str(case_root),
                    "exception": traceback.format_exc(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        raise


def publish_or_resume(case_root: Path, output_dir: Path) -> tuple[str, dict[str, Any]]:
    """Publish an absent boundary or reuse an existing independently valid one."""

    output_dir = output_dir.resolve()
    if not output_dir.exists():
        return "published", publish_integrated_dv(case_root, output_dir)
    checks, details = validate_published_artifact(output_dir, expected_case_root=case_root)
    if not checks or not all(checks.values()):
        raise RuntimeError(f"existing Q-Chem feature boundary is not reusable: {checks}")
    return "reused", details["manifest"]
