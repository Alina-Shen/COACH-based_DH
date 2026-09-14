"""Fail-closed shared WLS lease ledger; crashed owners require reconciliation."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import time

CAPACITY = 20
COOLDOWN = 330


def occupied(record, now):
    return record['closed'] is None or now < record['closed'] + COOLDOWN


class Ledger:
    def __init__(self, root):
        self.root = Path(root)

    @contextmanager
    def transaction(self):
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root/'lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            path = self.root/'leases.json'
            state = json.loads(path.read_text()) if path.exists() else {}
            yield state
            temp = self.root/('leases.'+str(os.getpid())+'.tmp')
            with temp.open('w') as stream:
                json.dump(state, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)

    def acquire(self, owner, now=None):
        now = time.time() if now is None else now
        with self.transaction() as state:
            if owner in state:
                raise ValueError('lease owner cannot be reused')
            if sum(occupied(r, now) for r in state.values()) >= CAPACITY:
                return False
            state[owner] = {'opened': now, 'closed': None}
            return True

    def close(self, owner, now=None):
        with self.transaction() as state:
            if state[owner]['closed'] is not None:
                raise ValueError('lease already closed')
            state[owner]['closed'] = time.time() if now is None else now

    def seed_legacy(self, owners):
        """Call under a migration hold; count running legacy jobs before new admission."""
        owners = list(owners)
        if len(owners) != len(set(owners)) or len(owners) > CAPACITY:
            raise ValueError('invalid legacy reservation list')
        with self.transaction() as state:
            if state:
                raise ValueError('ledger already initialized')
            for owner in owners:
                state[owner] = {'opened': time.time(), 'closed': None}
