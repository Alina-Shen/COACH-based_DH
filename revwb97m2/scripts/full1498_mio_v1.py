"""Approved full1498 bounded workflow; separate from frozen pilot and bulk fitting."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import numpy as np
from revwb97m2 import pilot100_inputs as adapter
from revwb97m2.fit_inputs import digest, load_inputs
from revwb97m2.fit_spec import DEFAULT_SPEC, load_fit_settings
from revwb97m2.scripts import run_pilot100_fit_v1 as fit
from revwb97m2.scripts import assemble_full1498_v1 as assembly
from revwb97m2.grid_selection import select_rows

ROOT=adapter.ROOT
PLAN=ROOT/'revwb97m2/manifests/full1498_mio_v1/plan.json'
MATRIX=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/full1498_v1')
MATRIX_SHA='493a6a465ea71539e291501645d6a186ffd86f1bd597174035d6fe7c1675eef8'
INPUT_SHA='8d9f0ddd0282598f05aa25f22b54c8b361f949453c438d396c3519e00817242e'
read,write,require=adapter.read,adapter.write,adapter.require
ROUTES=(('cm1','lr_qchem','condo_qchem'),('mhg','mhg','normal'),('lr8','lr_mhg2','mhg2_lr8_normal'))


def schedule():
    candidates=['discovery14','discovery80']
    return [dict(name=f'discovery{k}',budget=k,start=None,candidates=[]) for k in (14,80)]+[
        row for k in (14,80) for row in (
            dict(name=f'constrained{k}',budget=k,start=f'discovery{k}',candidates=candidates),
            dict(name=f'restart{k}',budget=k,start=f'constrained{k}',candidates=candidates))]


def check_plan(path=PLAN):
    plan=read(path)
    require(plan['schedule']==schedule() and plan['seconds']==600 and plan['threads']==16,
            'approved schedule changed')
    require(plan['memory_gib']==32 and plan['wall_minutes']==90, 'approved allocation changed')
    require(plan['matrix_validation_sha256']==MATRIX_SHA and plan['input_manifest_sha256']==INPUT_SHA,
            'wrong numerical matrix')
    require(plan['full_training_grid_advancement_gate'] is True, 'grid advancement gate changed')
    require(plan['specification_sha256']==digest(DEFAULT_SPEC), 'science changed')
    require(all(digest(ROOT/p)==h for p,h in plan['code_hashes'].items()), 'frozen code changed')
    return plan


def check_release(path):
    plan=check_plan();r=read(path)
    require(r.get('user_approved_submission') is True and r.get('resource_review_passed') is True and
            r.get('tests_passed') is True and r.get('plan_sha256')==digest(PLAN), 'release disabled')
    require(tuple(r['route'][k] for k in ('partition','account','qos')) in ROUTES,'unapproved route')
    evidence=ROOT/r['test_report']
    require(digest(evidence)==r['test_report_sha256'],'test evidence changed')
    tests=read(evidence)
    require(tests['passed'] is True and tests['plan_sha256']==digest(PLAN) and tests['commit']==r['commit'],
            'test evidence identity mismatch')
    sources={**plan['code_hashes'],str(PLAN.relative_to(ROOT)):digest(PLAN)}
    for source,sha in sources.items():
        data=subprocess.check_output(['git','show',r['commit']+':'+source],cwd=ROOT)
        require(hashlib.sha256(data).hexdigest()==sha,'uncommitted frozen file')
    return plan,r


def args_for(row,root,manifest):
    return SimpleNamespace(spec=DEFAULT_SPEC,manifest=manifest,output=root/row['name'],budget=row['budget'],
        seconds=600,threads=16,start=None if row['start'] is None else root/row['start'],
        grid_candidates=[root/p for p in row['candidates']],resume=False)


def matrix_manifest():
    require(digest(MATRIX/'validation.json')==MATRIX_SHA and digest(MATRIX/'inputs.json')==INPUT_SHA,
            'full matrix identity changed')
    assembly.validate(MATRIX)
    return MATRIX/'inputs.json'


def grid_report(arrays,coeff,selected_rows,settings,reaction_ids):
    selected=set(map(int,selected_rows));report={}
    for grid in ('99590','75302'):
        errors=np.abs(arrays['grid_difference_'+grid]@coeff)*settings.conversion
        bad=np.flatnonzero(errors>settings.grid_public_limit*settings.conversion)
        report[grid]=dict(max_kcal_mol=float(errors.max()),violations=[
            dict(row=int(i),reaction=reaction_ids[i],error_kcal_mol=float(errors[i]),selected=int(i) in selected)
            for i in bad])
    return report


def check_allocation(route):
    for env,key in (('SLURM_JOB_PARTITION','partition'),('SLURM_JOB_ACCOUNT','account'),('SLURM_JOB_QOS','qos')):
        require(os.environ.get(env)==route[key], 'scheduler route mismatch')
    require(os.environ.get('SLURM_CPUS_PER_TASK')=='16' and int(os.environ.get('SLURM_MEM_PER_NODE','0'))==32768,
            'scheduler allocation mismatch')


def execute_fit(args):
    # Readback must not read a license or construct a Gurobi environment.
    if args.resume:
        return fit.run(args)
    import gurobipy as gp
    fields={}
    for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
        key,sep,value=line.partition('=')
        if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):
            fields[key.strip()]=value.strip()
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag',0)
        for key in ('WLSACCESSID','WLSSECRET','LICENSEID'):
            env.setParam(key,int(fields[key]) if key=='LICENSEID' else fields[key])
        env.start()
        return fit.run(args,env)


def audit_case(row,root,manifest,arrays,settings,ids):
    args=args_for(row,root,manifest);args.resume=True
    before={p.name:digest(p) for p in args.output.iterdir() if p.is_file()}
    require(execute_fit(args)==0,'incumbent readback failed')
    require(before=={p.name:digest(p) for p in args.output.iterdir() if p.is_file()},'resume rewrote files')
    result=read(args.output/'result.json');telemetry=read(args.output/'telemetry.json')
    params=telemetry['parameters']
    require(params['Threads']==16 and params['TimeLimit']==600 and params['Seed']==settings.seed and
            all(params[k]==value for k,value in settings.solver_parameters),'solver parameters changed')
    require(telemetry['status']==result['status'] and telemetry['solution_count']==result['solution_count'],
            'telemetry mismatch')
    rows=np.array([],dtype=int)
    if row['candidates']:
        candidates=np.stack([np.load(root/p/'coefficients.npy',allow_pickle=False) for p in row['candidates']])
        rows=select_rows(arrays['grid_difference_99590'],candidates,settings.candidate_rows,settings.global_rows)
        require(np.array_equal(np.load(args.output/'grid_rows.npy'),rows),'full-data grid subset mismatch')
    grid=grid_report(arrays,np.load(args.output/'coefficients.npy'),rows,settings,ids)
    return dict(name=row['name'],result=result,telemetry=telemetry,selected_rows=rows.tolist(),grids=grid,
                advancement_passed=not row['candidates'] or not grid['99590']['violations'])


def validate(root,require_marker=True):
    root=Path(root);plan=check_plan();identity=read(root/'identity.json')
    require(identity['plan_sha256']==digest(PLAN),'pilot identity mismatch')
    require(digest(identity['release_path'])==identity['release_sha256'],'release changed')
    check_release(Path(identity['release_path']))
    control=read(root/'synthetic/integration_report.json')
    require(control['passed'] is True,'synthetic control failed')
    manifest=matrix_manifest();settings=load_fit_settings()
    arrays,input_record=load_inputs(manifest,settings)
    results=[]
    for row in schedule():
        audited=audit_case(row,root,manifest,arrays,settings,input_record['reaction_ids'])
        require(audited['advancement_passed'],'full-training grid advancement failed')
        require(read(root/(row['name']+'_audit.json'))==audited,'saved row audit changed')
        results.append(audited)
    if require_marker:
        publication=read(root/'validation.json')
        require((root/'PILOT_COMPLETE').read_text().strip()==digest(root/'validation.json'),'pilot incomplete')
        require(all(digest(root/p)==h for p,h in publication['artifacts'].items()),'pilot evidence changed')
        require(publication['results']==results,'result readback changed')
    return results


def run(release):
    plan,r=check_release(release)
    check_allocation(r['route'])
    job=os.environ['SLURM_JOB_ID'];require(job.isdigit(),'invalid job id')
    root=Path(plan['output_parent'])/job
    require(not root.exists(),'preserve existing pilot; validate or review failure, no automatic retry')
    manifest=matrix_manifest()
    import shutil
    parent=Path(plan['output_parent'])
    existing=parent
    while not existing.exists(): existing=existing.parent
    require(shutil.disk_usage(existing).free>32*1024**3,'insufficient storage headroom')
    root.mkdir(parents=True)
    write(root/'identity.json',dict(plan_sha256=digest(PLAN),release_path=str(Path(release).resolve()),
        release_sha256=digest(release),commit=r['commit'],job_id=job))
    try:
        settings=load_fit_settings();arrays,input_record=load_inputs(manifest,settings)
        control=[sys.executable,'-m','revwb97m2.scripts.test_v7_end_to_end','--output',str(root/'synthetic')]
        # Raw subprocess exception text is deliberately not copied to logs.
        require(subprocess.run(control,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0,
                'synthetic control failed')
        require(read(root/'synthetic/integration_report.json')['passed'] is True,'synthetic checks failed')
        for row in schedule():
            args=args_for(row,root,manifest)
            command=[sys.executable,'-m','revwb97m2.scripts.full1498_mio_v1','solve',
                     '--root',str(root),'--name',row['name']]
            code=subprocess.run(command,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode
            require(code==0 and read(args.output/'result.json')['passed'] is True,'solve failed; stop dependent stages')
            audited=audit_case(row,root,manifest,arrays,settings,input_record['reaction_ids'])
            write(root/(row['name']+'_audit.json'),audited)
            require(audited['advancement_passed'],'full-training grid advancement failed; inspect saved violations')
            print('PASS',row['name'],flush=True)
        results=validate(root,require_marker=False)
        artifacts={str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file()}
        write(root/'validation.json',dict(passed=True,results=results,artifacts=artifacts,
            note='Bounded feasible-incumbent workflow, not optimality or final model selection.'))
        (root/'PILOT_COMPLETE').write_text(digest(root/'validation.json')+'\n')
        print('PASS full1498 six solves and independent readback',flush=True)
    except Exception as error:
        write(root/'failure.json',dict(error_type=type(error).__name__,error_code=getattr(error,'errno',None)))
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('check','run','validate','solve'))
    p.add_argument('--release',type=Path);p.add_argument('--root',type=Path)
    p.add_argument('--name',choices=[r['name'] for r in schedule()])
    a=p.parse_args()
    if a.action=='check':check_plan();print('Frozen plan checked; no release or submission')
    elif a.action=='run':run(a.release)
    elif a.action=='solve':
        identity=read(a.root/'identity.json')
        require(identity['plan_sha256']==digest(PLAN),'solve plan changed')
        require(digest(identity['release_path'])==identity['release_sha256'],'solve release changed')
        plan,r=check_release(Path(identity['release_path']));check_allocation(r['route'])
        require(a.root.resolve()==(Path(plan['output_parent'])/os.environ['SLURM_JOB_ID']).resolve(), 'wrong solve root')
        row=next(row for row in schedule() if row['name']==a.name)
        for previous in schedule()[:schedule().index(row)]:
            require(read(a.root/(previous['name']+'_audit.json'))['advancement_passed'],'prior stage not accepted')
        raise SystemExit(execute_fit(args_for(row,a.root,matrix_manifest())))
    else:validate(a.root);print('PASS full1498 independent readback')


if __name__=='__main__':
    try: main()
    except Exception as error:
        print(type(error).__name__);raise SystemExit(1)
