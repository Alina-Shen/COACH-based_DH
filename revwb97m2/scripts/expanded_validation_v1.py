"""Six full-data expanded/big-M solves with immutable starts and grid readback."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np
from revwb97m2 import expanded_adapter as a
from revwb97m2.grid_selection import select_rows

c=a.c;ROOT=c.ROOT
PLAN=ROOT/'revwb97m2/manifests/expanded_validation_v1/plan.json'


def schedule():
    rows=c.d.full.schedule()
    for row in rows:
        if row['name'].startswith('discovery'):row['start']='source'
    return rows


def check(release):
    p=c.read(PLAN);r=c.read(release);a.settings()
    c.require(r.get('submission_authorized') is True and r.get('tests_passed') is True and
              r.get('resources_reviewed') is True and r['plan_sha256']==c.digest(PLAN),'release disabled')
    c.require(p['schedule']==schedule() and p['config_sha256']==c.digest(a.CONFIG) and
              p['matrix_sha256']==c.d.full.MATRIX_SHA and p['input_sha256']==c.d.full.INPUT_SHA,'scope changed')
    test=ROOT/r['test_report'];t=c.read(test)
    c.require(c.digest(test)==r['test_report_sha256'] and t['passed'] and t['commit']==r['commit'] and t['plan_sha256']==c.digest(PLAN),'tests')
    for name,sha in {**p['hashes'],str(PLAN.relative_to(ROOT)):c.digest(PLAN)}.items():
        raw=subprocess.check_output(['git','show',r['commit']+':'+name],cwd=ROOT)
        c.require(c.digest(ROOT/name)==sha and hashlib.sha256(raw).hexdigest()==sha,'uncommitted/changed')
    c.require(tuple(r['route'][k] for k in ('partition','account','qos')) in c.d.full.ROUTES,'route')
    return p,r


def source(p,arrays,settings):
    root=Path(p['source_root']);completion=c.read(root/'completion.json');pub=c.read(root/'publication.json')
    c.require(c.digest(root/'publication.json')==p['source_publication_sha256']==completion['publication_sha256'],'source publication')
    c.require(all(c.digest(root/n)==sha for n,sha in pub['artifacts'].items()),'source artifact changed')
    identity=c.read(root/'identity.json')
    c.require(c.digest(identity['release'])==identity['release_sha256'],'source release changed')
    a.e.check(Path(identity['release']))
    folder=root/'expanded_mio';result=c.read(folder/'result.json')
    b=np.load(folder/'coefficients.npy');z=np.load(folder/'selection.npy')
    checked=a.audit(arrays,b,z,14,np.array([],dtype=int),settings)
    c.require(result['passed'] and checked['passed'] and checked['semilocal_nonzero_count']>0,'source candidate')
    c.require(np.isclose(result['objective'],checked['independent']['regularized_objective_hartree2'],rtol=1e-7,atol=1e-10),'source objective')
    return b,z


def inputs(row,root,arrays,settings):
    b=np.load(root/row['start']/'coefficients.npy');z=np.load(root/row['start']/'selection.npy')
    rows=np.array([],dtype=int)
    if row['candidates']:
        candidates=np.stack([np.load(root/n/'coefficients.npy') for n in row['candidates']])
        rows=select_rows(arrays['grid_difference_99590'],candidates,settings.candidate_rows,settings.global_rows)
    return b,z,rows


def solve(row,root,arrays,settings,env):
    import gurobipy as gp
    folder=root/row['name'];folder.mkdir();b,z,rows=inputs(row,root,arrays,settings)
    c.write(folder/'start_audit.json',a.start_audit(arrays,b,z,row['budget'],rows,settings))
    for key,v in [('start_coefficients',b),('start_selection',z),('grid_rows',rows)]:np.save(folder/(key+'.npy'),v)
    m=None
    try:
        m,beta,selected=a.build(arrays,settings,row['budget'],rows,env)
        for i in range(292):beta[i].Start=float(b[i]);selected[i].Start=float(z[i])
        m.write(str(folder/'model.mps.gz'))
        keys=('Method','NodeMethod','Presolve','BarConvTol','NumericFocus','Threads','TimeLimit','Seed','FeasibilityTol','IntFeasTol','MIPGap','MIPGapAbs')
        c.write(folder/'model.json',dict(variables=m.NumVars,constraints=m.NumConstrs,binaries=m.NumBinVars,sos=m.NumSOS,
            parameters={k:m.getParamInfo(k)[2] for k in keys},version=list(gp.gurobi.version())))
        m.Params.LogToConsole=0;m.Params.LogFile='';m.Params.OutputFlag=1
        with (folder/'progress.jsonl').open('x') as stream:
            callback,errors=c.d.progress_callback(stream,gp.GRB);m.optimize(callback)
        result=dict(name=row['name'],budget=row['budget'],status=int(m.Status),runtime=float(m.Runtime),
            solution_count=int(m.SolCount),nodes=float(m.NodeCount),callback_errors=errors,passed=False,objective=None,bound=c.d.numeric(m.ObjBound))
        if m.SolCount:
            b=np.array([beta[i].X for i in range(292)]);z=np.array([selected[i].X for i in range(292)])
            np.save(folder/'coefficients.npy',b);np.save(folder/'selection.npy',z)
            checked=a.audit(arrays,b,z,row['budget'],rows,settings)
            result.update(objective=float(m.ObjVal),audit=checked,gaps=c.d.gap_report(m.ObjVal,m.ObjBound,m.MIPGap))
            result['passed']=bool(m.Status in (2,9) and not errors and checked['passed'] and
                np.isclose(m.ObjVal,checked['independent']['regularized_objective_hartree2'],rtol=1e-7,atol=1e-10))
        c.write(folder/'result.json',result)
        return result
    finally:
        if m is not None:m.dispose()


def audit_case(row,root,arrays,settings):
    folder=root/row['name'];r=c.read(folder/'result.json');model=c.read(folder/'model.json')
    b,z,rows=inputs(row,root,arrays,settings)
    c.require(np.array_equal(rows,np.load(folder/'grid_rows.npy')) and np.array_equal(b,np.load(folder/'start_coefficients.npy')) and
              np.array_equal(z,np.load(folder/'start_selection.npy')),'start/grid identity')
    c.require(c.read(folder/'start_audit.json')['grid_feasible']==a.start_audit(arrays,b,z,row['budget'],rows,settings)['grid_feasible'],'start feasibility identity')
    c.require((model['variables'],model['constraints'],model['binaries'],model['sos'])==(584,590+2*len(rows),292,0),'model shape')
    params=model['parameters'];c.require(params['Threads']==16 and params['TimeLimit']==600 and params['Seed']==settings.seed and
        all(params[k]==v for k,v in settings.solver_parameters),'parameters')
    c.require(r['passed'] and r['solution_count']>0 and r['status'] in (2,9) and not r['callback_errors'],'solve rejected')
    b=np.load(folder/'coefficients.npy');z=np.load(folder/'selection.npy')
    actual=a.audit(arrays,b,z,row['budget'],rows,settings)
    c.require(actual['passed'] and actual['independent']['checks']==r['audit']['independent']['checks'],'candidate checks')
    c.require(np.isclose(r['objective'],actual['independent']['regularized_objective_hartree2'],rtol=1e-7,atol=1e-10),'objective')
    gaps=c.d.gap_report(r['objective'],r['bound']['value'],r['gaps']['gap']);c.require(gaps['gap_consistent'],'gap')
    return dict(name=row['name'],passed=True,advancement_passed=bool(not row['candidates'] or actual['full_grid_passed']),
        audit=actual,selected_rows=rows.tolist(),gaps=gaps)


def validate(root):
    identity=c.read(root/'identity.json');p,r=check(Path(identity['release']))
    c.require(identity['plan_sha256']==c.digest(PLAN) and identity['release_sha256']==c.digest(identity['release']) and identity['commit']==r['commit'],'identity')
    done=c.read(root/'completion.json');pub=c.read(root/'publication.json')
    c.require(done['publication_sha256']==c.digest(root/'publication.json') and all(c.digest(root/n)==h for n,h in pub['artifacts'].items()),'artifact hashes')
    settings=a.settings();arrays,_=c.d.full.load_inputs(c.d.full.matrix_manifest(),settings)
    b,z=source(p,arrays,settings)
    c.require(np.array_equal(b,np.load(root/'source/coefficients.npy')) and np.array_equal(z,np.load(root/'source/selection.npy')),'source import')
    results=[audit_case(row,root,arrays,settings) for row in schedule()]
    c.require(all(x['advancement_passed'] for x in results),'full-grid advancement')
    return results


def run(release):
    p,record=check(release);c.d.full.check_allocation(record['route'])
    job=os.environ['SLURM_JOB_ID'];c.require(job.isdigit(),'job')
    root=Path(p['output_parent'])/job;c.require(not root.exists(),'preserve run')
    settings=a.settings();arrays,_=c.d.full.load_inputs(c.d.full.matrix_manifest(),settings)
    b,z=source(p,arrays,settings);parent=root.parent
    while not parent.exists():parent=parent.parent
    c.require(shutil.disk_usage(parent).free>32*1024**3,'storage');(root/'source').mkdir(parents=True)
    np.save(root/'source/coefficients.npy',b);np.save(root/'source/selection.npy',z)
    c.write(root/'identity.json',dict(plan_sha256=c.digest(PLAN),release=str(Path(release).resolve()),release_sha256=c.digest(release),commit=record['commit']))
    try:
        import gurobipy as gp
        fields={}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            k,sep,v=line.partition('=')
            if sep and k.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):fields[k.strip()]=v.strip()
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            for k in ('WLSACCESSID','WLSSECRET','LICENSEID'):env.setParam(k,int(fields[k]) if k=='LICENSEID' else fields[k])
            env.start()
            for row in schedule():
                r=solve(row,root,arrays,settings,env);c.require(r['passed'],'solve rejected')
                checked=audit_case(row,root,arrays,settings);c.write(root/(row['name']+'_audit.json'),checked)
                c.require(checked['advancement_passed'],'full99590 grid gate failed; review unselected rows')
                print('PASS',row['name'],flush=True)
        c.write(root/'publication.json',dict(artifacts={str(f.relative_to(root)):c.digest(f) for f in root.rglob('*') if f.is_file()}))
        c.write(root/'completion.json',dict(publication_sha256=c.digest(root/'publication.json'),bulk_authorized=False))
        validate(root);print('PASS six-stage independent readback',flush=True);return 0
    except Exception as exc:
        c.write(root/'failure.json',dict(error_type=type(exc).__name__,error_code=getattr(exc,'errno',None)));return 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['run','validate'])
    p.add_argument('--release',type=Path);p.add_argument('--root',type=Path);args=p.parse_args()
    if args.action=='run':raise SystemExit(run(args.release))
    else:validate(args.root);print('PASS independent readback')
