"""Offline continuous-subproblem tests; await user pre-test commit."""
from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2.scripts import continuous_k14_v1 as c


@pytest.mark.parametrize('kind',c.KINDS)
def test_configure_only_changes_selection_type_bounds(kind):
    z={i:SimpleNamespace(VType='B',LB=0.,UB=1.) for i in range(292)}
    m=SimpleNamespace(update=lambda:None,NumBinVars=0,NumIntVars=0)
    c.configure(m,z,kind)
    assert all(v.VType=='C' for v in z.values())
    assert all(z[i].LB==z[i].UB==1 for i in range(288,292))
    assert all(z[i].LB==0 and z[i].UB==(0 if kind=='fixed_scalars' else 1) for i in range(288))


def fixture():
    arrays=dict(feature_matrix=np.zeros((1498,292)),target=np.ones(1498),objective_weight=np.ones(1498))
    settings=c.d.full.load_fit_settings();coef,z,r,_=c.d.feasible_start(arrays,settings)
    return arrays,coef,z.astype(float),r,settings


def test_fixed_witness_feasible_not_promoted():
    args=fixture();result=c.audit(*args,'fixed_scalars')
    assert result['passed'] and result['fractional_selection_count']==0
    assert result['usable_as_mio_incumbent'] is False


def test_fractional_point_not_rounded_or_promoted():
    arrays,coef,z,r,settings=fixture();z[1]=.1;coef[1]=1.
    result=c.audit(arrays,coef,z,r,settings,'relaxed_k14')
    assert result['passed'] and result['fractional_selection_count']==1
    assert result['usable_as_mio_incumbent'] is False
    assert not c.audit(arrays,coef,z,r,settings,'fixed_scalars')['passed']


@pytest.mark.parametrize('change',['link','budget','ueg','scalar','residual','finite'])
def test_invalid_relaxation_rejected(change):
    arrays,coef,z,r,settings=fixture()
    if change=='link':coef[1]=1.
    if change=='budget':z[:20]=1.
    if change=='ueg':coef[288]=.5
    if change=='scalar':coef[289]=2.
    if change=='residual':r[0]+=1e-5
    if change=='finite':coef[0]=np.nan
    assert not c.audit(arrays,coef,z,r,settings,'relaxed_k14')['passed']


def test_disabled_release_stops(tmp_path,monkeypatch):
    path=tmp_path/'release.json';c.write(path,dict(user_approved_submission=False))
    monkeypatch.setattr(c,'check_plan',lambda:{})
    monkeypatch.setattr(c.subprocess,'check_output',lambda *a,**k:pytest.fail('git reached'))
    with pytest.raises(ValueError,match='disabled'):c.check_release(path)
