#!/usr/bin/env python3
"""Prepare immutable closed/open-shell Q-Chem scalar gateway cases."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from revwb97m2.qchem_scalar_features import (  # noqa: E402
    derive_pt2_input,
    derive_scalar_input,
    sha256,
    tree_manifest,
)

DEFAULT_MANIFEST = ROOT / "manifests/scalar_features/step9_qchem_same_archive_v3.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    manifest = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
    if manifest["status"] != "frozen_before_results":
        raise ValueError("manifest must be frozen before results")
    run_root = args.run_root.resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite {run_root}")
    run_root.mkdir(parents=True)
    records = []
    for case in manifest["cases"]:
        case_root = run_root / case["species"]
        scratch = case_root / "qcscratch" / "step9_scalar"
        case_root.mkdir(parents=True)
        source_input = Path(case["authoritative_input"])
        source_orbitals = Path(case["orbital_root"])
        if sha256(source_input) != case["authoritative_input_sha256"]:
            raise ValueError(f"authoritative input hash mismatch for {case['species']}")
        if sha256(source_orbitals / "qarchive.h5") != case["qarchive_sha256"]:
            raise ValueError(f"qarchive hash mismatch for {case['species']}")
        source_text = source_input.read_text(encoding="utf-8")
        derived, controls = derive_scalar_input(source_text)
        pt2_derived, pt2_controls = derive_pt2_input(source_text)
        shutil.copy2(source_input, case_root / "input.authoritative.in")
        (case_root / "input.step9.in").write_text(derived, encoding="utf-8")
        (case_root / "input.step9.pt2.in").write_text(pt2_derived, encoding="utf-8")
        source_tree = tree_manifest(source_orbitals)
        shutil.copytree(source_orbitals, scratch, copy_function=shutil.copy2)
        copy_tree = tree_manifest(scratch)
        if source_tree != copy_tree:
            raise RuntimeError(f"orbital copy differs for {case['species']}")
        record = {
            "species": case["species"],
            "role": case["role"],
            "authoritative_input": str(source_input),
            "authoritative_input_sha256": sha256(source_input),
            "source_orbital_root": str(source_orbitals),
            "source_tree": source_tree,
            "copy_tree": copy_tree,
            "controls": controls,
            "pt2_controls": pt2_controls,
        }
        (case_root / "PREPARED.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        records.append({key: value for key, value in record.items() if key not in ("source_tree", "copy_tree")})
    summary = {"schema_version": 2, "status": "prepared_not_run", "cases": records}
    (run_root / "PREPARED.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
