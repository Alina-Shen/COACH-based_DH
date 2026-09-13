"""Read-only dependency bridge for the existing isolated SCIP venv."""
import importlib.abc
import sys
from pathlib import Path


class NoGurobi(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'gurobipy' or fullname.startswith('gurobipy.'):
            raise ImportError('Gurobi is forbidden in the SCIP alternative process')
        return None


def bootstrap():
    sys.dont_write_bytecode = True
    if 'gurobipy' in sys.modules:
        raise RuntimeError('SCIP alternative must run in a fresh Gurobi-free process')
    sys.meta_path.insert(0, NoGurobi())
    # The SCIP venv uses dh's Python3.11. Reuse missing pure-Python/readback
    # dependencies from dh AFTER its own site-packages; do not alter either env.
    fallback = Path('/global/home/users/yaoshen/.conda/envs/dh/lib/python3.11/site-packages')
    if str(fallback) not in sys.path:
        sys.path.append(str(fallback))
