#!/usr/bin/env python3
"""Build 291-column reaction smoke artifacts from validated species outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=root / "revwb97m2.yaml")
    parser.add_argument("--reaction-spec", type=Path, default=root / "reaction_smoke.yaml")
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xyz_composition(path: Path) -> tuple[dict[str, int], int, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    natom = int(lines[0])
    metadata = {}
    for field in lines[1].split(","):
        if "=" in field:
            key, value = field.split("=", 1)
            metadata[key.strip().lower()] = value.strip()
    symbols = [line.split()[0] for line in lines[2 : 2 + natom]]
    if len(symbols) != natom:
        raise ValueError(f"{path}: malformed XYZ atom count")
    return dict(Counter(symbols)), int(metadata.get("charge", 0)), int(metadata.get("multiplicity", 1))


def species_nofit(manifest: dict) -> float:
    components = manifest["parent_components"]
    return float(
        components["nuclear_repulsion"]
        + components["one_electron"]
        + components["coulomb"]
        + components["unscaled_long_range_hf_exchange"]
    )


def oracle_vector(spec: dict) -> np.ndarray:
    width = int(spec["reference"]["coefficient_width"])
    beta = np.zeros(width, dtype=float)
    for index, value in spec["reference"]["nonzero_coefficients"].items():
        beta[int(index)] = float(value)
    return beta


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent
    config_path = args.config.resolve()
    spec_path = args.reaction_spec.resolve()
    config = load_yaml(config_path)
    spec = load_yaml(spec_path)
    data_root = Path(spec["data_root"]).resolve()
    output_dir = (args.output_dir or data_root / spec["processed_output_subdirectory"]).resolve()
    output_dir.relative_to(Path(config["project"]["generated_data_root"]).resolve())
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir.parent / f".{output_dir.name}.tmp.{os.getpid()}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    width = int(spec["validation"]["required_feature_width"])
    beta = oracle_vector(spec)
    if beta.shape != (width,):
        raise ValueError(f"Oracle width {beta.size} does not match required width {width}")

    species_root = data_root / spec["species_output_subdirectory"]
    species_records = {}
    for name, definition in spec["species"].items():
        run_dir = species_root / name
        if not (run_dir / "SMOKE_PASS").is_file():
            raise RuntimeError(f"Species {name} is missing SMOKE_PASS: {run_dir}")
        manifest_path = run_dir / "manifest.json"
        feature_path = run_dir / "r2_feature_vector_291.npy"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        feature = np.load(feature_path)
        if feature.shape != (width,) or not np.isfinite(feature).all():
            raise ValueError(f"Species {name} has invalid feature shape or values")

        xyz_path = (project_root / definition["xyz"]).resolve()
        observed_formula, observed_charge, observed_multiplicity = xyz_composition(xyz_path)
        expected_formula = {str(key): int(value) for key, value in definition["formula"].items()}
        if observed_formula != expected_formula:
            raise ValueError(f"Species {name} formula mismatch: {observed_formula} != {expected_formula}")
        if observed_charge != int(definition["charge"]):
            raise ValueError(f"Species {name} charge mismatch")
        if observed_multiplicity != int(definition["multiplicity"]):
            raise ValueError(f"Species {name} multiplicity mismatch")

        nofit = species_nofit(manifest)
        oracle_total = float(nofit + feature @ beta)
        grid_diffs = {
            grid_id: np.load(run_dir / f"r2_grid_diff_{grid_id}_minus_250974.npy")
            for grid_id in ("99590", "75302")
        }
        species_records[name] = {
            "feature": feature,
            "nofit": nofit,
            "oracle_total": oracle_total,
            "formula": expected_formula,
            "charge": observed_charge,
            "multiplicity": observed_multiplicity,
            "grid_diffs": grid_diffs,
            "manifest": str(manifest_path),
            "manifest_sha256": sha256(manifest_path),
        }

    reaction_names = []
    a_rows = []
    nofit_values = []
    reference_values = []
    b_values = []
    diff_rows = {"99590": [], "75302": []}
    reaction_records = {}
    for reaction_name, reaction_definition in spec["reactions"].items():
        stoichiometry = {name: float(value) for name, value in reaction_definition["stoichiometry"].items()}
        unknown = sorted(set(stoichiometry) - set(species_records))
        if unknown:
            raise KeyError(f"Reaction {reaction_name} has unknown species: {unknown}")

        element_balance: dict[str, float] = {}
        charge_balance = 0.0
        feature = np.zeros(width, dtype=float)
        nofit = 0.0
        reference = 0.0
        reaction_grid_diffs = {"99590": np.zeros(width), "75302": np.zeros(width)}
        for species_name, coefficient in stoichiometry.items():
            record = species_records[species_name]
            for element, count in record["formula"].items():
                element_balance[element] = element_balance.get(element, 0.0) + coefficient * count
            charge_balance += coefficient * record["charge"]
            feature += coefficient * record["feature"]
            nofit += coefficient * record["nofit"]
            reference += coefficient * record["oracle_total"]
            for grid_id in reaction_grid_diffs:
                reaction_grid_diffs[grid_id] += coefficient * record["grid_diffs"][grid_id]

        target = float(reference - nofit)
        reconstructed_reference = float(nofit + feature @ beta)
        reaction_names.append(reaction_name)
        a_rows.append(feature)
        nofit_values.append(nofit)
        reference_values.append(reference)
        b_values.append(target)
        for grid_id in diff_rows:
            diff_rows[grid_id].append(reaction_grid_diffs[grid_id])
        reaction_records[reaction_name] = {
            "stoichiometry": stoichiometry,
            "element_balance": element_balance,
            "charge_balance": charge_balance,
            "nofit_hartree": nofit,
            "reference_hartree": reference,
            "reference_kcal_per_mol": reference * float(config["project"]["units"]["hartree_to_kcal_per_mol"]),
            "tofit_hartree": target,
            "reconstructed_reference_hartree": reconstructed_reference,
            "reconstruction_residual_hartree": reconstructed_reference - reference,
        }

    arrays = {
        "A_matrix.npy": np.asarray(a_rows),
        "Nofit.npy": np.asarray(nofit_values),
        "reference_energy.npy": np.asarray(reference_values),
        "b_vec.npy": np.asarray(b_values),
        "weight_vec.npy": np.ones(len(reaction_names)),
        "oracle_beta_291.npy": beta,
        "diff_99590.npy": np.asarray(diff_rows["99590"]),
        "diff_75302.npy": np.asarray(diff_rows["75302"]),
    }
    artifact_hashes = {}
    for filename, array in arrays.items():
        path = temp_dir / filename
        np.save(path, array)
        artifact_hashes[filename] = sha256(path)
    (temp_dir / "name_list_training.txt").write_text("\n".join(reaction_names) + "\n", encoding="utf-8")

    public_species = {
        name: {key: value for key, value in record.items() if key not in {"feature", "grid_diffs"}}
        for name, record in species_records.items()
    }
    manifest = {
        "schema_version": 1,
        "status": "calculation_complete",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path),
        "config_sha256": sha256(config_path),
        "reaction_spec": str(spec_path),
        "reaction_spec_sha256": sha256(spec_path),
        "reference_type": spec["reference"]["type"],
        "scientific_benchmark": bool(spec["reference"]["scientific_benchmark"]),
        "reference_warning": spec["reference"]["warning"],
        "feature_width": width,
        "species_count": len(species_records),
        "reaction_count": len(reaction_names),
        "species": public_species,
        "reactions": reaction_records,
        "artifacts_sha256": artifact_hashes,
    }
    (temp_dir / "reaction_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (temp_dir / "CALCULATION_COMPLETE").write_text(
        datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8"
    )
    temp_dir.rename(output_dir)
    print(f"Built {len(reaction_names)} reactions from {len(species_records)} species in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
