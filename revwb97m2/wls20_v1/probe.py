"""Three independent simultaneous WLS environments; never print credentials."""
import concurrent.futures
import json
import multiprocessing as mp
import os
from pathlib import Path
import time


def worker(index, barrier):
    import gurobipy as gp
    report = {'index': index, 'passed': False}
    try:
        fields = {}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            key, sep, value = line.partition('=')
            if sep and key.strip() in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
                fields[key.strip()] = value.strip()
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.setParam('WLSTokenDuration', 5)
            for key in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
                env.setParam(key, int(fields[key]) if key == 'LICENSEID' else fields[key])
            env.start()
            report['opened'] = time.time()
            with gp.Model('r2_wls20_probe', env=env) as model:
                model.Params.Threads = 1
                model.Params.TimeLimit = 30
                x = model.addVars(300, lb=0., ub=2.)
                model.setObjective(gp.quicksum((x[i]-1.)**2 for i in range(300)))
                barrier.wait(timeout=90)
                model.optimize()
                report.update(status=model.Status, objective=model.ObjVal,
                    passed=model.Status == gp.GRB.OPTIMAL and abs(model.ObjVal) < 1e-6)
                barrier.wait(timeout=90)
                time.sleep(15)
            report['closing'] = time.time()
        report['closed'] = time.time()
    except Exception as exc:
        report.update(passed=False, error_type=type(exc).__name__)
        if isinstance(exc, gp.GurobiError):
            report['error_code'] = exc.errno
    return report


if __name__ == '__main__':
    if not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Compute allocation required')
    ctx = mp.get_context('spawn')
    with ctx.Manager() as manager:
        barrier = manager.Barrier(3)
        with concurrent.futures.ProcessPoolExecutor(max_workers=3, mp_context=ctx) as pool:
            reports = list(pool.map(worker, range(3), [barrier]*3))
    passed = all(r['passed'] for r in reports)
    overlap = min(r.get('closing', 0) for r in reports)-max(r.get('opened', float('inf')) for r in reports)
    passed = bool(passed and overlap >= 15)
    result = dict(job=os.environ['SLURM_JOB_ID'], passed=passed, simultaneous_new_sessions=3,
        overlap_seconds=overlap if overlap != -float('inf') else None, workers=reports,
        safe_scale_after_epoch=time.time()+330)
    print(json.dumps(result, indent=2), flush=True)
    if not passed:
        raise SystemExit(1)
    # Expiry margin after explicit model/environment disposal; no test sessions held.
    time.sleep(330)
    print('PASS: three simultaneous WLS sessions; post-disposal token cooldown complete', flush=True)
