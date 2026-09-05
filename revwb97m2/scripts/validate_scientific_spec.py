#!/usr/bin/env python3
"""Validate the frozen revwb97m2 scientific specification.

This is intentionally independent of the fitting code. It catches semantic
drift in feature rows, polynomial families, energy partitioning, constraints,
and storage roots before expensive data generation begins.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
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


def sha256(path: Path) -> str:
    """Return the SHA-256 digest of one lightweight specification artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    parser.add_argument("--output", type=Path, help="Optional path for the complete JSON report")
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
    workspace_root = config_path.resolve().parents[2]
    checks.check("schema_version_6", config.get("schema_version") == 6)
    checks.check("status_frozen", config.get("status") == "frozen")

    spec = config["scientific_specification"]
    checks.check("specification_version_6", spec["version"] == 6)
    checks.check("authority_matches_path", spec["authority"] == "revwb97m2/configs/scientific_spec.yaml")
    checks.check(
        "validator_matches_path",
        spec["validator"] == "revwb97m2/scripts/validate_scientific_spec.py"
        and (workspace_root / spec["validator"]).is_file(),
    )
    checks.check(
        "validation_report_path_versioned",
        spec["validation_report"]
        == "revwb97m2/manifests/scientific_spec/scientific_spec_v6_validation.json",
    )
    checks.check(
        "version_5_archived",
        spec["supersedes"] == "revwb97m2/configs/archive/scientific_spec.v5.yaml",
    )
    archived_v5 = workspace_root / spec["supersedes"]
    checks.check(
        "version_5_archive_hash",
        archived_v5.is_file()
        and sha256(archived_v5) == spec["amendment"]["previous_specification_sha256"],
    )
    checks.check(
        "independent_dispersion_amendment_recorded",
        spec["amendment"]["decision"]
        == "add_independently_fitted_coach_d4_atm_and_remove_vv10_pt2_sum",
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
    checks.check("orbital_source_qchem", orbital["source_engine"] == "qchem")
    checks.check(
        "orbital_source_fixed",
        orbital["policy"] == "reuse_validated_qchem_qarchive_without_orbital_optimization"
        and orbital["source_orbitals_were_generated_self_consistently"] is True
        and orbital["self_consistent_in_this_workflow"] is False
        and orbital["orbital_optimization_in_this_workflow"] == "forbidden"
        and orbital["fixed_during_feature_generation_and_fitting"] is True,
    )
    checks.check("qchem_orbitals_are_inputs", orbital["qchem_orbitals_are_production_inputs"] is True)
    checks.check(
        "no_silent_scf_fallback",
        orbital["missing_or_invalid_archive_policy"]
        == "stop_and_report_without_silent_scf_fallback"
        and orbital["pyscf_fallback"]["never_selected_automatically"] is True,
    )

    authority_path = workspace_root / orbital["orbital_authority"]
    authority_report_path = workspace_root / orbital["orbital_authority_validation"]
    checks.check("qchem_orbital_authority_exists", authority_path.is_file(), str(authority_path))
    checks.check(
        "qchem_orbital_authority_report_exists",
        authority_report_path.is_file(),
        str(authority_report_path),
    )
    if authority_path.is_file() and authority_report_path.is_file():
        authority = yaml.safe_load(authority_path.read_text(encoding="utf-8"))
        authority_report = json.loads(authority_report_path.read_text(encoding="utf-8"))
        checks.check(
            "qchem_orbital_authority_passed",
            authority_report["passed"] is True
            and authority_report["status"] == "passed"
            and all(authority_report["checks"].values())
            and authority_report["policy_sha256"] == sha256(authority_path),
        )
        checks.check(
            "qchem_canonical_archive_contract",
            authority["canonical_gscdb"]["expected_species"]
            == orbital["canonical_archive_count"]
            == authority_report["details"]["canonical_inventory"]["present_regular_nonempty"]
            == 14006
            and authority["canonical_gscdb"]["orbital_root"]
            == orbital["canonical_archive_root"],
        )
        checks.check(
            "qchem_external_scope_policy",
            authority_report["details"]["bignc_inventory"]["present_regular_nonempty"] == 75
            and authority["external_scopes"]["GDB9_W1_F12"]["status"]
            == "blocked_no_validated_qchem_orbital_archive_authority"
            and authority["external_scopes"]["GDB9_W1_F12"]["prohibit_silent_pyscf_regeneration"]
            is True,
        )

    qchem_execution = orbital["qchem_execution"]
    checks.check(
        "qchem_zero_scf_contract",
        qchem_execution["maximum_scf_cycles"] == 0
        and qchem_execution["gen_scfman"] is False
        and qchem_execution["forbid_orbital_update"] is True,
    )
    checks.check(
        "qchem_integrated_dv_output_contract",
        qchem_execution["integrated_dv_environment_variable"] == "QCHEM_PRINT_INTEGRATED_DV"
        and qchem_execution["integrated_dv_environment_value"] == "1"
        and qchem_execution["integrated_dv_requires_mgga"] is True
        and qchem_execution["printed_matrix_shape"] == [96, 180]
        and qchem_execution["stored_matrix_convention"] == "transpose_printed_matrix_to_180x96"
        and qchem_execution["selected_rows_after_transpose"] == [64, 154, 166]
        and qchem_execution["feature_grids"] == [250974, 99590, 75302]
        and qchem_execution["same_spin_gamma"] == 0.01
        and qchem_execution["historical_same_spin_gamma_not_adopted"] == 0.2,
    )
    checks.check(
        "qchem_archive_copy_safety",
        orbital["authoritative_archives_are_read_only_inputs"] is True
        and orbital["run_from_isolated_nonoverwriting_copy"] is True
        and orbital["archive_copy_requires_matching_source_and_copy_sha256"] is True,
    )
    input_definition = orbital["input_definition"]
    checks.check("qchem_orbital_files_used", input_definition["orbital_files_used"] is True)
    checks.check(
        "qchem_archive_and_scratch_used",
        input_definition["qarchive_files_used"] is True
        and input_definition["scratch_orbital_directories_used"] is True,
    )
    checks.check("input_metadata_root_exists", Path(input_definition["metadata_source"]).is_dir())
    input_manifest = input_definition["immutable_pyscf_manifest"]
    input_manifest_policy = config_path.resolve().parents[2] / input_manifest["policy"]
    input_manifest_pointer = config_path.resolve().parents[2] / input_manifest["pointer"]
    input_snapshot = Path(input_manifest["snapshot_root"])
    input_snapshot_paths = {
        field: input_snapshot / input_manifest[field]
        for field in (
            "records",
            "index",
            "provenance",
            "validation",
            "checksum_manifest",
            "immutable_marker",
        )
    }
    checks.check("pyscf_input_policy_path_exists", input_manifest_policy.is_file())
    checks.check("pyscf_input_pointer_path_exists", input_manifest_pointer.is_file())
    checks.check("pyscf_input_snapshot_exists", input_snapshot.is_dir(), str(input_snapshot))
    for field, path in input_snapshot_paths.items():
        checks.check(f"pyscf_input_{field}_exists", path.is_file(), str(path))
    if input_manifest_policy.is_file() and input_manifest_pointer.is_file() and all(
        path.is_file() for path in input_snapshot_paths.values()
    ):
        policy = yaml.safe_load(input_manifest_policy.read_text(encoding="utf-8"))
        pointer = json.loads(input_manifest_pointer.read_text(encoding="utf-8"))
        copied_policy = input_snapshot / "policy.yaml"
        marker = json.loads(
            input_snapshot_paths["immutable_marker"].read_text(encoding="utf-8")
        )
        input_validation = json.loads(
            input_snapshot_paths["validation"].read_text(encoding="utf-8")
        )
        checksum_lines = input_snapshot_paths["checksum_manifest"].read_text(
            encoding="utf-8"
        ).splitlines()
        checksum_entries = {
            name: digest
            for digest, name in (line.split(maxsplit=1) for line in checksum_lines)
        }
        checks.check(
            "pyscf_input_manifest_hash_frozen",
            sha256(input_snapshot_paths["checksum_manifest"])
            == input_manifest["manifest_sha256"]
            == marker["manifest_sha256"],
        )
        checks.check(
            "pyscf_input_records_hash_frozen",
            sha256(input_snapshot_paths["records"])
            == input_manifest["records_sha256"],
        )
        checks.check(
            "pyscf_input_checksum_entries_pass",
            all(
                (input_snapshot / name).is_file()
                and sha256(input_snapshot / name) == digest
                for name, digest in checksum_entries.items()
            ),
        )
        checks.check(
            "pyscf_input_policy_snapshot_identity",
            copied_policy.is_file() and sha256(copied_policy) == sha256(input_manifest_policy),
        )
        checks.check(
            "pyscf_input_all_uks_policy",
            policy["pyscf_molecule"]["reference_policy"]["scf_class"] == "UKS"
            and policy["pyscf_molecule"]["reference_policy"]["closed_shell_singlet"] == "UKS"
            and policy["pyscf_molecule"]["reference_policy"]["open_shell"] == "UKS"
            and policy["pyscf_molecule"]["reference_policy"]["exceptions_allowed"] is False,
        )
        checks.check(
            "pyscf_input_pointer_identity",
            pointer["snapshot_root"] == str(input_snapshot)
            and pointer["qchem_orbitals_used"] is False
            and all(
                (input_snapshot / name).is_file()
                and sha256(input_snapshot / name) == digest
                for name, digest in pointer["artifacts"].items()
            ),
        )
        checks.check(
            "pyscf_input_validation_passed",
            input_validation["status"] == "passed"
            and all(input_validation["checks"].values()),
        )
        checks.check(
            "pyscf_input_snapshot_marker_complete",
            marker["status"] == "immutable_complete"
            and marker["record_count"] == input_manifest["record_count"] == 17658
            and marker["reference_policy"]
            == input_manifest["reference_policy"]
            == "UKS_for_all_species"
            and marker["basis_bridge_status"]
            == input_manifest["basis_bridge_status"]
            == "pending_step_6_semantic_translation_and_validation",
        )
        checks.check(
            "pyscf_input_snapshot_read_only",
            input_snapshot.stat().st_mode & 0o222 == 0
            and all(path.stat().st_mode & 0o222 == 0 for path in input_snapshot.iterdir()),
        )
        checks.check(
            "pyscf_input_scope_counts_frozen",
            input_manifest["energy_role_species"] == 17452
            and input_manifest["opt_geometry_species"] == 206,
        )
    checks.check(
        "pyscf_snapshot_is_fallback_only",
        input_manifest["role"] == "validated_nonproduction_fallback"
        and orbital["pyscf_fallback"]["status"]
        == "validated_nonproduction_fallback_and_cross_engine_regression"
        and orbital["pyscf_fallback"]["use_requires_explicit_new_authorization"] is True,
    )
    bridge = orbital["input_definition"]["validated_basis_bridge"]
    bridge_paths = {
        key: workspace_root / bridge[key]
        for key in ("policy", "resolved_records", "provenance", "validation", "bridge_module")
    }
    bridge_policy = yaml.safe_load(bridge_paths["policy"].read_text(encoding="utf-8"))
    bridge_provenance = json.loads(bridge_paths["provenance"].read_text(encoding="utf-8"))
    bridge_validation = json.loads(bridge_paths["validation"].read_text(encoding="utf-8"))
    with bridge_paths["resolved_records"].open(newline="", encoding="utf-8") as handle:
        bridge_rows = list(csv.DictReader(handle))
    checks.check(
        "pyscf_basis_bridge_artifact_hashes",
        sha256(bridge_paths["policy"]) == bridge["policy_sha256"]
        and sha256(bridge_paths["resolved_records"]) == bridge["resolved_records_sha256"]
        and sha256(bridge_paths["provenance"]) == bridge["provenance_sha256"]
        and sha256(bridge_paths["validation"]) == bridge["validation_sha256"],
    )
    checks.check(
        "pyscf_basis_bridge_passed_all_records",
        bridge["status"] == "passed"
        and bridge["record_count"] == len(bridge_rows) == 17658
        and bridge_validation["status"] == "passed"
        and all(bridge_validation["checks"].values())
        and all(row["runnable_status"] == "runnable_basis_metadata_validated" for row in bridge_rows),
    )
    checks.check(
        "pyscf_basis_bridge_source_boundary",
        bridge["role"] == "validated_nonproduction_pyscf_fallback"
        and bridge["source_snapshot_remains_immutable"] is True
        and bridge["source_snapshot_pending_marker_is_superseded_by_this_overlay"] is True
        and bridge["qchem_orbitals_used"] is False
        and bridge_policy["translation"]["orbitals_used"] is False
        and bridge_provenance["qchem_orbitals_used"] is False,
    )
    checks.check(
        "unrestricted_reference_policy",
        orbital["reference_policy"]["closed_shell_singlet"] == "unrestricted"
        and orbital["reference_policy"]["open_shell"] == "unrestricted",
    )
    checks.check("omega_0p3", orbital["range_separation"]["omega_bohr_inverse"] == 0.3)
    checks.check("full_lr_hf", orbital["range_separation"]["long_range_hf_fraction"] == 1.0)
    checks.check("expected_sr_hf_0p15", orbital["range_separation"]["expected_short_range_hf_fraction"] == 0.15)

    basis = orbital["basis"]
    checks.check(
        "gscdb_per_species_basis_policy",
        basis["policy"] == "per_species_from_authoritative_gscdb_manifest",
    )
    checks.check("uniform_basis_forbidden", basis["forbid_uniform_override"] is True)
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
    checks.check(
        "qchem_basis_used_directly",
        basis["production_definition_source"] == "matching_verified_qchem_input"
        and basis["require_pyscf_semantic_translation_validation"] is False
        and basis["use_qchem_named_or_embedded_basis_and_ecp_directly"] is True
        and basis["translate_generated_basis_and_ecp_sections_in_production"] is False,
    )
    checks.check(
        "pyscf_fallback_basis_semantic_translation_passed",
        basis["pyscf_fallback_semantic_translation_status"] == "passed_step_6"
        and workspace_root / basis["pyscf_fallback_semantic_translation_validation"]
        == bridge_paths["validation"],
    )

    energy = config["double_hybrid_energy"]
    checks.check(
        "same_qchem_archive_for_all_orbital_features",
        energy["orbital_source"] == "same_imported_qchem_qarchive_for_all_orbital_dependent_terms"
        and energy["forbid_mixing_qchem_semilocal_with_independently_optimized_pyscf_orbitals"]
        is True
        and energy["vv10"]["engine"] == "qchem_on_same_imported_archive"
        and energy["pt2"]["engine"] == "qchem_on_same_imported_archive",
    )
    checks.check("vv10_b10", energy["vv10"]["b"] == 10.0)
    checks.check("vv10_c001", energy["vv10"]["C"] == 0.01)
    d4 = energy["dispersion_policy"]["d4_atm"]
    checks.check(
        "coach_d4_atm_definition",
        energy["dispersion_policy"]["include_coach_d4_atm"] is True
        and d4["definition"] == "pure_three_body_coach_d4_atm"
        and d4["geometry_and_charge_only"] is True
        and d4["orbital_and_grid_independent"] is True
        and d4["damping_parameters"]
        == {"s6": 0.0, "s8": 0.0, "s9": 1.0, "a1": 0.215, "a2": 5.8, "alp": 16.0}
        and d4["fitted_coefficient_name"] == "c_d4_atm",
    )
    checks.check("total_pt2_fit", energy["pt2"]["fitted_feature"] == "total_pt2_correlation")
    checks.check("scs_pt2_diagnostic_only", energy["pt2"]["fit_spin_components_separately"] is False)
    checks.check(
        "three_independently_fitted_scalar_terms",
        energy["vv10"]["fitted_coefficient_name"] == "c_vv10"
        and energy["pt2"]["fitted_coefficient_name"] == "c_pt2"
        and energy["fitted_energy_terms"][-3:]
        == ["vv10_correlation_b10_c001", "total_pt2_correlation", "coach_pure_three_body_d4_atm"],
    )
    auxiliary_basis = energy["pt2"]["auxiliary_basis"]
    checks.check(
        "per_species_auxiliary_basis_policy",
        auxiliary_basis["policy"]
        == "use_matching_qchem_input_named_or_embedded_auxiliary_basis",
    )
    checks.check(
        "qchem_aux_basis_used_directly",
        auxiliary_basis["translate_generated_aux_basis_sections"] is False,
    )
    checks.check(
        "pyscf_aux_basis_mapping_is_fallback_only",
        auxiliary_basis["require_pyscf_alias_mapping_validation"] is False
        and auxiliary_basis["pyscf_translation_role"] == "validated_nonproduction_fallback",
    )
    checks.check(
        "aux_basis_external_policy_frozen",
        auxiliary_basis["missing_source_assignments"]
        == {
            "BigNC_external": "rimp2-def2-TZVPPD",
            "GDB9_W1_F12_external": "rimp2-def2-TZVP",
            "OPT_external": "rimp2-def2-QZVPPD",
        }
        and auxiliary_basis["automatic_runtime_auxiliary_basis_generation"] == "forbidden",
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

    kernel_gate = semilocal["implementation_gate"]
    kernel_path = workspace_root / kernel_gate["kernel"]
    kernel_validator_path = workspace_root / kernel_gate["validator"]
    kernel_report_path = workspace_root / kernel_gate["validation_report"]
    checks.check(
        "integrated_dv_reference_passed_native_pending",
        kernel_gate["status"] == "python_reference_passed_qchem_native_validation_pending_step_7",
    )
    checks.check(
        "integrated_dv_gate_names_feature_semantics",
        kernel_gate["test"] == "selected_integrated_dv_features_match_frozen_semantics",
    )
    checks.check("integrated_dv_selected_shape", kernel_gate["output_shape"] == [3, 96])
    checks.check(
        "integrated_dv_not_coach_coefficient_reproduction",
        kernel_gate["published_coach_coefficients_used"] is False,
    )
    emitter = kernel_gate["production_emitter"]
    checks.check(
        "qchem_integrated_dv_emitter_contract",
        emitter["engine"] == "qchem"
        and emitter["activation"] == "QCHEM_PRINT_INTEGRATED_DV=1"
        and emitter["printed_shape"] == [96, 180]
        and emitter["stored_shape_after_transpose"] == [180, 96]
        and emitter["selected_rows"] == [64, 154, 166]
        and emitter["source_level_status"] == "passed"
        and emitter["native_qchem_status"] == "pending_step_7",
    )
    checks.check("integrated_dv_kernel_exists", kernel_path.is_file(), str(kernel_path))
    checks.check(
        "integrated_dv_validator_exists", kernel_validator_path.is_file(), str(kernel_validator_path)
    )
    checks.check("integrated_dv_report_exists", kernel_report_path.is_file(), str(kernel_report_path))
    if kernel_path.is_file() and kernel_report_path.is_file():
        kernel_report = json.loads(kernel_report_path.read_text(encoding="utf-8"))
        checks.check("integrated_dv_report_passed", kernel_report["passed"] is True)
        checks.check(
            "integrated_dv_report_source_hash",
            kernel_report["kernel_source_sha256"] == sha256(kernel_path),
        )
        checks.check(
            "integrated_dv_report_target",
            kernel_report["target"]
            == "new omegaB97M(2)-form fit on fixed omegaB97M-V densities",
        )

    parent_policy_path = workspace_root / "revwb97m2/manifests/parent_scf/step8_parent_scf_v1.yaml"
    parent_report_path = workspace_root / "revwb97m2/manifests/parent_scf/validation.json"
    checks.check("pyscf_fallback_parent_policy_exists", parent_policy_path.is_file(), str(parent_policy_path))
    checks.check("pyscf_fallback_parent_report_exists", parent_report_path.is_file(), str(parent_report_path))
    if parent_policy_path.is_file() and parent_report_path.is_file():
        parent_policy = yaml.safe_load(parent_policy_path.read_text(encoding="utf-8"))
        parent_report = json.loads(parent_report_path.read_text(encoding="utf-8"))
        checks.check("pyscf_fallback_parent_step8_passed", parent_policy["status"] == "passed_step_8_gateway")
        checks.check("pyscf_fallback_parent_validation_passed", parent_report["status"] == "passed")
        checks.check(
            "pyscf_fallback_parent_module_hash_valid",
            parent_report["parent_module_sha256"]
            == sha256(workspace_root / parent_report["parent_module"]),
        )
        checks.check(
            "pyscf_fallback_checkpoint_density_feature_identity",
            parent_report["checks"]["checkpoint_density_bitwise_identity"] is True
            and parent_report["checks"]["checkpoint_feature_bitwise_identity"] is True,
        )
        checks.check(
            "pyscf_fallback_all_uks_and_no_qchem_orbitals",
            parent_report["checks"]["all_uks_policy"] is True
            and parent_report["checks"]["no_qchem_orbitals"] is True,
        )

    model = config["feature_models"]["models"]["R2_coachform_292"]
    checks.check(
        "model_rows_match_semantics",
        list(model["integrated_dv_rows"].values()) == [64, 154, 166],
    )
    layout = model["feature_layout"]
    checks.check("exchange_slice", layout["exchange"] == {"start": 0, "stop": 96})
    checks.check("same_spin_slice", layout["same_spin_correlation"] == {"start": 96, "stop": 192})
    checks.check("opposite_spin_slice", layout["opposite_spin_correlation"] == {"start": 192, "stop": 288})
    checks.check(
        "scalar_layout",
        [layout["short_range_hf"], layout["vv10"], layout["pt2"], layout["d4_atm"]]
        == [288, 289, 290, 291],
    )
    checks.check("feature_width_292", layout["total"] == 292)
    checks.check(
        "legacy_smoke_preserved",
        config["feature_models"]["legacy_smoke_baseline"]["integrated_dv_rows"] == [64, 153, 166],
    )

    constraints = config["constraint_profiles"]
    c0 = constraints["definitions"]["C0_minimal_critical"]
    checks.check("first_profile_c0_only", constraints["active_for_first_real_fit"] == ["C0_minimal_critical"])
    checks.check("c0_ueg_enabled", c0["exchange_uniform_electron_gas"]["enabled"] is True)
    checks.check("c0_sampled_bounds_disabled", c0["sampled_enhancement_bounds"]["enabled"] is False)
    checks.check("c0_nonlocal_sum_disabled", c0["nonlocal_correlation_sum"]["enabled"] is False)
    scalar_bounds = c0["independently_fitted_scalar_bounds"]
    checks.check(
        "independent_open_interval_scalar_bounds",
        scalar_bounds["conceptual_domain"] == "(0,1)"
        and scalar_bounds["strict_inequality_solver_policy"] == "use_fixed_interior_margin"
        and scalar_bounds["solver_margin"] == 1.0e-8
        and scalar_bounds["cross_feature_equalities"] == []
        and scalar_bounds["features"]
        == {
            "vv10": {"coefficient": "c_vv10", "minimum": 1.0e-8, "maximum": 0.99999999},
            "pt2": {"coefficient": "c_pt2", "minimum": 1.0e-8, "maximum": 0.99999999},
            "d4_atm": {"coefficient": "c_d4_atm", "minimum": 1.0e-8, "maximum": 0.99999999},
        },
    )
    checks.check(
        "vv10_pt2_sum_constraint_removed",
        "C1_nonlocal_sum" not in constraints["definitions"]
        and "c_vv10 + c_pt2" not in str(constraints),
    )

    grids = config["coach_feature_grids"]
    checks.check("feature_grid_ids", [grids[k]["id"] for k in ("fitting_reference", "practical", "coarse_analysis")] == ["250974", "99590", "75302"])
    checks.check("grid_constraint_pass2_only", config["grid_sensitivity"]["enabled_in_pass1"] is False and config["grid_sensitivity"]["enabled_in_pass2"] is True)
    checks.check("grid_threshold_0p015", config["grid_sensitivity"]["threshold_kcal_per_mol"] == 0.015)
    checks.check(
        "grid_independent_d4_zero_difference",
        "d4_atm" in config["grid_sensitivity"]["zero_difference_features"],
    )

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
    weight_fields = (
        "training_weights",
        "training_weight_entries",
        "training_weight_source",
        "training_weight_provenance",
        "training_weight_validation",
    )
    weight_paths = {field: workspace_root / data_policy[field] for field in weight_fields}
    for field, path in weight_paths.items():
        checks.check(f"{field}_path_exists", path.is_file(), str(path))
    if all(path.is_file() for path in weight_paths.values()):
        with weight_paths["training_weights"].open(newline="", encoding="utf-8-sig") as handle:
            weight_rows = list(csv.DictReader(handle))
        with weight_paths["training_weight_entries"].open(newline="", encoding="utf-8-sig") as handle:
            weight_entries = list(csv.DictReader(handle))
        weight_validation = json.loads(
            weight_paths["training_weight_validation"].read_text(encoding="utf-8")
        )
        weight_hashes = weight_validation["artifact_sha256"]
        checks.check("final_cycle2_weight_row_count_49", len(weight_rows) == 49)
        checks.check("final_cycle2_weight_entry_count_1498", len(weight_entries) == 1498)
        checks.check("final_cycle2_weight_validation_passed", weight_validation["status"] == "passed")
        checks.check(
            "final_cycle2_weight_validation_checks_passed",
            all(weight_validation["checks"].values()),
        )
        checks.check(
            "final_cycle2_weight_artifact_hashes",
            sha256(weight_paths["training_weights"]) == weight_hashes["training_weights_csv"]
            and sha256(weight_paths["training_weight_entries"])
            == weight_hashes["expanded_entries_csv"]
            and sha256(weight_paths["training_weight_source"])
            == weight_hashes["transcription_yaml"]
            and sha256(weight_paths["training_weight_provenance"])
            == weight_hashes["provenance_json"],
        )
    role_fields = (
        "data_role_policy",
        "dataset_roles",
        "reaction_roles",
        "species_roles",
        "qchem_input_metadata",
        "data_role_provenance",
        "data_role_validation",
    )
    role_paths = {field: workspace_root / data_policy[field] for field in role_fields}
    for field, path in role_paths.items():
        checks.check(f"{field}_path_exists", path.is_file(), str(path))
    if all(path.is_file() for path in role_paths.values()):
        role_policy = yaml.safe_load(role_paths["data_role_policy"].read_text(encoding="utf-8"))
        role_validation = json.loads(
            role_paths["data_role_validation"].read_text(encoding="utf-8")
        )
        with role_paths["dataset_roles"].open(newline="", encoding="utf-8-sig") as handle:
            dataset_roles = list(csv.DictReader(handle))
        with role_paths["reaction_roles"].open(newline="", encoding="utf-8-sig") as handle:
            reaction_roles = list(csv.DictReader(handle))
        with role_paths["species_roles"].open(newline="", encoding="utf-8-sig") as handle:
            species_roles = list(csv.DictReader(handle))
        with role_paths["qchem_input_metadata"].open(newline="", encoding="utf-8-sig") as handle:
            qchem_input_metadata = list(csv.DictReader(handle))
        role_hashes = role_validation["artifact_sha256"]
        checks.check("data_role_validation_passed", role_validation["status"] == "passed")
        checks.check(
            "data_role_validation_checks_passed", all(role_validation["checks"].values())
        )
        checks.check(
            "data_role_artifact_hashes",
            sha256(role_paths["data_role_policy"]) == role_hashes["policy_yaml"]
            and sha256(role_paths["dataset_roles"]) == role_hashes["dataset_roles_csv"]
            and sha256(role_paths["reaction_roles"]) == role_hashes["reaction_roles_csv"]
            and sha256(role_paths["species_roles"]) == role_hashes["species_roles_csv"]
            and sha256(role_paths["qchem_input_metadata"])
            == role_hashes["qchem_input_metadata_csv"]
            and sha256(role_paths["data_role_provenance"]) == role_hashes["provenance_json"],
        )
        checks.check("data_role_dataset_count_142", len(dataset_roles) == 142)
        checks.check("data_role_reaction_count_11839", len(reaction_roles) == 11839)
        checks.check("data_role_species_count_17452", len(species_roles) == 17452)
        checks.check("qchem_input_metadata_count_17658", len(qchem_input_metadata) == 17658)
        checks.check(
            "data_role_geometry_authority",
            role_policy["geometry_and_basis_authority"]["policy"]
            == "parse_verified_immutable_qchem_inputs_but_never_qchem_orbitals"
            and role_policy["geometry_and_basis_authority"]["orbital_files_used"] is False,
        )
        checks.check(
            "qchem_input_metadata_manifest_linked",
            input_definition["parsed_metadata_manifest"] == data_policy["qchem_input_metadata"],
        )
    roles = data_policy["roles"]
    checks.check(
        "coefficient_fitting_role_locked",
        roles["coefficient_fitting"]["reactions"] == 1498
        and roles["coefficient_fitting"]["unique_species"] == 2799,
    )
    checks.check(
        "gscdb_model_selection_role_locked",
        roles["model_selection"]["reactions"] == 8377
        and roles["model_selection"]["unique_species"] == 13907
        and roles["model_selection"]["independent_holdout_from_fitting"] is False,
    )
    checks.check(
        "overfitting_role_locked",
        roles["overfitting_diagnostic"]["datasets"] == ["AE11", "MB08-165", "MB16-43"]
        and roles["overfitting_diagnostic"]["reactions"] == 219,
    )
    checks.check(
        "external_final_role_locked",
        roles["final_assessment"]["appended_datasets"] == ["SC74", "OEEFD"]
        and roles["final_assessment"]["appended_reactions"] == 71
        and roles["final_assessment"]["BigNC_datasets"] == ["L14", "vL11"]
        and roles["final_assessment"]["GDB9_W1_F12_datasets"] == ["GDB_W1-F12"]
        and roles["final_assessment"]["total_energy_reactions"] == 3462
        and roles["final_assessment"]["may_change_model"] is False,
    )
    bignc = data_policy["external_evaluation"]["BigNC"]
    checks.check(
        "bignc_separate_external_evaluation",
        bignc["part_of_gscdb137"] is False and bignc["part_of_training"] is False,
    )
    checks.check(
        "bignc_inputs_verified_without_orbital_inference",
        bignc["input_metadata_status"]
        == "available_in_verified_pinned_official_qchem_input_snapshot"
        and bignc["forbid_geometry_or_basis_inference_from_orbitals"] is True,
    )
    appended = data_policy["external_evaluation"]["appended_groups"]
    checks.check(
        "appended_external_final_groups",
        appended["datasets"] == ["SC74", "OEEFD"]
        and appended["part_of_gscdb137"] is False
        and appended["part_of_training"] is False,
    )
    checks.check("random_point_split_forbidden", data_policy["forbid_random_point_level_split"] is True)
    checks.check(
        "no_unversioned_gscdb_refit",
        data_policy["final_refit_on_all_gscdb137"]
        == "forbidden_without_new_specification_version",
    )

    protocol = config["execution_protocol"]
    checks.check(
        "zero_new_parent_orbital_cycles",
        protocol["base_orbital_training_cycles"] == 0
        and protocol["source_orbitals"] == "precomputed_self_consistent_qchem_wb97m_v_archives",
    )
    checks.check("no_parent_update", protocol["update_parent_orbitals_from_fitted_model"] is False)
    checks.check(
        "final_cycle2_weight_source",
        protocol["fitting_selection_and_weights"] == "updated_coach_si_final_cycle_table_2",
    )
    checks.check(
        "weight_manifest_gate_closed",
        protocol["fitting_weight_manifest"] == data_policy["training_weights"]
        and protocol["fitting_weight_entries_manifest"] == data_policy["training_weight_entries"]
        and protocol["fitting_weight_validation"] == data_policy["training_weight_validation"],
    )
    checks.check("two_numerical_grid_passes", protocol["numerical_grid_optimization_passes"] == 2)

    optimization = config["optimization"]
    checks.check(
        "selection_uses_locked_development_metrics",
        optimization["selection_uses"][:2]
        == ["gscdb137_dataset_and_category_NER", "overfitting_diagnostic_mean_NER"],
    )
    checks.check(
        "external_final_errors_forbidden_for_selection",
        optimization["selection_must_not_use"]
        == [
            "SC74_error",
            "OEEFD_error",
            "BigNC_error",
            "GDB9_W1_F12_error",
            "OPT_error",
            "final_test_error",
        ],
    )

    validation = config["validation"]
    gateway_report = workspace_root / validation["passed_rimp2_gateway_report"]
    checks.check("rimp2_gateway_report_exists", gateway_report.is_file(), str(gateway_report))
    if gateway_report.is_file():
        gateway = json.loads(gateway_report.read_text(encoding="utf-8"))
        checks.check("rimp2_gateway_passed", gateway["passed"] is True)
        checks.check(
            "rimp2_gateway_parent_tolerance",
            abs(gateway["differences"]["parent_pyscf_minus_qchem_hartree"])
            <= validation["cross_engine_parent_tolerance_hartree"],
        )
        checks.check(
            "rimp2_gateway_os_tolerance",
            abs(gateway["differences"]["scaled_os_pyscf_minus_qchem_hartree"])
            <= validation["cross_engine_scaled_os_rimp2_tolerance_hartree"],
        )
        ri_difference_kcal = abs(gateway["differences"]["ri_minus_conventional_total_hartree"]) * project["units"]["hartree_to_kcal_per_mol"]
        checks.check(
            "rimp2_gateway_conventional_reference",
            ri_difference_kcal <= validation["ri_mp2_vs_conventional_threshold_kcal_per_mol"],
            ri_difference_kcal,
        )

    required_gates = validation["required_gates_before_pilot"]
    expected_qchem_gates = {
        "qchem_orbital_authority_14006_complete",
        "qchem_full_build_and_binary_provenance",
        "qchem_archive_copy_hash_identity",
        "qchem_integrated_dv_delimiters_shape_and_finite_values",
        "qchem_restricted_and_unrestricted_three_grid_gateway",
        "qchem_final_complete_block_extractor",
        "qchem_same_archive_scalar_feature_identity",
    }
    checks.check("qchem_production_gates_required", expected_qchem_gates.issubset(required_gates))
    checks.check(
        "d4_and_independent_bound_gates_required",
        {"coach_d4_atm_definition_and_energy_validation", "independent_open_interval_scalar_coefficient_bounds"}
        .issubset(required_gates),
    )
    checks.check(
        "pyscf_production_gates_removed",
        not any(gate.startswith("pyscf_") or "all_uks_pyscf" in gate for gate in required_gates),
    )
    checks.check(
        "locked_data_role_gate_required_and_passed",
        "locked_data_roles_and_qchem_input_metadata" in required_gates
        and (workspace_root / validation["passed_data_role_validation"]).is_file(),
    )
    checks.check(
        "qchem_orbital_authority_gate_passed",
        "qchem_orbital_authority_14006_complete" in required_gates
        and workspace_root / validation["passed_qchem_orbital_authority_validation"]
        == authority_report_path,
    )

    safety = config["safety"]
    checks.check(
        "qchem_production_input_and_archive_safety",
        safety["qchem_orbitals_must_be_used_as_production_inputs"] is True
        and safety["authoritative_qchem_archives_must_not_be_modified"] is True
        and safety["qchem_runs_require_isolated_verified_archive_copy"] is True
        and safety["missing_or_invalid_qchem_archive_must_stop"] is True
        and safety["silent_pyscf_scf_fallback_forbidden"] is True
        and safety["production_qchem_requires_zero_scf_cycles"] is True,
    )
    checks.check("qchem_code_backup_exists", (workspace_root / safety["qchem_route_code_backup"]).is_dir())
    checks.check("qchem_smoke_backup_exists", Path(safety["qchem_route_smoke_backup"]).is_dir())

    checks.details["config"] = str(config_path.resolve())
    checks.details["config_sha256"] = sha256(config_path)
    checks.details["validator_sha256"] = sha256(Path(__file__).resolve())
    return checks


def main() -> int:
    args = parse_args()
    with args.config.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    checks = validate(config, args.config)
    report = {"passed": checks.passed, "checks": checks.results, "details": checks.details}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
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
