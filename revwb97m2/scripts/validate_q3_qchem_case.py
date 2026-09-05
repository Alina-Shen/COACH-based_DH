#!/usr/bin/env python3
"""Validate one Q3 native output against exact exported MGGA grid inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_integrated_dv_reference import full_integrated_dv_block  # noqa: E402


RTOL = 2.0e-12
ATOL = 2.0e-12
SELECTED_ROWS = (64, 154, 166)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_final_matrix(output: Path) -> tuple[np.ndarray, int]:
    lines = output.read_text(encoding="utf-8", errors="replace").splitlines()
    blocks: list[np.ndarray] = []
    begin = None
    for index, line in enumerate(lines):
        if "COACH integratedDV begin rows=96 cols=180" in line:
            begin = index
        elif "COACH integratedDV end" in line and begin is not None:
            body = lines[begin + 1 : index]
            if body and body[0].strip() == "integratedDV":
                try:
                    matrix = np.asarray([[float(value) for value in row.split()] for row in body[1:]], dtype=np.float64)
                except ValueError:
                    matrix = np.empty((0, 0))
                if matrix.shape == (96, 180):
                    blocks.append(matrix)
            begin = None
    if not blocks:
        raise ValueError("no complete 96x180 integratedDV block")
    return blocks[-1], len(blocks)


def iter_diagnostic(path: Path):
    with path.open("rb") as handle:
        if handle.read(8) != b"COACHDV1":
            raise ValueError("wrong diagnostic magic")
        while True:
            header = handle.read(8)
            if len(header) != 8:
                raise ValueError("truncated diagnostic batch header")
            (rows,) = struct.unpack("=Q", header)
            if rows == 0:
                if handle.read(1):
                    raise ValueError("trailing diagnostic bytes")
                return
            payload = handle.read(rows * 11 * 8)
            if len(payload) != rows * 11 * 8:
                raise ValueError("truncated diagnostic batch payload")
            yield np.frombuffer(payload, dtype=np.float64).reshape((rows, 11), order="F")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_root", type=Path)
    args = parser.parse_args()
    case_root = args.case_root.resolve()
    output = case_root / "qchem.out"
    diagnostic = case_root / "integrated_dv_inputs.bin"
    prepared_path = case_root / "PREPARED.json"
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    text = output.read_text(encoding="utf-8", errors="replace")
    native, block_count = parse_final_matrix(output)
    reference = np.zeros((96, 180), dtype=np.float64)
    batch_count = 0
    point_count = 0
    for values in iter_diagnostic(diagnostic):
        reference += full_integrated_dv_block(
            values[:, 0], values[:, 1], values[:, 2], values[:, 3:6],
            values[:, 6:9], values[:, 9], values[:, 10]
        )
        batch_count += 1
        point_count += values.shape[0]
    difference = np.abs(native - reference)
    selected_native = native.T[list(SELECTED_ROWS)]
    selected_reference = reference.T[list(SELECTED_ROWS)]
    selected_difference = np.abs(selected_native - selected_reference)
    checks = {
        "prepared_source_copy_identity": prepared["source_copy_tree_identity"] is True,
        "exactly_one_complete_block": block_count == 1,
        "native_shape": native.shape == (96, 180),
        "native_finite": bool(np.isfinite(native).all()),
        "diagnostic_batches_present": batch_count > 0 and point_count > 0,
        "reference_finite": bool(np.isfinite(reference).all()),
        "full_matrix_allclose": bool(np.allclose(native, reference, rtol=RTOL, atol=ATOL)),
        "selected_rows_allclose": bool(np.allclose(selected_native, selected_reference, rtol=RTOL, atol=ATOL)),
        "archive_read": text.count("Reading MOs from coefficient file") >= 2,
        "normal_qchem_termination": "Thank you very much for using Q-Chem" in text,
    }
    np.save(case_root / "integrated_dv_native_96x180.npy", native)
    np.save(case_root / "integrated_dv_python_reference_96x180.npy", reference)
    np.save(case_root / "selected_rows_native_3x96.npy", selected_native)
    np.save(case_root / "selected_rows_python_reference_3x96.npy", selected_reference)
    report = {
        "schema_version": 1,
        "passed": all(checks.values()),
        "species": prepared["species"],
        "role": prepared["role"],
        "grid": prepared["grid"],
        "tolerances_frozen_before_results": {"rtol": RTOL, "atol_hartree": ATOL},
        "checks": checks,
        "metrics": {
            "complete_block_count": block_count,
            "diagnostic_batch_count": batch_count,
            "diagnostic_grid_point_count": point_count,
            "full_matrix_max_abs_hartree": float(difference.max()),
            "selected_rows_max_abs_hartree": float(selected_difference.max()),
            "full_matrix_max_relative_scaled": float(np.max(difference / np.maximum(np.abs(reference), ATOL))),
            "selected_rows_max_relative_scaled": float(np.max(selected_difference / np.maximum(np.abs(selected_reference), ATOL))),
        },
        "hashes": {
            "prepared_json": sha256(prepared_path),
            "derived_input": sha256(case_root / "input.q3.in"),
            "qchem_output": sha256(output),
            "diagnostic_inputs": sha256(diagnostic),
            "native_matrix": sha256(case_root / "integrated_dv_native_96x180.npy"),
            "python_reference_matrix": sha256(case_root / "integrated_dv_python_reference_96x180.npy"),
        },
    }
    (case_root / "validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
