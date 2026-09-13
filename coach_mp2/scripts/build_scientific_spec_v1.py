"""One-time construction of Step 1 scientific artifacts from reviewed read-only sources.

Run with the dh environment and -B. Existing scientific artifacts are never overwritten.
This builder does not run chemistry, import reference runners, or submit work.
"""
from pathlib import Path
import copy
import csv
import hashlib
import json
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
REF = REPO / 'revwb97m2'
GSCDB = Path('/clusterfs/mhg-data/yaoshen/GSCDB')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(relative, value):
    path = ROOT / relative
    with path.open('x') as handle:
        handle.write(json.dumps(value, indent=2, allow_nan=False) + '\n')

def main():
    reference = yaml.safe_load((REF / 'configs/scientific_spec.yaml').read_text())
    semilocal = copy.deepcopy(reference['semilocal_model'])
    for field in ('implementation_gate', 'rationale'):
        semilocal.pop(field, None)
    semilocal['exchange']['correction_factors'][0] = 'short_range_exchange_attenuation_at_omega_0p27'
    semilocal['exchange']['omega_bohr_inverse'] = 0.27
    semilocal['flattening'] = {'order': 'C', 'local_index': '8 * companion_degree + u_degree',
                              'u_degree_range': [0, 7], 'companion_degree_range': [0, 11]}
    contract = {
      'schema_version': 1, 'specification_id': 'coach_mp2_M2_total_v1',
      'status': 'frozen_scientific_contract', 'frozen_on': '2026-09-12',
      'step_index': 'configs/step_index_v1.json',
      'scope': {'model': 'M2-total', 'energy_only': True, 'full_coach_energy_domain': True,
                'excluded_initial_models': ['M1-total', 'M1-SCS', 'M2-SCS'],
                'self_consistent_double_hybrid': False},
      'storage': {
        'code_root': str(ROOT), 'heavy_root': '/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2',
        'qchem_scratch_root': '/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2',
        'project_notes_root': '/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh',
        'policy': 'write_only_three_project_roots_except_explicit_project_notes',
        'reference_roots_read_only': [str(REF), str(REPO/'coach'), str(GSCDB)],
        'scratch_is_not_only_copy_of_reproducibility_artifacts': True,
        'atomic_nonoverwriting_publication': True, 'resolve_symlinks_before_writes': True,
        'prohibit_cross_project_cache_reuse_without_identity_audit': True},
      'units': {'stored_energy': 'hartree', 'reported_error': 'kcal_per_mol',
                'hartree_to_kcal_per_mol': 627.50947406, 'omega': 'bohr^-1'},
      'parent': {'method': 'COACH', 'engine': 'Q-Chem', 'source_path': None,
        'source_path_status': 'awaiting_user_path_later_step5', 'reference': 'UKS_all_species',
        'archive': 'qarchive.h5', 'documented_omega_bohr_inverse': 0.27,
        'documented_short_range_hf_fraction': 0.22878980716640696,
        'actual_method_version_requires_source_audit': True, 'source_orbitals_self_consistent': True,
        'new_scf_cycles': 0, 'orbital_updates': False, 'same_archive_all_orbital_dependent_terms': True,
        'source_read_only': True, 'copy_sha256_must_match': True,
        'missing_or_invalid_policy': 'stop_and_report_no_automatic_scf_fallback',
        'reference_archive_counts_are_not_COACH_coverage': True,
        'diagnostics': ['spin_contamination', 'gap', 'available_stability_evidence'],
        'never_replace_orbital_solution_automatically': True,
        'pt2_orbital_energies_and_denominators_require_native_identity_gate': True},
      'molecular_inputs': {'database_root': str(GSCDB),
        'geometry_charge_multiplicity_basis_ecp_authority': 'matching_verified_GSCDB_input_records',
        'orbital_basis': 'per_species_no_uniform_override',
        'auxiliary_basis': 'matching_named_or_embedded_AUX_BASIS_CORR',
        'automatic_auxiliary_generation': False, 'counterpoise_correction': False,
        'metadata_role_validation_step': 3, 'input_archive_compatibility_step': 4,
        'on_difference_from_pinned_reference': 'stop_reconcile_and_version_before_use'},
      'energy': {'evaluation': 'non_self_consistent_on_fixed_COACH_orbitals',
        'omega': {'value_bohr_inverse': 0.27, 'mode': 'fixed_for_initial_fit',
                  'is_initial_guess': False, 'long_range_hf_fraction': 1.0},
        'fixed_terms': ['nuclear_repulsion', 'one_electron', 'coulomb', 'full_long_range_hf_exchange'],
        'equation': 'E_fixed + F_SL @ beta_SL + c_sr_hf*E_SRHF + c_vv10*E_VV10 + c_pt2*(E_OS+E_SS) + c_d4_atm*E_ATM',
        'vv10': {'b': 5.5, 'C': 0.01, 'coefficient': 'c_vv10', 'grid': 'SG-1',
                 'engine': 'Q-Chem_same_imported_archive', 'nonlinear_refit_initially': False},
        'd4_atm': {'coefficient': 'c_d4_atm', 'backend': 'dftd4', 'reference_version': '4.2.0',
          'parameters': {'s6': 0.0, 's8': 0.0, 's9': 1.0, 'a1': 0.215, 'a2': 5.8, 'alp': 16.0},
          'geometry_charge_only': True, 'reuse_requires_exact_input_parameter_backend_identity': True},
        'pt2': {'method': 'canonical_RI_UMP2', 'engine': 'Q-Chem_same_imported_archive',
          'frozen_core': True, 'frozen_core_definition': 'matching_QChem_input_and_verified_engine_convention',
          'denominator_regularization': None, 'attenuation': None,
          'store_components': ['opposite_spin', 'same_spin'], 'fitted_feature': 'OS_plus_SS',
          'independent_spin_coefficients': False, 'conventional_MP2': 'small_system_gateway_reference'},
        'parent_and_target_energy_reconstructions_separate': True},
      'semilocal': semilocal,
      'feature_layout': {'total': 292, 'exchange': [0,96], 'same_spin': [96,192],
        'opposite_spin': [192,288], 'short_range_hf': 288, 'vv10': 289, 'pt2': 290, 'd4_atm': 291,
        'interval_convention': 'zero_based_half_open', 'selected_integrated_dv_rows': [64,154,166]},
      'qchem_feature_contract': {'MAX_SCF_CYCLES': 0, 'GEN_SCFMAN': False, 'SCF_GUESS': 'READ',
        'XC_FXC': 3, 'OMEGA': 270, 'OMEGA2': 270,
        'QCHEM_PRINT_INTEGRATED_DV': '1', 'printed_shape': [96,180], 'stored_shape': [180,96],
        'block_policy': 'strict_final_complete_finite_block_record_count',
        'feature_engine_omega_must_match_target': True,
        'build_status': 'native_COACH_gateway_pending',
        'source_patch_policy': 'prepare_only_under_code_root_do_not_modify_external_QChem_tree',
        'MP2_RESTART_NO_SCF': True},
      'grids': {'reference': '250974', 'practical': '99590', 'diagnostic': '75302',
        'pruning': 'none', 'radii_adjustment': 'none', 'threshold_kcal_per_mol': 0.015,
        'internal_safety_factor': 0.999, 'public_audit_slack_hartree': 0.0,
        'pass1_constraints': False, 'pass2_constraints': 'selected_rows_only',
        'selection': {'candidate_pool': 'all_138_validated_COACH_discoveries', 'top_per_candidate': 100,
          'additional_remaining_l1': 200, 'deduplicate_rows': True, 'retain_duplicate_candidates': True,
          'tie_order': 'reference_numpy_argsort_then_reverse_on_identical_row_order',
          'freeze_before_pass2': True},
        'full_grid_violations': 'report_for_user_review_not_automatic_all_row_rejection',
        'zero_difference_features': ['short_range_hf','pt2','d4_atm'],
        'vv10_difference': 'zero_on_fixed_SG1_record_reason_nonzero_only_if_evaluated_on_both_grids'},
      'constraints': {'profile': 'C0_minimal_critical', 'big_M': 25.0,
        'semilocal_bounds': [-25.0,25.0], 'short_range_hf_bounds': [0.0,1.0],
        'scalar_bounds': {'vv10': [1e-8,0.99999999], 'pt2': [1e-8,0.99999999], 'd4_atm': [1e-8,0.99999999]},
        'mandatory_selected_slots': [288,289,290,291], 'mandatory_slots_count_toward_K': True,
        'mandatory_SRHF_can_be_zero': True, 'support_constraint': 'sum(z)<=K',
        'linkage': '-25*z_j <= beta_j <= 25*z_j',
        'ueg_exchange': 'gx(0,0)+c_sr_hf=1', 'cross_scalar_equalities': [],
        'one_electron_bound_enabled': False, 'sampled_enhancement_bounds_enabled': False,
        'dense_factor_audit_required': True},
      'data_roles': copy.deepcopy(reference['data_policy']['roles']),
      'data_policy': {'weights': 'pinned_COACH_SI_final_cycle_Table2',
        'row_order_and_stoichiometry': 'identical_to_pinned_reference', 'random_point_split': False,
        'missing_species_or_reaction': 'stop_and_report_no_silent_exclusion',
        'final_refit_on_all_GSCDB': False, 'OPT': 'excluded_from_initial_fixed_geometry_energy_scope',
        'metadata_records': 17658, 'energy_role_species_union': 17452, 'OPT_records': 206,
        'original_COACH_ATM_L14_vL11_exposure_caveat': True,
        'metadata_pointers': {'entries': str(REF/'manifests/weights/coach_si_table2_final_cycle_entries.csv'),
          'weights': str(REF/'manifests/weights/coach_si_table2_final_cycle_training_weights.csv'),
          'roles': str(REF/'manifests/data_roles/revwb97m2_data_roles_v2.yaml')},
        'pointers_are_read_only_provenance_not_COACH_validation': True},
      'optimization': {'solver': 'Gurobi', 'objective': 'weighted_full_SSE_plus_ridge',
        'equation': 'sum_k w_k*(A_k@beta-y_k)^2 + 1e-10*sum_j beta_j^2',
        'objective_representation': 'expanded_quadratic', 'independent_audit': 'original_weighted_residual_space',
        'ridge': 1e-10, 'ridge_scope': 'all_292_coefficients', 'selection_linkage': 'big_M',
        'solver_parameters': copy.deepcopy(reference['optimization']['solver_parameters']),
        'other_solver_parameters': 'inherit_current_reference_defaults_record_actual_environment',
        'threads': 16, 'seconds_per_solve': 7200, 'seed': 0,
        'budgets': list(range(14,83)), 'discovery_solves': 138, 'selected_solves': 414,
        'total_solves': 552, 'phases': ['discovery','shared_grid_freeze','selected'],
        'starts': {'pass1': ['simple'], 'pass2': ['simple','matching_K_pass1_repeat0','matching_K_pass1_repeat1'],
          'repeats': ['original','original_plus_gaussian_noise'], 'sigma': 0.05,
          'noise_scope': 'all_292_including_zeros', 'noise_clip_or_project': False,
          'pass1_K_order': [14,24,32,40,48,64,80] + [k for k in range(14,83) if k not in [14,24,32,40,48,64,80]],
          'pass2_K_order': list(range(14,83)), 'rng': 'numpy_default_rng_seed0_reset_once_per_pass',
          'precompute_and_hash_vectors': True,
          'simple_nonzero_coefficients': {'0':0.85,'1':1.0,'96':1.0,'192':1.0,'288':0.15,
            '289':0.99999999,'290':0.027300022669629182,'291':0.99999999},
          'simple_seed_role': 'paired_algorithmic_initialization_not_COACH_result',
          'require_new_matrix_start_audit': True, 'noisy_feasibility': 'report_suggestion_not_require',
          'preceding_repeat_restart': False},
        'candidate_readback': {'precision': 'full_float64', 'hashes_exact': True,
          'report_comparison_rtol': 1e-12, 'report_comparison_atol': 1e-15,
          'report_tolerance_does_not_relax_feasibility': True,
          'time_limit_incumbent': 'accept_only_if_independently_valid_report_gap_not_optimality',
          'missing_candidate': 'block_downstream_no_silent_omission'},
        'resources': {'memory_gib_proposal': 32, 'wall_minutes_proposal': 150,
          'global_WLS_sessions': 2, 'global_active_Slurm_task_limit': 998,
          'forbidden_route': 'lr_lowprio', 'automatic_failed_retries': False,
          'partition_account_qos': 'live_review_before_submission',
          'initial_budget_excludes_future_omega_scan': True}},
      'selection': {'primary': 'lowest_overall_mean_NER_among_eligible_candidates',
        'metrics': 'dataset_specific_errors_then_NER_then_category_and_overall_mean',
        'diagnostics': ['overfitting_NER','solver_gaps','repeat_stability','grid_outliers','dense_factors','coefficient_bounds','parameter_count'],
        'final_user_review': True,
        'protected_from_selection': ['SC74','OEEFD','L14','vL11','GDB_W1-F12','OPT'],
        'deferred_nonblocking_details': ['near_tie_tolerance','category_tradeoffs','historical_candidate_trace'],
        'freeze_model_and_K_before_external_assessment': True},
      'future_options': {'omega_scan': {'enabled': False, 'method': 'discrete_outer_scan_with_inner_refits',
          'timing': 'after_functional_design_choices_fixed', 'grid': None, 'budget': None,
          'required_recompute': ['semilocal_exchange','SRHF','LRHF_Nofit','reaction_matrices','grid_differences'],
          'parent_orbital_updates_implied': False},
        'LMP2': {'enabled': False, 'requires_separate_backend_validation': True},
        'SCS_PT2': {'enabled': False}, 'VV10_damping_scan': {'enabled': False}},
      'validation': {'scope_of_step1_pass': 'scientific_contract_and_tracking_index_only',
        'tolerances': {key:value for key,value in reference['validation'].items() if 'tolerance' in key or 'threshold' in key},
        'native_COACH_gates_passed': False, 'orbital_inventory_complete': False,
        'runtime_ready': False, 'submission_authorized': False,
        'later_required_gates': ['source_method_input_basis_identity','copy_hash_identity','zero_SCF_density_and_MO_identity',
          'PT2_orbital_energy_denominator_identity','native_three_grid_omega_0p27','native_scalar_fixed_energy_partition',
          'OS_SS_closure_and_conventional_RI_agreement','role_weight_and_matrix_identity',
          'C0_UEG_and_grid_constraints','atomic_restart_and_cross_project_rejection','optimizer_pilot_and_independent_readback',
          'resource_and_execution_release_review'],
        'unknown_source_path_does_not_block_scientific_freeze': True},
      'change_control': {'scientific_changes': 'new_version_rationale_and_affected_validation',
        'step_ids': 'never_renumber_or_reuse',
        'runtime_manifests': 'separate_versioned_artifacts_may_bind_source_path_without_rewriting_spec',
        'runtime_discovery_conflicts': 'stop_and_amend_spec_before_execution',
        'reference_completion_claims_transfer': False}
    }
    # Remove irrelevant published comparator tolerances: they are not COACH gates.
    contract['validation']['tolerances'] = {k:v for k,v in contract['validation']['tolerances'].items() if not k.startswith('published_wb97m2')}
    source_files = set(json.loads((ROOT/'manifests/revwb97m2_reference_v1.json').read_text())['files'])
    source_files.update(['coach/paper/COACH_2026MHG.pdf','coach/paper/SI_COACH_2026MHG.pdf',
      'coach/FunctionalCOACH/coach_pyscf.py','coach/1_data_generation/qchem_codes_insert.C',
      'coach/1_data_generation/pyscf_integrated_dv.py','revwb97m2/selective_grid_v1.py','coach/2_optimization/coachopt/analysis.py','coach/2_optimization/coachopt/select_diff_constraints.py',
      'revwb97m2/expanded_adapter.py','revwb97m2/fit_spec.py','revwb97m2/mio.py',
      'revwb97m2/environment/baseline.json','revwb97m2/manifests/gscdb137/source/DatasetEval.csv',
      'revwb97m2/manifests/gscdb137/source/Datasets.csv','revwb97m2/manifests/gscdb137/source/Standard_errors.csv'])
    sources = [{'path':str(REPO/f),'sha256':digest(REPO/f),'role':'read_only_scientific_or_implementation_reference'} for f in sorted(source_files)]
    comparisons = {}
    for name in ['DatasetEval.csv','Datasets.csv','Standard_errors.csv']:
        local = GSCDB/'Info'/name; pinned = REF/'manifests/gscdb137/source'/name
        sources.append({'path':str(local),'sha256':digest(local),'role':'user_named_database_authority'})
        with local.open(newline='') as h: a=list(csv.DictReader(h))
        with pinned.open(newline='') as h: b=list(csv.DictReader(h))
        comparisons[name] = {'byte_identical':digest(local)==digest(pinned),'parsed_records_identical':a==b,
                             'database_rows':len(a),'reference_rows':len(b)}
    write('configs/scientific_spec_v1.json',contract)
    write('manifests/step1_sources_v1.json',{'schema_version':1,
      'repository_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,universal_newlines=True).strip(),
      'files':sources,'runtime_dependency_lock':False,'reference_projects_modified':False})
    write('results/step1_database_comparison.json',{'scope':'three_metadata_tables_only_not_full_role_or_orbital_validation',
      'tables':comparisons,'all_parsed_records_identical':all(x['parsed_records_identical'] for x in comparisons.values())})
    print('Created v1 scientific specification, source identity inventory and GSCDB metadata comparison.')

if __name__ == '__main__':
    main()
