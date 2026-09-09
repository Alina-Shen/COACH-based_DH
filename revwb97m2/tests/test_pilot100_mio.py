"""Offline tests; no WLS environment or native computation."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2 import pilot100_inputs as a
from revwb97m2.fit_inputs import ARRAYS, digest
from revwb97m2.fit_spec import load_fit_settings
from revwb97m2.scripts import pilot100_mio_v1 as p, run_pilot100_fit_v1 as fit


def matrix_fixture(tmp_path,monkeypatch):
    root=tmp_path/'matrix';root.mkdir();settings=load_fit_settings()
    rows=[dict(reaction=f'r{i}',set_or_subset=f'g{i%49}',reference_hartree=float(i),objective_weight=i+1.,
        stoichiometry=[dict(species=f's{j}',coefficient=1.) for j in range(i,224,100)]) for i in range(100)]
    for name in (*ARRAYS,'reference_energy','fixed_energy'):
        values=np.zeros((100,292)) if name=='feature_matrix' or name.startswith('grid_difference') else np.zeros(100)
        if name in ('reference_energy','target'):values=np.arange(100,dtype=float)
        if name=='objective_weight':values=np.arange(1,101,dtype=float)
        np.save(root/(name+'.npy'),values)
    a.write(root/'reactions.json',rows);a.write(root/'species.json',sorted(f's{i}' for i in range(224)))
    source=tmp_path/'source.json';a.write(source,rows)
    a.write(root/'validation.json',dict(passed=True,specification_sha256=settings.specification_sha256,
        source_reactions_sha256=digest(source),authorities={},
        code_sha256=digest(a.ROOT/'revwb97m2/scripts/assemble_pilot100_v1.py'),
        artifacts={x.name:digest(x) for x in root.iterdir()}))
    sha=digest(root/'validation.json');(root/'MATRIX_COMPLETE').write_text(sha+'\n')
    original=a.check_matrix
    monkeypatch.setattr(a,'MATRIX',root);monkeypatch.setattr(a,'VALIDATION_SHA',sha)
    monkeypatch.setattr(a,'check_matrix',lambda:original(root,sha,source))
    return root,source


def test_adapter_roundtrip_and_no_overwrite(tmp_path,monkeypatch):
    root,_=matrix_fixture(tmp_path,monkeypatch);before={x.name:digest(x) for x in root.iterdir()}
    out=tmp_path/'adapter';assert a.publish(out)==a.validate(out)
    assert before=={x.name:digest(x) for x in root.iterdir()}
    with pytest.raises(ValueError,match='preserve'):a.publish(out)


@pytest.mark.parametrize('target',['marker','array','source','adapter'])
def test_adapter_tamper_refused(tmp_path,monkeypatch,target):
    root,source=matrix_fixture(tmp_path,monkeypatch);out=tmp_path/'adapter';a.publish(out)
    path={'marker':root/'MATRIX_COMPLETE','array':root/'target.npy','source':source,'adapter':out/'inputs.json'}[target]
    path.write_text('tampered')
    with pytest.raises((ValueError,AssertionError)):a.validate(out)


def test_schedule_and_start_lineage():
    rows=p.schedule();assert len(rows)==6 and [x['budget'] for x in rows]==[14,40,14,14,40,40]
    assert rows[0]['start'] is None and rows[1]['start'] is None
    for row in rows[2:]:assert row['candidates']==['discovery14','discovery40']
    assert rows[3]['start']=='constrained14' and rows[5]['start']=='constrained40'
    args=p.args_for(rows[2],Path('/tmp/pilot'),Path('/tmp/manifest'))
    assert args.seconds==300 and args.threads==16 and args.start==Path('/tmp/pilot/discovery14')


def test_disabled_release_never_checks_git(tmp_path,monkeypatch):
    release=tmp_path/'release.json';a.write(release,dict(user_approved_submission=False))
    monkeypatch.setattr(p,'check_plan',lambda:{})
    monkeypatch.setattr(p.subprocess,'check_output',lambda *x,**kw:pytest.fail('git must not be reached'))
    with pytest.raises(ValueError,match='disabled'):p.check_release(release)


def fake_run(tmp_path,monkeypatch):
    manifest=tmp_path/'inputs.json';a.write(manifest,{})
    arrays={name:np.zeros((100,292)) if name=='feature_matrix' or name.startswith('grid_difference') else np.ones(100) for name in ARRAYS}
    monkeypatch.setattr(fit,'load_inputs',lambda *args:(arrays,{}))
    model=SimpleNamespace(Status=9,SolCount=0,Runtime=300.,NodeCount=2.,
        optimize=lambda:None,dispose=lambda:None,getParamInfo=lambda key:(key,None,1))
    monkeypatch.setattr(fit,'build_model',lambda *args,**kw:(model,{},{}))
    monkeypatch.setitem(sys.modules,'gurobipy',SimpleNamespace(gurobi=SimpleNamespace(version=lambda:(13,0,0))))
    args=p.args_for(p.schedule()[0],tmp_path,manifest)
    return args


def test_no_incumbent_explicit_failure(tmp_path,monkeypatch):
    args=fake_run(tmp_path,monkeypatch)
    assert fit.run(args)==1
    result=a.read(args.output/'result.json')
    assert result['passed'] is False and result['solution_count']==0
    assert not (args.output/'coefficients.npy').exists()
    assert (args.output/'telemetry.json').exists()


def test_resume_does_not_optimize_or_write(tmp_path,monkeypatch):
    args=fake_run(tmp_path,monkeypatch);fit.run(args)
    before={x.name:digest(x) for x in args.output.iterdir()}
    monkeypatch.setattr(fit,'build_model',lambda *x,**kw:pytest.fail('resume called solver'))
    monkeypatch.setattr(fit,'readback',lambda *x:None)
    args.resume=True;assert fit.run(args)==0
    assert before=={x.name:digest(x) for x in args.output.iterdir()}
    args.seconds=301
    with pytest.raises(ValueError,match='resume contract'):fit.run(args)


def test_warm_start_rejects_failed_incumbent(tmp_path):
    identity=dict(specification_sha256='science',input_manifest_sha256='data')
    a.write(tmp_path/'contract.json',identity);a.write(tmp_path/'result.json',dict(passed=False))
    with pytest.raises(ValueError,match='no validated incumbent'):fit.load_start(tmp_path,identity)


def test_warm_start_rejects_changed_identity(tmp_path):
    a.write(tmp_path/'contract.json',dict(specification_sha256='old',input_manifest_sha256='old'))
    a.write(tmp_path/'result.json',dict(passed=True))
    with pytest.raises(ValueError,match='identity mismatch'):
        fit.load_start(tmp_path,dict(specification_sha256='new',input_manifest_sha256='new'))
