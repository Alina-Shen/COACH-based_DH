"""Offline scope, solver configuration and semilocal-start acceptance gates."""
from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2.scripts import search_diagnostic_v1 as s
from revwb97m2.tests.test_continuous_k14_v1 import fixture


def test_support_matches_coach_seed_plus_dh_scalars():
    assert s.SUPPORT==(0,1,96,192,288,289,290,291)


@pytest.mark.parametrize('case',list(s.CASES))
def test_configuration(case):
    values={};z={i:SimpleNamespace(VType='B',LB=0.,UB=1.) for i in range(292)}
    m=SimpleNamespace(update=lambda:None,NumBinVars=0,NumIntVars=0,setParam=lambda k,v:values.update({k:v}))
    s.configure(m,z,case)
    assert values==s.CASES[case]['params']
    if case=='fixed_coach8':
        assert all(z[i].LB==z[i].UB==float(i in s.SUPPORT) for i in z)
    if 'barrier' in case and s.CASES[case]['kind'] in ('root','mio'):
        assert values['Method']==values['NodeMethod']==2


def semilocal():
    arrays,b,z,r,settings=fixture()
    z[:]=0;z[list(s.SUPPORT)]=1;b[0]=.85;b[288]=.15;b[1]=b[96]=b[192]=1.
    return arrays,b,z,r,settings


def test_semilocal_witness_and_import():
    arrays,b,z,r,settings=semilocal()
    assert s.candidate(arrays,settings,b,z,r,'fixed')['passed']
    beta={i:SimpleNamespace() for i in range(292)};sel={i:SimpleNamespace() for i in range(292)}
    rs={f'weighted_residual[{i}]':SimpleNamespace() for i in range(1498)}
    m=SimpleNamespace(getVarByName=rs.get)
    s.assign_start(m,beta,sel,dict(coefficients=b,selection=z,residuals=r),arrays,settings)
    assert np.array_equal([beta[i].Start for i in beta],b)
    assert np.array_equal([sel[i].Start for i in sel],z)


@pytest.mark.parametrize('bad',['fractional','ueg','residual','wrong_support'])
def test_invalid_fixed_start_rejected(bad):
    arrays,b,z,r,settings=semilocal()
    if bad=='fractional':z[1]=.2
    if bad=='ueg':b[288]=.5
    if bad=='residual':r[0]+=1e-5
    if bad=='wrong_support':z[2]=1
    assert not s.candidate(arrays,settings,b,z,r,'fixed')['passed']


def test_disabled_release(tmp_path,monkeypatch):
    plan=tmp_path/'plan.json';release=tmp_path/'release.json'
    s.c.write(plan,{});s.c.write(release,dict(submission_authorized=False))
    monkeypatch.setattr(s,'PLAN',plan)
    with pytest.raises(ValueError,match='disabled'):s.check(release)
