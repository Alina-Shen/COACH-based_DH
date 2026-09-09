"""Fail-closed Slurm feeder; operational only, never changes frozen chemistry.

An intent is durable BEFORE sbatch. An uncertain response requires human
reconciliation, never a blind retry. A singleton lock spans the whole process.
All of yaoshen's expanded queue tasks count, including other projects.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROUTES = {'cm1': ('lr_qchem', 'condo_qchem'), 'mhg': ('mhg', 'normal'),
          'lr8': ('lr_mhg2', 'mhg2_lr8_normal'), 'lr7': ('lr_mhg2', 'condo_mhg_lr7')}
ACTIVE = {'PENDING', 'RUNNING', 'CONFIGURING', 'COMPLETING', 'SUSPENDED',
          'RESIZING', 'REQUEUED', 'REQUEUE_FED', 'REQUEUE_HOLD', 'SIGNALING',
          'STAGE_OUT', 'SPECIAL_EXIT'}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def command(argv, timeout=45):
    result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    require(result.returncode == 0, f'{argv[0]} failed: {result.stderr.strip()}')
    return result.stdout, result.stderr


def queue_rows(text):
    rows = {}
    for line in text.splitlines():
        fields = line.strip().split('|')
        require(len(fields) == 4 and re.fullmatch(r'\d+(?:_\d+)?(?:\+\d+)?', fields[0]),
                'Unexpanded/malformed queue: refusing to undercount')
        require(fields[0] not in rows and fields[1] in ACTIVE,
                'Duplicate/unknown scheduler queue record')
        rows[fields[0]] = dict(zip(('state', 'name', 'partition'), fields[1:]))
    return rows


def queue():
    return queue_rows(command(['squeue', '-u', 'yaoshen', '-h', '-r',
                               '-o', '%i|%T|%j|%P'])[0])


def room(rows, jobs, limit=998):
    # Reserve invisible, not-yet-accounted tasks against Slurm visibility lag.
    invisible = sum(f"{j['job_id']}_{i}" not in rows and i not in j['completed']
                    for j in jobs for i in j['indices'])
    return max(0, limit - len(rows) - invisible)


def remaining(record, jobs):
    used = {i for j in jobs if j['record'] == record['name'] for i in j['indices']}
    return [i for i in range(record['species']) if i not in used]


def eligible_records(campaign, state):
    gateway = next(r for r in campaign['records'] if r['name'] == 'ecp21_gateway')
    done = sum(len(j['completed']) for j in state['jobs'] if j['record'] == gateway['name'])
    if done != gateway['species']:
        return [gateway]
    return sorted((r for r in campaign['records'] if r != gateway),
                  key=lambda r: (-r['memory_gib'], r['name']))


def publication(record, index):
    case = record['cases'][index]
    root = Path(record['output_root']) / case['species']
    require((root / 'GENERATION_COMPLETE').read_text().strip() == 'complete',
            f'Missing completion marker: {root}')
    require(read(root / 'identity.json') == {'plan_sha256': record['plan_sha256'],
                                           'species': case['species']}, 'Publication identity mismatch')
    species = read(root / 'species.json')
    require(species['plan_sha256'] == record['plan_sha256'] and
            species['species'] == case['species'] and
            species['specification_sha256'] == record['specification_sha256'], 'Wrong publication')
    required = {'ready/feature_vector_292.npy', 'ready/fixed_energy.json',
                'ready/scalar_values.json', 'ready/grid_difference_99590.npy',
                'ready/grid_difference_75302.npy'}
    require(set(species['artifacts']) == required, 'Unexpected artifact set')
    for relative, expected in species['artifacts'].items():
        require(digest(root / relative) == expected, f'Artifact hash mismatch: {root / relative}')


def reconcile(campaign, state, rows):
    records = {r['name']: r for r in campaign['records']}
    unsettled = [j for j in state['jobs'] if len(j['completed']) < len(j['indices'])]
    for offset in range(0, len(unsettled), 50):
        group = unsettled[offset:offset + 50]
        if not group:
            continue
        output = command(['sacct', '-j', ','.join(j['job_id'] for j in group), '-nP',
                          '--format=JobID%80,State%40,ExitCode'])[0]
        accounting = {}
        for line in output.splitlines():
            fields = line.split('|')
            require(len(fields) >= 3, 'Malformed accounting response')
            if re.fullmatch(r'\d+_\d+', fields[0]):
                accounting[fields[0]] = (fields[1].split()[0], fields[2])
        for job in group:
            for index in job['indices']:
                if index in job['completed']:
                    continue
                task = f"{job['job_id']}_{index}"
                status, exit_code = accounting.get(task, ('UNKNOWN', ''))
                require(status in ACTIVE | {'UNKNOWN', 'COMPLETED'},
                        f'{task}: {status} {exit_code}; no automatic retry')
                if task not in rows and status == 'COMPLETED':
                    require(exit_code == '0:0', f'{task}: nonzero exit {exit_code}')
                    publication(records[job['record']], index)
                    job['completed'].append(index)
                elif task not in rows and status == 'UNKNOWN':
                    # A short accounting delay reserves capacity. A long one stops.
                    require(time.time() - job['submitted_epoch'] < 900,
                            f'{task}: absent from both queue and accounting for >15 minutes')


def sbatch_args(campaign, record, partition, indices, sequence):
    require(partition in ROUTES and partition in record['releases'], 'Unapproved route')
    account, qos = ROUTES[partition]
    return ['sbatch', '--parsable', '--no-requeue', '--nodes=1', '--ntasks=1',
            '--partition=' + partition, '--account=' + account, '--qos=' + qos,
            '--cpus-per-task=' + str(record['cpus']), '--mem=' + str(record['memory_gib']) + 'G',
            '--time=' + str(record['wall_hours']) + ':00:00',
            '--array=' + ','.join(map(str, indices)),
            '--job-name=' + campaign['job_prefix'] + f'{sequence:04d}',
            campaign['launcher'], record['releases'][partition]['path'], record['plan']]


def choose_route(campaign, record, indices, sequence, rows):
    # Slurm's own prospective starts are estimates, not promises. Test each
    # reviewed route with unchanged CPU/memory/time requests and exact array.
    candidates = []
    diagnostics = {}
    for partition in record['releases']:
        argv = sbatch_args(campaign, record, partition, indices, sequence)
        result = subprocess.run(argv[:1] + ['--test-only'] + argv[1:],
                                capture_output=True, text=True, timeout=45)
        output = result.stdout + result.stderr
        diagnostics[partition] = {'returncode': result.returncode, 'output': output}
        require(result.returncode == 0, f'Route test failed for {partition}: {output}')
        match = re.search(r'to start at (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', output)
        require(match is not None, f'No trustworthy start estimate for {partition}: {output}')
        eta = dt.datetime.fromisoformat(match[1]).timestamp()
        pending = sum(r['partition'] == partition and r['state'] == 'PENDING' for r in rows.values())
        candidates.append((eta, pending, list(ROUTES).index(partition), partition))
    return min(candidates)[-1], diagnostics


def submit(campaign, state, state_path, record, partition, indices, diagnostics):
    require(state.get('intent') is None and not state.get('halted'), 'Unresolved submission/halt')
    require(indices and not (set(indices) - set(remaining(record, state['jobs']))), 'Duplicate/invalid tasks')
    require(not (state_path.parent / 'STOP').exists(), 'STOP requested')
    live = queue()  # Last read immediately before durable intent and actual sbatch.
    require(len(indices) <= room(live, state['jobs'], campaign['active_limit']), 'Queue changed: capacity insufficient')
    sequence = len(state['jobs'])
    argv = sbatch_args(campaign, record, partition, indices, sequence)
    state['intent'] = {'record': record['name'], 'indices': indices, 'partition': partition,
                       'argv': argv, 'route_tests': diagnostics, 'epoch': time.time()}
    save(state_path, state)
    stdout, stderr = command(argv)
    require(re.fullmatch(r'\d+(?:;[A-Za-z0-9_.-]+)?', stdout.strip()) is not None,
            'Ambiguous sbatch response: preserve intent and reconcile manually')
    state['jobs'].append(dict(state['intent'], job_id=stdout.strip().split(';')[0],
                              completed=[], submitted_epoch=time.time(), stderr=stderr))
    state['intent'] = None
    save(state_path, state)


def run(campaign_path, expected_hash, state_root):
    require(digest(campaign_path) == expected_hash, 'Campaign changed')
    campaign = read(campaign_path)
    require(campaign['active_limit'] == 998 and campaign['user'] == 'yaoshen', 'Wrong cap/user')
    require(digest(__file__) == campaign['controller_sha256'], 'Controller changed')
    state_root = Path(state_root)
    state_root.mkdir(parents=True, exist_ok=True)
    with (state_root / 'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        path = state_root / 'state.json'
        state = read(path) if path.exists() else {'campaign_sha256': expected_hash, 'jobs': [], 'intent': None}
        require(state['campaign_sha256'] == expected_hash, 'Wrong persistent state')
        require(not state.get('intent') and not state.get('halted'), 'Manual reconciliation required; not restarting')
        try:
            while True:
                require(not (state_root / 'STOP').exists(), 'STOP requested; running jobs untouched')
                require(digest(campaign_path) == expected_hash and
                        digest(__file__) == campaign['controller_sha256'], 'Controller/campaign changed')
                for p, h in campaign['guard_hashes'].items():
                    require(digest(p) == h, 'Frozen authority changed: ' + p)
                rows = queue()
                require(len(rows) <= campaign['active_limit'], 'All-user queue exceeds 998; submissions halted')
                reconcile(campaign, state, rows)
                state.update(heartbeat=dt.datetime.now().astimezone().isoformat(),
                             host=os.uname().nodename, pid=os.getpid(), active_all_user=len(rows),
                             submitted=sum(len(j['indices']) for j in state['jobs']),
                             completed=sum(len(j['completed']) for j in state['jobs']))
                save(path, state)
                print(json.dumps({k: state[k] for k in ('heartbeat', 'active_all_user', 'submitted', 'completed')}), flush=True)
                if state['completed'] == campaign['total_species']:
                    state['finished'] = True
                    save(path, state)
                    return
                candidates = eligible_records(campaign, state)
                available = room(rows, state['jobs'], campaign['active_limit'])
                for record in candidates:
                    indices = remaining(record, state['jobs'])[:min(32, available)]
                    if indices:
                        partition, tests = choose_route(campaign, record, indices, len(state['jobs']), rows)
                        submit(campaign, state, path, record, partition, indices, tests)
                        print(f"Submitted {state['jobs'][-1]['job_id']}: {record['name']} {indices} on {partition}", flush=True)
                        break
                # One transaction per poll: no burst, and fresh accounting before
                # every refill. This is a submission rate, NOT a running-task cap.
                time.sleep(campaign['poll_seconds'])
        except BaseException as error:
            state['halted'] = f'{type(error).__name__}: {error}'
            state['heartbeat'] = dt.datetime.now().astimezone().isoformat()
            save(path, state)
            print('HALTED: ' + state['halted'], flush=True)
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--state-root', type=Path, required=True)
    args = parser.parse_args()
    run(args.campaign, args.sha256, args.state_root)
