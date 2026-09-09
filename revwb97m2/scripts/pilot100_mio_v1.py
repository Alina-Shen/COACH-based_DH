"""Gated, serial six-solve pilot; no automatic retries or bulk authorization."""
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

ROOT=adapter.ROOT
PLAN=ROOT/'revwb97m2/manifests/pilot100_mio_v1/plan.json'
read,write,require=adapter.read,adapter.write,adapter.require
ROUTES=(('cm1','lr_qchem','condo_qchem'),('mhg','mhg','normal'),('lr8','lr_mhg2','mhg2_lr8_normal'))


def schedule():
    candidates=['discovery14','discovery40']
    return [dict(name=f'discovery{k}',budget=k,start=None,candidates=[]) for k in (14,40)]+[
        row for k in (14,40) for row in (
            dict(name=f'constrained{k}',budget=k,start=f'discovery{k}',candidates=candidates),
            dict(name=f'restart{k}',budget=k,start=f'constrained{k}',candidates=candidates))]


def check_plan(path=PLAN):
    plan=read(path)
    require(plan['schedule']==schedule() and plan['seconds']==300 and plan['threads']==16,
            'approved schedule changed')
    require(plan['memory_gib']==16 and plan['wall_minutes']==45, 'approved allocation changed')
    require(plan['matrix_validation_sha256']==adapter.VALIDATION_SHA, 'wrong numerical matrix')
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
        seconds=300,threads=16,start=None if row['start'] is None else root/row['start'],
        grid_candidates=[root/p for p in row['candidates']],resume=False)


def fit_command(args):
    command=[sys.executable,'-m','revwb97m2.scripts.run_pilot100_fit_v1',
        '--manifest',str(args.manifest),'--output',str(args.output),'--budget',str(args.budget),
        '--seconds','300','--threads','16']
    if args.start is not None: command+=['--start',str(args.start)]
    if args.grid_candidates: command+=['--grid-candidates',*[str(p) for p in args.grid_candidates]]
    return command


def validate(root,require_marker=True):
    root=Path(root);plan=check_plan();identity=read(root/'identity.json')
    require(identity['plan_sha256']==digest(PLAN),'pilot identity mismatch')
    require(digest(identity['release_path'])==identity['release_sha256'],'release changed')
    check_release(Path(identity['release_path']))
    control=read(root/'synthetic/integration_report.json')
    require(control['passed'] is True,'synthetic control failed')
    manifest=adapter.validate(root/'adapter');settings=load_fit_settings()
    arrays,_=load_inputs(manifest,settings)
    results=[]
    for row in schedule():
        args=args_for(row,root,manifest);out=args.output
        before={p.name:digest(p) for p in out.iterdir() if p.is_file()}
        args.resume=True
        # Direct resume never constructs a Gurobi environment or calls optimize.
        require(fit.run(args)==0,'readback failed')
        require(before=={p.name:digest(p) for p in out.iterdir() if p.is_file()},'resume rewrote files')
        result=read(out/'result.json');telemetry=read(out/'telemetry.json')
        params=telemetry['parameters']
        require(params['Threads']==16 and params['TimeLimit']==300 and params['Seed']==settings.seed and
                all(params[k]==value for k,value in settings.solver_parameters),'solver parameters changed')
        require(telemetry['status']==result['status'] and telemetry['solution_count']==result['solution_count'],
                'telemetry mismatch')
        if row['candidates']:
            require(np.array_equal(np.load(out/'grid_rows.npy'),np.arange(100)),'not all pilot rows selected')
            require(result['grid_max_kcal_mol']['99590']<=.015,'public grid limit failed')
        results.append(dict(name=row['name'],result=result,telemetry=telemetry))
    if require_marker:
        publication=read(root/'validation.json')
        require((root/'PILOT_COMPLETE').read_text().strip()==digest(root/'validation.json'),'pilot incomplete')
        require(all(digest(root/p)==h for p,h in publication['artifacts'].items()),'pilot evidence changed')
        require(publication['results']==results,'result readback changed')
    return results


def run(release):
    plan,r=check_release(release)
    for env,key in (('SLURM_JOB_PARTITION','partition'),('SLURM_JOB_ACCOUNT','account'),('SLURM_JOB_QOS','qos')):
        require(os.environ.get(env)==r['route'][key], 'scheduler route mismatch')
    require(os.environ.get('SLURM_CPUS_PER_TASK')=='16' and int(os.environ.get('SLURM_MEM_PER_NODE','0'))==16384,
            'scheduler allocation mismatch')
    job=os.environ['SLURM_JOB_ID'];require(job.isdigit(),'invalid job id')
    root=Path(plan['output_parent'])/job
    require(not root.exists(),'preserve existing pilot; validate or review failure, no automatic retry')
    adapter.check_matrix()
    import shutil
    parent=Path(plan['output_parent'])
    existing=parent
    while not existing.exists(): existing=existing.parent
    require(shutil.disk_usage(existing).free>16*1024**3,'insufficient storage headroom')
    root.mkdir(parents=True)
    write(root/'identity.json',dict(plan_sha256=digest(PLAN),release_path=str(Path(release).resolve()),
        release_sha256=digest(release),commit=r['commit'],job_id=job))
    try:
        manifest=adapter.publish(root/'adapter')
        control=[sys.executable,'-m','revwb97m2.scripts.test_v7_end_to_end','--output',str(root/'synthetic')]
        # Raw subprocess exception text is deliberately not copied to logs.
        require(subprocess.run(control,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0,
                'synthetic control failed')
        require(read(root/'synthetic/integration_report.json')['passed'] is True,'synthetic checks failed')
        for row in schedule():
            args=args_for(row,root,manifest)
            code=subprocess.run(fit_command(args),cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode
            require(code==0 and read(args.output/'result.json')['passed'] is True,'solve failed; stop dependent stages')
            print('PASS',row['name'],flush=True)
        results=validate(root,require_marker=False)
        artifacts={str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file()}
        write(root/'validation.json',dict(passed=True,results=results,artifacts=artifacts,
            note='Bounded feasible-incumbent workflow, not optimality or final model selection.'))
        (root/'PILOT_COMPLETE').write_text(digest(root/'validation.json')+'\n')
        print('PASS pilot100 six solves and independent readback',flush=True)
    except Exception as error:
        write(root/'failure.json',dict(error_type=type(error).__name__,error_code=getattr(error,'errno',None)))
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('check','run','validate'))
    p.add_argument('--release',type=Path);p.add_argument('--root',type=Path)
    a=p.parse_args()
    if a.action=='check':check_plan();print('Frozen plan checked; no release or submission')
    elif a.action=='run':run(a.release)
    else:validate(a.root);print('PASS pilot100 independent readback')


if __name__=='__main__':
    try: main()
    except Exception as error:
        print(type(error).__name__);raise SystemExit(1)
