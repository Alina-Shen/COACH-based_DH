"""Additive SCIP-only tests; no legacy test files or environments changed."""
from types import SimpleNamespace
import numpy as np
import pytest
from . import backend


def problem():
    a=np.zeros((4,292)); a[:,288:]=np.eye(4)
    y=np.array([1.,.4,.2,.6])
    arrays=dict(feature_matrix=a,target=y,objective_weight=np.ones(4),
                grid_difference_99590=np.zeros_like(a))
    settings=SimpleNamespace(ridge=1e-10,seed=0,grid_limit=.015/627.5094740631*.999)
    return arrays,settings


def test_expanded_matches_independent_residual():
    arrays,s=problem(); rng=np.random.default_rng(10)
    q,l,c=backend.terms(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],s.ridge)
    for _ in range(5):
        b=rng.normal(size=292)
        assert np.isclose(b@q@b-2*l@b+c,backend.objective(arrays,b,s.ridge),rtol=1e-12)


def test_constraints_and_scalar_bounds():
    a,s=problem();m,b,z,t,meta=backend.build(a,s,14,np.array([0,1]),seconds=2,threads=1)
    try:
        assert (meta['variables'],meta['constraints'])==(585,595)
        assert b[288].getLbOriginal()==0 and b[288].getUbOriginal()==1
        assert b[289].getLbOriginal()==1e-8 and b[291].getUbOriginal()==.99999999
        names={c.name for c in m.getConss()}
        assert {'UEG_exchange','support_budget','expanded_objective_epigraph','grid_upper[1]'} <= names
    finally:m.freeProb()


def test_known_optimum_full_292_column_model():
    a,s=problem();m,b,z,t,meta=backend.build(a,s,4,np.array([],dtype=int),seconds=10,threads=1)
    try:
        start=np.zeros(292);start[288:]=a['target'];sel=np.zeros(292);sel[288:]=1
        backend.assign_start(m,b,z,t,a,s,start,sel)
        m.optimize()
        assert m.getNSols()>0
        coeff=np.array([m.getVal(v) for v in b])
        assert backend.objective(a,coeff,s.ridge)<1e-7
        assert abs(coeff[288]-1)<1e-9
    finally:m.freeProb()


@pytest.mark.parametrize('rows',[np.array([0,0]),np.array([-1]),np.array([4]),np.array([0.])])
def test_invalid_grid_identity(rows):
    a,s=problem()
    with pytest.raises(ValueError):backend.build(a,s,14,rows)


def test_scip_gap_not_relabelled_gurobi_gap():
    x=backend.gaps(2.,1.,1.)
    assert x['scip_raw_gap']==1. and x['common_primal_normalized_gap']==.5


def test_gurobi_import_blocked():
    from .runtime import bootstrap
    bootstrap()
    with pytest.raises(ImportError,match='forbidden'):
        __import__('gurobipy')
