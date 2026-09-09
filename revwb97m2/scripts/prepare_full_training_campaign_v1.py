"""Prepare immutable operational releases after committed scientific checks.

Does not submit jobs or modify old plans. Runtime still performs the original
release checks on every compute task. CPU/memory/time remain frozen.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess

from revwb97m2.scripts import generate_training_features_v3 as g
from revwb97m2.scripts import full_training_feeder_v1 as f


def prepare(destination):
    root = g.ROOT.parent
    summary_path = g.ROOT / 'manifests/full_training_execution_v1/summary.json'
    summary = f.read(summary_path)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    f.require(commit == '50e3b7a56fc9f18cf38b31812c1704305bb7e45d', 'Unexpected execution commit')
    f.require(not destination.exists(), 'Refuse to overwrite existing campaign')
    f.require(summary['passed'] and summary['generation_species'] == 2569, 'Wrong selection')
    # Live review: accounts/QOS and unlimited partition walltimes were inspected
    # separately. These physical ceilings are verified anew here, not assumed.
    nodes = f.command(['sinfo', '-N', '-p', 'cm1,mhg,lr8,lr7', '-h', '-o', '%P|%m|%c|%t'])[0]
    capacities = {p: [] for p in f.ROUTES}
    for line in nodes.splitlines():
        partition, memory, cpus, state = line.split('|')
        if not any(bad in state.lower() for bad in ('down', 'drain', 'maint', 'fail')):
            capacities[partition.rstrip('*')].append((int(memory), int(cpus)))
    g.corrected.validate_registry()
    print('Corrected seven-canary evidence PASS', flush=True)
    records, guards = [], {str(summary_path): f.digest(summary_path)}
    seen = set()
    for record in summary['records']:
        plan_path = Path(record['plan'])
        f.require(f.digest(plan_path) == record['plan_sha256'], 'Frozen plan changed')
        plan, _ = g.load(plan_path)
        f.require(not Path(plan['output_root']).exists() and not Path(plan['scratch_root']).exists(),
                  'Execution namespace already exists: investigate duplicates')
        for path, hash_value in dict(plan['code_hashes'], **{str(plan_path): record['plan_sha256']}).items():
            guards[path] = hash_value
            try:
                relative = str(Path(path).relative_to(root))
            except ValueError:
                continue
            content = subprocess.check_output(['git', 'show', commit + ':' + relative], cwd=root)
            f.require(g.hashlib.sha256(content).hexdigest() == hash_value, 'Uncommitted production authority')
        names = [c['species'] for c in plan['cases']]
        f.require(not seen.intersection(names) and len(names) == record['species'], 'Duplicate/wrong coverage')
        seen.update(names)
        candidates = [p for p, nodes in capacities.items() if any(
            memory > record['memory_gib'] * 1024 and cpus >= record['cpus'] for memory, cpus in nodes)]
        f.require(candidates, 'No physical route for ' + record['name'])
        releases = {}
        for partition in candidates:
            release_path = destination / f"{record['name']}_{partition}_release.json"
            release = f.read(plan_path.with_name(record['name'] + '_release_draft.json'))
            account, qos = f.ROUTES[partition]
            release.update(user_approved_submission=True, resource_review_passed=True,
                           commit=commit, ecp_native_gateway_authorized=record['name'] == 'ecp21_gateway',
                           active_all_user_task_limit=998,
                           scheduler_routes={n: {'partition': partition, 'account': account, 'qos': qos} for n in names})
            g.reviewed_routes(plan, release)
            releases[partition] = {'path': str(release_path), 'content': release}
        records.append(dict(record, releases=releases, output_root=plan['output_root'],
                            specification_sha256=plan['specification_sha256'],
                            cases=[{'species': n} for n in names]))
        print('Committed contract PASS:', record['name'], candidates, flush=True)
    f.require(len(seen) == 2569, 'Wrong campaign size')
    free = min(g.native.available_bytes(g.native.DATA), g.native.available_bytes(g.native.SCRATCH))
    f.require(free > summary['total_minimum_copy_bytes'] + 557 * 1024**3, 'Insufficient storage')
    f.require(not f.queue(), 'Initial user queue is no longer empty; review before first release')
    destination.mkdir(parents=True)
    for record in records:
        for release in record['releases'].values():
            f.save(release['path'], release.pop('content'))
            release['sha256'] = f.digest(release['path'])
            guards[release['path']] = release['sha256']
    campaign = dict(schema_version=1, created=dt.datetime.now().astimezone().isoformat(),
                    production_commit=commit, user='yaoshen', active_limit=998,
                    poll_seconds=60, transaction_tasks=32, total_species=2569,
                    gateway='ecp21_gateway', job_prefix='r2f26_',
                    controller_sha256=f.digest(f.__file__),
                    launcher=str(g.ARRAY_LAUNCHER), guard_hashes=guards, records=records,
                    resource_snapshot=nodes, free_bytes=free,
                    policy='ECP21 native completion/publication gate; automatic remainder; no retries; no lr_lowprio')
    f.save(destination / 'campaign.json', campaign)
    print('CAMPAIGN', destination / 'campaign.json', f.digest(destination / 'campaign.json'), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path, required=True)
    prepare(p.parse_args().destination)
