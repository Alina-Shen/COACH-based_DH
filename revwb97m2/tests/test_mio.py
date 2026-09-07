import numpy as np
import pytest
from revwb97m2.mio import feature_names,ueg_vector,build_model,audit_solution


def test_explicit_solver_environment():
    gp = pytest.importorskip('gurobipy')
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.start()
        m, _, _ = build_model(np.zeros((1,292)), np.zeros(1), np.ones(1),
                              columns=[0,288,289,290,291], budget=5, env=env)
        try:
            m.optimize()
            assert m.Status == gp.GRB.OPTIMAL
        finally:
            m.dispose()


def test_named_models_and_ueg_basis():
    assert len(feature_names('R1'))==79
    assert len(feature_names('R2'))==292
    u=ueg_vector('R2')
    assert u[0]==1 and u[8]==0 and u[16]==-.5 and u[288]==1
    assert np.count_nonzero(ueg_vector('R1'))==2


def test_mandatory_scalars_and_no_sum_equality():
    pytest.importorskip('gurobipy')
    a=np.zeros((1,292))
    m,b,z=build_model(a,np.zeros(1),np.ones(1),columns=[0,288,289,290,291],budget=5)
    assert b[289].LB==1e-8 and b[291].UB==.99999999
    # A feasible vector can have VV10+PT2 != 1; scalars count toward the budget.
    coeff=np.zeros(292); coeff[[0,288,289,290,291]]=[.8,.2,.3,.4,.5]
    selected=np.zeros(292,dtype=bool); selected[[0,288,289,290,291]]=True
    assert audit_solution(a,np.zeros(1),np.ones(1),coeff,selected,model_name='R2',budget=5)['passed']
    assert not audit_solution(a,np.zeros(1),np.ones(1),coeff,selected,model_name='R2',budget=4)['passed']
    m.dispose()


def test_solver_fits_independent_scalars_and_optional_grid_constraint():
    pytest.importorskip('gurobipy')
    a=np.zeros((4,292)); a[:,288:]=np.eye(4)
    target=np.array([.2,.3,.4,.5])
    diff=np.zeros((1,292)); diff[0,289]=1e-4
    m,b,z=build_model(a,target,np.ones(4),columns=[0,288,289,290,291],budget=5,grid_difference=diff)
    m.optimize()
    assert m.Status==2
    assert b[289].X<=.015/627.5094740631/1e-4+1e-8
    assert b[290].X==pytest.approx(.4,abs=1e-6)
    assert b[291].X==pytest.approx(.5,abs=1e-6)
    assert b[0].X+b[288].X==pytest.approx(1.,abs=1e-10)
    m.dispose()
