"""Roundoff must not weaken scientific or discrete acceptance checks."""
from copy import deepcopy
import numpy as np
import pytest
from revwb97m2.scripts import continuous_readback_v2 as r
from revwb97m2.tests.test_continuous_k14_v1 import fixture


def example():
    return r.c.audit(*fixture(),'fixed_scalars')


def test_roundoff_allowed():
    a=example();b=deepcopy(a)
    b['objective']=np.nextafter(b['objective'],np.inf).item()
    assert r.audits_match(a,b)


@pytest.mark.parametrize('key',['weighted_sse','ridge','objective'])
@pytest.mark.parametrize('value',[float('nan'),float('inf'),1e9])
def test_changed_or_nonfinite_numeric_rejected(key,value):
    a=example();b=deepcopy(a);b[key]=value
    assert not r.audits_match(a,b)


@pytest.mark.parametrize('change',['check','passed','fraction','missing'])
def test_exact_fields_rejected(change):
    a=example();b=deepcopy(a)
    if change=='check':b['checks']['ueg']=False
    if change=='passed':b['passed']=False
    if change=='fraction':b['fractional_selection_count']=1
    if change=='missing':del b['note']
    assert not r.audits_match(a,b)


def test_fixed_start_reaudited_not_submitted():
    arrays,coef,z,residual,settings=fixture()
    start=r.fixed_start(arrays,settings,coef,z,residual)
    assert start['audit']['passed'] and not start['submission_authorized']
    assert not start['grid_constraints_audited']


@pytest.mark.parametrize('change',['fraction','ueg','residual'])
def test_invalid_start_rejected(change):
    arrays,coef,z,residual,settings=fixture()
    if change=='fraction':z[0]=1e-12
    if change=='ueg':coef[288]-=1e-7
    if change=='residual':residual[0]+=1e-7
    with pytest.raises(ValueError):r.fixed_start(arrays,settings,coef,z,residual)
