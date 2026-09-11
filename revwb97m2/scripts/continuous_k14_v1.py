"""Two continuous K14 subproblems; never promotes fractional solutions to MIO."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import numpy as np
from revwb97m2.scripts import k14_diagnostic_v1 as d
from revwb97m2.mio import ueg_vector

ROOT=d.ROOT
PLAN=ROOT/'revwb97m2/manifests/continuous_k14_v1/plan.json'
KINDS=('fixed_scalars','relaxed_k14')
read,write,require,digest=d.read,d.write,d.require,d.digest


def configure(model,z,kind):
    require(kind in KINDS,'unknown subproblem')
    for i,var in z.items():
        var.VType='C'
        var.LB=1. if i>=288 else 0.
        var.UB=0. if kind=='fixed_scalars' and i<288 else 1.
    model.update()
    require(model.NumBinVars==0 and model.NumIntVars==0,'integrality not removed')


def audit(arrays,c,z,r,settings,kind):
    require(kind in KINDS,'unknown subproblem')
    require(c.shape==z.shape==(292,) and r.shape==arrays['target'].shape,'invalid diagnostic shape')
    residual=np.sqrt(arrays['objective_weight'])*(arrays['feature_matrix']@c-arrays['target'])
    checks=dict(finite=bool(all(np.isfinite(v).all() for v in (c,z,r))),
        selection_bounds=bool(np.all(z>=-1e-9) and np.all(z<=1+1e-9)),
        support_budget=bool(z.sum()<=14+1e-9),mandatory=bool(np.max(np.abs(z[288:]-1))<=1e-9),
        linkage=bool(np.max(np.abs(c)-25*z)<=1e-9),
        coefficient_bounds=bool(np.max(np.abs(c))<=25+1e-9),
        ueg=bool(abs(ueg_vector('R2')@c-1)<=1e-10),
        sr_bounds=bool(-1e-9<=c[288]<=1+1e-9),
        scalar_bounds=bool(np.all(c[289:]>=1e-8-1e-9) and np.all(c[289:]<=.99999999+1e-9)),
        residual_identity=bool(np.max(np.abs(r-residual))<=1e-9))
    if kind=='fixed_scalars':
        checks['fixed_support']=bool(np.max(np.abs(z[:288]))<=1e-9 and np.max(np.abs(c[:288]))<=1e-9)
    sse=float(residual@residual);ridge=float(settings.ridge*(c@c))
    return dict(passed=all(checks.values()),checks=checks,weighted_sse=sse,ridge=ridge,objective=sse+ridge,
                fractional_selection_count=int(np.sum(np.abs(z-np.round(z))>1e-9)),
                usable_as_mio_incumbent=False,
                note='No automatic promotion: relaxed solution may be fractional; fixed support needs separate MIO-start audit/import.')


def check_plan():
    plan=read(PLAN)
    require(plan['kinds']==list(KINDS) and (plan['seconds_each'],plan['threads'],plan['memory_gib'],plan['wall_minutes'])==
            (600,16,32,90),'continuous diagnostic scope changed')
    require(all(digest(ROOT/p)==h for p,h in plan['code_hashes'].items()),'frozen diagnostic code changed')
    require(plan['matrix_sha256']==d.full.MATRIX_SHA and plan['input_sha256']==d.full.INPUT_SHA,'matrix changed')
    return plan


def check_release(path):
    plan=check_plan();r=read(path)
    require(r.get('user_approved_submission') is True and r.get('tests_passed') is True and
            r.get('resource_review_passed') is True and r.get('plan_sha256')==digest(PLAN),'release disabled')
    require(tuple(r['route'][k] for k in ('partition','account','qos')) in d.full.ROUTES,'unapproved route')
    require(digest(ROOT/r['test_report'])==r['test_report_sha256'],'test report changed')
    tests=read(ROOT/r['test_report'])
    require(tests['passed'] and tests['commit']==r['commit'] and tests['plan_sha256']==digest(PLAN),'test identity')
    for path,sha in {**plan['code_hashes'],str(PLAN.relative_to(ROOT)):digest(PLAN)}.items():
        content=subprocess.check_output(['git','show',r['commit']+':'+path],cwd=ROOT)
        require(hashlib.sha256(content).hexdigest()==sha,'uncommitted diagnostic')
    return plan,r


def solve(root,kind,arrays,settings,env):
    import gurobipy as gp
    require(not root.exists(),'preserve existing subproblem');root.mkdir()
    m=None
    try:
        m,beta,z=d.build_model(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                              settings=settings,budget=14,seconds=600,threads=16,env=env)
        configure(m,z,kind)
        require((m.NumVars,m.NumConstrs)==(2082,2088),'unexpected model dimensions')
        m.write(str(root/'model.mps.gz'))
        write(root/'model.json',dict(kind=kind,variables=m.NumVars,binaries=m.NumBinVars,integers=m.NumIntVars,
              constraints=m.NumConstrs,gurobi_version=list(gp.gurobi.version()),
              parameters={key:m.getParamInfo(key)[2] for key in
                ('Threads','TimeLimit','Seed','Method','Presolve','FeasibilityTol','IntFeasTol','MIPGap','MIPGapAbs')}))
        m.Params.LogToConsole=0;m.Params.LogFile='';m.Params.OutputFlag=1
        with (root/'progress.jsonl').open('x') as stream:
            callback,errors=d.progress_callback(stream,gp.GRB);m.optimize(callback)
        result=dict(kind=kind,status=int(m.Status),solution_count=int(m.SolCount),runtime_seconds=float(m.Runtime),
                    iterations=d.numeric(m.IterCount),barrier_iterations=int(m.BarIterCount),callback_errors=errors,
                    passed=False,optimal_status=bool(m.Status==2),objective=None,audit=None,
                    bound_note='No MIP bound/gap for continuous diagnostics. Nonoptimal feasible QP objective is not a certified lower bound.')
        if m.SolCount:
            c=np.array([beta[i].X for i in range(292)]);s=np.array([z[i].X for i in range(292)])
            r=np.array([m.getVarByName(f'weighted_residual[{i}]').X for i in range(1498)])
            for key,value in [('coefficients',c),('selection_relaxed',s),('residuals',r)]:np.save(root/(key+'.npy'),value)
            checked=audit(arrays,c,s,r,settings,kind)
            result.update(objective=float(m.ObjVal),audit=checked,
                passed=bool(not errors and m.Status in (2,9) and checked['passed'] and
                            np.isclose(m.ObjVal,checked['objective'],rtol=1e-7,atol=1e-10)))
        write(root/'result.json',result)
        return result
    finally:
        if m is not None:m.dispose()


def validate(root):
    identity=read(root/'identity.json')
    require(identity['plan_sha256']==digest(PLAN) and digest(identity['release_path'])==identity['release_sha256'],'identity changed')
    check_release(identity['release_path'])
    require((root/'CONTINUOUS_DIAGNOSTIC_COMPLETE').read_text().strip()==digest(root/'publication.json'),'incomplete diagnostics')
    pub=read(root/'publication.json')
    require(all(digest(root/p)==h for p,h in pub['artifacts'].items()),'diagnostic artifact changed')
    manifest=d.full.matrix_manifest();settings=d.full.load_fit_settings();arrays,_=d.full.load_inputs(manifest,settings)
    results=[]
    for kind in KINDS:
        folder=root/kind;result=read(folder/'result.json');model=read(folder/'model.json')
        require(model['kind']==result['kind']==kind and (model['variables'],model['constraints'],model['binaries'],model['integers'])==
                (2082,2088,0,0),'wrong model')
        params=model['parameters']
        require(params['Threads']==16 and params['TimeLimit']==600 and params['Seed']==settings.seed and
                all(params[k]==v for k,v in settings.solver_parameters),'parameter mismatch')
        require(result['optimal_status']==(result['status']==2),'incorrect optimal flag')
        if result['solution_count']:
            values=[np.load(folder/(key+'.npy'),allow_pickle=False) for key in ('coefficients','selection_relaxed','residuals')]
            checked=audit(arrays,*values,settings,kind)
            require(checked==result['audit'],'solution audit changed')
            expected=bool(not result['callback_errors'] and result['status'] in (2,9) and checked['passed'] and
                          np.isclose(result['objective'],checked['objective'],rtol=1e-7,atol=1e-10))
            require(result['passed']==expected,'wrong acceptance')
        else:require(not result['passed'] and result['objective'] is None,'fabricated solution')
        results.append(result)
    return results


def run(release):
    plan,record=check_release(release);d.full.check_allocation(record['route'])
    job=os.environ['SLURM_JOB_ID'];require(job.isdigit(),'invalid job')
    root=Path(plan['output_parent'])/job;require(not root.exists(),'preserve existing diagnostic')
    manifest=d.full.matrix_manifest();settings=d.full.load_fit_settings();arrays,_=d.full.load_inputs(manifest,settings)
    import shutil
    parent=Path(plan['output_parent'])
    while not parent.exists():parent=parent.parent
    require(shutil.disk_usage(parent).free>32*1024**3,'insufficient storage')
    root.mkdir(parents=True)
    write(root/'identity.json',dict(plan_sha256=digest(PLAN),release_path=str(Path(release).resolve()),
          release_sha256=digest(release),commit=record['commit']))
    try:
        import gurobipy as gp
        fields={}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            key,sep,value=line.partition('=')
            if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):fields[key.strip()]=value.strip()
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            for key in ('WLSACCESSID','WLSSECRET','LICENSEID'):
                env.setParam(key,int(fields[key]) if key=='LICENSEID' else fields[key])
            env.start()
            for kind in KINDS:
                result=solve(root/kind,kind,arrays,settings,env)
                print(kind,'status',result['status'],'audit_passed',result['passed'],flush=True)
                require(not result['callback_errors'],'callback failed; stop diagnostic')
                # These subproblems are independent; a timeout/no solution in
                # the first is useful evidence and does not suppress the second.
        write(root/'publication.json',dict(artifacts={str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file()}))
        (root/'CONTINUOUS_DIAGNOSTIC_COMPLETE').write_text(digest(root/'publication.json')+'\n')
        return 0 if all(r['passed'] for r in validate(root)) else 1
    except Exception as exc:
        write(root/'failure.json',dict(error_type=type(exc).__name__,error_code=getattr(exc,'errno',None)))
        return 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['check','run','validate'])
    parser.add_argument('--release',type=Path);parser.add_argument('--root',type=Path)
    args=parser.parse_args()
    try:
        if args.action=='check':check_plan();print('Frozen continuous diagnostic plan; no launch')
        elif args.action=='run':raise SystemExit(run(args.release))
        else:print([(r['kind'],r['passed']) for r in validate(args.root)])
    except Exception as exc:
        print(type(exc).__name__);raise SystemExit(1)
