#!/usr/bin/env python3
"""Aggregate the Step-10 gateway and early Step-12 resource measurements."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HEAVY_ROOT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def percentile(values: list[int], fraction: float) -> float:
    """Return a linearly interpolated percentile without a NumPy dependency."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile requires at least one value")
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def population_summary() -> dict:
    roles_path = ROOT / "manifests" / "data_roles" / "species_roles.csv"
    bridge_path = ROOT / "manifests" / "basis_bridge" / "resolved_basis_records.csv"
    energy_role_columns = (
        "coefficient_fitting",
        "model_selection",
        "overfitting_diagnostic",
        "final_assessment",
    )
    with roles_path.open(newline="", encoding="utf-8") as handle:
        roles = {
            (row["scope"], row["species"]): row
            for row in csv.DictReader(handle)
            if any(row[column].lower() == "true" for column in energy_role_columns)
        }
    with bridge_path.open(newline="", encoding="utf-8") as handle:
        bridge = {
            (row["scope"], row["species"]): row for row in csv.DictReader(handle)
        }
    missing = sorted(set(roles) - set(bridge))
    if missing:
        raise RuntimeError(f"role-minimal species missing from basis bridge: {missing[:5]}")
    rows = [bridge[key] for key in roles]
    aos = [int(row["orbital_spherical_aos"]) for row in rows]
    auxiliary = [int(row["auxiliary_spherical_aos"]) for row in rows]
    df_gib = [
        naux * nao * (nao + 1) / 2 * 8 / 1024**3
        for nao, naux in zip(aos, auxiliary)
    ]
    scopes: dict[str, int] = {}
    for scope, _species in roles:
        scopes[scope] = scopes.get(scope, 0) + 1
    return {
        "definition": "union of locked fixed-geometry energy roles; OPT excluded",
        "species_count": len(rows),
        "scope_counts": dict(sorted(scopes.items())),
        "orbital_aos": {
            "minimum": min(aos),
            "median": statistics.median(aos),
            "p90": percentile(aos, 0.90),
            "p95": percentile(aos, 0.95),
            "p99": percentile(aos, 0.99),
            "maximum": max(aos),
            "above_step10_stop_1800": sum(value > 1800 for value in aos),
        },
        "auxiliary_aos": {
            "minimum": min(auxiliary),
            "median": statistics.median(auxiliary),
            "p90": percentile(auxiliary, 0.90),
            "p95": percentile(auxiliary, 0.95),
            "p99": percentile(auxiliary, 0.99),
            "maximum": max(auxiliary),
            "above_step10_stop_4500": sum(value > 4500 for value in auxiliary),
        },
        "static_df_three_center_gib": {
            "median": statistics.median(df_gib),
            "p90": percentile(df_gib, 0.90),
            "p95": percentile(df_gib, 0.95),
            "p99": percentile(df_gib, 0.99),
            "maximum": max(df_gib),
            "above_20_gib": sum(value > 20 for value in df_gib),
            "above_100_gib": sum(value > 100 for value in df_gib),
        },
    }


def measured_species(entry: dict, heavy_root: Path) -> dict:
    name = entry["name"]
    paths = {
        "parent": heavy_root / "gateway" / name / "parent_manifest.json",
        "semilocal": heavy_root
        / "semilocal"
        / "gateway"
        / name
        / "semilocal_manifest.json",
        "scalar": heavy_root / "scalar" / "gateway" / name / "scalar_manifest.json",
    }
    validation_dir = heavy_root / "validation" / "gateway" / name
    report = {
        "species": name,
        "categories": entry["categories"],
        "orbital_aos": entry["expected"]["orbital_aos"],
        "auxiliary_aos": entry["expected"]["auxiliary_aos"],
        "complete": False,
        "estimated_df_three_center_gib": entry["expected"]["auxiliary_aos"]
        * entry["expected"]["orbital_aos"]
        * (entry["expected"]["orbital_aos"] + 1)
        / 2
        * 8
        / 1024**3,
        "stages": {},
    }
    for stage, path in paths.items():
        if not path.is_file():
            report["stages"][stage] = {"status": "missing"}
            continue
        manifest = load_json(path)
        resource = manifest.get("resource_usage", {})
        report["stages"][stage] = {
            "status": manifest.get("status"),
            "resource_usage": resource,
            "retained_directory_bytes": sum(
                child.stat().st_size for child in path.parent.iterdir() if child.is_file()
            ),
        }
        if stage == "semilocal":
            report["stages"][stage]["grid_measurements"] = {
                grid["id"]: {
                    "grid_points": grid["grid_points"],
                    "wall_seconds": grid["wall_seconds"],
                }
                for grid in manifest["grids"].values()
            }
    validation = {}
    for stage in paths:
        path = validation_dir / f"{stage}_validation.json"
        validation[stage] = load_json(path).get("status") if path.is_file() else "missing"
    report["validation"] = validation
    report["complete"] = (
        (validation_dir / "GATEWAY_COMPLETE").is_file()
        and all(status == "passed" for status in validation.values())
    )
    return report


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
        default=ROOT / "manifests" / "gateway_matrix" / "step10_resources.json",
    )
    args = parser.parse_args()
    matrix = yaml.safe_load(args.matrix.read_text(encoding="utf-8"))
    measured = [measured_species(entry, args.heavy_root) for entry in matrix["species"]]
    complete_count = sum(entry["complete"] for entry in measured)
    high_cost_complete = all(
        entry["complete"]
        for entry in measured
        if "larger_high_cost" in entry["categories"]
    )
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "complete" if complete_count == len(measured) else "measurement_in_progress",
        "gateway": {
            "species_count": len(measured),
            "complete_count": complete_count,
            "high_cost_measurement_complete": high_cost_complete,
            "species": measured,
        },
        "role_minimal_population": population_summary(),
        "early_step12_decision": {
            "production_submission_authorized": False,
            "reason": (
                "Step-10 matrix complete; Step-11 reproduction and full Step-12 cost "
                "extrapolation/sign-off remain required."
                if complete_count == len(measured)
                else "The high-cost gateway measurement is not yet complete."
            ),
            "measured_restart_boundaries": [
                "parent_scf_checkpoint",
                "three_grid_semilocal_features",
                "vv10_and_ri_mp2_scalar_features",
            ],
            "quantitative_provisional_stops": {
                "orbital_aos": matrix["preflight_stop_conditions"]["maximum_orbital_aos"],
                "auxiliary_aos": matrix["preflight_stop_conditions"]["maximum_auxiliary_aos"],
                "static_df_three_center_fraction_of_requested_memory": matrix[
                    "preflight_stop_conditions"
                ]["maximum_estimated_df_3center_gib_fraction_of_requested_memory"],
                "stop_on_nonconvergence_hash_identity_oom_or_timeout": True,
            },
            "interpretation": (
                "These are evidence-preserving gateway limits, not production resource "
                "claims. No CPU-hour extrapolation is reported until the largest gateway "
                "finishes; extrapolating from only the small cases would be misleading."
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
