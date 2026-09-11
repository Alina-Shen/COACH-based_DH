"""Offline execution gates and full-primal start import, no license required."""
from types import SimpleNamespace
import numpy as np
import pytest
from revwb97m2.scripts import solver_recovery_v1 as s
from revwb97m2.tests.test_continuous_k14_v1 import fixture


def test_precision_variants_do_not_change_scientific_tolerances():
    assert s.VARIANTS=={'barrier_tight':{'BarConvTol':1e-12},
        'barrier_careful':{'BarConvTol':1e-12,'NumericFocus':3},'mio_7200':{}}


def test_disabled_release(tmp_path,monkeypatch):
    plan=tmp_path/'plan.json';release=tmp_path/'release.json'
    s.c.write(plan,{});s.c.write(release,{'submission_authorized':False})
    monkeypatch.setattr(s,'PLAN',plan)
    with pytest.raises(ValueError,match='disabled'):s.check(release)


@pytest.mark.parametrize('invalid',[False,True])
def test_start_import_all_primal_variables(invalid):
    arrays,coef,z,residual,settings=fixture()
    start=s.reader.fixed_start(arrays,settings,coef,z,residual)
    if invalid:start['coefficients'][288]=.5
    beta={i:SimpleNamespace() for i in range(292)}
    selected={i:SimpleNamespace() for i in range(292)}
    r={f'weighted_residual[{i}]':SimpleNamespace() for i in range(1498)}
    model=SimpleNamespace(getVarByName=r.get)
    if invalid:
        with pytest.raises(ValueError):s.import_start(model,beta,selected,start,arrays,settings)
        assert not hasattr(beta[0],'Start')
    else:
        s.import_start(model,beta,selected,start,arrays,settings)
        assert np.array_equal([beta[i].Start for i in range(292)],coef)
        assert np.array_equal([selected[i].Start for i in range(292)],z)
        assert np.array_equal([r[f'weighted_residual[{i}]'].Start for i in range(1498)],residual)
