#!/usr/bin/env python3
"""Validate the frozen revwb97m2 scientific specification.

This is intentionally independent of the fitting code. It catches semantic
drift in feature rows, polynomial families, energy partitioning, constraints,
and storage roots before expensive data generation begins.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required to validate the scientific specification") from exc


FAMILY_NAMES = {
    0: "exchange_mgga",
    1: "exchange_mgga_with_nonuniform_scaling",
    2: "range_separated_mgga",
    3: "range_separated_mgga_with_nonuniform_scaling",
    4: "pw92_same_spin",
    5: "pw92_same_spin_with_self_correlation_correction",
    6: "pw92_opposite_spin",
    7: "scan_alpha1_same_spin",
    8: "scan_alpha1_same_spin_with_self_correlation_correction",
    9: "scan_alpha1_opposite_spin",
}
POLYNOMIAL_NAMES = ("monomial", "legendre", "chebyshev")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=root / "configs" / "scientific_spec.yaml",
        help="Frozen scientific specification YAML",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a text report")
    return parser.parse_args()


def decode_integrated_dv_row(row: int) -> dict[str, Any]:
    """Decode one 0-based integratedDV row using the maintained COACH layout."""
    if row not in range(180):
        raise ValueError(f"integratedDV row must be in [0, 179], got {row}")
    family_index, group = divmod(row, 18)
    companion_variable = "w" if group < 9 else "beta_f"
    basis_index = group % 9
    u_family = POLYNOMIAL_NAMES[basis_index // 3]
    companion_family = POLYNOMIAL_NAMES[basis_index % 3]
    return {
        "row": row,
        "family_index": family_index,
        "family": FAMILY_NAMES[family_index],
        "group": group,
        "u_polynomial_family": u_family,
        "companion_variable": companion_variable,
        "companion_polynomial_family": companion_family,
    }


class Checks:
    def __init__(self) -> None:
        self.results: dict[str, bool] = {}
        self.details: dict[str, Any] = {}

    def check(self, name: str, condition: bool, detail: Any | None = None) -> None:
        self.results[name] = bool(condition)
        if detail is not None:
            self.details[name] = detail

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(self.results.values())


def validate(config: dict[str, Any], config_path: Path) -> Checks:
    checks = Checks()
    checks.check("schema_version_2", config.get("schema_version") == 2)
    checks.check("status_frozen", config.get("status") == "frozen")

    spec = config["scientific_specification"]
    checks.check("specification_version_2", spec["version"] == 2)
    checks.check("authority_matches_path", spec["authority"] == "revwb97m2/configs/scientific_spec.yaml")
    checks.check(
        "version_1_archived",
        spec["supersedes"] == "revwb97m2/configs/archive/scientific_spec.v1.yaml",
    )
    checks.check(
        "basis_amendment_recorded",
        spec["amendment"]["decision"] == "follow_authoritative_gscdb_per_species_basis_assignments",
    )

    project = config["project"]
    vc_root = Path(project["version_controlled_root"])
    data_root = Path(project["heavy_data_root"])
    checks.check(
        "version_controlled_root",
        vc_root == Path("/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2"),
    )
    checks.check(
        "heavy_data_root",
        data_root == Path("/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2"),
    )

    orbital = config["orbital_source"]
    copy_root = Path(orbital["verified_copy_root"])
    checks.check("orbital_source_qchem", orbital["source_engine"] == "qchem")
    checks.check("orbital_source_fixed", orbital["policy"] == "copy_then_read_without_orbital_optimization")
    checks.check("orbital_copy_under_heavy_root", copy_root.is_relative_to(data_root), str(copy_root))
    checks.check("omega_0p3", orbital["range_separation"]["omega_bohr_inverse"] == 0.3)
    checks.check("full_lr_hf", orbital["range_separation"]["long_range_hf_fraction"] == 1.0)
    checks.check("expected_sr_hf_0p15", orbital["range_separation"]["expected_short_range_hf_fraction"] == 0.15)

    basis = orbital["basis"]
    checks.check(
        "gscdb_per_species_basis_policy",
        basis["policy"] == "per_species_from_authoritative_gscdb_manifest",
    )
    checks.check("uniform_basis_forbidden", basis["forbid_uniform_override"] is True)
    workspace_root = config_path.resolve().parents[2]
    basis_manifest = workspace_root / basis["manifest"]
    with basis_manifest.open(newline="", encoding="utf-8") as handle:
        manifest_rows = list(csv.DictReader(handle))
    core_rows = [row for row in manifest_rows if row[basis["scope_field"]] == basis["core_scope_value"]]
    observed_basis_distribution = Counter(row[basis["basis_field"]] for row in core_rows)
    checks.check(
        "gscdb_core_species_count",
        len(core_rows) == basis["expected_core_species"] == 13907,
        len(core_rows),
    )
    checks.check(
        "gscdb_basis_distribution",
        observed_basis_distribution == Counter(basis["expected_core_distribution"]),
        dict(observed_basis_distribution),
    )
    checks.check("qchem_basis_semantic_match_required", basis["require_qchem_input_semantic_match"] is True)
    checks.check("generated_orbital_basis_preserved", basis["preserve_generated_basis_sections"] is True)

    energy = config["double_hybrid_energy"]
    checks.check("vv10_b10", energy["vv10"]["b"] == 10.0)
    checks.check("vv10_c001", energy["vv10"]["C"] == 0.01)
    checks.check("no_coach_d4", energy["dispersion_policy"]["include_coach_d4_atm"] is False)
    checks.check("total_pt2_fit", energy["pt2"]["fitted_feature"] == "total_pt2_correlation")
    checks.check("scs_pt2_diagnostic_only", energy["pt2"]["fit_spin_components_separately"] is False)
    auxiliary_basis = energy["pt2"]["auxiliary_basis"]
    checks.check(
        "per_species_auxiliary_basis_policy",
        auxiliary_basis["policy"] == "preserve_per_species_qchem_input",
    )
    checks.check(
        "generated_aux_basis_preserved",
        auxiliary_basis["preserve_generated_aux_basis_sections"] is True,
    )
    checks.check(
        "qchem_aux_basis_authoritative",
        auxiliary_basis["qchem_input_is_authoritative_on_disagreement"] is True,
    )
    checks.check(
        "fixed_energy_partition",
        energy["fixed_energy_terms"]
        == ["nuclear_repulsion", "one_electron", "coulomb", "full_long_range_hf_exchange"],
    )

    semilocal = config["semilocal_model"]
    expected_semantics = {
        "exchange": {
            "row": 64,
            "family": "range_separated_mgga_with_nonuniform_scaling",
            "u": "monomial",
            "companion_variable": "beta_f",
            "companion": "legendre",
        },
        "same_spin_correlation": {
            "row": 154,
            "family": "scan_alpha1_same_spin_with_self_correlation_correction",
            "u": "monomial",
            "companion_variable": "beta_f",
            "companion": "legendre",
        },
        "opposite_spin_correlation": {
            "row": 166,
            "family": "scan_alpha1_opposite_spin",
            "u": "legendre",
            "companion_variable": "w",
            "companion": "legendre",
        },
    }
    decoded_rows: dict[str, Any] = {}
    for channel, expected in expected_semantics.items():
        channel_spec = semilocal[channel]
        decoded = decode_integrated_dv_row(channel_spec["integrated_dv_row"])
        decoded_rows[channel] = decoded
        checks.check(f"{channel}_row", decoded["row"] == expected["row"], decoded)
        checks.check(f"{channel}_family", decoded["family"] == expected["family"], decoded)
        checks.check(f"{channel}_u_polynomial", decoded["u_polynomial_family"] == expected["u"], decoded)
        checks.check(
            f"{channel}_companion_variable",
            decoded["companion_variable"] == expected["companion_variable"],
            decoded,
        )
        checks.check(
            f"{channel}_companion_polynomial",
            decoded["companion_polynomial_family"] == expected["companion"],
            decoded,
        )
        checks.check(
            f"{channel}_declared_u_polynomial",
            channel_spec["variables"]["u"]["polynomial_family"] == expected["u"],
        )
        checks.check(
            f"{channel}_declared_companion_polynomial",
            channel_spec["variables"]["companion"]["polynomial_family"] == expected["companion"],
        )
    checks.details["decoded_integrated_dv_rows"] = decoded_rows

    model = config["feature_models"]["models"]["R2_coachform_291"]
    checks.check(
        "model_rows_match_semantics",
        list(model["integrated_dv_rows"].values()) == [64, 154, 166],
    )
    layout = model["feature_layout"]
    checks.check("exchange_slice", layout["exchange"] == {"start": 0, "stop": 96})
    checks.check("same_spin_slice", layout["same_spin_correlation"] == {"start": 96, "stop": 192})
    checks.check("opposite_spin_slice", layout["opposite_spin_correlation"] == {"start": 192, "stop": 288})
    checks.check("scalar_layout", [layout["short_range_hf"], layout["vv10"], layout["pt2"]] == [288, 289, 290])
    checks.check("feature_width_291", layout["total"] == 291)
    checks.check(
        "legacy_smoke_preserved",
        config["feature_models"]["legacy_smoke_baseline"]["integrated_dv_rows"] == [64, 153, 166],
    )

    constraints = config["constraint_profiles"]
    c0 = constraints["definitions"]["C0_minimal_critical"]
    c1 = constraints["definitions"]["C1_nonlocal_sum"]
    checks.check("first_profiles_c0_c1", constraints["active_for_first_real_fit"] == ["C0_minimal_critical", "C1_nonlocal_sum"])
    checks.check("c0_ueg_enabled", c0["exchange_uniform_electron_gas"]["enabled"] is True)
    checks.check("c0_sampled_bounds_disabled", c0["sampled_enhancement_bounds"]["enabled"] is False)
    checks.check("c0_nonlocal_sum_disabled", c0["nonlocal_correlation_sum"]["enabled"] is False)
    checks.check("c1_nonlocal_sum_enabled", c1["nonlocal_correlation_sum"]["enabled"] is True)

    grids = config["coach_feature_grids"]
    checks.check("feature_grid_ids", [grids[k]["id"] for k in ("fitting_reference", "practical", "coarse_analysis")] == ["250974", "99590", "75302"])
    checks.check("grid_constraint_pass2_only", config["grid_sensitivity"]["enabled_in_pass1"] is False and config["grid_sensitivity"]["enabled_in_pass2"] is True)
    checks.check("grid_threshold_0p015", config["grid_sensitivity"]["threshold_kcal_per_mol"] == 0.015)

    data_policy = config["data_policy"]
    checks.check("target_gscdb137", data_policy["target_database"] == "GSCDB137")
    checks.check("metadata_gate_active", data_policy["must_set_metadata_paths_before_fit"] is True)
    for field in (
        "reaction_metadata",
        "dataset_information",
        "standard_errors",
        "species_manifest",
        "source_provenance",
    ):
        path = workspace_root / data_policy[field]
        checks.check(f"{field}_path_exists", path.is_file(), str(path))
    checks.check("training_weights_still_open", data_policy["training_weights"] is None)
    bignc = data_policy["external_evaluation"]["BigNC"]
    checks.check(
        "bignc_separate_external_evaluation",
        bignc["part_of_gscdb137"] is False and bignc["part_of_training"] is False,
    )
    checks.check("random_point_split_forbidden", data_policy["forbid_random_point_level_split"] is True)

    checks.details["config"] = str(config_path.resolve())
    return checks


def main() -> int:
    args = parse_args()
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    checks = validate(config, args.config)
    report = {"passed": checks.passed, "checks": checks.results, "details": checks.details}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for name, passed in checks.results.items():
            print(f"{'PASS' if passed else 'FAIL'} {name}")
        print(f"\nScientific specification: {'PASS' if checks.passed else 'FAIL'}")
        print(f"Config: {args.config.resolve()}")
    return 0 if checks.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
