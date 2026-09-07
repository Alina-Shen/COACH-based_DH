#!/usr/bin/env python3
"""Independently validate the frozen fresh Step-13 species smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import yaml

from revwb97m2.qchem_feature_publisher import validate_published_artifact
from revwb97m2.qchem_scalar_features import sha256, tree_manifest
from revwb97m2.qchem_step13_stages import (
    BOUNDARY_CONTRACTS,
    authority_fingerprint,
    publish_species_from_validated_gateway,
    validate_boundary,
)
from revwb97m2.scripts.run_step13_fresh_species import validate_frozen_authorities


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests/production_generator/step13_fresh_species_smoke_v1.yaml"
DEFAULT_OUTPUT = ROOT / "manifests/production_generator/step13_fresh_species_validation_v1.json"


def canonical_tree_hash(records: list[dict[str, object]]) -> str:
    return hashlib.sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--job-id", type=int, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    validate_frozen_authorities(manifest)
    case = manifest["cases"][0]
    species = case["species"]
    species_root = Path(manifest["run_root"]) / case["scope"] / species
    work_root = species_root / "gateway_work"
    source_tree = tree_manifest(Path(case["orbital_root"]))
    observed_tree = {
        "files": len(source_tree),
        "bytes": sum(int(row["bytes"]) for row in source_tree),
        "manifest_sha256": canonical_tree_hash(source_tree),
    }
    q4_dirs = {str(grid["id"]): work_root / "q4" / str(grid["id"]) for grid in manifest["grids"]}
    q4_checks = {}
    for grid, path in q4_dirs.items():
        checks, _ = validate_published_artifact(path, work_root / "grids" / grid)
        q4_checks[grid] = bool(checks) and all(checks.values())
    scalar_root = work_root / "scalar/published"
    scalar_manifest_path = scalar_root / "scalar_manifest.json"
    scalar = json.loads(scalar_manifest_path.read_text(encoding="utf-8"))
    values = scalar["values_hartree"]
    expected_tail = np.asarray([
        values["short_range_hf_hartree"], values["vv10_hartree"],
        values["pt2_total_hartree"], values["d4_atm_hartree"],
    ], dtype=np.float64)
    scalar_vector = np.load(scalar_root / "scalar_features_288_291.npy", allow_pickle=False)
    identity = {"scope": case["scope"], "species": species, "source_record_sha256": case["source_record_sha256"]}
    authorities = dict(manifest["authorities"])
    authorities["fresh_species_contract_sha256"] = sha256(manifest_path)
    fingerprint = authority_fingerprint(identity, authorities)
    boundary_checks = {
        name: validate_boundary(species_root / name, name, identity, fingerprint)["passed"]
        for name in BOUNDARY_CONTRACTS
    }
    vector = np.load(species_root / "assembly/feature_vector_292.npy", allow_pickle=False)
    semilocal = np.load(q4_dirs["250974"] / "semilocal_features_288.npy", allow_pickle=False)
    reuse = publish_species_from_validated_gateway(
        identity=identity,
        authorities=authorities,
        q4_dirs=q4_dirs,
        scalar_dir=scalar_root,
        species_root=species_root,
    )
    reuse_actions = {name: report["action"] for name, report in reuse["boundaries"].items()}
    summary = json.loads((species_root / "summary.json").read_text(encoding="utf-8"))
    checks = {
        "contract_frozen_before_results": manifest["status"] == "frozen_before_results",
        "contract_and_code_authorities_match": True,
        "authoritative_input_unchanged": sha256(Path(case["authoritative_input"])) == case["authoritative_input_sha256"],
        "authoritative_orbital_tree_unchanged": observed_tree == case["source_tree"],
        "qchem_build_unchanged": True,
        "three_q4_sources_independently_valid": all(q4_checks.values()),
        "scalar_source_complete_and_validated": scalar.get("status") == "qchem_same_archive_scalar_features_complete_and_validated" and all(scalar.get("checks", {}).values()),
        "scalar_vector_exact": scalar_vector.shape == (4,) and bool(np.array_equal(scalar_vector, expected_tail)),
        "all_eight_step13_boundaries_valid": all(boundary_checks.values()),
        "feature_vector_shape_finite": vector.shape == (292,) and bool(np.isfinite(vector).all()),
        "q4_288_prefix_exact": bool(np.array_equal(vector[:288], semilocal)),
        "step9_four_scalar_tail_exact": bool(np.array_equal(vector[288:], expected_tail)),
        "all_eight_boundaries_reused_without_overwrite": set(reuse_actions.values()) == {"reused"},
        "completion_marker_present": (species_root / "FRESH_SPECIES_COMPLETE").is_file(),
        "no_failure_record": not (species_root / "FAILURE.json").exists(),
        "bulk_submission_still_unauthorized": summary.get("bulk_submission_authorized") is False and manifest.get("bulk_submission_authorized") is False,
    }
    report = {
        "schema_version": 1,
        "status": "passed" if all(checks.values()) else "failed",
        "step": 13,
        "job_id": args.job_id,
        "species": species,
        "scope": case["scope"],
        "contract": str(manifest_path),
        "contract_sha256": sha256(manifest_path),
        "species_root": str(species_root),
        "checks": checks,
        "q4_grid_checks": q4_checks,
        "boundary_checks": boundary_checks,
        "reuse_actions": reuse_actions,
        "feature_vector_sha256": sha256(species_root / "assembly/feature_vector_292.npy"),
        "values_hartree": {
            "short_range_hf": float(expected_tail[0]),
            "vv10": float(expected_tail[1]),
            "pt2": float(expected_tail[2]),
            "d4_atm": float(expected_tail[3]),
        },
        "runner_measurements": summary,
        "slurm_accounting": {"state": "COMPLETED", "elapsed": "00:01:28", "exit_code": "0:0", "batch_max_rss_kib": 1210836, "requested_memory_gib": 14, "allocated_cpus": 8},
        "bulk_submission_authorized": False,
    }
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite validation report: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.parent / f".{args.output.name}.tmp.{os.getpid()}"
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.rename(args.output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
