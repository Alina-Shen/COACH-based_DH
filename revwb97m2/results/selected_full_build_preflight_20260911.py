"""Deferred real-data maximum-row construction check; no optimize() call."""
import argparse
import os
from pathlib import Path
import sys
import numpy as np
from revwb97m2 import selected_full_v1 as f


def main(release):
    import gurobipy as gp
    p, r, graph, root = f.check(release)
    f.old.c.require(f.old.c.digest(Path(__file__)) == r['build_preflight_sha256'], 'preflight identity')
    f.old.c.d.full.check_allocation(r['route'])
    # No WLS before every actual discovery result is validated.
    source_reports = f.e.validate(f.DISCOVERY_RELEASE)
    arrays, ids, settings = f.old.load_data()
    out = root.with_name(root.name + '_build_preflight')
    out.mkdir(parents=True, exist_ok=False)
    rows = np.arange(len(ids), dtype=int)  # Construction upper bound, NOT chosen production rows.
    fields = {}
    for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
            fields[key.strip()] = value.strip()
    cases = []
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        for key in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
            env.setParam(key, int(fields[key]) if key == 'LICENSEID' else fields[key])
        env.start()
        for k in (14, 82):
            for repeat in (0, 1):
                task = next(t for t in graph['tasks'] if t['phase'] == 2 and t['budget'] == k
                            and t['repeat'] == repeat and t['start_source'] == 'simple')
                original, b, z, diagnostic = f.old.start_inputs(task, out, graph, arrays, ids, settings, rows)
                model, beta, selected = f.old.build(arrays, settings, task, rows, env)
                try:
                    for j in range(292):
                        beta[j].Start = float(b[j])
                        selected[j].Start = float(z[j])
                    model.update()
                    f.old.c.require(np.array_equal([beta[j].Start for j in range(292)], b), 'start import')
                    f.old.c.require(np.array_equal([selected[j].Start for j in range(292)], z), 'binary start import')
                    dims = [model.NumVars, model.NumConstrs, model.NumBinVars, model.NumSOS]
                    f.old.c.require(dims == [584, 3586, 292, 0], 'max-row dimensions')
                    f.old.c.require(model.Params.TimeLimit == 7200 and model.Params.Threads == 16, 'resources')
                    cases.append(dict(k=k, repeat=repeat, dimensions=dims, passed=True,
                                      start_diagnostically_feasible=diagnostic['passed']))
                finally:
                    model.dispose()
    f.old.c.write(out / 'report.json', dict(passed=True, job=os.environ['SLURM_JOB_ID'],
        release_sha256=f.old.c.digest(release), commit=r['commit'], plan_sha256=f.old.c.digest(f.PLAN),
        source_candidates=len(source_reports), grid_rows_tested=len(rows), cases=cases,
        optimization_performed=False, production_rows_selected=False))
    f.old.publish(out)
    print('PASS138 sources and four max-row build/start cases; no optimization', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    args = parser.parse_args()
    try:
        main(args.release)
    except Exception as exc:
        print('FAIL', type(exc).__name__, 'code', getattr(exc, 'errno', None), flush=True)
        sys.exit(1)
