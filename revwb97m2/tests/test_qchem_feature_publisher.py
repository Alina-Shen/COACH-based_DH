from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from revwb97m2.qchem_feature_publisher import (
    BEGIN_TOKEN,
    COMPLETION_MARKER,
    MANIFEST_NAME,
    publish_integrated_dv,
    publish_or_resume,
    parse_integrated_dv_output,
    sha256,
    validate_published_artifact,
)


def block(matrix: np.ndarray, *, rows: int = 96, cols: int = 180) -> str:
    body = "\n".join(" ".join(f"{value:.17g}" for value in row) for row in matrix)
    return (
        f"{BEGIN_TOKEN} rows={rows} cols={cols}\n"
        f"integratedDV\n{body}\nCOACH integratedDV end\n"
    )


def matrix(offset: float = 0.0) -> np.ndarray:
    return np.arange(96 * 180, dtype=np.float64).reshape(96, 180) / 1000.0 + offset


def write_output(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def valid_case(tmp_path: Path, output_text: str | None = None) -> Path:
    source = tmp_path / "authoritative_orbitals"
    source.mkdir()
    source_archive = source / "qarchive.h5"
    source_archive.write_bytes(b"Q-Chem archive fixture")
    case = tmp_path / "case"
    scratch = case / "qcscratch" / "job"
    scratch.mkdir(parents=True)
    copied_archive = scratch / "qarchive.h5"
    copied_archive.write_bytes(source_archive.read_bytes())
    authoritative = case / "input.authoritative.in"
    authoritative.write_text("authoritative fixture\n", encoding="utf-8")
    derived = case / "input.q3.in"
    derived.write_text(
        "$rem\n"
        "METHOD wB97M-V\nUNRESTRICTED TRUE\nSCF_GUESS READ\n"
        "MAX_SCF_CYCLES 0\nGEN_SCFMAN FALSE\nXC_FXC 3\n"
        "XC_GRID 000250000974\n$end\n",
        encoding="utf-8",
    )
    digest = sha256(source_archive)
    prepared = {
        "species": "fixture",
        "role": "closed_shell_singlet_uks",
        "grid": "250974",
        "case_root": str(case.resolve()),
        "source_orbital_root": str(source.resolve()),
        "source_tree": [{"path": "qarchive.h5", "bytes": source_archive.stat().st_size, "sha256": digest}],
        "copy_tree": [{"path": "qarchive.h5", "bytes": copied_archive.stat().st_size, "sha256": digest}],
        "source_copy_tree_identity": True,
        "authoritative_input_sha256": sha256(authoritative),
        "derived_input_sha256": sha256(derived),
    }
    (case / "PREPARED.json").write_text(json.dumps(prepared), encoding="utf-8")
    if output_text is None:
        output_text = (
            "Reading MOs from coefficient file\n" * 2
            + block(matrix())
            + "Thank you very much for using Q-Chem\n"
        )
    write_output(case / "qchem.out", output_text)
    return case


def test_parser_selects_one_complete_block(tmp_path: Path) -> None:
    expected = matrix()
    output = tmp_path / "qchem.out"
    write_output(output, "header\n" + block(expected) + "footer\n")
    observed, count = parse_integrated_dv_output(output)
    assert count == 1
    assert np.array_equal(observed, expected)


def test_parser_selects_final_of_multiple_complete_blocks(tmp_path: Path) -> None:
    first, final = matrix(), matrix(3.0)
    output = tmp_path / "qchem.out"
    write_output(output, block(first) + "between\n" + block(final))
    observed, count = parse_integrated_dv_output(output)
    assert count == 2
    assert np.array_equal(observed, final)


def test_parser_rejects_zero_and_truncated_blocks(tmp_path: Path) -> None:
    output = tmp_path / "qchem.out"
    write_output(output, "ordinary output without feature markers\n")
    with pytest.raises(ValueError, match="no complete"):
        parse_integrated_dv_output(output)
    write_output(output, f"{BEGIN_TOKEN} rows=96 cols=180\nintegratedDV\n1 2\n")
    with pytest.raises(ValueError, match="truncated"):
        parse_integrated_dv_output(output)


def test_parser_rejects_wrong_shape_and_nonfinite_values(tmp_path: Path) -> None:
    output = tmp_path / "qchem.out"
    write_output(output, block(matrix(), rows=95))
    with pytest.raises(ValueError, match="wrong declared"):
        parse_integrated_dv_output(output)
    bad = matrix()
    bad[4, 7] = np.nan
    write_output(output, block(bad))
    with pytest.raises(FloatingPointError, match="non-finite"):
        parse_integrated_dv_output(output)


@pytest.mark.parametrize(
    "content, message",
    [
        ("COACH integratedDV begin\nintegratedDV\n", "malformed"),
        ("COACH integratedDV end\n", "unmatched"),
        (
            f"{BEGIN_TOKEN} rows=96 cols=180\n{BEGIN_TOKEN} rows=96 cols=180\n",
            "nested",
        ),
        (
            f"{BEGIN_TOKEN} rows=96 cols=180\nwrong-label\nCOACH integratedDV end\n",
            "wrong label",
        ),
    ],
)
def test_parser_rejects_malformed_marker_structures(
    tmp_path: Path, content: str, message: str
) -> None:
    output = tmp_path / "qchem.out"
    write_output(output, content)
    with pytest.raises(ValueError, match=message):
        parse_integrated_dv_output(output)


def test_atomic_publish_layout_hashes_and_restart_reuse(tmp_path: Path) -> None:
    case = valid_case(tmp_path)
    output = tmp_path / "published"
    manifest = publish_integrated_dv(case, output)
    assert manifest["complete_block_count"] == 1
    assert (output / COMPLETION_MARKER).is_file()
    assert np.load(output / "integrated_dv_180x96.npy").shape == (180, 96)
    assert np.load(output / "selected_features_3x96.npy").shape == (3, 96)
    assert np.load(output / "semilocal_features_288.npy").shape == (288,)
    checks, _ = validate_published_artifact(output, case)
    assert all(checks.values())
    action, resumed = publish_or_resume(case, output)
    assert action == "reused"
    assert resumed["source"]["qarchive_sha256"] == manifest["source"]["qarchive_sha256"]
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        publish_integrated_dv(case, output)


def test_restart_refuses_existing_corrupt_artifact(tmp_path: Path) -> None:
    case = valid_case(tmp_path)
    output = tmp_path / "published"
    publish_integrated_dv(case, output)
    (output / MANIFEST_NAME).write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="not reusable"):
        publish_or_resume(case, output)


@pytest.mark.parametrize("mutation", ["changed", "missing"])
def test_publication_refuses_missing_or_changed_qarchive(
    tmp_path: Path, mutation: str
) -> None:
    case = valid_case(tmp_path)
    copied = next((case / "qcscratch").glob("*/qarchive.h5"))
    if mutation == "changed":
        copied.write_bytes(b"changed")
    else:
        copied.unlink()
    output = tmp_path / "rejected"
    with pytest.raises((FileNotFoundError, ValueError), match="qarchive"):
        publish_integrated_dv(case, output)
    assert not output.exists()
    failures = list(tmp_path.glob(".rejected.tmp.*/FAILURE.json"))
    assert len(failures) == 1
    assert json.loads(failures[0].read_text())["status"] == "qchem_integrated_dv_publication_failed"
