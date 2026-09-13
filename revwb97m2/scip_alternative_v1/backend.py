"""SCIP expanded-quadratic epigraph with the existing R2 big-M constraints."""
import math
import numpy as np


def terms(a, y, weights, ridge):
    x = np.sqrt(weights)[:, None] * a
    target = np.sqrt(weights) * y
    q = x.T @ x + ridge * np.eye(a.shape[1])
    return (q + q.T) * .5, x.T @ target, float(target @ target)


def objective(arrays, beta, ridge):
    residual = arrays['feature_matrix'] @ beta - arrays['target']
    return float(arrays['objective_weight'] @ (residual * residual) + ridge * (beta @ beta))


def build(arrays, settings, budget, rows, seconds=7200, threads=16, memory_mib=32768):
    from pyscipopt import Model, quicksum
    from revwb97m2.mio import ueg_vector
    a, y, w = (np.asarray(arrays[k]) for k in ('feature_matrix', 'target', 'objective_weight'))
    rows = np.asarray(rows)
    if (a.ndim != 2 or a.shape[1] != 292 or y.shape != (len(a),) or w.shape != y.shape
            or not all(np.isfinite(x).all() for x in (a, y, w)) or np.any(w <= 0)
            or type(budget) is not int or not 4 <= budget <= 292
            or rows.ndim != 1 or rows.dtype.kind not in 'iu' or len(set(rows.tolist())) != len(rows)
            or np.any(rows < 0) or np.any(rows >= len(a))
            or not math.isfinite(seconds) or seconds <= 0 or type(threads) is not int or threads < 1
            or not math.isfinite(memory_mib) or memory_mib <= 0):
        raise ValueError('invalid SCIP model inputs')
    d = np.asarray(arrays['grid_difference_99590'])
    if d.shape != a.shape or not np.isfinite(d).all() or settings.ridge < 0:
        raise ValueError('invalid grid/ridge')
    m = Model('revwb97m2_scip_expanded_v1')
    m.hideOutput()
    params = {'limits/time': float(seconds), 'limits/memory': float(memory_mib),
        'limits/gap': 1e-4, 'limits/absgap': 1e-10, 'numerics/feastol': 1e-9,
        'randomization/randomseedshift': int(settings.seed), 'parallel/maxnthreads': threads}
    for key, value in params.items():
        m.setParam(key, value)
    beta = [m.addVar(name=f'beta[{j}]', lb=-25., ub=25.) for j in range(292)]
    z = [m.addVar(name=f'selected[{j}]', vtype='B') for j in range(292)]
    for j in range(292):
        m.addCons(beta[j] <= 25*z[j], name=f'link_upper[{j}]')
        m.addCons(beta[j] >= -25*z[j], name=f'link_lower[{j}]')
    for j in range(288, 292):
        m.addCons(z[j] == 1, name=f'mandatory[{j}]')
        m.chgVarLb(beta[j], 0. if j == 288 else 1e-8)
        m.chgVarUb(beta[j], 1. if j == 288 else .99999999)
    m.addCons(quicksum(z) <= budget, name='support_budget')
    ueg = ueg_vector('R2')
    m.addCons(quicksum(float(ueg[j])*beta[j] for j in range(292)) == 1, name='UEG_exchange')
    for i in rows:
        expr = quicksum(float(d[i,j])*beta[j] for j in range(292))
        m.addCons(expr <= settings.grid_limit, name=f'grid_upper[{i}]')
        m.addCons(expr >= -settings.grid_limit, name=f'grid_lower[{i}]')
    q, linear, constant = terms(a, y, w, settings.ridge)
    quadratic = quicksum(float(q[i,i])*beta[i]*beta[i] for i in range(292))
    quadratic += quicksum(float(2*q[i,j])*beta[i]*beta[j] for i in range(292) for j in range(i+1,292)
                          if q[i,j] != 0.)
    quadratic -= quicksum(float(2*linear[j])*beta[j] for j in range(292))
    quadratic += constant
    t = m.addVar(name='objective_epigraph', lb=0.)
    m.addCons(quadratic <= t, name='expanded_objective_epigraph')
    m.setObjective(t, 'minimize')
    metadata = dict(variables=m.getNVars(), constraints=m.getNConss(), binaries=292,
        linear_constraints=590+2*len(rows), quadratic_epigraph_constraints=1,
        parameters={k: m.getParam(k) for k in params}, selected_rows=len(rows), budget=budget,
        quadratic_constant=constant, scip_version=[m.getMajorVersion(),m.getMinorVersion(),m.getTechVersion()],
        thread_note='optimize() uses SCIP default solving mode; parallel/maxnthreads is only a ceiling')
    assert metadata['variables'] == 585 and metadata['constraints'] == 591+2*len(rows)
    return m, beta, z, t, metadata


def assign_start(m, beta, z, t, arrays, settings, coefficients, selection):
    b, selected = np.asarray(coefficients), np.asarray(selection)
    if b.shape != (292,) or selected.shape != (292,) or not np.isfinite(b).all() or not np.isfinite(selected).all():
        raise ValueError('invalid start')
    sol = m.createSol()
    for j in range(292):
        m.setSolVal(sol, beta[j], float(b[j]))
        m.setSolVal(sol, z[j], float(selected[j]))
    m.setSolVal(sol, t, objective(arrays, b, settings.ridge))
    # May reject an infeasible noisy suggestion; never clip/project coefficients.
    return bool(m.addSol(sol, free=True))


def gaps(primal, dual, raw_gap):
    # Preserve SCIP's own gap; common normalization is comparable with Gurobi.
    finite = math.isfinite(primal) and math.isfinite(dual)
    absolute = abs(primal-dual) if finite else None
    common = absolute/abs(primal) if finite and primal != 0 else None
    return dict(scip_raw_gap=raw_gap if math.isfinite(raw_gap) else None,
                absolute_gap=absolute, common_primal_normalized_gap=common)
