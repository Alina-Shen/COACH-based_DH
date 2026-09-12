"""Released 56-solve execution and readback; no automatic submission on import."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import numpy as np
from revwb97m2 import production_multistart_plan_v1 as planner
from revwb97m2 import selective_readback_v2 as reader

v = reader.v
c = v.c
ROOT = v.ROOT
PLAN = ROOT / 'revwb97m2/manifests/production_multistart_v1/plan.json'
GRAPH = ROOT / 'revwb97m2/manifests/production_multistart_preparation_v1/task_graph.json'
PARAMS = ('Method', 'NodeMethod', 'Presolve', 'BarConvTol', 'NumericFocus', 'Threads',
          'TimeLimit', 'Seed', 'FeasibilityTol', 'IntFeasTol', 'MIPGap', 'MIPGapAbs')


def graph():
    g = c.read(GRAPH)
    expected = planner.task_graph()
    c.require(g['tasks'] == expected['tasks'] and g['grid_selection'] == expected['grid_selection'],
              'graph/noise mismatch')
    source = Path(g['source_coefficients_path'])
    c.require(c.digest(source) == g['source_coefficients_sha256'], 'simple scalar source changed')
    seed = planner.simple_seed(np.load(source))
    c.require(np.array_equal(seed, g['simple_seed']), 'simple seed changed')
    return g


def check(release):
    p, r = c.read(PLAN), c.read(release)
    c.require(all(r.get(k) is True for k in ('submission_authorized', 'tests_passed',
        'resources_reviewed', 'prebulk_approved')), 'production release disabled')
    c.require(r['plan_sha256'] == c.digest(PLAN) and p['graph_sha256'] == c.digest(GRAPH), 'plan identity')
    for name, sha in {**p['hashes'], str(PLAN.relative_to(ROOT)): c.digest(PLAN)}.items():
        raw = subprocess.check_output(['git', 'show', r['commit'] + ':' + name], cwd=ROOT)
        c.require(c.digest(ROOT / name) == sha and hashlib.sha256(raw).hexdigest() == sha,
                  'uncommitted/changed code or input identity')
    test = ROOT / r['test_report']
    t = c.read(test)
    c.require(c.digest(test) == r['test_report_sha256'] and t['passed'] and t['commit'] == r['commit']
              and t['plan_sha256'] == c.digest(PLAN), 'test release mismatch')
    c.require(tuple(r['route'][k] for k in ('partition', 'account', 'qos')) in c.d.full.ROUTES
              and 'lr_lowprio' not in r['route'].values(), 'route')
    c.require(re.fullmatch(r'[A-Za-z0-9_-]+', r['run_name']) is not None, 'run name')
    g = graph()
    root = Path(p['output_parent']) / r['run_name']
    return p, r, g, root


def publish(folder):
    c.write(folder / 'publication.json', dict(artifacts={str(f.relative_to(folder)): c.digest(f)
        for f in folder.rglob('*') if f.is_file()}))
    c.write(folder / 'completion.json', dict(publication_sha256=c.digest(folder / 'publication.json')))


def verify_publication(folder):
    done, pub = c.read(folder / 'completion.json'), c.read(folder / 'publication.json')
    c.require(done['publication_sha256'] == c.digest(folder / 'publication.json'), 'publication changed')
    actual = {str(f.relative_to(folder)) for f in folder.rglob('*') if f.is_file()}
    c.require(actual == set(pub['artifacts']) | {'publication.json', 'completion.json'}, 'unexpected artifacts')
    c.require(all(c.digest(folder / n) == h for n, h in pub['artifacts'].items()), 'artifact changed')


def load_data():
    s = v.policy.settings()
    arrays, manifest = c.d.full.load_inputs(c.d.full.matrix_manifest(), s)
    return arrays, manifest['reaction_ids'], s


def selection_guess(beta):
    z = (np.abs(beta) >= 1e-6).astype(float)
    z[288:] = 1.0  # Approved mandatory DH scalar slots, unlike COACH's iszero encoding.
    return z


def start_inputs(task, root, g, arrays, ids, settings, rows):
    if task['start_source'] == 'simple':
        original = np.asarray(g['simple_seed'])
    else:
        parent = next(t for t in g['tasks'] if t['id'] == task['start_source'])
        c.require(parent['phase'] == 1 and parent['budget'] == task['budget'], 'wrong-K start')
        audit_task(parent, root, g, arrays, ids, settings, np.array([], dtype=int))
        original = np.load(root / parent['id'] / 'coefficients.npy')
    beta = planner.materialize_start(task, original)
    z = selection_guess(beta)
    # This is a diagnostic, NOT an acceptance gate for a noisy solver suggestion.
    checked = v.policy.audit(arrays, beta, z, task['budget'], rows, settings, ids)
    return original, beta, z, checked


def build(arrays, settings, task, rows, env):
    m, beta, z = v.a.build(arrays, settings, task['budget'], rows, env)
    m.Params.TimeLimit = task['seconds']
    m.Params.Threads = task['threads']
    return m, beta, z


def solve(task, root, g, arrays, ids, settings, rows, env):
    import gurobipy as gp
    folder = root / task['id']
    folder.mkdir()  # Never overwrite or automatically retry an existing task.
    original, b, z, start_report = start_inputs(task, root, g, arrays, ids, settings, rows)
    c.write(folder / 'task.json', task)
    c.write(folder / 'start_audit.json', start_report)
    for name, value in [('original_start', original), ('start_coefficients', b), ('start_selection', z),
                        ('grid_rows', rows)]:
        np.save(folder / (name + '.npy'), value)
    m = None
    try:
        m, beta, selected = build(arrays, settings, task, rows, env)
        for i in range(292):
            beta[i].Start = float(b[i])
            selected[i].Start = float(z[i])
        m.write(str(folder / 'model.mps.gz'))
        c.write(folder / 'model.json', dict(variables=m.NumVars, constraints=m.NumConstrs,
            binaries=m.NumBinVars, sos=m.NumSOS, version=list(gp.gurobi.version()),
            parameters={k: m.getParamInfo(k)[2] for k in PARAMS}))
        m.Params.LogToConsole = 0
        m.Params.LogFile = ''
        m.Params.OutputFlag = 1
        with (folder / 'progress.jsonl').open('x') as stream:
            callback, errors = c.d.progress_callback(stream, gp.GRB)
            m.optimize(callback)
        result = dict(status=int(m.Status), runtime=float(m.Runtime), solution_count=int(m.SolCount),
            nodes=float(m.NodeCount), callback_errors=errors, objective=None,
            bound=c.d.numeric(m.ObjBound), passed=False)
        if m.SolCount:
            b = np.array([beta[i].X for i in range(292)])
            z = np.array([selected[i].X for i in range(292)])
            np.save(folder / 'coefficients.npy', b)
            np.save(folder / 'selection.npy', z)
            report = v.policy.audit(arrays, b, z, task['budget'], rows, settings, ids)
            result.update(objective=float(m.ObjVal), report=report,
                          gaps=c.d.gap_report(m.ObjVal, m.ObjBound, m.MIPGap))
            result['passed'] = bool(m.Status in (2, 9) and not errors and report['passed']
                and np.isclose(m.ObjVal, report['audit']['independent']['regularized_objective_hartree2'],
                               rtol=1e-7, atol=1e-10))
        c.write(folder / 'result.json', result)
        c.require(result['passed'], 'production solution rejected')
        publish(folder)
        audit_task(task, root, g, arrays, ids, settings, rows)
    except Exception as exc:
        c.write(folder / 'failure.json', dict(error_type=type(exc).__name__, error_code=getattr(exc, 'errno', None)))
        raise
    finally:
        if m is not None:
            m.dispose()


def audit_task(task, root, g, arrays, ids, settings, rows):
    folder = root / task['id']
    c.require(not (folder / 'failure.json').exists(), 'task has failure marker')
    verify_publication(folder)
    c.require(c.read(folder / 'task.json') == task, 'task identity')
    original, b, z, start_report = start_inputs(task, root, g, arrays, ids, settings, rows)
    for name, expected in [('original_start', original), ('start_coefficients', b), ('start_selection', z),
                           ('grid_rows', rows)]:
        c.require(np.array_equal(np.load(folder / (name + '.npy')), expected), 'start/grid identity')
    reader.compare_report(start_report, c.read(folder / 'start_audit.json'))
    model, r = c.read(folder / 'model.json'), c.read(folder / 'result.json')
    c.require((model['variables'], model['constraints'], model['binaries'], model['sos']) ==
              (584, 590 + 2 * len(rows), 292, 0), 'model dimensions')
    params = model['parameters']
    c.require(params['TimeLimit'] == 7200 and params['Threads'] == 16 and params['Seed'] == settings.seed
              and all(params[k] == val for k, val in settings.solver_parameters), 'model parameters')
    c.require(r['passed'] and r['status'] in (2, 9) and r['solution_count'] > 0 and not r['callback_errors'],
              'solver result')
    actual = v.policy.audit(arrays, np.load(folder / 'coefficients.npy'),
                            np.load(folder / 'selection.npy'), task['budget'], rows, settings, ids)
    c.require(actual['passed'], 'scientific/selected-grid failure')
    reader.compare_report(actual, r['report'])
    c.require(np.isclose(r['objective'], actual['audit']['independent']['regularized_objective_hartree2'],
                         rtol=1e-7, atol=1e-10), 'objective')
    c.require(r['bound']['state'] == 'finite' and r['gaps']['gap_state'] == 'finite', 'nonfinite gap/bound')
    gap = c.d.gap_report(r['objective'], r['bound']['value'], r['gaps']['gap'])
    c.require(gap['gap_consistent'], 'gap')
    reader.compare_report(gap, r['gaps'])
    return dict(task=task['id'], objective=r['objective'], gap=gap, report=actual)


def select_grid(root, g, arrays, ids, settings, write=False):
    discovery = [t for t in g['tasks'] if t['phase'] == 1]
    pool = g['grid_selection']['candidate_pool']
    c.require(pool == [t['id'] for t in discovery], 'candidate pool')
    for task in discovery:
        audit_task(task, root, g, arrays, ids, settings, np.array([], dtype=int))
    candidates = np.stack([np.load(root / name / 'coefficients.npy') for name in pool])
    rows = v.policy.select_rows(arrays['grid_difference_99590'], candidates, 100, 200)
    identity = dict(pool=pool, source_publications={name: c.digest(root / name / 'publication.json') for name in pool})
    folder = root / 'grid_selection'
    if write:
        folder.mkdir()
        np.save(folder / 'rows.npy', rows)
        c.write(folder / 'identity.json', identity)
        publish(folder)
    else:
        verify_publication(folder)
        c.require(c.read(folder / 'identity.json') == identity and np.array_equal(np.load(folder / 'rows.npy'), rows),
                  'selected rows/source changed')
    return rows


def check_run_identity(root, release, record):
    expected = dict(release=str(Path(release).resolve()), release_sha256=c.digest(release),
                    plan_sha256=c.digest(PLAN), commit=record['commit'])
    c.require(c.read(root / 'identity.json') == expected, 'run identity')


def execute(release, phase, index=None):
    c.require(phase in ('1', '2', 'grid'), 'phase required')
    p, r, g, root = check(release)
    c.d.full.check_allocation(r['route'])
    check_run_identity(root, release, r)
    arrays, ids, settings = load_data()
    if phase == 'grid':
        select_grid(root, g, arrays, ids, settings, write=True)
        print('PASS all14 discovery audits and grid publication', flush=True)
        return
    tasks = [t for t in g['tasks'] if t['phase'] == int(phase)]
    c.require(index is not None and 0 <= index < len(tasks), 'array index')
    rows = np.array([], dtype=int) if phase == '1' else select_grid(root, g, arrays, ids, settings)
    c.require(shutil.disk_usage(root).free > 32 * 1024**3, 'free storage')
    import gurobipy as gp
    fields = {}
    for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
            fields[key.strip()] = value.strip()
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        for key in ('WLSACCESSID', 'WLSSECRET', 'LICENSEID'):
            env.setParam(key, int(fields[key]) if key == 'LICENSEID' else fields[key])
        env.start()
        solve(tasks[index], root, g, arrays, ids, settings, rows, env)
    print('PASS', tasks[index]['id'], 'final model review required', flush=True)


def validate(release):
    p, r, g, root = check(release)
    before = {str(f.relative_to(root)): c.digest(f) for f in root.rglob('*') if f.is_file()}
    check_run_identity(root, release, r)
    arrays, ids, settings = load_data()
    rows = select_grid(root, g, arrays, ids, settings)
    results = [audit_task(t, root, g, arrays, ids, settings,
                          np.array([], dtype=int) if t['phase'] == 1 else rows) for t in g['tasks']]
    c.require(before == {str(f.relative_to(root)): c.digest(f) for f in root.rglob('*') if f.is_file()},
              'readback changed artifacts')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'validate'])
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--phase', choices=['1', '2', 'grid'])
    parser.add_argument('--index', type=int)
    args = parser.parse_args()
    if args.action == 'validate':
        validate(args.release)
        print('PASS56 independently validated solves; final model review required')
    else:
        execute(args.release, args.phase, args.index)
