"""Offline full-data orchestration tests; execute only after pre-test commit."""
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2.scripts import full1498_mio_v1 as p
from revwb97m2.grid_selection import select_rows
from revwb97m2.fit_spec import load_fit_settings


def test_schedule():
    rows=p.schedule()
    assert [r['budget'] for r in rows]==[14,80,14,14,80,80]
    assert rows[3]['start']=='constrained14' and rows[5]['start']=='constrained80'
    for r in rows[2:]: assert r['candidates']==['discovery14','discovery80']
    args=p.args_for(rows[2],Path('/tmp/full'),Path('/tmp/input'))
    assert (args.seconds,args.threads)==(600,16)
    assert args.start==Path('/tmp/full/discovery14')


def test_disabled_release_stops_before_git(tmp_path,monkeypatch):
    path=tmp_path/'release.json';p.write(path,dict(user_approved_submission=False))
    monkeypatch.setattr(p,'check_plan',lambda:{})
    monkeypatch.setattr(p.subprocess,'check_output',lambda *x,**k:pytest.fail('git reached'))
    with pytest.raises(ValueError,match='disabled'):p.check_release(path)


def test_matrix_identity_refused_before_reader(monkeypatch):
    monkeypatch.setattr(p,'digest',lambda x:'wrong')
    monkeypatch.setattr(p.assembly,'validate',lambda x:pytest.fail('reader reached'))
    with pytest.raises(ValueError,match='identity changed'):p.matrix_manifest()


def test_resume_never_opens_license(monkeypatch):
    args=SimpleNamespace(resume=True)
    monkeypatch.delenv('GRB_LICENSE_FILE',raising=False)
    monkeypatch.setattr(p.fit,'run',lambda a:0)
    monkeypatch.setattr(Path,'read_text',lambda *x,**k:pytest.fail('license/file read'))
    assert p.execute_fit(args)==0


def test_pilot_start_identity_rejected(tmp_path):
    p.write(tmp_path/'contract.json',dict(specification_sha256='same',input_manifest_sha256='pilot100'))
    p.write(tmp_path/'result.json',dict(passed=True))
    with pytest.raises(ValueError,match='identity mismatch'):
        p.fit.load_start(tmp_path,dict(specification_sha256='same',input_manifest_sha256=p.INPUT_SHA))


def test_full_grid_union_and_unselected_violation():
    settings=load_fit_settings();d=np.zeros((1498,292))
    d[:200,0]=2.;d[200:300,1]=1.;d[300:400,2]=1.
    candidates=np.zeros((2,292));candidates[0,1]=1.;candidates[1,2]=1.
    rows=select_rows(d,candidates,100,200)
    np.testing.assert_array_equal(rows,np.arange(400))
    # A later fitted direction can expose a row outside the discovery union.
    d[1000,3]=1.;coeff=np.zeros(292);coeff[3]=1.
    report=p.grid_report({'grid_difference_99590':d,'grid_difference_75302':d},coeff,rows,
                         settings,[f'r{i}' for i in range(1498)])
    assert report['99590']['violations']==[dict(row=1000,reaction='r1000',
        error_kcal_mol=settings.conversion,selected=False)]


@pytest.mark.parametrize('change',['cpu','memory','route'])
def test_allocation_mismatch(monkeypatch,change):
    route=dict(partition='cm1',account='lr_qchem',qos='condo_qchem')
    for key,value in dict(SLURM_JOB_PARTITION='cm1',SLURM_JOB_ACCOUNT='lr_qchem',
        SLURM_JOB_QOS='condo_qchem',SLURM_CPUS_PER_TASK='16',SLURM_MEM_PER_NODE='32768').items():
        monkeypatch.setenv(key,value)
    p.check_allocation(route)
    key,value={'cpu':('SLURM_CPUS_PER_TASK','8'),'memory':('SLURM_MEM_PER_NODE','16384'),
               'route':('SLURM_JOB_PARTITION','lr_lowprio')}[change]
    monkeypatch.setenv(key,value)
    with pytest.raises(ValueError,match='mismatch'):p.check_allocation(route)


def test_no_incumbent_stops_before_next_solve(tmp_path,monkeypatch):
    route=dict(partition='cm1',account='lr_qchem',qos='condo_qchem')
    plan=dict(output_parent=str(tmp_path/'outputs'))
    monkeypatch.setattr(p,'check_release',lambda x:(plan,dict(route=route,commit='test')))
    monkeypatch.setattr(p,'check_allocation',lambda x:None)
    monkeypatch.setenv('SLURM_JOB_ID','123')
    monkeypatch.setattr(p,'matrix_manifest',lambda:tmp_path/'inputs.json')
    monkeypatch.setattr(p,'digest',lambda x:'sha')
    monkeypatch.setattr(p,'load_inputs',lambda *x:({},{}))
    import shutil
    monkeypatch.setattr(shutil,'disk_usage',lambda x:SimpleNamespace(free=100*1024**3))
    calls=[]
    def run(command,**kwargs):
        calls.append(command)
        if 'revwb97m2.scripts.test_v7_end_to_end' in command:
            root=tmp_path/'outputs/123/synthetic';root.mkdir()
            p.write(root/'integration_report.json',dict(passed=True))
            return SimpleNamespace(returncode=0)
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(p.subprocess,'run',run)
    with pytest.raises(ValueError,match='solve failed'):p.run(tmp_path/'release.json')
    assert len(calls)==2 and calls[-1][-1]=='discovery14'
    assert (tmp_path/'outputs/123/failure.json').exists()


def test_check_plan_rejects_schedule_change(tmp_path,monkeypatch):
    path=tmp_path/'plan.json';p.write(path,dict(schedule=[],seconds=600,threads=16))
    with pytest.raises(ValueError,match='schedule'):p.check_plan(path)
