#!/usr/bin/env python3
"""Independently validate the R2 reaction-level smoke artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reaction-spec", type=Path, default=root / "reaction_smoke.yaml")
    parser.add_argument("--run-dir", type=Path, required=True)
    return parser.parse_args()


def species_nofit(manifest: dict) -> float:
    components = manifest["parent_components"]
    return float(sum(components[key] for key in (
        "nuclear_repulsion", "one_electron", "coulomb", "unscaled_long_range_hf_exchange"
    )))


def main() -> int:
    args = parse_args()
    spec = yaml.safe_load(args.reaction_spec.read_text(encoding="utf-8"))
    run_dir = args.run_dir.resolve()
    data_root = Path(spec["data_root"]).resolve()
    species_root = data_root / spec["species_output_subdirectory"]
    tolerance = float(spec["validation"]["array_tolerance_hartree"])
    reconstruction_tolerance = float(spec["validation"]["reconstruction_tolerance_hartree"])
    width = int(spec["validation"]["required_feature_width"])

    saved_a = np.load(run_dir / "A_matrix.npy")
    saved_nofit = np.load(run_dir / "Nofit.npy")
    saved_reference = np.load(run_dir / "reference_energy.npy")
    saved_b = np.load(run_dir / "b_vec.npy")
    saved_weights = np.load(run_dir / "weight_vec.npy")
    beta = np.load(run_dir / "oracle_beta_291.npy")
    names = (run_dir / "name_list_training.txt").read_text(encoding="utf-8").splitlines()
    saved_diffs = {grid: np.load(run_dir / f"diff_{grid}.npy") for grid in ("99590", "75302")}

    species = {}
    for name in spec["species"]:
        species_dir = species_root / name
        manifest = json.loads((species_dir / "manifest.json").read_text(encoding="utf-8"))
        feature = np.load(species_dir / "r2_feature_vector_291.npy")
        species[name] = {
            "feature": feature,
            "nofit": species_nofit(manifest),
            "formula": {str(k): int(v) for k, v in spec["species"][name]["formula"].items()},
            "charge": int(spec["species"][name]["charge"]),
            "diffs": {
                grid: np.load(species_dir / f"r2_grid_diff_{grid}_minus_250974.npy")
                for grid in ("99590", "75302")
            },
        }

    rebuilt_a = []
    rebuilt_nofit = []
    rebuilt_reference = []
    rebuilt_diffs = {"99590": [], "75302": []}
    balance_checks = {}
    for reaction_name, definition in spec["reactions"].items():
        feature = np.zeros(width)
        nofit = 0.0
        reference = 0.0
        element_balance = {}
        charge_balance = 0.0
        grid_diffs = {"99590": np.zeros(width), "75302": np.zeros(width)}
        for species_name, raw_coefficient in definition["stoichiometry"].items():
            coefficient = float(raw_coefficient)
            record = species[species_name]
            feature += coefficient * record["feature"]
            nofit += coefficient * record["nofit"]
            reference += coefficient * (record["nofit"] + record["feature"] @ beta)
            charge_balance += coefficient * record["charge"]
            for element, count in record["formula"].items():
                element_balance[element] = element_balance.get(element, 0.0) + coefficient * count
            for grid in grid_diffs:
                grid_diffs[grid] += coefficient * record["diffs"][grid]
        rebuilt_a.append(feature)
        rebuilt_nofit.append(nofit)
        rebuilt_reference.append(reference)
        for grid in rebuilt_diffs:
            rebuilt_diffs[grid].append(grid_diffs[grid])
        balance_checks[f"{reaction_name}_elements_balanced"] = all(value == 0.0 for value in element_balance.values())
        balance_checks[f"{reaction_name}_charge_balanced"] = charge_balance == 0.0

    rebuilt_a = np.asarray(rebuilt_a)
    rebuilt_nofit = np.asarray(rebuilt_nofit)
    rebuilt_reference = np.asarray(rebuilt_reference)
    rebuilt_b = rebuilt_reference - rebuilt_nofit
    checks = {
        "reaction_names_match": names == list(spec["reactions"]),
        "reaction_count": len(names) == int(spec["validation"]["required_reaction_count"]),
        "A_shape": saved_a.shape == (len(names), width),
        "Nofit_shape": saved_nofit.shape == (len(names),),
        "reference_shape": saved_reference.shape == (len(names),),
        "b_shape": saved_b.shape == (len(names),),
        "weights_are_one": np.array_equal(saved_weights, np.ones(len(names))),
        "oracle_shape": beta.shape == (width,),
        "all_arrays_finite": all(np.isfinite(array).all() for array in (
            saved_a, saved_nofit, saved_reference, saved_b, beta, *saved_diffs.values()
        )),
        "species_stoichiometry_A": np.allclose(saved_a, rebuilt_a, atol=tolerance, rtol=0.0),
        "species_stoichiometry_Nofit": np.allclose(saved_nofit, rebuilt_nofit, atol=tolerance, rtol=0.0),
        "species_stoichiometry_reference": np.allclose(saved_reference, rebuilt_reference, atol=tolerance, rtol=0.0),
        "Tofit_equals_reference_minus_Nofit": np.allclose(saved_b, saved_reference - saved_nofit, atol=tolerance, rtol=0.0),
        "Tofit_equals_A_beta": np.allclose(saved_b, saved_a @ beta, atol=reconstruction_tolerance, rtol=0.0),
        "reference_equals_Nofit_plus_A_beta": np.allclose(
            saved_reference, saved_nofit + saved_a @ beta, atol=reconstruction_tolerance, rtol=0.0
        ),
    }
    for grid in saved_diffs:
        rebuilt = np.asarray(rebuilt_diffs[grid])
        checks[f"diff_{grid}_shape"] = saved_diffs[grid].shape == (len(names), width)
        checks[f"diff_{grid}_stoichiometry"] = np.allclose(saved_diffs[grid], rebuilt, atol=tolerance, rtol=0.0)
        checks[f"diff_{grid}_nongrid_zero"] = np.array_equal(saved_diffs[grid][:, 288:], np.zeros((len(names), 3)))
    checks.update(balance_checks)
    checks = {name: bool(value) for name, value in checks.items()}
    residual = saved_reference - (saved_nofit + saved_a @ beta)
    report = {
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "passed": all(checks.values()),
        "checks": checks,
        "maximum_reference_reconstruction_residual_hartree": float(np.max(np.abs(residual))),
        "reference_is_synthetic": True,
        "reference_warning": spec["reference"]["warning"],
    }
    (run_dir / "validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not report["passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Reaction smoke validation failed: {', '.join(failed)}")
    (run_dir / "REACTION_SMOKE_PASS").write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
