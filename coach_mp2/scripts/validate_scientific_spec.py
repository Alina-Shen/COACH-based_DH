"""Read-only semantic/source/freeze validator for COACH MP2 Step 1.

A PASS establishes the scientific contract, never chemistry/runtime readiness.
Stdlib only, Python >=3.9. Optional report writes are confined to the code root.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2')
HEAVY = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2')
SCRATCH = Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2')
SPEC = ROOT / 'configs/scientific_spec_v1.json'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    def invalid(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), parse_constant=invalid, object_pairs_hook=pairs)

def confined(path, roots=(CODE, HEAVY, SCRATCH)):
    """Resolve existing symlinks and reject sibling-prefix/path-traversal escapes."""
    resolved = Path(path).resolve()
    if not any(resolved == root.resolve() or root.resolve() in resolved.parents for root in roots):
        raise ValueError('Output outside authorized project roots: ' + str(path))
    return resolved

def semantic_checks(s):
    checks = {}
    def check(name, condition):
        checks[name] = bool(condition)
    try:
        check('identity', s['schema_version'] == 1 and s['specification_id'] == 'coach_mp2_M2_total_v1'
              and s['status'] == 'frozen_scientific_contract')
        check('scope', s['scope']['model'] == 'M2-total' and s['scope']['energy_only'] is True
              and s['scope']['self_consistent_double_hybrid'] is False)
        st = s['storage']
        check('three_write_roots', [st[k] for k in ('code_root','heavy_root','qchem_scratch_root')]
              == [str(CODE),str(HEAVY),str(SCRATCH)])
        check('isolated_publication', st['resolve_symlinks_before_writes'] is True
              and st['atomic_nonoverwriting_publication'] is True)
        p = s['parent']
        check('COACH_source', p['method']=='COACH' and p['engine']=='Q-Chem'
              and p['reference']=='UKS_all_species' and p['source_path'] is None)
        check('no_orbital_updates', p['new_scf_cycles']==0 and p['orbital_updates'] is False
              and p['same_archive_all_orbital_dependent_terms'] is True)
        check('archive_identity', p['copy_sha256_must_match'] is True and p['source_read_only'] is True
              and p['pt2_orbital_energies_and_denominators_require_native_identity_gate'] is True
              and p['missing_or_invalid_policy']=='stop_and_report_no_automatic_scf_fallback')
        e = s['energy']; q = s['qchem_feature_contract']; sl = s['semilocal']
        check('omega_consistency', e['omega']['value_bohr_inverse']==0.27
              and e['omega']['mode']=='fixed_for_initial_fit' and e['omega']['is_initial_guess'] is False
              and sl['exchange']['omega_bohr_inverse']==0.27 and q['OMEGA']==q['OMEGA2']==270
              and 'short_range_exchange_attenuation_at_omega_0p27' in sl['exchange']['correction_factors'])
        check('fixed_energy', e['fixed_terms']==['nuclear_repulsion','one_electron','coulomb','full_long_range_hf_exchange']
              and e['omega']['long_range_hf_fraction']==1.0)
        check('native_zero_scf', q['MAX_SCF_CYCLES']==0 and q['GEN_SCFMAN'] is False
              and q['SCF_GUESS']=='READ' and q['XC_FXC']==3 and q['MP2_RESTART_NO_SCF'] is True)
        check('matrix_extraction', q['printed_shape']==[96,180] and q['stored_shape']==[180,96]
              and q['block_policy']=='strict_final_complete_finite_block_record_count')
        l = s['feature_layout']
        check('292_layout', all(l[k]==v for k,v in {'total':292,'exchange':[0,96],'same_spin':[96,192],
          'opposite_spin':[192,288],'short_range_hf':288,'vv10':289,'pt2':290,'d4_atm':291,
          'selected_integrated_dv_rows':[64,154,166]}.items()))
        for channel,row,gamma,u_family in [('exchange',64,.004,'monomial'),
              ('same_spin_correlation',154,.01,'monomial'),('opposite_spin_correlation',166,.006,'legendre')]:
            c = sl[channel]
            check('semilocal_'+channel,c['integrated_dv_row']==row and c['variables']['u']['gamma']==gamma
                  and c['variables']['u']['polynomial_family']==u_family
                  and c['variables']['companion']['polynomial_family']=='legendre')
        check('flattening', sl['flattening']=={'order':'C','local_index':'8 * companion_degree + u_degree',
              'u_degree_range':[0,7],'companion_degree_range':[0,11]})
        check('VV10', e['vv10']['b']==5.5 and e['vv10']['C']==.01 and e['vv10']['grid']=='SG-1')
        check('pure_ATM', e['d4_atm']['parameters']==dict(s6=0.,s8=0.,s9=1.,a1=.215,a2=5.8,alp=16.))
        pt = e['pt2']
        check('total_PT2', pt['method']=='canonical_RI_UMP2' and pt['frozen_core'] is True
              and pt['denominator_regularization'] is None and pt['attenuation'] is None
              and pt['store_components']==['opposite_spin','same_spin']
              and pt['fitted_feature']=='OS_plus_SS' and pt['independent_spin_coefficients'] is False)
        co=s['constraints']
        check('C0_bounds', co['profile']=='C0_minimal_critical' and co['big_M']==25.
              and co['semilocal_bounds']==[-25.,25.] and co['short_range_hf_bounds']==[0.,1.]
              and co['scalar_bounds']=={k:[1e-8,.99999999] for k in ('vv10','pt2','d4_atm')})
        check('C0_support',co['mandatory_selected_slots']==[288,289,290,291]
              and co['support_constraint']=='sum(z)<=K' and co['mandatory_slots_count_toward_K'] is True
              and co['mandatory_SRHF_can_be_zero'] is True)
        check('C0_UEG_and_independent_scalars',co['ueg_exchange']=='gx(0,0)+c_sr_hf=1'
              and co['cross_scalar_equalities']==[] and co['one_electron_bound_enabled'] is False
              and co['sampled_enhancement_bounds_enabled'] is False)
        g=s['grids']
        check('three_grids', [g[k] for k in ('reference','practical','diagnostic')]==['250974','99590','75302']
              and g['pruning']=='none')
        check('grid_limits',g['threshold_kcal_per_mol']==.015 and g['internal_safety_factor']==.999
              and g['public_audit_slack_hartree']==0)
        check('grid_acceptance',g['pass1_constraints'] is False and g['pass2_constraints']=='selected_rows_only'
              and g['full_grid_violations']=='report_for_user_review_not_automatic_all_row_rejection')
        check('remaining_row_selection',g['selection']['top_per_candidate']==100
              and g['selection']['additional_remaining_l1']==200
              and g['selection']['candidate_pool']=='all_138_validated_COACH_discoveries'
              and g['selection']['freeze_before_pass2'] is True)
        check('units',s['units']['hartree_to_kcal_per_mol']==627.50947406)
        d=s['data_roles']; policy=s['data_policy']; sel=s['selection']
        check('fit_population',d['coefficient_fitting']['reactions']==1498
              and d['coefficient_fitting']['unique_species']==2799)
        check('development_roles',d['model_selection']['reactions']==8377
              and d['model_selection']['unique_species']==13907
              and d['model_selection']['independent_holdout_from_fitting'] is False)
        check('final_roles',d['final_assessment']['total_energy_reactions']==3462
              and d['final_assessment']['may_change_model'] is False
              and set(sel['protected_from_selection'])=={'SC74','OEEFD','L14','vL11','GDB_W1-F12','OPT'})
        check('no_leakage_or_silent_shrink',policy['random_point_split'] is False
              and policy['final_refit_on_all_GSCDB'] is False
              and policy['missing_species_or_reaction']=='stop_and_report_no_silent_exclusion'
              and sel['freeze_model_and_K_before_external_assessment'] is True)
        opt=s['optimization']
        check('objective',opt['objective_representation']=='expanded_quadratic' and opt['ridge']==1e-10
              and opt['objective']=='weighted_full_SSE_plus_ridge' and opt['selection_linkage']=='big_M'
              and opt['independent_audit']=='original_weighted_residual_space')
        check('solver_tolerances',opt['solver_parameters']==dict(FeasibilityTol=1e-9,IntFeasTol=1e-9,MIPGap=1e-4,MIPGapAbs=1e-10))
        check('campaign',opt['budgets']==list(range(14,83)) and opt['discovery_solves']==2*69
              and opt['selected_solves']==6*69 and opt['total_solves']==8*69
              and opt['seconds_per_solve']==7200 and opt['threads']==16)
        starts=opt['starts']; initial=[14,24,32,40,48,64,80]
        check('noise_mapping',starts['pass1_K_order']==initial+[k for k in range(14,83) if k not in initial]
              and starts['pass2_K_order']==list(range(14,83)) and starts['sigma']==.05
              and starts['noise_clip_or_project'] is False and starts['preceding_repeat_restart'] is False)
        check('readback',opt['candidate_readback']['precision']=='full_float64'
              and opt['candidate_readback']['hashes_exact'] is True
              and opt['candidate_readback']['report_tolerance_does_not_relax_feasibility'] is True)
        check('global_resource_policy',opt['resources']['global_WLS_sessions']==2
              and opt['resources']['global_active_Slurm_task_limit']==998
              and opt['resources']['automatic_failed_retries'] is False)
        f=s['future_options']['omega_scan']
        check('future_omega_disabled',f['enabled'] is False and f['grid'] is None and f['budget'] is None
              and f['timing']=='after_functional_design_choices_fixed' and f['parent_orbital_updates_implied'] is False)
        v=s['validation']
        check('no_transferred_runtime_pass',all(v[k] is False for k in
              ('native_COACH_gates_passed','orbital_inventory_complete','runtime_ready','submission_authorized')))
        check('no_transferred_release',s['change_control']['reference_completion_claims_transfer'] is False)
        check('finite_numbers',_finite(s))
    except (KeyError,TypeError,ValueError) as exc:
        checks['schema_shape'] = False
        checks['schema_error'] = str(exc)
    return checks

def _finite(value):
    if isinstance(value,float): return math.isfinite(value)
    if isinstance(value,dict): return all(_finite(v) for v in value.values())
    if isinstance(value,list): return all(_finite(v) for v in value)
    return True

def verify_hashes(files, root=ROOT):
    return bool(files) and all(digest(confined(root / f, (CODE,))) == h for f, h in files.items())

def validate(spec_path=SPEC, require_freeze=True):
    s=read(spec_path); checks=semantic_checks(s)
    idx=read(ROOT/'configs/step_index_v1.json'); lock=read(ROOT/'manifests/step_index_v1.freeze.json')
    checks['index_hash']=digest(ROOT/lock['path'])==lock['sha256']
    checks['index_ids']=[x['id'] for x in idx['steps']]==list(range(1,19))
    checks['optional_LMP2_nonblocking']=idx['steps'][6]['optional'] is True and all(
        7 not in x['prerequisites'] for x in idx['steps'])
    source=read(ROOT/'manifests/step1_sources_v1.json')
    checks['source_hashes']=all(Path(f['path']).is_file() and digest(f['path'])==f['sha256'] for f in source['files'])
    checks['source_inventory_nonempty']=len(source['files'])>=30
    database=read(ROOT/'results/step1_database_comparison.json')
    checks['database_tables_match']=database['all_parsed_records_identical'] is True
    # The historical preparation contract remains a guide; the scientific spec is authoritative.
    mirror=read(ROOT/'configs/mirror_contract_v1.json')
    checks['mirror_consistency']=mirror['target_omega']['value_bohr_inverse']==s['energy']['omega']['value_bohr_inverse'] and mirror['runtime_ready'] is False
    if require_freeze:
        freeze=read(ROOT/'manifests/scientific_spec_v1.freeze.json')
        checks['frozen_spec_identity']=digest(spec_path)==freeze['files']['configs/scientific_spec_v1.json']
        checks['freeze_manifest_hashes']=verify_hashes(freeze['files'])
    passed=all(value is True for value in checks.values())
    return {'passed':passed,'scope':'Step1 scientific contract only; no chemistry/runtime pass',
            'checks':checks,'spec_sha256':digest(spec_path),'validator_sha256':digest(__file__),
            'source_count':len(source['files']),'runtime_ready':False,'submission_authorized':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,default=SPEC)
    parser.add_argument('--pre-freeze',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        report=validate(args.spec,not args.pre_freeze)
        if args.output:
            path=confined(args.output,(CODE,))
            with path.open('x') as handle: json.dump(report,handle,indent=2,allow_nan=False);handle.write('\n')
        print(json.dumps(report,indent=2))
        return 0 if report['passed'] else 1
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'passed':False,'error':str(exc)}));return 1

if __name__=='__main__':
    raise SystemExit(main())
