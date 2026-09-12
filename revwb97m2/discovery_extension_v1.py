"""Add missing K14..82 discovery fits without changing the active seven-K runner."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import numpy as np
from revwb97m2 import production_multistart_v1 as old

PLAN = old.ROOT / 'revwb97m2/manifests/discovery_extension_v1/plan.json'
OLD_RELEASE = old.ROOT / 'revwb97m2/manifests/production_multistart_v1/release_20260911.json'


def additional_tasks():
    # Preserve the seven original noise draws; extend that sweep in ascending
    # missing-K order. This avoids discarding/relabeling already running fits.
    rng = np.random.default_rng(0)
    for _ in old.planner.BUDGETS:
        rng.normal(scale=.05, size=292)
    result = []
    for k in range(14, 83):
        if k in old.planner.BUDGETS:
            continue
        for repeat in (0, 1):
            noise = np.zeros(292) if repeat == 0 else rng.normal(scale=.05, size=292)
            result.append(dict(id=f'p1_k{k}_simple_r{repeat}', phase=1, budget=k,
                start_source='simple', repeat=repeat, noise=noise.tolist(), seconds=7200,
                threads=16, dependencies=[], acceptance='ungridded'))
    return result


def check(release):
    p, r = old.c.read(PLAN), old.c.read(release)
    old.c.require(all(r.get(k) is True for k in ('submission_authorized', 'tests_passed',
        'resources_reviewed', 'wls_sessions_reserved_for_campaign')), 'extension release disabled')
    old.c.require(r['plan_sha256'] == old.c.digest(PLAN), 'plan identity')
    for name, sha in {**p['hashes'], str(PLAN.relative_to(old.ROOT)): old.c.digest(PLAN)}.items():
        raw = subprocess.check_output(['git', 'show', r['commit'] + ':' + name], cwd=old.ROOT)
        old.c.require(old.c.digest(old.ROOT / name) == sha == hashlib.sha256(raw).hexdigest(), 'source identity')
    tests = old.c.read(old.ROOT / r['test_report'])
    old.c.require(old.c.digest(old.ROOT / r['test_report']) == r['test_report_sha256'] and tests['passed']
        and tests['commit'] == r['commit'] and tests['plan_sha256'] == old.c.digest(PLAN), 'test identity')
    _, _, graph, previous_root = old.check(OLD_RELEASE)
    old.c.require(p['additional_tasks'] == additional_tasks(), 'task/noise identity')
    old.c.require(tuple(r['route'][k] for k in ('partition', 'account', 'qos')) in old.c.d.full.ROUTES, 'route')
    return p, r, graph, previous_root


def execute(release, index):
    p, r, graph, previous_root = check(release)
    old.c.d.full.check_allocation(r['route'])
    old.c.require(0 <= index < len(p['additional_tasks']), 'array index')
    task = p['additional_tasks'][index]
    root = Path(p['output_root'])
    root.mkdir(parents=True, exist_ok=True)
    # Exclusive per-task receipt prevents blind reruns even after partial failure.
    old.c.write(root / (task['id'] + '.execution.json'), dict(release=str(Path(release).resolve()),
        release_sha256=old.c.digest(release), commit=r['commit'], plan_sha256=old.c.digest(PLAN),
        job=os.environ['SLURM_JOB_ID'], task=task['id']))
    arrays, ids, settings = old.load_data()
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
        old.solve(task, root, graph, arrays, ids, settings, np.array([], dtype=int), env)
    print('PASS', task['id'], 'discovery only', flush=True)


def validate(release):
    p, r, graph, previous_root = check(release)
    old.check_run_identity(previous_root, OLD_RELEASE, old.c.read(OLD_RELEASE))
    arrays, ids, settings = old.load_data()
    reports = []
    for task in [t for t in graph['tasks'] if t['phase'] == 1] + p['additional_tasks']:
        root = previous_root if task['budget'] in old.planner.BUDGETS else Path(p['output_root'])
        if root != previous_root:
            record = old.c.read(root / (task['id'] + '.execution.json'))
            old.c.require(record['release_sha256'] == old.c.digest(release)
                and record['plan_sha256'] == old.c.digest(PLAN) and record['commit'] == r['commit']
                and record['task'] == task['id'], 'execution identity')
        reports.append(old.audit_task(task, root, graph, arrays, ids, settings, np.array([], dtype=int)))
    old.c.require(len(reports) == 138, 'incomplete discovery pool')
    return reports


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'validate'])
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--index', type=int)
    args = parser.parse_args()
    if args.action == 'run':
        old.c.require(args.index is not None, 'index required')
        execute(args.release, args.index)
    else:
        validate(args.release)
        print('PASS all138 discovery candidates; grid selection not performed')
