"""Frozen precision diagnostics and improved-start two-hour K14 confirmation."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import shutil
import numpy as np
from revwb97m2.scripts import continuous_readback_v2 as reader

c=reader.c
ROOT=c.ROOT
PLAN=ROOT/'revwb97m2/manifests/solver_recovery_v1/plan.json'
VARIANTS={'barrier_tight':{'BarConvTol':1e-12},
          'barrier_careful':{'BarConvTol':1e-12,'NumericFocus':3},'mio_7200':{}}


def check(release):
    plan=c.read(PLAN);record=c.read(release)
    c.require(record.get('submission_authorized') is True and record.get('tests_passed') is True and
              record.get('resources_reviewed') is True and record['plan_sha256']==c.digest(PLAN), 'release disabled')
    c.require(plan['variants']==VARIANTS and plan['matrix_sha256']==c.d.full.MATRIX_SHA and
              plan['input_sha256']==c.d.full.INPUT_SHA, 'scope changed')
    report=ROOT/record['test_report']
    c.require(c.digest(report)==record['test_report_sha256'], 'tests changed')
    tested=c.read(report)
    c.require(tested['passed'] and tested['commit']==record['commit'] and
              tested['plan_sha256']==c.digest(PLAN), 'test identity')
    for name,sha in {**plan['hashes'],str(PLAN.relative_to(ROOT)):c.digest(PLAN)}.items():
        c.require(c.digest(ROOT/name)==sha, 'working file changed')
        content=subprocess.check_output(['git','show',record['commit']+':'+name],cwd=ROOT)
        c.require(hashlib.sha256(content).hexdigest()==sha, 'uncommitted execution checkpoint')
    c.require(tuple(record['route'][k] for k in ('partition','account','qos')) in c.d.full.ROUTES, 'route')
    return plan,record


def import_start(model,beta,z,start,arrays,settings):
    coeff=np.asarray(start['coefficients']);selected=np.asarray(start['selected'],dtype=float)
    residual=np.asarray(start['residuals'])
    checked=reader.fixed_start(arrays,settings,coeff,selected,residual)
    for i in range(292):
        beta[i].Start=float(coeff[i]);z[i].Start=float(selected[i])
    for i,value in enumerate(checked['residuals']):
        variable=model.getVarByName(f'weighted_residual[{i}]')
        c.require(variable is not None,'missing residual variable')
        variable.Start=value
    return checked


def solve(folder,variant,arrays,settings,start,env):
    import gurobipy as gp
    folder.mkdir();m=None
    try:
        is_mio=variant=='mio_7200'
        m,beta,z=c.d.build_model(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
            settings=settings,budget=14,seconds=7200 if is_mio else 600,threads=16,env=env)
        if is_mio:
            c.write(folder/'imported_start.json',import_start(m,beta,z,start,arrays,settings))
        else:
            c.configure(m,z,'relaxed_k14')
        for key,value in VARIANTS[variant].items():m.setParam(key,value)
        c.require((m.NumVars,m.NumConstrs,m.NumBinVars)==(2082,2088,292 if is_mio else 0), 'model dimensions')
        m.write(str(folder/'model.mps.gz'))
        keys=('TimeLimit','Threads','Seed','Method','Presolve','BarConvTol','NumericFocus',
              'FeasibilityTol','IntFeasTol','MIPGap','MIPGapAbs')
        c.write(folder/'model.json',dict(variant=variant,parameters={k:m.getParamInfo(k)[2] for k in keys},
            gurobi_version=list(gp.gurobi.version()),variables=m.NumVars,constraints=m.NumConstrs,binaries=m.NumBinVars))
        m.Params.LogToConsole=0;m.Params.LogFile='';m.Params.OutputFlag=1
        with (folder/'progress.jsonl').open('x') as stream:
            callback,errors=c.d.progress_callback(stream,gp.GRB);m.optimize(callback)
        result=dict(variant=variant,status=int(m.Status),runtime_seconds=float(m.Runtime),
            solution_count=int(m.SolCount),callback_errors=errors,passed=False,objective=None)
        if is_mio:
            result.update(bound=c.d.numeric(m.ObjBound),nodes=float(m.NodeCount))
        if m.SolCount:
            coeff=np.array([beta[i].X for i in range(292)])
            selected=np.array([z[i].X for i in range(292)])
            residual=np.array([m.getVarByName(f'weighted_residual[{i}]').X for i in range(1498)])
            for name,value in [('coefficients',coeff),('selection',selected),('residuals',residual)]:
                np.save(folder/(name+'.npy'),value)
            audit=c.audit(arrays,coeff,selected,residual,settings,'relaxed_k14')
            result.update(objective=float(m.ObjVal),audit=audit,
                max_ueg_error=float(abs(c.ueg_vector('R2')@coeff-1)),
                max_residual_error=float(np.max(np.abs(residual-np.sqrt(arrays['objective_weight'])*
                    (arrays['feature_matrix']@coeff-arrays['target'])))),
                quality={k:c.d.numeric(m.getAttr(k)) for k in ('ConstrVio','BoundVio')})
            valid=audit['passed']
            if is_mio:
                integral=bool(np.max(np.abs(selected-np.rint(selected)))<=1e-9)
                mio_audit=c.d.audit_solution(arrays['feature_matrix'],arrays['target'],arrays['objective_weight'],
                    coeff,selected>.5,model_name='R2',budget=14,settings=settings)
                result.update(integral=integral,mio_audit=mio_audit,
                    gaps=c.d.gap_report(m.ObjVal,m.ObjBound,m.MIPGap),
                    improvement=float(start['audit']['regularized_objective_hartree2']-m.ObjVal))
                valid=valid and integral and mio_audit['passed']
            result['passed']=bool(m.Status in (2,9) and not errors and valid and
                np.isclose(m.ObjVal,audit['objective'],rtol=1e-7,atol=1e-10))
        c.write(folder/'result.json',result)
        return result
    finally:
        if m is not None:m.dispose()


def run(release,mode):
    plan,record=check(release);c.d.full.check_allocation(record['route'])
    job=os.environ['SLURM_JOB_ID'];c.require(job.isdigit(),'job ID')
    root=Path(plan['output_parent'])/f'{job}_{mode}'
    c.require(not root.exists(),'preserve outputs')
    # Revalidate original artifacts, not merely the exported JSON's passed flag.
    source=Path(plan['source']);results,arrays,settings=reader.validate(source)
    c.require(results[0]['passed'],'source fixed solution failed')
    exported=c.read(ROOT/plan['start_report'])
    c.require(exported['publication_sha256']==c.digest(source/'publication.json') and
              exported['matrix_sha256']==plan['matrix_sha256'] and exported['input_sha256']==plan['input_sha256'],
              'start provenance')
    parent=root.parent
    while not parent.exists():parent=parent.parent
    c.require(shutil.disk_usage(parent).free>32*1024**3,'insufficient storage')
    root.mkdir(parents=True)
    c.write(root/'identity.json',dict(plan_sha256=c.digest(PLAN),release=str(Path(release).resolve()),
        release_sha256=c.digest(release),commit=record['commit'],mode=mode))
    try:
        import gurobipy as gp
        fields={}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            key,sep,value=line.partition('=')
            if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):fields[key.strip()]=value.strip()
        results=[]
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            for key in ('WLSACCESSID','WLSSECRET','LICENSEID'):
                env.setParam(key,int(fields[key]) if key=='LICENSEID' else fields[key])
            env.start()
            for variant in (('mio_7200',) if mode=='mio' else ('barrier_tight','barrier_careful')):
                result=solve(root/variant,variant,arrays,settings,exported['fixed_start'],env)
                results.append(result);print(variant,result['status'],result['passed'],flush=True)
                c.require(not result['callback_errors'],'callback failed')
        c.write(root/'publication.json',dict(artifacts={str(p.relative_to(root)):c.digest(p)
            for p in root.rglob('*') if p.is_file()}))
        c.write(root/'completion.json',dict(publication_sha256=c.digest(root/'publication.json'),
            all_passed=all(r['passed'] for r in results),bulk_authorized=False))
        return 0 if all(r['passed'] for r in results) else 1
    except Exception as exc:
        c.write(root/'failure.json',dict(error_type=type(exc).__name__,error_code=getattr(exc,'errno',None)))
        return 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',type=Path,required=True)
    parser.add_argument('--mode',choices=['precision','mio'],required=True)
    args=parser.parse_args()
    raise SystemExit(run(args.release,args.mode))
