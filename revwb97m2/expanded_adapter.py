"""Versioned expanded execution overlay; preserve immutable v7 science provenance."""
from pathlib import Path
import numpy as np
import yaml
from revwb97m2.scripts import expanded_objective_v1 as e

c=e.c
CONFIG=c.ROOT/'revwb97m2/configs/expanded_validation_v1.yaml'


def settings():
    config=yaml.safe_load(CONFIG.read_text())
    expected=dict(schema_version=1,stage='full1498_expanded_validation',
        base_scientific_specification='revwb97m2/configs/scientific_spec.yaml',
        base_scientific_specification_sha256='32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc',
        overrides=dict(objective_representation='expanded_quadratic',objective_normalization='full_sse',
                       selection='big_M',seconds_per_solve=600,threads=16),budgets=[14,80],grid='99590',
        full_training_grid_advancement_gate=True,SOS1='deferred',bulk_authorized=False)
    c.require(config==expected,'unsupported execution overlay')
    base=c.d.full.load_fit_settings()
    c.require(base.specification_sha256==config['base_scientific_specification_sha256'],'science changed')
    return base


def build(arrays,fit_settings,budget,rows,env):
    import gurobipy as gp
    m,beta,z=c.d.build_model(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
        settings=fit_settings,budget=budget,seconds=600,threads=16,env=env)
    try:
        e.expand_model(m,beta,arrays,fit_settings)
        for i in rows:
            expr=gp.quicksum(float(v)*beta[j] for j,v in enumerate(arrays['grid_difference_99590'][i]))
            m.addConstr(expr<=fit_settings.grid_limit,name=f'grid_upper[{i}]')
            m.addConstr(expr>=-fit_settings.grid_limit,name=f'grid_lower[{i}]')
        m.update()
        c.require((m.NumVars,m.NumConstrs,m.NumBinVars,m.NumSOS)==(584,590+2*len(rows),292,0),'expanded dimensions')
        return m,beta,z
    except Exception:
        m.dispose();raise


def audit(arrays,b,z,budget,rows,fit_settings):
    c.require(b.shape==z.shape==(292,),'shape')
    finite=bool(np.isfinite(b).all() and np.isfinite(z).all())
    integral=bool(finite and np.max(np.abs(z-np.rint(z)))<=1e-9 and np.all(z>=-1e-9) and np.all(z<=1+1e-9))
    selected=z>.5
    checked=c.d.audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],b,selected,
        model_name='R2',budget=budget,settings=fit_settings,
        grid_difference=arrays['grid_difference_99590'][rows] if len(rows) else None)
    link=bool(finite and np.max(np.abs(b)-25*z)<=1e-9)
    maxima={g:float(np.max(np.abs(arrays['grid_difference_'+g]@b))*fit_settings.conversion) for g in ('99590','75302')}
    passed=bool(finite and integral and link and checked['passed'])
    return dict(passed=passed,integral=integral,linkage=link,independent=checked,grid_max_kcal_mol=maxima,
        full_grid_passed=bool(maxima['99590']<=fit_settings.grid_public_limit*fit_settings.conversion),
        semilocal_nonzero_count=int(np.count_nonzero(np.abs(b[:288])>1e-9)))


def start_audit(arrays,b,z,budget,rows,fit_settings):
    ungridded=audit(arrays,b,z,budget,np.array([],dtype=int),fit_settings)
    c.require(ungridded['passed'],'invalid primal start')
    # Discovery starts can violate newly selected grid rows. Record this honestly;
    # Gurobi may repair or reject the start; never call it grid-feasible in advance.
    return dict(ungridded=ungridded,grid_feasible=audit(arrays,b,z,budget,rows,fit_settings)['passed'])
