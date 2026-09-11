"""Algebraic identity and release checks, no Gurobi license."""
import numpy as np
import pytest
from revwb97m2.scripts import expanded_objective_v1 as e


@pytest.mark.parametrize('ridge',[0.,1e-10,.1])
def test_full_sse_algebra(ridge):
    rng=np.random.default_rng(7);a=rng.normal(size=(20,8));b=rng.normal(size=20)
    w=np.exp(rng.normal(size=20));coef=rng.normal(size=8)
    q,l,k=e.quadratic_terms(a,b,w,ridge)
    direct=np.sum(w*(a@coef-b)**2)+ridge*(coef@coef)
    assert np.isclose(coef@q@coef-2*l@coef+k,direct,rtol=1e-12,atol=1e-12)
    assert np.array_equal(q,q.T)
    assert np.allclose(2*q@coef-2*l,2*a.T@(w*(a@coef-b))+2*ridge*coef)


def test_ridge_matches_twice_coach_objective():
    a=np.array([[1.,2.],[3.,1.]]);b=np.array([2.,4.]);w=np.array([3.,2.]);coef=np.array([.5,.1])
    q,l,k=e.quadratic_terms(a,b,w,1e-10)
    coach=.5*coef@q@coef-l@coef+.5*k
    assert np.isclose(2*coach,np.sum(w*(a@coef-b)**2)+1e-10*(coef@coef),rtol=1e-12)


def test_disabled_release(tmp_path,monkeypatch):
    plan=tmp_path/'plan.json';release=tmp_path/'release.json'
    e.c.write(plan,{});e.c.write(release,dict(submission_authorized=False))
    monkeypatch.setattr(e,'PLAN',plan)
    with pytest.raises(ValueError,match='disabled'):e.check(release)
