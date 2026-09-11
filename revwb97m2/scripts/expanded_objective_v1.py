"""Matched residual versus COACH-style expanded objective; retain big-M and science."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np
from revwb97m2.scripts import search_diagnostic_v1 as base

c=base.c
ROOT=c.ROOT
PLAN=ROOT/'revwb97m2/manifests/expanded_objective_v1/plan.json'
CASES=('residual_mio','expanded_qp','expanded_mio')


def quadratic_terms(a,b,w,ridge):
    """Full-SSE normalization: beta'Q beta -2*l'beta + constant."""
    x=np.sqrt(w)[:,None]*a;y=np.sqrt(w)*b
    q=x.T@x+ridge*np.eye(a.shape[1])
    return (q+q.T)*.5,x.T@y,float(y@y)


def expand_model(m,beta,arrays,settings):
    import gurobipy as gp
    q,l,k=quadratic_terms(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],settings.ridge)
    residual=[m.getVarByName(f'weighted_residual[{i}]') for i in range(len(arrays['target']))]
    c.require(all(v is not None for v in residual),'missing original residual variables')
    rows={}
    for v in residual:
        column=m.getCol(v)
        c.require(column.size()==1,'unexpected residual constraint structure')
        con=column.getConstr(0);rows[con.index]=con
    c.require(len(rows)==len(residual),'shared residual rows')
    m.setObjective(0)
    m.remove(list(rows.values()));m.remove(residual);m.update()
    objective=gp.quicksum(float(q[i,i])*beta[i]*beta[i] for i in range(292))
    objective+=gp.quicksum(float(2*q[i,j])*beta[i]*beta[j] for i in range(292) for j in range(i+1,292))
    objective-=gp.quicksum(float(2*l[i])*beta[i] for i in range(292));objective+=k
    m.setObjective(objective,gp.GRB.MINIMIZE);m.update()
    c.require((m.NumVars,m.NumConstrs,m.NumSOS)==(584,590,0),'expanded dimensions/big-M')
    return q,l,k


def check(release):
    p=c.read(PLAN);r=c.read(release)
    c.require(r.get('submission_authorized') is True and r.get('tests_passed') is True and
              r.get('resources_reviewed') is True and r['plan_sha256']==c.digest(PLAN),'release disabled')
    c.require(p['cases']==list(CASES) and p['matrix_sha256']==c.d.full.MATRIX_SHA and
              p['input_sha256']==c.d.full.INPUT_SHA and p['selection']=='big_M','scope')
    report=ROOT/r['test_report'];t=c.read(report)
    c.require(c.digest(report)==r['test_report_sha256'] and t['passed'] and t['commit']==r['commit'] and
              t['plan_sha256']==c.digest(PLAN),'tests')
    for name,sha in {**p['hashes'],str(PLAN.relative_to(ROOT)):c.digest(PLAN)}.items():
        raw=subprocess.check_output(['git','show',r['commit']+':'+name],cwd=ROOT)
        c.require(c.digest(ROOT/name)==sha and hashlib.sha256(raw).hexdigest()==sha,'uncommitted/changed')
    c.require(tuple(r['route'][k] for k in ('partition','account','qos')) in c.d.full.ROUTES,'route')
    return p,r


def solve(folder,case,arrays,settings,start,env):
    import gurobipy as gp
    folder.mkdir();m=None
    try:
        m,beta,z=c.d.build_model(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
            settings=settings,budget=14,seconds=600,threads=16,env=env)
        expanded=case.startswith('expanded');qp=case=='expanded_qp'
        terms=expand_model(m,beta,arrays,settings) if expanded else None
        if qp:
            c.configure(m,z,'relaxed_k14');m.Params.Method=2;m.Params.BarConvTol=1e-12
        else:
            b=np.asarray(start['coefficients']);sel=np.asarray(start['selection']);r=np.asarray(start['residuals'])
            c.require(base.candidate(arrays,settings,b,sel,r,'mio')['passed'],'start audit')
            if not expanded:base.assign_start(m,beta,z,start,arrays,settings)
            else:
                for i in range(292):beta[i].Start=float(b[i]);z[i].Start=float(sel[i])
            c.write(folder/'start.json',start)
        c.require(m.NumSOS==0,'SOS1 forbidden')
        m.write(str(folder/'model.mps.gz'))
        keys=('Method','NodeMethod','Presolve','PreQLinearize','BarConvTol','NumericFocus','TimeLimit',
              'Threads','Seed','FeasibilityTol','IntFeasTol','MIPGap','MIPGapAbs')
        c.write(folder/'model.json',dict(case=case,variables=m.NumVars,constraints=m.NumConstrs,binaries=m.NumBinVars,
            sos=m.NumSOS,version=list(gp.gurobi.version()),parameters={k:m.getParamInfo(k)[2] for k in keys},
            objective_normalization='full_SSE',selection='big_M'))
        if terms is not None:
            for name,value in zip(('Q','linear','constant'),terms):np.save(folder/(name+'.npy'),value)
        m.Params.OutputFlag=1;m.Params.LogToConsole=0;m.Params.LogFile=''
        with (folder/'progress.jsonl').open('x') as stream:
            callback,errors=c.d.progress_callback(stream,gp.GRB);m.optimize(callback)
        result=dict(case=case,status=int(m.Status),runtime=float(m.Runtime),solution_count=int(m.SolCount),
            callback_errors=errors,passed=False,objective=None)
        if not qp:result.update(bound=c.d.numeric(m.ObjBound),nodes=float(m.NodeCount))
        if m.SolCount:
            b=np.array([beta[i].X for i in range(292)]);sel=np.array([z[i].X for i in range(292)])
            direct=np.sqrt(arrays['objective_weight'])*(arrays['feature_matrix']@b-arrays['target'])
            r=direct if expanded else np.array([m.getVarByName(f'weighted_residual[{i}]').X for i in range(1498)])
            checked=base.candidate(arrays,settings,b,sel,r,'qp' if qp else 'mio')
            for name,value in [('coefficients',b),('selection',sel),('residuals',r)]:np.save(folder/(name+'.npy'),value)
            actual=checked['continuous_audit']['objective']
            result.update(objective=float(m.ObjVal),audit=checked,recomputed_objective=actual,
                objective_disagreement=float(m.ObjVal-actual),residual_source='recomputed_not_solver' if expanded else 'solver',
                passed=bool(m.Status in (2,9) and not errors and checked['passed'] and np.isclose(m.ObjVal,actual,rtol=1e-7,atol=1e-10)))
            if not qp:result['gaps']=c.d.gap_report(m.ObjVal,m.ObjBound,m.MIPGap)
        c.write(folder/'result.json',result);return result
    finally:
        if m is not None:m.dispose()


def run(release):
    p,record=check(release);c.d.full.check_allocation(record['route'])
    job=os.environ['SLURM_JOB_ID'];c.require(job.isdigit(),'job')
    root=Path(p['output_parent'])/job;c.require(not root.exists(),'preserve outputs')
    settings=c.d.full.load_fit_settings();arrays,_=c.d.full.load_inputs(c.d.full.matrix_manifest(),settings)
    source=c.read(ROOT/p['start_report'])['fixed_start']
    start=dict(coefficients=source['coefficients'],selection=source['selected'],residuals=source['residuals'])
    parent=root.parent
    while not parent.exists():parent=parent.parent
    c.require(shutil.disk_usage(parent).free>32*1024**3,'storage')
    root.mkdir(parents=True)
    c.write(root/'identity.json',dict(plan_sha256=c.digest(PLAN),release=str(Path(release).resolve()),
        release_sha256=c.digest(release),commit=record['commit']))
    try:
        import gurobipy as gp
        fields={}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            k,sep,v=line.partition('=')
            if sep and k.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):fields[k.strip()]=v.strip()
        results=[]
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            for k in ('WLSACCESSID','WLSSECRET','LICENSEID'):env.setParam(k,int(fields[k]) if k=='LICENSEID' else fields[k])
            env.start()
            for case in CASES:
                r=solve(root/case,case,arrays,settings,start,env);results.append(r)
                print(case,r['status'],r['passed'],flush=True);c.require(not r['callback_errors'],'callback')
        c.write(root/'publication.json',dict(artifacts={str(f.relative_to(root)):c.digest(f) for f in root.rglob('*') if f.is_file()}))
        c.write(root/'completion.json',dict(publication_sha256=c.digest(root/'publication.json'),results=results,bulk_authorized=False))
        return 0 if all(r['passed'] for r in results) else 1
    except Exception as exc:
        c.write(root/'failure.json',dict(error_type=type(exc).__name__,error_code=getattr(exc,'errno',None)));return 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True)
    raise SystemExit(run(p.parse_args().release))
