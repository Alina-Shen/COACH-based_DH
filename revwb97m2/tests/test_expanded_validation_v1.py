"""Offline expanded six-stage scope, audit and grid/restart identity checks."""
import numpy as np
import pytest
from revwb97m2 import expanded_adapter as a
from revwb97m2.scripts import expanded_validation_v1 as v


def fixture():
    settings=a.settings()
    arrays=dict(feature_matrix=np.zeros((4,292)),target=np.ones(4),objective_weight=np.ones(4),
        grid_difference_99590=np.zeros((4,292)),grid_difference_75302=np.zeros((4,292)))
    b=np.zeros(292);b[0]=.8;b[288]=.2;b[289:]=.1
    z=np.zeros(292);z[[0,288,289,290,291]]=1
    return arrays,b,z,settings


def test_six_stage_schedule():
    rows=v.schedule()
    assert [r['name'] for r in rows]==['discovery14','discovery80','constrained14','restart14','constrained80','restart80']
    assert rows[0]['start']==rows[1]['start']=='source'
    assert rows[3]['start']=='constrained14' and rows[5]['start']=='constrained80'
    assert rows[2]['candidates']==rows[3]['candidates']==rows[4]['candidates']==rows[5]['candidates']


def test_feasible_semilocal_start():
    arrays,b,z,s=fixture()
    r=a.audit(arrays,b,z,14,np.array([],dtype=int),s)
    assert r['passed'] and r['semilocal_nonzero_count']==1 and r['full_grid_passed']


def test_grid_violating_start_is_not_falsely_called_feasible():
    arrays,b,z,s=fixture();arrays['grid_difference_99590'][0,0]=1
    r=a.start_audit(arrays,b,z,14,np.array([0]),s)
    assert r['ungridded']['passed'] and not r['grid_feasible']


def test_unselected_grid_violation_blocks_advancement():
    arrays,b,z,s=fixture();arrays['grid_difference_99590'][1,0]=1
    r=a.audit(arrays,b,z,14,np.array([0]),s)
    assert r['passed'] and not r['full_grid_passed']


def test_75302_is_monitor_only():
    arrays,b,z,s=fixture();arrays['grid_difference_75302'][1,0]=1
    r=a.audit(arrays,b,z,14,np.array([0]),s)
    assert r['passed'] and r['full_grid_passed'] and r['grid_max_kcal_mol']['75302']>0


@pytest.mark.parametrize('bad',['fractional','ueg','bound','support'])
def test_invalid_start_rejected(bad):
    arrays,b,z,s=fixture()
    if bad=='fractional':z[1]=.5
    if bad=='ueg':b[0]=.7
    if bad=='bound':b[1]=26;z[1]=1
    if bad=='support':z[:20]=1
    with pytest.raises(ValueError):a.start_audit(arrays,b,z,14,np.array([],dtype=int),s)


def test_budget80_supported():
    arrays,b,z,s=fixture();z[:20]=1
    assert a.audit(arrays,b,z,80,np.array([],dtype=int),s)['passed']
    assert not a.audit(arrays,b,z,14,np.array([],dtype=int),s)['passed']


def test_grid_rows_frozen_between_constrained_and_restart(tmp_path):
    arrays,b,z,s=fixture()
    for name in ('discovery14','discovery80','constrained14'):
        (tmp_path/name).mkdir();np.save(tmp_path/name/'coefficients.npy',b);np.save(tmp_path/name/'selection.npy',z)
    x=v.inputs(v.schedule()[2],tmp_path,arrays,s)
    y=v.inputs(v.schedule()[3],tmp_path,arrays,s)
    assert np.array_equal(x[2],y[2])


def test_disabled_release(tmp_path,monkeypatch):
    plan=tmp_path/'plan.json';release=tmp_path/'release.json'
    v.c.write(plan,{});v.c.write(release,dict(submission_authorized=False));monkeypatch.setattr(v,'PLAN',plan)
    with pytest.raises(ValueError,match='disabled'):v.check(release)
