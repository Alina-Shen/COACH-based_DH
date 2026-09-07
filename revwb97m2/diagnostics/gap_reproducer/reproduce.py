"""Standalone Gurobi gap probe. Requires only Python and gurobipy.

Optional --model is a research-derived LP export; do not share it unreviewed.
Uses the caller's license, never includes or prints credentials.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import gurobipy as gp


def summary(model, label):
    result = {'case':label,'status':model.Status,'solution_count':model.SolCount}
    if model.SolCount:
        obj, bound, raw = model.ObjVal, model.ObjBound, model.MIPGap
        ratio = abs(obj-bound)/abs(obj) if obj else (0. if bound == 0 else math.inf)
        result.update(objective=obj,bound=bound,unrounded_bound=model.ObjBoundC,
                      raw_gap=raw if math.isfinite(raw) else str(raw),
                      getAttr_gap=str(model.getAttr('MIPGap')),
                      derived_gap=ratio if math.isfinite(ratio) else str(ratio),
                      discrepancy=math.isfinite(ratio) and not math.isclose(raw,ratio,rel_tol=1e-7,abs_tol=1e-10),
                      variables=model.NumVars, constraints=model.NumConstrs)
    return result


def build_from_data(env, path):
    data=json.loads(path.read_text())
    a,b,w,ueg=(data[k] for k in ('a','b','weights','ueg'))
    m=gp.Model('COACH_C0_R2',env=env)
    m.Params.OutputFlag=0
    m.Params.Threads=1
    m.Params.TimeLimit=60
    m.Params.Seed=0
    m.Params.FeasibilityTol=1e-9
    m.Params.IntFeasTol=1e-9
    cols=list(range(292))
    beta=m.addVars(cols,lb=-25.,ub=25.,name='beta')
    selected=m.addVars(cols,vtype=gp.GRB.BINARY,name='selected')
    for i in cols:
        m.addConstr(beta[i]<=25*selected[i])
        m.addConstr(beta[i]>=-25*selected[i])
    for i in range(288,292):
        m.addConstr(selected[i]==1)
        beta[i].LB=0. if i==288 else 1e-8
        beta[i].UB=1. if i==288 else .99999999
    m.addConstr(gp.quicksum(selected.values())<=14,name='support_budget')
    m.addConstr(gp.quicksum(ueg[i]*beta[i] for i in cols)==1.,name='UEG_exchange')
    residual=m.addVars(len(a),lb=-gp.GRB.INFINITY,name='weighted_residual')
    for j in range(len(a)):
        m.addConstr(residual[j]==math.sqrt(w[j])*(gp.quicksum(a[j][i]*beta[i] for i in cols)-b[j]))
    m.setObjective(gp.quicksum(residual[j]*residual[j] for j in range(len(a))),gp.GRB.MINIMIZE)
    m.update()
    return m


def run(env, model_path, data_path=None):
    results=[]
    # Tiny synthetic MIQPs: test small nonzero objectives without research data.
    for scale in (1.,1e-6,1e-9):
        with gp.Model(env=env) as m:
            m.Params.Threads=1
            m.Params.TimeLimit=2
            x=m.addVar(vtype=gp.GRB.BINARY)
            m.setObjective(scale*(x-.25)*(x-.25))
            m.optimize()
            results.append(summary(m,f'synthetic_scale_{scale}'))
    if model_path or data_path:
        for repeat in range(2):
            with (build_from_data(env,data_path) if data_path else gp.read(str(model_path),env=env)) as m:
                for key,value in {'Threads':1,'TimeLimit':60,'Seed':0,
                                  'FeasibilityTol':1e-9,'IntFeasTol':1e-9}.items():
                    m.setParam(key,value)
                # LP does not retain the original MIP start: restore it explicitly.
                for i in range(292):
                    value=.8 if i==0 else .2 if i==288 else .5 if i in (289,290,291) else 0.
                    m.getVarByName(f'beta[{i}]').Start=value
                    m.getVarByName(f'selected[{i}]').Start=float(value!=0)
                m.optimize()
                results.append(summary(m,f'{"direct" if data_path else "lp"}_replay_{repeat}'))
    return {'python':platform.python_version(),'gurobi':gp.gurobi.version(),
            'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest() if model_path else None,
            'data_sha256':hashlib.sha256(data_path.read_bytes()).hexdigest() if data_path else None,
            'results':results}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    inputs=parser.add_mutually_exclusive_group()
    inputs.add_argument('--model',type=Path)
    inputs.add_argument('--data',type=Path)
    args=parser.parse_args()
    try:
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            license_path=os.getenv('GRB_LICENSE_FILE')
            if license_path:
                for line in Path(license_path).read_text().splitlines():
                    key,sep,value=line.partition('=')
                    if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):
                        env.setParam(key.strip(),int(value.strip()) if key.strip()=='LICENSEID' else value.strip())
            env.start()
            print(json.dumps(run(env,args.model,args.data),indent=2,allow_nan=False))
    except Exception as exc:
        print(json.dumps({'error_type':type(exc).__name__,
                          'gurobi_code':exc.errno if isinstance(exc,gp.GurobiError) else None}))
        raise SystemExit(1)
