"""Controlled QP/root comparison and COACH-informed sparse start; no bulk fitting."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np
from revwb97m2.scripts import solver_recovery_v1 as old

c=old.c
ROOT=c.ROOT
PLAN=ROOT/'revwb97m2/manifests/search_diagnostic_v1/plan.json'
SUPPORT=(0,1,96,192,288,289,290,291)
CASES={
    'qp_dual':dict(kind='qp',params={'Method':1}),
    'qp_barrier':dict(kind='qp',params={'Method':2,'BarConvTol':1e-12}),
    'root_auto':dict(kind='root',params={'NodeLimit':1}),
    'root_barrier':dict(kind='root',params={'NodeLimit':1,'Method':2,'NodeMethod':2,'BarConvTol':1e-12}),
    'fixed_coach8':dict(kind='fixed',params={'Method':2,'BarConvTol':1e-12}),
    'semilocal_auto':dict(kind='mio',params={}),
    'semilocal_barrier':dict(kind='mio',params={'Method':2,'NodeMethod':2,'BarConvTol':1e-12}),
}


def check(release):
    p=c.read(PLAN);r=c.read(release)
    c.require(r.get('submission_authorized') is True and r.get('tests_passed') is True and
              r.get('resources_reviewed') is True and r['plan_sha256']==c.digest(PLAN),'release disabled')
    c.require(p['cases']==CASES and p['support']==list(SUPPORT) and
              p['matrix_sha256']==c.d.full.MATRIX_SHA and p['input_sha256']==c.d.full.INPUT_SHA,'scope changed')
    test=ROOT/r['test_report'];t=c.read(test)
    c.require(c.digest(test)==r['test_report_sha256'] and t['passed'] and t['commit']==r['commit'] and
              t['plan_sha256']==c.digest(PLAN),'test identity')
    for name,sha in {**p['hashes'],str(PLAN.relative_to(ROOT)):c.digest(PLAN)}.items():
        raw=subprocess.check_output(['git','show',r['commit']+':'+name],cwd=ROOT)
        c.require(c.digest(ROOT/name)==sha and hashlib.sha256(raw).hexdigest()==sha,'uncommitted/changed file')
    c.require(tuple(r['route'][k] for k in ('partition','account','qos')) in c.d.full.ROUTES,'route')
    return p,r


def configure(model,z,case):
    kind=CASES[case]['kind']
    if kind in ('qp','fixed'):
        c.configure(model,z,'relaxed_k14')
    if kind=='fixed':
        for i,v in z.items():v.LB=v.UB=float(i in SUPPORT)
    for k,v in CASES[case]['params'].items():model.setParam(k,v)
    model.update()


def candidate(arrays,settings,b,z,r,kind):
    audit=c.audit(arrays,b,z,r,settings,'relaxed_k14')
    if kind in ('qp','fixed'):
        integral=bool(np.array_equal(z,np.rint(z)))
    else:
        integral=bool(np.max(np.abs(z-np.rint(z)))<=1e-9)
    checked=None
    if integral:
        checked=c.d.audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
            b,z>.5,model_name='R2',budget=14,settings=settings)
    valid=audit['passed'] and (kind=='qp' or (integral and checked['passed']))
    if kind=='fixed':valid=valid and np.array_equal(z,np.isin(np.arange(292),SUPPORT).astype(float))
    return dict(passed=bool(valid),continuous_audit=audit,integral=integral,mio_audit=checked)


def assign_start(m,beta,z,start,arrays,settings):
    b=np.asarray(start['coefficients']);sel=np.asarray(start['selection']);r=np.asarray(start['residuals'])
    audited=candidate(arrays,settings,b,sel,r,'mio')
    c.require(audited['passed'] and np.array_equal(sel,np.rint(sel)),'invalid start')
    fresh=np.sqrt(arrays['objective_weight'])*(arrays['feature_matrix']@b-arrays['target'])
    for i in range(292):beta[i].Start=float(b[i]);z[i].Start=float(sel[i])
    for i,v in enumerate(fresh):m.getVarByName(f'weighted_residual[{i}]').Start=float(v)
    return audited


def solve(folder,case,arrays,settings,start,env):
    import gurobipy as gp
    folder.mkdir();m=None
    try:
        m,beta,z=c.d.build_model(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
            settings=settings,budget=14,seconds=600,threads=16,env=env)
        configure(m,z,case);kind=CASES[case]['kind']
        if kind in ('root','mio'):
            c.write(folder/'start.json',dict(start=start,audit=assign_start(m,beta,z,start,arrays,settings)))
        m.write(str(folder/'model.mps.gz'))
        keys=('Method','NodeMethod','NodeLimit','Presolve','PreQLinearize','MIQCPMethod','BarConvTol',
              'NumericFocus','TimeLimit','Threads','Seed','FeasibilityTol','IntFeasTol','MIPGap','MIPGapAbs')
        c.write(folder/'model.json',dict(case=case,variables=m.NumVars,constraints=m.NumConstrs,
            binaries=m.NumBinVars,version=list(gp.gurobi.version()),parameters={k:m.getParamInfo(k)[2] for k in keys}))
        # Quiet WLS environment was started before model-only diagnostics are enabled.
        # Persist only selected algorithm/presolve/root/numerical messages; never license data.
        m.Params.OutputFlag=1;m.Params.LogToConsole=0;m.Params.LogFile=''
        with (folder/'progress.jsonl').open('x') as stream, (folder/'algorithm.txt').open('x') as alg:
            base,errors=c.d.progress_callback(stream,gp.GRB)
            def callback(model,where):
                base(model,where)
                try:
                    if where==gp.GRB.Callback.MESSAGE:
                        msg=model.cbGet(gp.GRB.Callback.MSG_STRING).strip()
                        prefixes=('Presolve','Presolved:','Root relaxation:','Root barrier','Root simplex',
                            'Barrier solved','Barrier performed','Concurrent','Deterministic concurrent',
                            'Warning:','Model has','Variable types:','Explored ','Solution count ',
                            'Optimal solution','Time limit','Node limit','Best objective')
                        if msg.startswith(prefixes) and not any(k in msg.lower() for k in ('license','wls','secret','accessid')):
                            alg.write(msg+'\n');alg.flush()
                except Exception as exc:errors.append(type(exc).__name__);model.terminate()
            m.optimize(callback)
        result=dict(case=case,status=int(m.Status),runtime=float(m.Runtime),solution_count=int(m.SolCount),
            passed=False,callback_errors=errors,objective=None)
        exported=None
        if kind in ('root','mio'):
            result.update(bound=c.d.numeric(m.ObjBound),nodes=float(m.NodeCount))
        if m.SolCount:
            b=np.array([beta[i].X for i in range(292)]);sel=np.array([z[i].X for i in range(292)])
            r=np.array([m.getVarByName(f'weighted_residual[{i}]').X for i in range(1498)])
            for name,v in [('coefficients',b),('selection',sel),('residuals',r)]:np.save(folder/(name+'.npy'),v)
            checked=candidate(arrays,settings,b,sel,r,kind)
            result.update(objective=float(m.ObjVal),audit=checked,quality={k:c.d.numeric(m.getAttr(k)) for k in ('ConstrVio','BoundVio')},
                semilocal_nonzero_count=int(np.count_nonzero(np.abs(b[:288])>1e-9)))
            result['passed']=bool(m.Status in ((2,8,9) if kind=='root' else (2,9)) and not errors and
                checked['passed'] and np.isclose(m.ObjVal,checked['continuous_audit']['objective'],rtol=1e-7,atol=1e-10))
            if kind in ('root','mio'):result['gaps']=c.d.gap_report(m.ObjVal,m.ObjBound,m.MIPGap)
            if kind=='fixed' and result['passed'] and result['semilocal_nonzero_count']>0:
                exported=dict(coefficients=b.tolist(),selection=sel.tolist(),
                    residuals=(np.sqrt(arrays['objective_weight'])*(arrays['feature_matrix']@b-arrays['target'])).tolist())
                c.write(folder/'candidate_start.json',dict(start=exported,audit=checked,
                    grid_audited=False,production_authorized=False,matrix_sha256=c.d.full.MATRIX_SHA))
        c.write(folder/'result.json',result)
        return result,exported
    finally:
        if m is not None:m.dispose()


def run(release):
    p,record=check(release);c.d.full.check_allocation(record['route'])
    job=os.environ['SLURM_JOB_ID'];c.require(job.isdigit(),'job id')
    root=Path(p['output_parent'])/job;c.require(not root.exists(),'preserve output')
    settings=c.d.full.load_fit_settings();arrays,_=c.d.full.load_inputs(c.d.full.matrix_manifest(),settings)
    source=c.read(ROOT/p['start_report'])['fixed_start']
    start=dict(coefficients=source['coefficients'],selection=source['selected'],residuals=source['residuals'])
    parent=root.parent
    while not parent.exists():parent=parent.parent
    c.require(shutil.disk_usage(parent).free>32*1024**3,'storage')
    root.mkdir(parents=True)
    c.write(root/'identity.json',dict(plan_sha256=c.digest(PLAN),commit=record['commit'],release=str(Path(release).resolve()),release_sha256=c.digest(release)))
    try:
        import gurobipy as gp
        fields={}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            k,sep,v=line.partition('=')
            if sep and k.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):fields[k.strip()]=v.strip()
        results=[];semi=None
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            for k in ('WLSACCESSID','WLSSECRET','LICENSEID'):env.setParam(k,int(fields[k]) if k=='LICENSEID' else fields[k])
            env.start()
            for case in CASES:
                if CASES[case]['kind']=='mio' and semi is None:
                    results.append(dict(case=case,passed=False,skipped='no audited semilocal start'));continue
                result,new=solve(root/case,case,arrays,settings,semi if CASES[case]['kind']=='mio' else start,env)
                results.append(result)
                if case=='fixed_coach8':semi=new
                print(case,result['status'],result['passed'],flush=True)
                c.require(not result['callback_errors'],'callback error')
        c.write(root/'publication.json',dict(artifacts={str(f.relative_to(root)):c.digest(f) for f in root.rglob('*') if f.is_file()}))
        c.write(root/'completion.json',dict(publication_sha256=c.digest(root/'publication.json'),results=results,bulk_authorized=False))
        return 0 if all(r['passed'] for r in results) else 1
    except Exception as exc:
        c.write(root/'failure.json',dict(error_type=type(exc).__name__,error_code=getattr(exc,'errno',None)));return 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--release',type=Path,required=True)
    raise SystemExit(run(parser.parse_args().release))
