"""Named-feature C0 best-subset weighted least squares, independent of legacy COACH."""
import numpy as np

SCALARS = ('short_range_hf', 'vv10', 'pt2', 'd4_atm')


def feature_names(model):
    if model not in ('R1', 'R2'):
        raise ValueError(model)
    nw, nu = (5, 5) if model == 'R1' else (12, 8)
    return [f'{channel}_w{w}_u{u}' for channel in ('exchange','same_spin','opposite_spin')
            for w in range(nw) for u in range(nu)] + list(SCALARS)


def ueg_vector(model):
    names = feature_names(model)
    result = np.zeros(len(names))
    if model == 'R1':
        result[0] = 1.
    else:
        # Exchange is monomial in u and Legendre in the companion coordinate.
        result[np.arange(12)*8] = np.polynomial.legendre.legvander(0.,11).reshape(-1)
    result[names.index('short_range_hf')] = 1.
    return result


def build_model(a, b, weights, *, model_name='R2', budget=14,
                columns=None, grid_difference=None, seconds=60, threads=1, seed=0):
    import gurobipy as gp
    from gurobipy import GRB
    names = feature_names(model_name)
    a, b, weights = np.asarray(a), np.asarray(b), np.asarray(weights)
    if a.ndim != 2 or a.shape[1] != len(names) or b.shape != (len(a),) or weights.shape != b.shape:
        raise ValueError('named model/input dimensions disagree')
    if not all(np.isfinite(x).all() for x in (a,b,weights)) or np.any(weights<=0):
        raise ValueError('nonfinite data or nonpositive weights')
    cols = list(range(len(names))) if columns is None else list(columns)
    mandatory = [names.index(s) for s in SCALARS]
    if len(set(cols))!=len(cols) or not set(mandatory)<=set(cols) or any(i<0 or i>=len(names) for i in cols):
        raise ValueError('invalid columns or missing mandatory scalar')
    if not 4<=budget<=len(cols):
        raise ValueError('invalid sparsity budget')
    m=gp.Model('COACH_C0_'+model_name)
    m.Params.OutputFlag=0
    m.Params.Threads=threads
    m.Params.TimeLimit=seconds
    m.Params.Seed=seed
    m.Params.FeasibilityTol=1e-9
    m.Params.IntFeasTol=1e-9
    beta=m.addVars(cols,lb=-25.,ub=25.,name='beta')
    selected=m.addVars(cols,vtype=GRB.BINARY,name='selected')
    for i in cols:
        m.addConstr(beta[i]<=25*selected[i])
        m.addConstr(beta[i]>=-25*selected[i])
    for i in mandatory:
        m.addConstr(selected[i]==1)
        beta[i].LB=0. if names[i]=='short_range_hf' else 1e-8
        beta[i].UB=1. if names[i]=='short_range_hf' else .99999999
    m.addConstr(gp.quicksum(selected.values())<=budget,name='support_budget')
    ueg=ueg_vector(model_name)
    m.addConstr(gp.quicksum(ueg[i]*beta[i] for i in cols)==1.,name='UEG_exchange')
    residual=m.addVars(len(a),lb=-GRB.INFINITY,name='weighted_residual')
    for j in range(len(a)):
        m.addConstr(residual[j]==np.sqrt(weights[j])*(gp.quicksum(a[j,i]*beta[i] for i in cols)-b[j]))
    m.setObjective(gp.quicksum(residual[j]*residual[j] for j in range(len(a))),GRB.MINIMIZE)
    if grid_difference is not None:
        d=np.asarray(grid_difference)
        if d.ndim!=2 or d.shape[1]!=len(names) or not np.isfinite(d).all():
            raise ValueError('invalid grid difference')
        for row in d:
            expr=gp.quicksum(row[i]*beta[i] for i in cols)
            m.addConstr(expr<=.015/627.5094740631)
            m.addConstr(expr>=-.015/627.5094740631)
    m.update()
    return m,beta,selected


def audit_solution(a,b,weights,coeff,selected,*,model_name,budget,grid_difference=None):
    names=feature_names(model_name)
    coeff=np.asarray(coeff)
    checks={
        'finite':bool(np.isfinite(coeff).all()),
        'coefficient_bound':bool(np.max(np.abs(coeff))<=25.+1e-8),
        'ueg':bool(abs(ueg_vector(model_name)@coeff-1.)<=1e-10),
        'support_budget':sum(selected)<=budget,
        'unselected_zero':bool(np.max(np.abs(coeff[np.logical_not(selected)]),initial=0.)<=1e-9),
        'mandatory_selected':all(selected[names.index(s)] for s in SCALARS),
        'sr_bounds':0.-1e-9<=coeff[-4]<=1.+1e-9,
        'independent_scalar_bounds':bool(np.all(coeff[-3:]>=1e-8-1e-9) and np.all(coeff[-3:]<=.99999999+1e-9)),
    }
    if grid_difference is not None:
        checks['grid']=bool(np.max(np.abs(grid_difference@coeff),initial=0.)<=.015/627.5094740631+1e-9)
    objective=float(np.sum(weights*(a@coeff-b)**2))
    return {'checks':checks,'passed':all(checks.values()),'weighted_sse_hartree2':objective}
