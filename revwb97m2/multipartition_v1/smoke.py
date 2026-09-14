"""Two-node shared-lock check and isolated real-data adapter/readback."""
import hashlib
import json
import os
from pathlib import Path
import socket
import time
from .adapter import DATA, ROOT, run
from .leases import Ledger


def sources():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
        [ROOT/'revwb97m2/multipartition_v1'/n for n in
         ('__init__.py','policy.py','leases.py','adapter.py','audit.py','run.sh','smoke_model.py')]}


if __name__ == '__main__':
    rank = int(os.environ['SLURM_PROCID'])
    root = DATA/'dispatch/activation_checks_v1'/os.environ['SLURM_JOB_ID']
    own = root/str(rank)
    own.mkdir(parents=True, exist_ok=False)
    ledger = Ledger(root/'shared_lock_test')
    accepted = [str(rank)+'_'+str(i) for i in range(20) if ledger.acquire(str(rank)+'_'+str(i))]
    (own/'lock.json').write_text(json.dumps({'host': socket.gethostname(), 'accepted': accepted}))
    deadline = time.monotonic()+120
    other = root/str(1-rank)/'lock.json'
    while not other.exists():
        if time.monotonic() > deadline: raise RuntimeError('peer lock check timeout')
        time.sleep(1)
    peer = json.loads(other.read_text())
    if peer['host'] == socket.gethostname() or len(accepted)+len(peer['accepted']) != 20:
        raise RuntimeError('cross-node locking failed')
    session_ledger = Ledger(own/'wls_ledger')
    session_ledger.seed_legacy([])
    auth = dict(released=True, purpose='smoke', capacity=20, migration_verified=False,
        ledger_initialized=True, indices={'discovery':[0], 'selected':[]}, source_hashes=sources(),
        ledger=str(own/'wls_ledger'), receipts=str(own/'receipts'),
        discovery_gate=str(own/'unused_gate.json'), smoke_root=str(own/'isolated_fit'))
    auth_path = own/'authorization.json'
    auth_path.write_text(json.dumps(auth, indent=2))
    run(auth_path, 'discovery', 0)
    (own/'passed.json').write_text(json.dumps({'passed':True, 'host':socket.gethostname(),
        'cross_node_capacity':20, 'real_adapter_readback':True, 'closed_epoch':time.time()}))
    print('PASS cross-node lock and real adapter/readback', rank, flush=True)
