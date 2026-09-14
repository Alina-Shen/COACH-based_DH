import json
from concurrent.futures import ThreadPoolExecutor
import pytest
from .policy import ROUTES, allocation, dependency, pending_targets
from .leases import Ledger, occupied
from .adapter import checked_authorization


@pytest.mark.parametrize('partition', list(ROUTES))
def test_allowed_routes(partition):
    account, qos = ROUTES[partition]
    env = dict(SLURM_JOB_PARTITION=partition, SLURM_JOB_ACCOUNT=account,
               SLURM_JOB_QOS=qos, SLURM_JOB_ID='100', SLURM_CPUS_PER_TASK='16', SLURM_MEM_PER_NODE='32768')
    assert allocation(env)['partition'] == partition
    for key, value in [('SLURM_JOB_QOS', 'lr_lowprio'), ('SLURM_CPUS_PER_TASK', '8'),
                       ('SLURM_MEM_PER_NODE', '16384'), ('SLURM_JOB_ACCOUNT', 'wrong')]:
        with pytest.raises(ValueError):
            allocation({**env, key: value})


def test_only_pending_target_project():
    rows = [dict(array='25801134', name='r2_discovery_ext', state=s, index=i)
            for i,s in enumerate(['RUNNING', 'PENDING', 'COMPLETED'])]
    rows += [dict(array='25837199', name='coach_s10_high', state='RUNNING', index=0)]
    assert pending_targets(rows, '25801134') == [1]
    with pytest.raises(ValueError): pending_targets(rows, '25837199')


def test_phase_dependencies_fail_closed():
    assert dependency('audit', terminal_jobs=['1','2']) == 'afterany:1:2'
    assert dependency('build', validated='3') == 'afterok:3'
    assert dependency('grid', validated='3', build='4') == 'afterok:3:4'
    assert dependency('selected', validated='3', build='4', grid='5') == 'afterok:3:4:5'
    for kind in ('audit', 'build', 'grid', 'selected'):
        with pytest.raises(ValueError): dependency(kind)


def test_global_capacity_atomic(tmp_path):
    ledger = Ledger(tmp_path)
    with ThreadPoolExecutor(max_workers=12) as pool:
        accepted = list(pool.map(lambda n: ledger.acquire(str(n), now=0), range(40)))
    assert sum(accepted) == 20


def test_legacy_cooldown_and_crash_fail_closed(tmp_path):
    ledger = Ledger(tmp_path)
    ledger.seed_legacy(['old_'+str(i) for i in range(3)])
    assert sum(ledger.acquire('new_'+str(i), now=0) for i in range(20)) == 17
    ledger.close('old_0', now=100)
    assert not ledger.acquire('early', now=429)
    assert ledger.acquire('after_expiry', now=430)
    assert not ledger.acquire('crashed_owner_not_expired', now=1000000)
    with pytest.raises(ValueError): ledger.seed_legacy([])


def test_duplicate_owner_is_not_double_counted(tmp_path):
    ledger = Ledger(tmp_path)
    assert ledger.acquire('one', now=0)
    with pytest.raises(ValueError): ledger.acquire('one', now=1)
    ledger.close('one', now=2)
    with pytest.raises(ValueError): ledger.close('one', now=3)


def test_unreleased_authorization_rejected(tmp_path):
    path = tmp_path/'draft.json'
    path.write_text(json.dumps(dict(released=False, capacity=20)))
    with pytest.raises(ValueError, match='not authorized'): checked_authorization(path)


def test_unknown_routes_rejected():
    with pytest.raises(ValueError): allocation({'SLURM_JOB_PARTITION':'lr6'})


def test_expiry_boundary():
    assert occupied({'closed':10}, 339)
    assert not occupied({'closed':10}, 340)
    assert occupied({'closed':None}, 1000000)


@pytest.mark.parametrize('solve_fails', [False, True])
def test_adapter_disposes_before_cooldown(tmp_path, monkeypatch, solve_fails):
    import sys
    from types import SimpleNamespace
    from . import adapter
    from revwb97m2 import discovery_extension_v1 as e
    output = tmp_path/'outputs'
    auth_path = tmp_path/'authorization.json'
    auth_path.write_text('{}')
    auth = dict(indices={'discovery':[0]}, ledger=str(tmp_path/'ledger'), receipts=str(tmp_path/'receipts'))
    monkeypatch.setattr(adapter, 'checked_authorization', lambda path: auth)
    for key, value in dict(SLURM_JOB_PARTITION='lr7', SLURM_JOB_ACCOUNT='lr_mhg2',
            SLURM_JOB_QOS='condo_mhg_lr7', SLURM_JOB_ID='123', SLURM_CPUS_PER_TASK='16',
            SLURM_MEM_PER_NODE='32768').items():
        monkeypatch.setenv(key, value)
    license_path = tmp_path/'dummy.lic'
    license_path.write_text('WLSACCESSID=dummy\nWLSSECRET=dummy\nLICENSEID=1\n')
    monkeypatch.setenv('GRB_LICENSE_FILE', str(license_path))
    task = {'id':'test_task'}
    monkeypatch.setattr(e, 'check', lambda path: (dict(output_root=str(output), additional_tasks=[task]),
                        dict(commit='test'), {}, None))
    monkeypatch.setattr(e.old, 'load_data', lambda: ({}, [], None))
    events = []
    class Env:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def setParam(self, key, value):
            if key == 'WLSTokenDuration': assert value == 5
        def start(self): events.append('opened')
        def __exit__(self, *args): events.append('disposed')
    monkeypatch.setitem(sys.modules, 'gurobipy', SimpleNamespace(Env=Env))
    def solve(task, root, graph, arrays, ids, settings, rows, env):
        assert len(rows) == 0
        assert events == ['opened']
        if solve_fails: raise RuntimeError('synthetic solve failure')
    monkeypatch.setattr(e.old, 'solve', solve)
    if solve_fails:
        with pytest.raises(RuntimeError, match='synthetic'): adapter.run(auth_path, 'discovery', 0)
    else:
        adapter.run(auth_path, 'discovery', 0)
    assert events == ['opened', 'disposed']
    state = json.loads((tmp_path/'ledger/leases.json').read_text())
    assert state['123:discovery:0']['closed'] is not None
    receipt = json.loads((tmp_path/'receipts/discovery_0.json').read_text())
    assert receipt['actual_route']['partition'] == 'lr7'
    execution = json.loads((output/'test_task.execution.json').read_text())
    assert execution['dispatch_receipt'].endswith('discovery_0.json')
