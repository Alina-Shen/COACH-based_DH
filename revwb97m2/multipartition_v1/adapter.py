"""Additional route authorization; call frozen solve/readback, never spoof Slurm."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import numpy as np
from .leases import Ledger
from .policy import allocation

ROOT = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh')
DATA = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2')


def checked_authorization(path):
    auth = json.loads(path.read_text())
    if auth.get('released') is not True or auth.get('capacity') != 20:
        raise ValueError('dispatch release not authorized')
    if set(auth['source_hashes']) != {'revwb97m2/multipartition_v1/'+n for n in
            ('__init__.py', 'policy.py', 'leases.py', 'adapter.py', 'audit.py', 'run.sh', 'smoke_model.py')}:
        raise ValueError('incomplete dispatch source identity')
    for name, sha in auth['source_hashes'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != sha:
            raise ValueError('dispatch source changed')
    smoke = auth.get('purpose') == 'smoke'
    if not smoke and auth.get('baseline_confirmed') is not True:
        raise ValueError('unconfirmed WLS baseline for production dispatch')
    if (not smoke and not auth.get('migration_verified')) or not auth.get('ledger_initialized'):
        raise ValueError('migration/admission gate closed')
    if smoke and (auth['indices'] != {'discovery': [0], 'selected': []}
                  or DATA/'dispatch' not in Path(auth['smoke_root']).resolve().parents):
        raise ValueError('invalid isolated smoke authorization')
    for phase, size in (('discovery', 124), ('selected', 414)):
        indices = auth['indices'][phase]
        if (not isinstance(indices, list) or any(type(i) is not int or not 0 <= i < size for i in indices)
                or len(indices) != len(set(indices))):
            raise ValueError('invalid authorized task indices')
    for key in ('ledger', 'receipts', 'discovery_gate'):
        if DATA not in Path(auth[key]).resolve().parents:
            raise ValueError('dispatch data path outside project')
    if not (Path(auth['ledger'])/'leases.json').is_file():
        raise ValueError('initialized lease ledger missing; refuse fresh empty admission state')
    return auth


def run(authorization, phase, index):
    from revwb97m2 import discovery_extension_v1 as e, selected_full_v1 as s
    old = e.old
    auth = checked_authorization(authorization)
    route = allocation(os.environ)
    if phase not in ('discovery', 'selected') or index not in auth['indices'][phase]:
        raise ValueError('task outside dispatch authorization')
    release = ROOT / ('revwb97m2/manifests/' +
        ('discovery_extension_v1' if phase == 'discovery' else 'selected_full_v1') + '/release_20260911.json')
    job_key = (os.environ['SLURM_ARRAY_JOB_ID']+'_'+os.environ['SLURM_ARRAY_TASK_ID']
               if 'SLURM_ARRAY_JOB_ID' in os.environ else os.environ['SLURM_JOB_ID'])
    owner = job_key+':'+phase+':'+str(index)
    receipts = Path(auth['receipts'])
    receipts.mkdir(parents=True, exist_ok=True)
    receipt = receipts/(phase+'_'+str(index)+'.json')
    ledger = Ledger(auth['ledger'])
    # A launcher must bound admissions; do not consume an untracked WLS token.
    if auth.get('require_reserved_lease'):
        ledger.activate(owner)
    else:
        deadline = time.monotonic()+600
        while not ledger.acquire(owner):
            if time.monotonic() >= deadline:
                raise RuntimeError('WLS admission timeout; no license environment opened')
            time.sleep(10)
    try:
        p, record, graph, root = e.check(release) if phase == 'discovery' else s.check(release)
        if phase == 'discovery':
            root = Path(p['output_root'])
            task = p['additional_tasks'][index]
            if auth.get('purpose') == 'smoke':
                root = Path(auth['smoke_root'])
                task = {**task, 'seconds': 120}
        else:
            task = [t for t in graph['tasks'] if t['phase'] == 2][index]
            # Refuse a mere grid-file existence test: revalidate the full snapshot.
            gate = json.loads(Path(auth['discovery_gate']).read_text())
            if gate != {'passed': True, 'candidates': 138,
                        'dispatch_authorization_sha256': hashlib.sha256(authorization.read_bytes()).hexdigest()}:
                raise ValueError('discovery audit barrier not certified')
        launch = dict(authorization=str(authorization.resolve()),
            authorization_sha256=hashlib.sha256(authorization.read_bytes()).hexdigest(),
            actual_route=route, job=os.environ['SLURM_JOB_ID'], phase=phase, index=index,
            scientific_release=str(release), scientific_release_sha256=old.c.digest(release))
        old.c.write(receipt, launch)
        root.mkdir(parents=True, exist_ok=True)
        if phase == 'discovery':
            old.c.write(root/(task['id']+'.execution.json'), dict(release=str(release),
                release_sha256=old.c.digest(release), commit=record['commit'],
                plan_sha256=old.c.digest(e.PLAN), job=os.environ['SLURM_JOB_ID'],
                task=task['id'], dispatch_receipt=str(receipt)))
        arrays, ids, settings = old.load_data()
        rows = np.array([], dtype=int) if phase == 'discovery' else s.read_grid(
            release, record, graph, root, arrays, ids, settings)
        import gurobipy as gp
        fields = {}
        for line in Path(os.environ['GRB_LICENSE_FILE']).read_text().splitlines():
            key, sep, value = line.partition('=')
            if sep and key.strip() in ('WLSACCESSID','WLSSECRET','LICENSEID'):
                fields[key.strip()] = value.strip()
        with gp.Env(empty=True) as env:
            env.setParam('OutputFlag', 0)
            env.setParam('WLSTokenDuration', 5)
            for key, value in fields.items():
                env.setParam(key, int(value) if key == 'LICENSEID' else value)
            env.start()
            if auth.get('purpose') == 'smoke':
                from .smoke_model import solve
                solve(old, task, root, graph, arrays, ids, settings, rows, env)
            else:
                old.solve(task, root, graph, arrays, ids, settings, rows, env)
        if auth.get('purpose') == 'smoke':
            old.c.write(receipts/'smoke_pass.json', {'passed': True, 'job': os.environ['SLURM_JOB_ID']})
    finally:
        # After context-manager disposal, keep the slot occupied for expiry margin.
        ledger.close(owner)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorization', type=Path, required=True)
    parser.add_argument('--phase', choices=['discovery','selected'], required=True)
    parser.add_argument('--index', type=int, required=True)
    args = parser.parse_args()
    run(args.authorization, args.phase, args.index)
