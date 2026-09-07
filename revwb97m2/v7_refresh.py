"""Bounded Step14-cohort VV10 refresh. No new SCF or PT2 generation.

All public operations are explicit: freeze, run one species, then assemble.
Historical outputs remain read-only and failures/partial directories are kept.
"""
import json
import shutil
from pathlib import Path
import numpy as np
from revwb97m2.fit_spec import ROOT, load_fit_settings
from revwb97m2.fit_inputs import ARRAYS, digest, load_inputs
from revwb97m2.qchem_scalar_features import derive_scalar_input, tree_manifest, parse_qchem_fixed_energy_output
from revwb97m2.qchem_feature_publisher import validate_published_artifact
from revwb97m2.step14_recovery_v2 import scalar_values, fixed_energy
from revwb97m2.reaction_assembly import assemble_reaction_arrays
from revwb97m2.scripts.run_step13_fresh_species import canonical_tree_hash, run_qchem, QCHEM_ROOT

COHORT = ROOT/'manifests/reaction_features/step14_real_reaction_cohort_v1.json'
BASELINE = ROOT/'manifests/reaction_features/step14_recovery_complete_v2.json'
GRIDS = ('99590','75302')


def read(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    with Path(path).open('x') as handle:
        json.dump(obj,handle,indent=2,sort_keys=True,allow_nan=False)
        handle.write('\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_vector(path):
    value=np.load(path,allow_pickle=False)
    require(value.shape==(292,) and np.isfinite(value).all(),'invalid species vector')
    return value


def legacy_fixed_values(text, sr_hf, *, recovered):
    """Preserve the validated ordinary/recovery parser, including print precision."""
    parser=fixed_energy if recovered else parse_qchem_fixed_energy_output
    return parser(text,sr_hf)


def legacy_species(case, entry, cohort):
    """Recheck recovery semantics without rerunning historical hash-pinned drivers."""
    name=case['species'];artifact=Path(entry['artifact'])
    original=Path(cohort['run_root'])/case['scope']/name
    recovered=entry['recovered']
    marker='RECOVERY_COMPLETE' if recovered else 'REACTION_READY_COMPLETE'
    require((artifact/marker).is_file(),'missing legacy completion marker')
    vector=checked_vector(artifact/'feature_vector_292.npy')
    require(digest(artifact/'feature_vector_292.npy')==entry['vector_sha256'],'changed legacy vector')
    require(digest(case['authoritative_input'])==case['authoritative_input_sha256'],'changed source input')
    scalar=original/'gateway_work/scalar/qchem.out'
    pt2=original/'gateway_work/scalar/qchem.pt2.out'
    one=name=='W4-17_h'
    values=scalar_values(scalar.read_text(),None if one else pt2.read_text(),one_electron=one)
    require(np.array_equal(vector[288:291],[values[k] for k in
        ('short_range_hf_hartree','vv10_hartree','pt2_total_hartree')]),'legacy scalar mismatch')
    fixed_file=artifact/'fixed_energy.json';payload=read(fixed_file)
    fixed_values=payload if recovered else payload['values']
    fixed_output=artifact/'fixed/qchem.out' if recovered else original/'gateway_work/fixed_energy/qchem.out'
    rederived=legacy_fixed_values(fixed_output.read_text(),vector[288],recovered=recovered)
    require(abs(rederived['fixed_energy_hartree']-fixed_values['fixed_energy_hartree'])<=1e-10,
            'legacy fixed-energy/field mismatch')
    require(abs(rederived['pure_hf_reconstruction_error_hartree'])<=2e-8,'legacy HF identity failed')
    if recovered:
        record=read(artifact/'validation.json')
        require(bool(record['checks']) and all(record['checks'].values()),'failed legacy recovery')
        require(record['values']==values,'recovery values changed')
    else:
        record=read(artifact/'reaction_ready_manifest.json')
        require(all(digest(artifact/n)==h for n,h in record['artifacts_sha256'].items()),'legacy hashes changed')
    dependencies=[artifact/'feature_vector_292.npy',fixed_file,fixed_output,scalar,
                  artifact/('validation.json' if recovered else 'reaction_ready_manifest.json')]
    if not one:dependencies.append(pt2)
    differences={}
    for g in ('250974',)+GRIDS:
        q4=original/f'gateway_work/q4/{g}'
        checks,_=validate_published_artifact(q4,original/f'gateway_work/grids/{g}')
        require(bool(checks) and all(checks.values()),'legacy Q4 validation failed')
        semilocal=q4/'semilocal_features_288.npy';dependencies.append(semilocal)
        if g=='250974':
            require(np.array_equal(vector[:288],np.load(semilocal)),'legacy semilocal mismatch')
        else:
            p=artifact/f'grid_difference_{g}_minus_250974.npy'
            differences[g]=checked_vector(p);dependencies.append(p)
            expected=np.r_[np.load(semilocal)-vector[:288],np.zeros(4)]
            require(np.array_equal(differences[g],expected),'legacy grid mismatch')
    return vector,float(fixed_values['fixed_energy_hartree']),differences,dependencies


def freeze(plan_path, output_root):
    """Read-only source audit and new lightweight plan; no jobs or archive copies."""
    settings=load_fit_settings();cohort=read(COHORT);baseline=read(BASELINE)
    require(baseline['status']=='passed' and digest(COHORT)==baseline['cohort_sha256'],'invalid baseline')
    require(len(cohort['cases'])==38 and len(cohort['reactions'])==20,'not the bounded cohort')
    root=Path(output_root).resolve()
    require(not root.exists(),'new refresh root must not already exist')
    entries={r['species']:r for r in baseline['species']}
    vectors,fixed,diffs,cases={},{},{},[]
    for case in cohort['cases']:
        name=case['species'];entry=entries[name]
        protected=[Path(case['orbital_root']).resolve(),Path(case['authoritative_input']).resolve().parent,
                   Path(entry['artifact']).resolve(),Path(cohort['run_root']).resolve()]
        require(not any(root==p or p in root.parents for p in protected),
                'refresh output cannot be inside an authoritative or historical input tree')
        vector,f,d,dependencies=legacy_species(case,entry,cohort)
        vectors[name],fixed[name],diffs[name]=vector,f,d
        cases.append({**case,'legacy_entry':entry,'reuse_hashes':{str(p):digest(p) for p in dependencies}})
    assembled=assemble_reaction_arrays(cohort['reactions'],vectors,fixed,diffs,GRIDS)
    old=Path(baseline['output_root'])
    require(all(digest(old/n)==h for n,h in baseline['artifacts_sha256'].items()),'changed old assembly')
    for key in ('feature_matrix','target','fixed_energy','reference_energy','objective_weight'):
        require(np.allclose(assembled[key],np.load(old/(key+'.npy')),rtol=0,atol=1e-12),
                'legacy assembly does not reconstruct: '+key)
    code=[Path(__file__),ROOT/'fit_spec.py',ROOT/'fit_inputs.py',ROOT/'qchem_scalar_features.py',
          ROOT/'qchem_feature_publisher.py',ROOT/'step14_recovery_v2.py',ROOT/'reaction_assembly.py',
          ROOT/'scripts/run_step13_fresh_species.py',ROOT/'scripts/v7_refresh.py']
    plan={'schema_version':1,'status':'frozen_before_refresh','purpose':'bounded_38_species_20_reactions',
          'scientific_specification_sha256':settings.specification_sha256,'output_root':str(root),
          'source_hashes':{str(p):digest(p) for p in (COHORT,BASELINE)},
          'code_hashes':{str(p):digest(p) for p in code},
          'build_hashes':{str(QCHEM_ROOT/p):digest(QCHEM_ROOT/p) for p in
                         ('bin/qchem','exe/qcprog.exe','lib/libks.so','lib/libks_ham.so',
                          'lib/libks_ref.so','lib/libks_utils.so')},
          'cases':cases,'reactions':cohort['reactions'],'sr_reuse_tolerance_hartree':1e-8,
          'bulk_submission_authorized':False,'new_scf_forbidden':True}
    write(plan_path,plan)


def load_plan(path):
    plan=read(path);settings=load_fit_settings()
    require(plan['status']=='frozen_before_refresh' and plan['schema_version']==1,'invalid refresh plan')
    require(plan['scientific_specification_sha256']==settings.specification_sha256,'changed spec')
    require(len(plan['cases'])==38 and len(plan['reactions'])==20,'bounded scope changed')
    for key in ('source_hashes','code_hashes','build_hashes'):
        require(all(digest(p)==h for p,h in plan[key].items()),'changed '+key)
    return plan,settings


def refresh_species(plan_path, name, cpus):
    plan,settings=load_plan(plan_path)
    matches=[c for c in plan['cases'] if c['species']==name]
    require(len(matches)==1,'species outside frozen cohort');case=matches[0]
    require(type(cpus) is int and cpus==case['resources']['cpus'],'CPU allocation mismatch')
    require(all(digest(p)==h for p,h in case['reuse_hashes'].items()),'changed reuse inputs')
    old,fixed,differences,_=legacy_species(case,case['legacy_entry'],read(COHORT))
    source=Path(case['orbital_root'])
    require(canonical_tree_hash(tree_manifest(source))==case['source_tree']['manifest_sha256'],
            'source orbital tree changed')
    out=Path(plan['output_root'])/'species'/name
    if out.exists():
        validate_species(plan_path,name)
        return  # successful identical restart; partials fail and are preserved
    out.mkdir(parents=True,exist_ok=False)
    try:
        scratch=out/'qcscratch'/'v7_scalar'
        scratch.parent.mkdir()
        shutil.copytree(source,scratch,copy_function=shutil.copy2)
        require(canonical_tree_hash(tree_manifest(scratch))==case['source_tree']['manifest_sha256'],
                'archive-copy identity failed')
        derived,controls=derive_scalar_input(Path(case['authoritative_input']).read_text(),settings=settings)
        (out/'scalar.in').write_text(derived)
        write(out/'prepared.json',{'plan_sha256':digest(plan_path),'species':name,'controls':controls,
                                  'input_sha256':digest(out/'scalar.in')})
        run_qchem(out,'scalar.in','qchem.out','v7_scalar',cpus,False)
        require(digest(scratch/'qarchive.h5')==case['qarchive_sha256'],'working qarchive changed')
        require(canonical_tree_hash(tree_manifest(source))==case['source_tree']['manifest_sha256'],
                'authoritative tree changed during run')
        original=Path(read(COHORT)['run_root'])/case['scope']/name
        values=scalar_values((out/'qchem.out').read_text(),None if name=='W4-17_h' else
                             (original/'gateway_work/scalar/qchem.pt2.out').read_text(),one_electron=name=='W4-17_h')
        require(abs(values['short_range_hf_hartree']-old[288])<=plan['sr_reuse_tolerance_hartree'],
                'SR-HF changed; cannot reuse fixed partition')
        require(np.isfinite(values['vv10_hartree']),'nonfinite VV10')
        new=old.copy();new[289]=values['vv10_hartree']
        ready=out/'ready';ready.mkdir()
        np.save(ready/'feature_vector_292.npy',new)
        for g in GRIDS:np.save(ready/f'grid_difference_{g}.npy',differences[g])
        write(ready/'fixed_energy.json',{'fixed_energy_hartree':fixed,'policy':'unchanged_v6_field_aware'})
        write(out/'species.json',{'species':name,'plan_sha256':digest(plan_path),
            'specification_sha256':settings.specification_sha256,
            'artifacts':{str(p.relative_to(out)):digest(p) for p in
                         [out/'scalar.in',out/'qchem.out',out/'prepared.json',*ready.iterdir()]}})
        validate_species(plan_path,name,require_marker=False)
        (out/'REFRESH_COMPLETE').write_text('complete\n')
    except Exception as exc:
        write(out/'failure.json',{'error_type':type(exc).__name__})
        raise


def validate_species(plan_path,name,require_marker=True):
    """Reparse output independently of publication and compare every reused column."""
    import re
    from revwb97m2.qchem_scalar_features import FLOAT
    plan,settings=load_plan(plan_path);case=next(c for c in plan['cases'] if c['species']==name)
    out=Path(plan['output_root'])/'species'/name;record=read(out/'species.json')
    require(not require_marker or (out/'REFRESH_COMPLETE').is_file(),'incomplete refresh')
    require(record['plan_sha256']==digest(plan_path) and record['species']==name,'stale species identity')
    require(all(digest(out/p)==h for p,h in record['artifacts'].items()),'changed refresh outputs')
    require(all(digest(p)==h for p,h in case['reuse_hashes'].items()),'changed reuse data')
    expected,controls=derive_scalar_input(Path(case['authoritative_input']).read_text(),settings=settings)
    require((out/'scalar.in').read_text()==expected,'input parameters changed')
    text=(out/'qchem.out').read_text()
    require('Thank you very much for using Q-Chem' in text,'abnormal termination')
    require(text.count('Reading MOs from coefficient file')>=2,'missing orbital-read evidence')
    def last(pattern):
        matches=re.findall(pattern,text,re.I)
        require(bool(matches),'missing independent scalar output')
        return float(matches[-1].replace('D','E').replace('d','e'))
    vv=last(rf'(?:Nonlocal\s+correlation|DFT\s+Correlation\s+Energy)\s*=\s*({FLOAT})')
    sr=sum(last(rf'{spin}\s+Exchange\s+Energy\s*=\s*({FLOAT})') for spin in ('Alpha','Beta'))
    old,fixed,differences,_=legacy_species(case,case['legacy_entry'],read(COHORT))
    new=checked_vector(out/'ready/feature_vector_292.npy')
    keep=np.arange(292)!=289
    require(np.array_equal(new[keep],old[keep]),'a reused feature changed')
    require(new[289]==vv and abs(sr-old[288])<=plan['sr_reuse_tolerance_hartree'],'scalar readback mismatch')
    require(read(out/'ready/fixed_energy.json')['fixed_energy_hartree']==fixed,'fixed energy changed')
    for g in GRIDS:
        require(np.array_equal(checked_vector(out/f'ready/grid_difference_{g}.npy'),differences[g]),'grid changed')
    require(digest(out/'qcscratch/v7_scalar/qarchive.h5')==case['qarchive_sha256'],'working archive changed')
    return new,fixed,differences


def independently_check_assembly(reactions,names,vectors,fixed,differences,result):
    """Matrix-based reconstruction independent of the loop-based assembler."""
    coefficients=np.zeros((len(reactions),len(names)))
    for i,row in enumerate(reactions):
        for term in row['stoichiometry']:
            coefficients[i,names.index(term['species'])]+=float(term['coefficient'])
    expected={'feature_matrix':coefficients@np.stack([vectors[n] for n in names]),
              'fixed_energy':coefficients@np.array([fixed[n] for n in names]),
              'reference_energy':np.array([r['reference_hartree'] for r in reactions]),
              'objective_weight':np.array([r['objective_weight'] for r in reactions])}
    expected['target']=expected['reference_energy']-expected['fixed_energy']
    for key,array in expected.items():
        require(np.allclose(result[key],array,rtol=0,atol=1e-12),'independent assembly failed: '+key)
    for g in GRIDS:
        matrix=coefficients@np.stack([differences[n][g] for n in names])
        require(np.allclose(result['grid_differences'][g],matrix,rtol=0,atol=1e-12),'independent D failed')


def assemble(plan_path):
    plan,settings=load_plan(plan_path)
    vectors,fixed,differences={},{},{}
    names=[c['species'] for c in plan['cases']]
    for name in names:
        vectors[name],fixed[name],differences[name]=validate_species(plan_path,name)
    result=assemble_reaction_arrays(plan['reactions'],vectors,fixed,differences,GRIDS)
    independently_check_assembly(plan['reactions'],names,vectors,fixed,differences,result)
    # The old reference/fixed/weight target must be unchanged by VV10-only refresh.
    old=Path(read(BASELINE)['output_root'])
    require(all(digest(old/n)==h for n,h in read(BASELINE)['artifacts_sha256'].items()),
            'historical assembly changed before v7 publication')
    for key in ('fixed_energy','reference_energy','target','objective_weight'):
        require(np.allclose(result[key],np.load(old/(key+'.npy')),rtol=0,atol=1e-12),'unexpected target change')
    output=Path(plan['output_root'])/'reactions'
    output.mkdir(parents=True,exist_ok=False)
    arrays={key:result[key] for key in ('feature_matrix','target','objective_weight')}
    arrays.update({f'grid_difference_{g}':result['grid_differences'][g] for g in GRIDS})
    artifacts={}
    for name,array in arrays.items():
        path=output/(name+'.npy');np.save(path,array)
        require(np.array_equal(array,np.load(path,allow_pickle=False)),'array serialization failed')
        artifacts[name]={'path':path.name,'sha256':digest(path)}
    # Preserve fixed/reference energies and explicit reaction names as audit evidence.
    for key in ('fixed_energy','reference_energy'):np.save(output/(key+'.npy'),result[key])
    write(output/'reaction_names.json',result['reaction_names'])
    evidence=output/'assembly_validation.json'
    write(evidence,{'passed':True,'purpose':'bounded_real_20_entry_v7_refresh',
        'scientific_specification_sha256':settings.specification_sha256,
        'plan_sha256':digest(plan_path),'species_count':len(names),'reaction_count':len(plan['reactions']),
        'array_sha256':{name:artifacts[name]['sha256'] for name in ARRAYS},
        'species_manifest_sha256':{n:digest(Path(plan['output_root'])/'species'/n/'species.json') for n in names},
        'checks':{'independent_stoichiometry':True,'unchanged_target_and_weights':True,
                  'all_species_output_reparsed':True,'array_readback':True},
        'additional_artifacts':{p.name:digest(p) for p in
                                [output/'fixed_energy.npy',output/'reference_energy.npy',output/'reaction_names.json']}})
    artifacts['assembly_validation']={'path':evidence.name,'sha256':digest(evidence)}
    manifest={'schema_version':1,'status':'validated','purpose':'bounded_real_cohort_not_full_training',
        'scientific_specification_sha256':settings.specification_sha256,'role':'coefficient_fitting',
        'weights_policy':'coach_si_table2_final_cycle','reaction_ids':result['reaction_names'],
        'energy_parameters':{'omega':.3,'gamma_ss':.01,'vv10_b':5.5,'vv10_c':.01},
        'vv10_grid_policy':'single_grid_zero_difference',
        'vv10_grid_zero_reason':'VV10 evaluated on SG-1 only; not a both-grid VV10 sensitivity test',
        'artifacts':artifacts}
    # Publish the fitter-facing manifest only after independent validation.
    temporary=output/'inputs.pending.json';write(temporary,manifest)
    load_inputs(temporary,settings)
    temporary.rename(output/'inputs.json')
    (output/'ASSEMBLY_COMPLETE').write_text('complete\n')
