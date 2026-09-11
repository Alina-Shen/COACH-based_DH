"""Single full-data K14 feasibility-start diagnostic; no cold/bulk retry loop."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time
import numpy as np
from revwb97m2.scripts import full1498_mio_v1 as full
from revwb97m2.mio import build_model, audit_solution
from revwb97m2.solver_reporting import gap_report, number_state

ROOT=full.ROOT
PLAN=ROOT/'revwb97m2/manifests/k14_diagnostic_v1/plan.json'
read,write,require,digest=full.read,full.write,full.require,full.digest


def numeric(value):
    value=float(value)
    # Gurobi also uses finite +/-1e100 sentinels for unavailable bounds.
    state=number_state(value)
    if state=='finite' and abs(value)>=1e100:state='solver_infinity_sentinel'
    return dict(value=value if state=='finite' else None,state=state,
                raw_sentinel=value if state=='solver_infinity_sentinel' else None)


def feasible_start(arrays,settings):
    coeff=np.zeros(292);coeff[288]=1.;coeff[289:]=1e-8
    selected=np.zeros(292,dtype=bool);selected[288:]=True
    audit=audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                         coeff,selected,model_name='R2',budget=14,settings=settings)
    residual=np.sqrt(arrays['objective_weight'])*(arrays['feature_matrix']@coeff-arrays['target'])
    require(audit['passed'] and np.isfinite(residual).all(),'invalid analytic start')
    return coeff,selected,residual,audit


def check_plan():
    plan=read(PLAN)
    require((plan['budget'],plan['seconds'],plan['threads'],plan['memory_gib'],plan['wall_minutes'])==
            (14,600,16,32,90),'diagnostic scope changed')
    require(plan['grid_candidates']==[] and plan['start_policy']=='analytic_four_scalar_full_primal',
            'diagnostic start/grid changed')
    require(plan['matrix_sha256']==full.MATRIX_SHA and plan['input_sha256']==full.INPUT_SHA,'wrong full matrix')
    require(all(digest(ROOT/p)==h for p,h in plan['code_hashes'].items()),'diagnostic code changed')
    return plan


def check_release(path):
    plan=check_plan();r=read(path)
    require(r.get('user_approved_submission') is True and r.get('tests_passed') is True and
            r.get('resource_review_passed') is True and r.get('plan_sha256')==digest(PLAN),'disabled release')
    require(tuple(r['route'][k] for k in ('partition','account','qos')) in full.ROUTES,'unapproved route')
    require(digest(ROOT/r['test_report'])==r['test_report_sha256'],'test report changed')
    tests=read(ROOT/r['test_report'])
    require(tests['passed'] and tests['commit']==r['commit'] and tests['plan_sha256']==digest(PLAN),'test identity')
    for path,sha in {**plan['code_hashes'],str(PLAN.relative_to(ROOT)):digest(PLAN)}.items():
        content=subprocess.check_output(['git','show',r['commit']+':'+path],cwd=ROOT)
        require(hashlib.sha256(content).hexdigest()==sha,'uncommitted diagnostic')
    return plan,r


def progress_callback(stream,GRB):
    last={};errors=[]
    def callback(model,where):
        try:
            C=GRB.Callback
            if where==C.MESSAGE:
                message=model.cbGet(C.MSG_STRING).strip()
                # Only start-acceptance diagnostics, never general/license output.
                if message.startswith(('User MIP start','Loaded user MIP start')):
                    stream.write(json.dumps(dict(event='start_message',message=message))+'\n');stream.flush()
                return
            phases={C.PRESOLVE:('presolve',('PRE_COLDEL','PRE_ROWDEL')),
                    C.SIMPLEX:('simplex',('SPX_ITRCNT','SPX_OBJVAL','SPX_PRIMINF','SPX_DUALINF')),
                    C.BARRIER:('barrier',('BARRIER_ITRCNT','BARRIER_PRIMOBJ','BARRIER_DUALOBJ')),
                    C.MIP:('mip',('MIP_OBJBST','MIP_OBJBND','MIP_NODCNT','MIP_SOLCNT','MIP_ITRCNT')),
                    C.MIPSOL:('solution_event',('MIPSOL_OBJ','MIPSOL_OBJBND','MIPSOL_NODCNT'))}
            if where not in phases:return
            phase,fields=phases[where];now=float(model.cbGet(C.RUNTIME))
            if phase!='solution_event' and now-last.get(phase,-100)<5:return
            last[phase]=now
            event=dict(event=phase,seconds=now,values={key:numeric(model.cbGet(getattr(C,key))) for key in fields})
            stream.write(json.dumps(event,allow_nan=False)+'\n');stream.flush()
        except Exception as exc:
            errors.append(type(exc).__name__);model.terminate()
    return callback,errors


def solve(root,arrays,settings,env):
    import gurobipy as gp
    root=Path(root);require(not root.exists(),'preserve diagnostic output');root.mkdir(parents=True)
    coeff,selected,residual,start_audit=feasible_start(arrays,settings)
    for name,value in [('start_coefficients',coeff),('start_selected',selected),('start_residuals',residual)]:
        np.save(root/(name+'.npy'),value)
    write(root/'start.json',dict(passed=True,audit=start_audit,
          role='analytic_feasible_start_not_solver_incumbent',matrix_sha256=full.MATRIX_SHA,input_sha256=full.INPUT_SHA))
    model=None;began=time.monotonic()
    try:
        model,beta,z=build_model(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                               budget=14,settings=settings,seconds=600,threads=16,env=env)
        for i in beta:beta[i].Start=float(coeff[i]);z[i].Start=float(selected[i])
        for i,value in enumerate(residual):
            variable=model.getVarByName(f'weighted_residual[{i}]')
            require(variable is not None,'residual variable missing');variable.Start=float(value)
        parameters={key:model.getParamInfo(key)[2] for key in
                    ('Threads','TimeLimit','Seed','FeasibilityTol','IntFeasTol','MIPGap','MIPGapAbs')}
        write(root/'model.json',dict(variables=model.NumVars,binaries=model.NumBinVars,
              constraints=model.NumConstrs,quadratic_objective_terms=model.NumQNZs,
              build_and_start_seconds=time.monotonic()-began,parameters=parameters,
              gurobi_version=list(gp.gurobi.version())))
        # Environment started quietly before logging is enabled; console/file logs
        # remain disabled. Callback persists numerical progress and start messages.
        model.Params.LogToConsole=0;model.Params.LogFile='';model.Params.OutputFlag=1
        with (root/'progress.jsonl').open('x') as stream:
            callback,errors=progress_callback(stream,gp.GRB);model.optimize(callback)
        result=dict(passed=False,status=int(model.Status),solution_count=int(model.SolCount),
                    runtime_seconds=float(model.Runtime),nodes=float(model.NodeCount),
                    bound=numeric(model.ObjBound),callback_errors=errors,
                    start_supplied=True,start_is_not_automatically_an_incumbent=True)
        if model.SolCount:
            c=np.array([beta[i].X for i in range(292)]);s=np.array([z[i].X>.5 for i in range(292)])
            audit=audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                                 c,s,model_name='R2',budget=14,settings=settings)
            result.update(objective=float(model.ObjVal),audit=audit,
                gaps=gap_report(model.ObjVal,model.ObjBound,model.MIPGap),
                grid_max_kcal_mol={g:float(np.max(np.abs(arrays['grid_difference_'+g]@c))*settings.conversion)
                                  for g in ('99590','75302')})
            np.save(root/'coefficients.npy',c);np.save(root/'selected.npy',s)
            result['passed']=bool(model.Status in (2,9) and not errors and audit['passed'] and
                np.isclose(model.ObjVal,audit['regularized_objective_hartree2'],rtol=1e-7,atol=1e-10))
        else:result.update(objective=None,gaps=None)
        write(root/'result.json',result)
        return result
    finally:
        if model is not None:model.dispose()


def validate(root):
    root=Path(root);identity=read(root/'identity.json')
    require(identity['plan_sha256']==digest(PLAN) and digest(identity['release_path'])==identity['release_sha256'],
            'diagnostic identity changed')
    check_release(identity['release_path'])
    publication=read(root/'publication.json')
    require((root/'DIAGNOSTIC_COMPLETE').read_text().strip()==digest(root/'publication.json'),'diagnostic incomplete')
    require(all(digest(root/p)==h for p,h in publication['artifacts'].items()),'diagnostic artifact changed')
    manifest=full.matrix_manifest();settings=full.load_fit_settings();arrays,_=full.load_inputs(manifest,settings)
    c,s,r,audit=feasible_start(arrays,settings);work=root/'solve'
    for name,value in [('start_coefficients',c),('start_selected',s),('start_residuals',r)]:
        np.testing.assert_array_equal(np.load(work/(name+'.npy'),allow_pickle=False),value)
    require(read(work/'start.json')['audit']==audit,'start audit changed')
    model=read(work/'model.json');params=model['parameters']
    require((model['variables'],model['binaries'],model['constraints'])==(2082,292,2088),'model dimensions changed')
    require(params['Threads']==16 and params['TimeLimit']==600 and params['Seed']==settings.seed and
            all(params[k]==v for k,v in settings.solver_parameters),'solver parameters changed')
    result=read(work/'result.json')
    if result['solution_count']:
        c=np.load(work/'coefficients.npy');s=np.load(work/'selected.npy')
        fresh=audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],c,s,
                             model_name='R2',budget=14,settings=settings)
        require(fresh==result['audit'],'incumbent audit changed')
        require(not result['passed'] or (fresh['passed'] and result['status'] in (2,9) and
                not result['callback_errors'] and np.isclose(result['objective'],fresh['regularized_objective_hartree2'],
                rtol=1e-7,atol=1e-10)),'invalid acceptance')
        from revwb97m2.solver_reporting import raw_gap_from_record
        bound=result['bound']['value']
        if bound is None:
            bound=result['bound'].get('raw_sentinel')
            if bound is None:
                bound={'negative_infinity':-math.inf,'positive_infinity':math.inf,'nan':math.nan}[result['bound']['state']]
        require(gap_report(result['objective'],bound,raw_gap_from_record(result['gaps']))==result['gaps'],
                'gap readback changed')
        for grid in ('99590','75302'):
            maximum=float(np.max(np.abs(arrays['grid_difference_'+grid]@c))*settings.conversion)
            require(np.isclose(maximum,result['grid_max_kcal_mol'][grid],rtol=1e-12,atol=1e-12),'grid readback changed')
    else:require(not result['passed'] and result['objective'] is None and result['gaps'] is None,'fabricated incumbent')
    return result


def run(release):
    plan,record=check_release(release);full.check_allocation(record['route'])
    job=os.environ['SLURM_JOB_ID'];require(job.isdigit(),'invalid job')
    root=Path(plan['output_parent'])/job;require(not root.exists(),'preserve previous diagnostic')
    manifest=full.matrix_manifest();settings=full.load_fit_settings();arrays,_=full.load_inputs(manifest,settings)
    import shutil
    parent=Path(plan['output_parent'])
    while not parent.exists():parent=parent.parent
    require(shutil.disk_usage(parent).free>32*1024**3,'insufficient storage headroom')
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
            for key,value in fields.items():env.setParam(key,int(value) if key=='LICENSEID' else value)
            env.start();result=solve(root/'solve',arrays,settings,env)
        write(root/'publication.json',dict(artifacts={str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file()}))
        (root/'DIAGNOSTIC_COMPLETE').write_text(digest(root/'publication.json')+'\n')
        validate(root)
        print('Diagnostic complete; independently accepted incumbent:',result['passed'])
        return 0 if result['passed'] else 1
    except Exception as exc:
        write(root/'failure.json',dict(error_type=type(exc).__name__,error_code=getattr(exc,'errno',None)))
        return 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['check','run','validate'])
    parser.add_argument('--release',type=Path);parser.add_argument('--root',type=Path)
    args=parser.parse_args()
    try:
        if args.action=='check':check_plan();print('Frozen diagnostic check PASS; not release')
        elif args.action=='run':raise SystemExit(run(args.release))
        else:print('Readback:',validate(args.root)['passed'])
    except Exception as exc:
        print(type(exc).__name__);raise SystemExit(1)
