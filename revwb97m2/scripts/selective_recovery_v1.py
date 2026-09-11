"""Two-stage K80 recovery; preserve old source failure and report grid outliers."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np
from revwb97m2 import selective_grid_v1 as policy
from revwb97m2.scripts import expanded_validation_v1 as old

a = old.a
c = old.c
ROOT = old.ROOT
PLAN = ROOT / 'revwb97m2/manifests/selective_recovery_v1/plan.json'


def schedule():
    return [dict(name='constrained80', budget=80, start='discovery80'),
            dict(name='restart80', budget=80, start='constrained80')]


def check(release):
    p, r = c.read(PLAN), c.read(release)
    c.require(all(r.get(k) is True for k in ('submission_authorized', 'tests_passed', 'resources_reviewed')),
              'release disabled')
    policy.settings()
    c.require(r['plan_sha256'] == c.digest(PLAN) and p['schedule'] == schedule()
              and p['config_sha256'] == c.digest(policy.CONFIG)
              and p['matrix_sha256'] == c.d.full.MATRIX_SHA
              and p['input_sha256'] == c.d.full.INPUT_SHA, 'scope changed')
    test = ROOT / r['test_report']
    t = c.read(test)
    c.require(c.digest(test) == r['test_report_sha256'] and t['passed']
              and t['commit'] == r['commit'] and t['plan_sha256'] == c.digest(PLAN), 'tests')
    for name, sha in {**p['hashes'], str(PLAN.relative_to(ROOT)): c.digest(PLAN)}.items():
        committed = subprocess.check_output(['git', 'show', r['commit'] + ':' + name], cwd=ROOT)
        c.require(c.digest(ROOT / name) == sha and hashlib.sha256(committed).hexdigest() == sha,
                  'uncommitted/changed source')
    c.require(tuple(r['route'][k] for k in ('partition', 'account', 'qos')) in c.d.full.ROUTES, 'route')
    return p, r


def source(p, arrays, settings):
    root = Path(p['source_root'])
    report = c.read(ROOT / p['source_audit'])
    c.require(report['job'] == '25790995' and report['partial_readback_passed']
              and not report['completed_workflow'], 'partial source identity')
    for name, sha in report['artifact_hashes'].items():
        c.require(c.digest(root / name) == sha, 'source artifact changed')
    identity = c.read(root / 'identity.json')
    previous, release = old.check(Path(identity['release']))
    c.require(identity['release_sha256'] == c.digest(identity['release'])
              and identity['plan_sha256'] == c.digest(old.PLAN)
              and identity['commit'] == release['commit'], 'source release identity')
    beta, z = old.source(previous, arrays, settings)
    c.require(np.array_equal(beta, np.load(root / 'source/coefficients.npy'))
              and np.array_equal(z, np.load(root / 'source/selection.npy')), 'source import')
    for row in old.schedule()[:5]:
        # Only the previous selected-model acceptance is required here. Its old
        # all-grid failure is preserved, not retrospectively relabelled a pass.
        actual = old.audit_case(row, root, arrays, settings)
        c.require(actual == c.read(root / (row['name'] + '_audit.json')), 'source audit mismatch')
    return {name: (np.load(root / name / 'coefficients.npy'), np.load(root / name / 'selection.npy'))
            for name in ('discovery14', 'discovery80')}


def inputs(row, root, arrays, settings):
    beta = np.load(root / row['start'] / 'coefficients.npy')
    z = np.load(root / row['start'] / 'selection.npy')
    candidates = np.stack([np.load(root / name / 'coefficients.npy')
                           for name in ('discovery14', 'discovery80')])
    rows = policy.select_rows(arrays['grid_difference_99590'], candidates,
                              settings.candidate_rows, settings.global_rows)
    return beta, z, rows


def solve(row, root, arrays, settings, entry_ids, env):
    import gurobipy as gp
    folder = root / row['name']
    folder.mkdir()
    b, z, rows = inputs(row, root, arrays, settings)
    c.write(folder / 'start_audit.json', a.start_audit(arrays, b, z, 80, rows, settings))
    for key, value in [('start_coefficients', b), ('start_selection', z), ('grid_rows', rows)]:
        np.save(folder / (key + '.npy'), value)
    m = None
    try:
        m, beta, selected = a.build(arrays, settings, 80, rows, env)
        for i in range(292):
            beta[i].Start = float(b[i])
            selected[i].Start = float(z[i])
        m.write(str(folder / 'model.mps.gz'))
        keys = ('Method', 'NodeMethod', 'Presolve', 'BarConvTol', 'NumericFocus', 'Threads',
                'TimeLimit', 'Seed', 'FeasibilityTol', 'IntFeasTol', 'MIPGap', 'MIPGapAbs')
        c.write(folder / 'model.json', dict(variables=m.NumVars, constraints=m.NumConstrs,
            binaries=m.NumBinVars, sos=m.NumSOS, version=list(gp.gurobi.version()),
            parameters={k: m.getParamInfo(k)[2] for k in keys}))
        m.Params.LogToConsole = 0
        m.Params.LogFile = ''
        m.Params.OutputFlag = 1
        with (folder / 'progress.jsonl').open('x') as stream:
            callback, errors = c.d.progress_callback(stream, gp.GRB)
            m.optimize(callback)
        result = dict(name=row['name'], budget=80, status=int(m.Status), runtime=float(m.Runtime),
            solution_count=int(m.SolCount), nodes=float(m.NodeCount), callback_errors=errors,
            passed=False, objective=None, bound=c.d.numeric(m.ObjBound))
        if m.SolCount:
            b = np.array([beta[i].X for i in range(292)])
            z = np.array([selected[i].X for i in range(292)])
            np.save(folder / 'coefficients.npy', b)
            np.save(folder / 'selection.npy', z)
            checked = policy.audit(arrays, b, z, 80, rows, settings, entry_ids)
            result.update(objective=float(m.ObjVal), audit=checked,
                          gaps=c.d.gap_report(m.ObjVal, m.ObjBound, m.MIPGap))
            result['passed'] = bool(m.Status in (2, 9) and not errors and checked['passed']
                and np.isclose(m.ObjVal, checked['audit']['independent']['regularized_objective_hartree2'],
                               rtol=1e-7, atol=1e-10))
        c.write(folder / 'result.json', result)
        return result
    finally:
        if m is not None:
            m.dispose()


def audit_case(row, root, arrays, settings, entry_ids):
    folder = root / row['name']
    r, model = c.read(folder / 'result.json'), c.read(folder / 'model.json')
    b, z, rows = inputs(row, root, arrays, settings)
    for name, expected in [('start_coefficients', b), ('start_selection', z), ('grid_rows', rows)]:
        c.require(np.array_equal(expected, np.load(folder / (name + '.npy'))), 'start/grid identity')
    c.require(c.read(folder / 'start_audit.json') == a.start_audit(arrays, b, z, 80, rows, settings),
              'start audit identity')
    c.require((model['variables'], model['constraints'], model['binaries'], model['sos']) ==
              (584, 590 + 2 * len(rows), 292, 0), 'model dimensions')
    params = model['parameters']
    c.require(params['Threads'] == 16 and params['TimeLimit'] == 600 and params['Seed'] == settings.seed
              and all(params[k] == value for k, value in settings.solver_parameters), 'parameters')
    c.require(r['name'] == row['name'] and r['budget'] == 80 and r['passed']
              and r['status'] in (2, 9) and r['solution_count'] > 0 and not r['callback_errors'], 'solve rejected')
    actual = policy.audit(arrays, np.load(folder / 'coefficients.npy'),
                          np.load(folder / 'selection.npy'), 80, rows, settings, entry_ids)
    c.require(actual == r['audit'] and actual['passed'], 'candidate/report mismatch')
    c.require(np.isclose(r['objective'], actual['audit']['independent']['regularized_objective_hartree2'],
                         rtol=1e-7, atol=1e-10), 'objective mismatch')
    gaps = c.d.gap_report(r['objective'], r['bound']['value'], r['gaps']['gap'])
    c.require(gaps == r['gaps'] and gaps['gap_consistent'], 'gap mismatch')
    return dict(name=row['name'], passed=True, selected_rows=rows.tolist(), report=actual, gaps=gaps)


def validate(root):
    identity = c.read(root / 'identity.json')
    p, r = check(Path(identity['release']))
    c.require(identity['plan_sha256'] == c.digest(PLAN)
              and identity['release_sha256'] == c.digest(identity['release'])
              and identity['commit'] == r['commit'], 'identity')
    done, pub = c.read(root / 'completion.json'), c.read(root / 'publication.json')
    c.require(done['publication_sha256'] == c.digest(root / 'publication.json')
              and done['bulk_authorized'] is False and done['final_model_user_review_required'] is True,
              'completion identity')
    c.require(all(c.digest(root / name) == sha for name, sha in pub['artifacts'].items()), 'artifact hashes')
    settings = policy.settings()
    arrays, manifest = c.d.full.load_inputs(c.d.full.matrix_manifest(), settings)
    for name, (b, z) in source(p, arrays, settings).items():
        c.require(np.array_equal(b, np.load(root / name / 'coefficients.npy'))
                  and np.array_equal(z, np.load(root / name / 'selection.npy')), 'source copy changed')
    results = [audit_case(row, root, arrays, settings, manifest['reaction_ids']) for row in schedule()]
    for result in results:
        c.require(result == c.read(root / (result['name'] + '_audit.json')), 'saved audit mismatch')
    return results


def run(release):
    p, record = check(release)
    c.d.full.check_allocation(record['route'])
    job = os.environ['SLURM_JOB_ID']
    c.require(job.isdigit(), 'job')
    root = Path(p['output_parent']) / job
    c.require(not root.exists(), 'preserve run')
    settings = policy.settings()
    arrays, manifest = c.d.full.load_inputs(c.d.full.matrix_manifest(), settings)
    starts = source(p, arrays, settings)
    parent = root.parent
    while not parent.exists():
        parent = parent.parent
    c.require(shutil.disk_usage(parent).free > 32 * 1024**3, 'storage')
    root.mkdir(parents=True)
    for name, (b, z) in starts.items():
        (root / name).mkdir()
        np.save(root / name / 'coefficients.npy', b)
        np.save(root / name / 'selection.npy', z)
    c.write(root / 'identity.json', dict(plan_sha256=c.digest(PLAN), release=str(Path(release).resolve()),
        release_sha256=c.digest(release), commit=record['commit']))
    try:
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
            for row in schedule():
                result = solve(row, root, arrays, settings, manifest['reaction_ids'], env)
                c.require(result['passed'], 'selected-model solve rejected')
                audit = audit_case(row, root, arrays, settings, manifest['reaction_ids'])
                c.write(root / (row['name'] + '_audit.json'), audit)
                print('PASS', row['name'], 'full99590 violations:', audit['report']['grids']['99590']['count'],
                      '(reported for user review)', flush=True)
        c.write(root / 'publication.json', dict(artifacts={str(f.relative_to(root)): c.digest(f)
            for f in root.rglob('*') if f.is_file()}))
        c.write(root / 'completion.json', dict(publication_sha256=c.digest(root / 'publication.json'),
            bulk_authorized=False, final_model_user_review_required=True))
        validate(root)
        print('PASS selective recovery independent readback; final user review required', flush=True)
        return 0
    except Exception as exc:
        c.write(root / 'failure.json', dict(error_type=type(exc).__name__, error_code=getattr(exc, 'errno', None)))
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'validate'])
    parser.add_argument('--release', type=Path)
    parser.add_argument('--root', type=Path)
    args = parser.parse_args()
    if args.action == 'run':
        raise SystemExit(run(args.release))
    validate(args.root)
    print('PASS independent readback')
