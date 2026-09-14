"""16 independent WLS processes, six-minute overlap and repeat solves."""
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing as mp
import os
from pathlib import Path
import re
import time

COUNT = 16
HOLD = 360


def worker(index, barrier):
    import gurobipy as gp
    result = dict(index=index, passed=False)
    try:
        fields = {}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            key, sep, value = line.partition('=')
            if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):
                fields[key.strip()] = value.strip()
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag',0)
            env.setParam('WLSTokenDuration',5)
            for key in ('WLSACCESSID','WLSSECRET','LICENSEID'):
                env.setParam(key,int(fields[key]) if key=='LICENSEID' else fields[key])
            env.start()
            result['opened']=time.time()
            with gp.Model('sustained_wls_retest',env=env) as model:
                model.Params.Threads=1
                model.Params.TimeLimit=20
                x=model.addVars(300,lb=0.,ub=2.)
                model.setObjective(gp.quicksum((x[j]-1.)**2 for j in range(300)))
                barrier.wait(timeout=90)
                model.optimize()
                if model.Status!=gp.GRB.OPTIMAL or abs(model.ObjVal)>1e-6:
                    raise ValueError('first solve failed')
                barrier.wait(timeout=90)
                if index==0: print('All16 sessions solved; beginning360second concurrent hold',flush=True)
                time.sleep(HOLD)
                model.reset()
                model.optimize()
                if model.Status!=gp.GRB.OPTIMAL or abs(model.ObjVal)>1e-6:
                    raise ValueError('repeat solve failed')
                barrier.wait(timeout=90)
                result.update(passed=True,first_solve=True,repeat_solve=True,objective=model.ObjVal)
            result['closing']=time.time()
        result['closed']=time.time()
    except Exception as exc:
        result.update(passed=False,error_type=type(exc).__name__)
        if isinstance(exc,gp.GurobiError):
            result['error_code']=exc.errno
            # Extract only non-secret session counts, never raw license errors.
            match=re.search(r'(\d+) active sessions.*baseline of (\d+)',str(exc))
            if match: result.update(active_sessions=int(match[1]),baseline=int(match[2]))
    return result


if __name__=='__main__':
    if not os.environ.get('SLURM_JOB_ID'): raise SystemExit('Compute allocation required')
    ctx=mp.get_context('spawn')
    with ctx.Manager() as manager:
        barrier=manager.Barrier(COUNT)
        with ProcessPoolExecutor(max_workers=COUNT,mp_context=ctx) as pool:
            reports=list(pool.map(worker,range(COUNT),[barrier]*COUNT))
    passed=all(r['passed'] for r in reports)
    overlap=min(r.get('closing',0) for r in reports)-max(r.get('opened',float('inf')) for r in reports)
    passed=bool(passed and overlap>=HOLD)
    report=dict(job=os.environ['SLURM_JOB_ID'],passed=passed,count=COUNT,hold_seconds=HOLD,
        overlap_seconds=overlap if passed else None,workers=reports,
        cooldown_until=time.time()+330)
    print(json.dumps(report,indent=2),flush=True)
    # Allow any issued five-minute tokens to expire even after a failed test.
    time.sleep(330)
    print('PASS sustained WLS retest; cooldown complete' if passed else 'FAIL sustained WLS retest; cooldown complete',flush=True)
    raise SystemExit(0 if passed else 1)
