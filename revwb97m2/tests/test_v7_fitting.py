"""Pre-commit test additions. Intentionally not executed during implementation."""
import copy
import json
from argparse import Namespace
from pathlib import Path
import numpy as np
import pytest
import yaml
from revwb97m2.fit_spec import load_fit_settings, DEFAULT_SPEC
from revwb97m2.fit_inputs import ARRAYS, digest, load_inputs
from revwb97m2.grid_selection import select_rows
from revwb97m2.mio import build_model, audit_solution
from revwb97m2.qchem_scalar_features import derive_scalar_input
from revwb97m2.scripts.run_v7_fit import load_start, run


def test_resolved_science_and_units():
    s=load_fit_settings()
    assert s.ridge == 1e-10
    assert s.grid_limit*s.conversion == pytest.approx(.014985)
    assert s.grid_public_limit*s.conversion == pytest.approx(.015)
    assert s.vv10_b == 5.5 and s.vv10_c == .01


@pytest.mark.parametrize('keys,value',[
    (('schema_version',),6),
    (('optimization','ridge','coefficient'),0.),
    (('optimization','objective_normalization'),'half_sse'),
    (('double_hybrid_energy','vv10','b'),10.),
    (('double_hybrid_energy','range_separation','omega_bohr_inverse'),.27),
    (('constraint_profiles','active_for_first_real_fit'),['C3_full_coach_sampled']),
    (('grid_sensitivity','internal_safety_factor'),1.),
])
def test_reject_unsupported_spec(tmp_path,keys,value):
    spec=yaml.safe_load(DEFAULT_SPEC.read_text())
    node=spec
    for key in keys[:-1]: node=node[key]
    node[keys[-1]]=value
    path=tmp_path/'spec.yaml';path.write_text(yaml.safe_dump(spec))
    with pytest.raises(ValueError): load_fit_settings(path)


def test_scalar_v7_is_explicit_and_legacy_unchanged():
    source='$rem\nMETHOD wb97m(os)\nAUX_BASIS_CORR rimp2-def2-qzvppd\n$end\n'
    assert derive_scalar_input(source)[1]['NL_VV_B']=='1000'
    _,rem=derive_scalar_input(source,settings=load_fit_settings())
    assert rem['NL_VV_B']=='550' and rem['OMEGA']=='300'
    assert rem['MAX_SCF_CYCLES']=='0' and rem['SCF_GUESS']=='READ'


def test_ridge_audit_and_public_grid_limit():
    s=load_fit_settings();a=np.zeros((2,292));a[:,0]=[1,2]
    c=np.zeros(292);c[[0,288,289,290,291]]=[.8,.2,.3,.4,.5]
    z=c!=0;b=np.array([.7,1.4]);w=np.array([2.,3.])
    r=audit_solution(a,b,w,c,z,model_name='R2',budget=5,settings=s)
    expected=2*.1**2+3*.2**2
    assert r['weighted_sse_hartree2']==pytest.approx(expected)
    assert r['ridge_penalty_hartree2']==pytest.approx(1e-10*(c@c),rel=1e-12,abs=0)
    assert r['regularized_objective_hartree2']==pytest.approx(expected+1e-10*(c@c))
    d=np.zeros((1,292));d[0,0]=s.grid_public_limit/.8*1.000001
    assert not audit_solution(a,b,w,c,z,model_name='R2',budget=5,settings=s,grid_difference=d)['passed']
    with pytest.raises(ValueError):
        audit_solution(a,b,w,c,np.full(292,.5),model_name='R2',budget=5,settings=s)


def test_grid_selection_over_200_independent_reference():
    rng=np.random.default_rng(17);d=rng.normal(size=(700,12));c=rng.normal(size=(3,12))
    expected=set(sorted(range(700),key=lambda i:-sum(abs(v) for v in d[i]))[:200])
    for beta in c:
        expected.update(sorted(range(700),key=lambda i:-abs(sum(x*y for x,y in zip(d[i],beta))))[:100])
    assert select_rows(d,c).tolist()==sorted(expected)
    assert len(expected)>200 and len(expected)<700


def data_fixture(tmp_path):
    s=load_fit_settings();artifacts={}
    arrays={name:np.zeros((2,292)) for name in ARRAYS}
    arrays['target']=np.zeros(2);arrays['objective_weight']=np.ones(2)
    for name,array in arrays.items():
        path=tmp_path/(name+'.npy');np.save(path,array)
        artifacts[name]={'path':path.name,'sha256':digest(path)}
    evidence=tmp_path/'assembly.json'
    evidence.write_text(json.dumps({'passed':True,'scientific_specification_sha256':s.specification_sha256,
        'array_sha256':{name:r['sha256'] for name,r in artifacts.items()}}))
    artifacts['assembly_validation']={'path':evidence.name,'sha256':digest(evidence)}
    m={'schema_version':1,'status':'validated','scientific_specification_sha256':s.specification_sha256,
       'role':'coefficient_fitting','weights_policy':'coach_si_table2_final_cycle',
       'reaction_ids':['synthetic_1','synthetic_2'],
       'energy_parameters':{'omega':.3,'gamma_ss':.01,'vv10_b':5.5,'vv10_c':.01},
       'vv10_grid_policy':'single_grid_zero_difference','vv10_grid_zero_reason':'synthetic fixture',
       'artifacts':artifacts}
    path=tmp_path/'inputs.json';path.write_text(json.dumps(m));return path,m


def test_input_hash_identity_and_stale_b_rejection(tmp_path):
    path,m=data_fixture(tmp_path);s=load_fit_settings()
    assert load_inputs(path,s)[0]['feature_matrix'].shape==(2,292)
    m['energy_parameters']['vv10_b']=10.;path.write_text(json.dumps(m))
    with pytest.raises(ValueError):load_inputs(path,s)
    m['energy_parameters']['vv10_b']=5.5;path.write_text(json.dumps(m))
    np.save(tmp_path/'target.npy',np.ones(2))
    with pytest.raises(ValueError):load_inputs(path,s)


def test_failed_start_cannot_resume(tmp_path):
    identity={'specification_sha256':'x','input_manifest_sha256':'y'}
    (tmp_path/'contract.json').write_text(json.dumps(identity))
    (tmp_path/'result.json').write_text(json.dumps({'passed':False}))
    with pytest.raises(ValueError):load_start(tmp_path,identity)


def test_solver_v7_ridge_and_legacy_comparison():
    gp=pytest.importorskip('gurobipy');s=load_fit_settings()
    for settings in (None,s):
        m,b,z=build_model(np.zeros((1,292)),np.zeros(1),np.ones(1),settings=settings,
                          columns=[0,288,289,290,291],budget=5,seconds=2,threads=1)
        try:
            q=m.getObjective()
            coeff={q.getVar1(i).VarName:q.getCoeff(i) for i in range(q.size())
                   if q.getVar1(i).sameAs(q.getVar2(i))}
            assert coeff.get('beta[0]',0)==(0 if settings is None else 1e-10)
            if settings:
                assert m.Params.MIPGap==1e-4
                assert m.Params.MIPGapAbs==1e-10
        finally:m.dispose()


@pytest.mark.parametrize('mode',['no_incumbent','exception'])
def test_runner_failure_never_publishes(tmp_path,monkeypatch,mode):
    from revwb97m2.scripts import run_v7_fit
    path,_=data_fixture(tmp_path)
    class NoIncumbent:
        Status=9
        SolCount=0
        Runtime=.1
        def optimize(self): pass
        def dispose(self): pass
    def builder(*args,**kwargs):
        if mode=='exception':raise ValueError('synthetic failure')
        return NoIncumbent(),{},{}
    monkeypatch.setattr(run_v7_fit,'build_model',builder)
    args=Namespace(spec=DEFAULT_SPEC,manifest=path,output=tmp_path/'run',budget=14,
                   seconds=2,threads=1,start=None,grid_candidates=[],resume=False)
    assert run(args)==1
    assert not (args.output/'coefficients.npy').exists()
    assert (args.output/('failure.json' if mode=='exception' else 'result.json')).exists()
    args.resume=True
    with pytest.raises((ValueError,FileNotFoundError)):run(args)
