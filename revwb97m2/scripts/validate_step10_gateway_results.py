#!/usr/bin/env python3
"""Validate completion and scientific coverage of the Step-10 gateway matrix."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HEAVY_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_species(entry: dict, heavy_root: Path) -> dict:
    name = entry["name"]
    parent_dir = heavy_root / "gateway" / name
    semilocal_dir = heavy_root / "semilocal" / "gateway" / name
    scalar_dir = heavy_root / "scalar" / "gateway" / name
    validation_dir = heavy_root / "validation" / "gateway" / name
    paths = {
        "parent_manifest": parent_dir / "parent_manifest.json",
        "semilocal_manifest": semilocal_dir / "semilocal_manifest.json",
        "scalar_manifest": scalar_dir / "scalar_manifest.json",
        "parent_validation": validation_dir / "parent_validation.json",
        "semilocal_validation": validation_dir / "semilocal_validation.json",
        "scalar_validation": validation_dir / "scalar_validation.json",
    }
    checks = {f"{key}_exists": path.is_file() for key, path in paths.items()}
    checks.update(
        {
            "parent_marker": (parent_dir / "PARENT_COMPLETE").is_file(),
            "semilocal_marker": (semilocal_dir / "SEMILOCAL_COMPLETE").is_file(),
            "scalar_marker": (scalar_dir / "SCALAR_COMPLETE").is_file(),
            "gateway_marker": (validation_dir / "GATEWAY_COMPLETE").is_file(),
        }
    )
    if not all(checks.values()):
        return {"species": name, "status": "incomplete", "checks": checks}
    parent = load_json(paths["parent_manifest"])
    semilocal = load_json(paths["semilocal_manifest"])
    scalar = load_json(paths["scalar_manifest"])
    checks.update(
        {
            "parent_status": parent["status"]
            == "parent_complete_and_checkpoint_validated",
            "semilocal_status": semilocal["status"]
            == "three_grid_semilocal_features_complete_and_validated",
            "scalar_status": scalar["status"]
            == "scalar_features_complete_and_validated",
            "species_names_match": all(
                manifest["species"] == name for manifest in (parent, semilocal, scalar)
            ),
            "checkpoint_only": all(
                manifest.get("qchem_orbitals_used") is False
                and manifest.get("qarchive_used") is False
                for manifest in (parent, semilocal, scalar)
            ),
            "three_frozen_grids": sorted(
                grid["id"] for grid in semilocal["grids"].values()
            )
            == ["250974", "75302", "99590"],
            "all_grid_point_counts_positive": all(
                grid["grid_points"] > 0 for grid in semilocal["grids"].values()
            ),
            "semilocal_shape_declaration": semilocal["matrix_shape_per_grid"]
            == [3, 96],
            "scalar_vector_shape": np.load(
                scalar_dir / "feature_vector_291.npy", mmap_mode="r"
            ).shape
            == (291,),
            "all_independent_validators_passed": all(
                load_json(paths[f"{stage}_validation"])["status"] == "passed"
                for stage in ("parent", "semilocal", "scalar")
            ),
        }
    )
    for grid_id in ("250974", "99590", "75302"):
        checks[f"semilocal_{grid_id}_shape"] = np.load(
            semilocal_dir / f"selected_features_{grid_id}.npy", mmap_mode="r"
        ).shape == (3, 96)
    return {
        "species": name,
        "categories": entry["categories"],
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=ROOT / "manifests" / "gateway_matrix" / "step10_gateway_matrix_v1.yaml",
    )
    parser.add_argument("--heavy-root", type=Path, default=DEFAULT_HEAVY_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "manifests" / "gateway_matrix" / "validation.json",
    )
    args = parser.parse_args()
    matrix = yaml.safe_load(args.matrix.read_text(encoding="utf-8"))
    species = [validate_species(entry, args.heavy_root) for entry in matrix["species"]]
    covered = {
        category for entry in matrix["species"] for category in entry["categories"]
    }
    checks = {
        "species_count_5_to_10": 5 <= len(species) <= 10,
        "all_required_categories_covered": set(matrix["required_categories"]) <= covered,
        "all_species_passed": all(entry["status"] == "passed" for entry in species),
    }
    report = {
        "schema_version": 1,
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "covered_categories": sorted(covered),
        "species": species,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
