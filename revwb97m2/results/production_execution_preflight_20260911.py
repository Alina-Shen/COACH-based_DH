"""Build/start round-trip only on a compute node; never calls optimize()."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import numpy as np
from revwb97m2 import production_multistart_v1 as r

COMMIT = '488dba7ac0129b375797ed8057a00ba210ab6063'


def main():
    import gurobipy as gp
    plan = r.c.read(r.PLAN)
    for name, sha in {**plan['hashes'], str(r.PLAN.relative_to(r.ROOT)): r.c.digest(r.PLAN)}.items():
        raw = subprocess.check_output(['git', 'show', COMMIT + ':' + name], cwd=r.ROOT)
        r.c.require(hashlib.sha256(raw).hexdigest() == sha == r.c.digest(r.ROOT / name), 'source identity')
    r.c.d.full.check_allocation(dict(partition='cm1', account='lr_qchem', qos='condo_qchem'))
    out = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/production_preflight_v1') / os.environ['SLURM_JOB_ID']
    out.mkdir(parents=True, exist_ok=False)
    graph = r.graph()
    arrays, ids, settings = r.load_data()
    source = Path(graph['source_coefficients_path']).parent.parent
    source_reports = r.reader.validate(source)
    # Existing validated rows exercise grid construction only: never production rows.
    rows = np.load(source / 'constrained80' / 'grid_rows.npy')
    fields = {}
    for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
            fields[key.strip()] = value.strip()
    reports = []
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        for key in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
            env.setParam(key, int(fields[key]) if key == 'LICENSEID' else fields[key])
        env.start()
        # K endpoints, both repeat types, grid/no-grid; one license session, serial.
        for k in (14, 80):
            for constrained in (False, True):
                active_rows = rows if constrained else np.array([], dtype=int)
                for repeat in (0, 1):
                    task = next(t for t in graph['tasks'] if t['phase'] == 1 and t['budget'] == k and t['repeat'] == repeat)
                    original, beta0, z0, diagnostic = r.start_inputs(task, out, graph, arrays, ids, settings, active_rows)
                    name = f'k{k}_grid{int(constrained)}_repeat{repeat}'
                    folder = out / name
                    folder.mkdir()
                    model, beta, z = r.build(arrays, settings, task, active_rows, env)
                    try:
                        for j in range(292):
                            beta[j].Start = float(beta0[j])
                            z[j].Start = float(z0[j])
                        model.update()
                        r.c.require(np.array_equal([beta[j].Start for j in range(292)], beta0), 'start assignment')
                        r.c.require(np.array_equal([z[j].Start for j in range(292)], z0), 'selection assignment')
                        model.write(str(folder / 'model.mps.gz'))
                        model.write(str(folder / 'start.mst'))
                        clone = gp.read(str(folder / 'model.mps.gz'), env=env)
                        try:
                            clone.read(str(folder / 'start.mst'))
                            clone.update()
                            actual = np.array([clone.getVarByName(beta[j].VarName).Start for j in range(292)])
                            selected = np.array([clone.getVarByName(z[j].VarName).Start for j in range(292)])
                            r.c.require(np.allclose(actual, beta0, rtol=1e-14, atol=1e-15), 'coefficient start roundtrip')
                            r.c.require(np.array_equal(selected, z0), 'selection start roundtrip')
                        finally:
                            clone.dispose()
                        params = {p: model.getParamInfo(p)[2] for p in r.PARAMS}
                        r.c.require(params['TimeLimit'] == 7200 and params['Threads'] == 16, 'execution parameters')
                        item = dict(name=name, budget=k, selected_rows=len(active_rows),
                            variables=model.NumVars, constraints=model.NumConstrs, binaries=model.NumBinVars,
                            sos=model.NumSOS, start_feasible=diagnostic['passed'], start_roundtrip_passed=True,
                            parameters=params)
                        r.c.require((item['variables'], item['constraints'], item['binaries'], item['sos']) ==
                                    (584, 590 + 2 * len(active_rows), 292, 0), 'dimensions')
                        r.c.write(folder / 'start_audit.json', diagnostic)
                        r.c.write(folder / 'model.json', item)
                        reports.append(item)
                    finally:
                        model.dispose()
    r.c.write(out / 'report.json', dict(passed=True, commit=COMMIT, plan_sha256=r.c.digest(r.PLAN),
        harness_sha256=r.c.digest(Path(__file__)), job=os.environ['SLURM_JOB_ID'],
        version=list(gp.gurobi.version()), source_readback_cases=len(source_reports), cases=reports,
        optimization_performed=False, production_rows_selected=False, production_authorized=False,
        scope='Eight build/start serialization cases; not solver acceptance, search or full production orchestration'))
    r.publish(out)
    r.verify_publication(out)
    print('PASS eight production model/start roundtrips; no optimization; no production release', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('FAIL', type(exc).__name__, 'code', getattr(exc, 'errno', None), flush=True)
        sys.exit(1)
