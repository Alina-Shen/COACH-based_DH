"""Full K14..82 selected pass; immutable 138-discovery snapshot and 414 solves."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import numpy as np
from revwb97m2 import discovery_extension_v1 as e

old = e.old
PLAN = old.ROOT / 'revwb97m2/manifests/selected_full_v1/plan.json'
DISCOVERY_RELEASE = old.ROOT / 'revwb97m2/manifests/discovery_extension_v1/release_20260911.json'


def task_graph():
    original = old.planner.task_graph()
    discovery = [t for t in original['tasks'] if t['phase'] == 1] + e.additional_tasks()
    rng = np.random.default_rng(0)  # Fresh pass-2 sweep in ascending K order.
    selected = []
    for k in range(14, 83):
        for source in ('simple', 'pass1_r0', 'pass1_r1'):
            for repeat in (0, 1):
                noise = np.zeros(292) if repeat == 0 else rng.normal(scale=.05, size=292)
                selected.append(dict(id=f'p2_k{k}_{source}_r{repeat}', phase=2, budget=k,
                    start_source='simple' if source == 'simple' else f'p1_k{k}_simple_r{source[-1]}',
                    repeat=repeat, noise=noise.tolist(), seconds=7200, threads=16,
                    dependencies=['grid_selection'], acceptance='selected_constraints_only'))
    pool = [t['id'] for t in discovery]
    return dict(tasks=discovery + selected, grid_selection=dict(id='grid_selection',
        dependencies=pool, candidate_pool=pool, top_per_candidate=100, additional_remaining_l1=200))


def check(release):
    p, r = old.c.read(PLAN), old.c.read(release)
    old.c.require(all(r.get(k) is True for k in ('submission_authorized', 'tests_passed',
        'resources_reviewed', 'wls_sessions_reserved_for_campaign')), 'selected release disabled')
    old.c.require(r['plan_sha256'] == old.c.digest(PLAN), 'plan identity')
    for name, sha in {**p['hashes'], str(PLAN.relative_to(old.ROOT)): old.c.digest(PLAN)}.items():
        raw = subprocess.check_output(['git', 'show', r['commit'] + ':' + name], cwd=old.ROOT)
        old.c.require(old.c.digest(old.ROOT / name) == sha == hashlib.sha256(raw).hexdigest(), 'source identity')
    report = old.ROOT / r['test_report']
    tests = old.c.read(report)
    old.c.require(old.c.digest(report) == r['test_report_sha256'] and tests['passed']
        and tests['commit'] == r['commit'] and tests['plan_sha256'] == old.c.digest(PLAN), 'test identity')
    old.c.require(p['graph'] == task_graph(), 'task/noise/pool identity')
    old.c.require(tuple(r['route'][k] for k in ('partition', 'account', 'qos')) in old.c.d.full.ROUTES, 'route')
    e.check(DISCOVERY_RELEASE)
    graph = {**p['graph'], 'simple_seed': old.graph()['simple_seed']}
    return p, r, graph, Path(p['output_root'])


def identity(release, record):
    return dict(release=str(Path(release).resolve()), release_sha256=old.c.digest(release),
                plan_sha256=old.c.digest(PLAN), commit=record['commit'])


def prepare_grid(release):
    p, r, graph, root = check(release)
    old.c.d.full.check_allocation(r['route'])
    # Complete source audit before creating any new snapshot or grid publication.
    e.validate(DISCOVERY_RELEASE)
    ep, er, eg, previous = e.check(DISCOVERY_RELEASE)
    arrays, ids, settings = old.load_data()
    root.mkdir(parents=True, exist_ok=False)
    old.c.write(root / 'identity.json', identity(release, r))
    sources = {}
    for task in [t for t in graph['tasks'] if t['phase'] == 1]:
        origin = previous if task['budget'] in old.planner.BUDGETS else Path(ep['output_root'])
        src = origin / task['id']
        # Copy published artifacts without editing originals; independent hashes
        # and audits are checked again after copying by select_grid.
        shutil.copytree(src, root / task['id'])
        sources[task['id']] = dict(path=str(src), publication_sha256=old.c.digest(src / 'publication.json'))
    old.c.write(root / 'discovery_sources.json', sources)
    rows = old.select_grid(root, graph, arrays, ids, settings, write=True)
    old.c.write(root / 'grid_summary.json', dict(candidates=138, selected_rows=len(rows),
        source_map_sha256=old.c.digest(root / 'discovery_sources.json'), identity_sha256=old.c.digest(root / 'identity.json'),
        grid_publication_sha256=old.c.digest(root / 'grid_selection/publication.json')))
    print('PASS138 discovery snapshot and shared rows', len(rows), flush=True)


def read_grid(release, record, graph, root, arrays, ids, settings):
    old.c.require(old.c.read(root / 'identity.json') == identity(release, record), 'run identity')
    summary = old.c.read(root / 'grid_summary.json')
    sources = old.c.read(root / 'discovery_sources.json')
    old.c.require(set(sources) == set(graph['grid_selection']['candidate_pool']), 'source coverage')
    old.c.require(summary['source_map_sha256'] == old.c.digest(root / 'discovery_sources.json')
        and summary['identity_sha256'] == old.c.digest(root / 'identity.json')
        and summary['grid_publication_sha256'] == old.c.digest(root / 'grid_selection/publication.json'), 'snapshot metadata')
    ep, er, eg, previous = e.check(DISCOVERY_RELEASE)
    for task in [t for t in graph['tasks'] if t['phase'] == 1]:
        src = (previous if task['budget'] in old.planner.BUDGETS else Path(ep['output_root'])) / task['id']
        old.c.require(sources[task['id']] == dict(path=str(src), publication_sha256=old.c.digest(src / 'publication.json')),
                      'source identity')
        old.c.require(old.c.digest(root / task['id'] / 'publication.json') == sources[task['id']]['publication_sha256'],
                      'copied publication identity')
    rows = old.select_grid(root, graph, arrays, ids, settings)
    old.c.require(summary['candidates'] == 138 and summary['selected_rows'] == len(rows), 'grid counts')
    return rows


def execute(release, index):
    p, r, graph, root = check(release)
    old.c.d.full.check_allocation(r['route'])
    tasks = [t for t in graph['tasks'] if t['phase'] == 2]
    old.c.require(index is not None and 0 <= index < len(tasks), 'array index')
    arrays, ids, settings = old.load_data()
    rows = read_grid(release, r, graph, root, arrays, ids, settings)
    old.c.require(shutil.disk_usage(root).free > 32 * 1024**3, 'free storage')
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
        old.solve(tasks[index], root, graph, arrays, ids, settings, rows, env)
    print('PASS', tasks[index]['id'], 'final user review required', flush=True)


def validate(release):
    p, r, graph, root = check(release)
    before = {str(f.relative_to(root)): old.c.digest(f) for f in root.rglob('*') if f.is_file()}
    arrays, ids, settings = old.load_data()
    rows = read_grid(release, r, graph, root, arrays, ids, settings)
    reports = [old.audit_task(t, root, graph, arrays, ids, settings, rows)
               for t in graph['tasks'] if t['phase'] == 2]
    old.c.require(len(reports) == 414, 'selected coverage')
    old.c.require(before == {str(f.relative_to(root)): old.c.digest(f) for f in root.rglob('*') if f.is_file()},
                  'readback changed artifacts')
    return reports


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['grid', 'run', 'validate'])
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--index', type=int)
    args = parser.parse_args()
    if args.action == 'grid':
        prepare_grid(args.release)
    elif args.action == 'run':
        execute(args.release, args.index)
    else:
        validate(args.release)
        print('PASS414 selected fits; final user review required')
