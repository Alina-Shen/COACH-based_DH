#!/usr/bin/env python3
"""Prepare six non-overwriting Q3 Q-Chem archive-read gateway cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/qchem_gateway/q3_native_gateway_v1.yaml"
DEFAULT_RUN_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q3_native_v1"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_manifest(root: Path) -> list[dict[str, object]]:
    return [
        {"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def replace_one(rem: str, key: str, value: str, *, add_if_missing: bool = True) -> str:
    pattern = re.compile(rf"(?im)^\s*{re.escape(key)}\s*(?:=\s*)?\S+\s*$")
    count = len(pattern.findall(rem))
    if count > 1:
        raise ValueError(f"expected at most one {key}, found {count}")
    if count == 1:
        return pattern.sub(f"{key} {value}", rem)
    if not add_if_missing:
        raise ValueError(f"required control missing: {key}")
    end = re.search(r"(?im)^\s*\$end\s*$", rem)
    if end is None:
        raise ValueError("$rem has no terminator")
    return rem[: end.start()] + f"{key} {value}\n" + rem[end.start() :]


def derive_input(source: str, grid: str) -> str:
    match = re.search(r"(?ims)^\s*\$rem\s*$.*?^\s*\$end\s*$", source)
    if match is None:
        raise ValueError("authoritative input has no complete $rem block")
    rem = match.group(0)
    required = {
        "SCF_GUESS": "READ",
        "MAX_SCF_CYCLES": "0",
        "GEN_SCFMAN": "FALSE",
        "METHOD": "wB97M-V",
        "UNRESTRICTED": "TRUE",
        "XC_FXC": "3",
        "XC_GRID": grid,
    }
    for key, value in required.items():
        rem = replace_one(rem, key, value, add_if_missing=key not in {"SCF_GUESS", "UNRESTRICTED"})
    # The gateway evaluates the parent functional only; no perturbative step is requested.
    rem = re.sub(r"(?im)^\s*DH_PT2_ENGINE\s*(?:=\s*)?\S+\s*\n?", "", rem)
    derived = source[: match.start()] + rem + source[match.end() :]
    for key, value in required.items():
        if not re.search(rf"(?im)^\s*{key}\s+(?:{re.escape(value)})\s*$", rem):
            raise AssertionError(f"derived input did not freeze {key}={value}")
    return derived


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    args = parser.parse_args()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    if manifest["status"] != "frozen_before_results":
        raise ValueError("Q3 manifest must be frozen before case preparation")
    run_root = args.run_root.resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite existing Q3 run root: {run_root}")
    run_root.mkdir(parents=True)
    cases = []
    for case in manifest["cases"]:
        source_input = Path(case["authoritative_input"])
        source_orbitals = Path(case["orbital_root"])
        if sha256(source_input) != case["authoritative_input_sha256"]:
            raise ValueError(f"authoritative input hash mismatch: {case['species']}")
        if sha256(source_orbitals / "qarchive.h5") != case["qarchive_sha256"]:
            raise ValueError(f"qarchive hash mismatch: {case['species']}")
        source_tree = tree_manifest(source_orbitals)
        for grid in manifest["grids"]:
            case_root = run_root / case["species"] / grid["id"]
            scratch_case = case_root / "qcscratch" / "q3_gateway"
            case_root.mkdir(parents=True)
            shutil.copy2(source_input, case_root / "input.authoritative.in")
            (case_root / "input.q3.in").write_text(
                derive_input(source_input.read_text(encoding="utf-8"), grid["qchem_value"]),
                encoding="utf-8",
            )
            shutil.copytree(source_orbitals, scratch_case, copy_function=shutil.copy2)
            copy_tree = tree_manifest(scratch_case)
            if source_tree != copy_tree:
                raise ValueError(f"orbital copy mismatch: {case['species']} {grid['id']}")
            record = {
                "species": case["species"],
                "role": case["role"],
                "grid": grid["id"],
                "case_root": str(case_root),
                "source_orbital_root": str(source_orbitals),
                "source_tree": source_tree,
                "copy_tree": copy_tree,
                "source_copy_tree_identity": True,
                "authoritative_input_sha256": sha256(source_input),
                "derived_input_sha256": sha256(case_root / "input.q3.in"),
            }
            (case_root / "PREPARED.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            cases.append(record)
    summary = {
        "schema_version": 1,
        "status": "prepared_not_run",
        "manifest": str(args.manifest.resolve()),
        "manifest_sha256": sha256(args.manifest),
        "case_count": len(cases),
        "cases": [{key: value for key, value in case.items() if key not in {"source_tree", "copy_tree"}} for case in cases],
    }
    (run_root / "PREPARED.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
