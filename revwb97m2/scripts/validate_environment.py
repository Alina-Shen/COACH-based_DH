#!/usr/bin/env python3
"""Validate the pinned revwb97m2 Python environment and Gurobi license."""

from __future__ import annotations

import importlib.metadata as metadata
import json
import sys
from pathlib import Path

import basis_set_exchange
import dftd4
import gurobipy as gp
import h5py
import numpy
import pandas
import pyscf
import pytest
import scipy
import yaml
from pyscf import dft


EXPECTED = {
    "basis-set-exchange": "0.12",
    "coach-workflow": "0.1.0",
    "dftd4": "4.2.0",
    "gurobipy": "13.0.3",
    "h5py": "3.16.0",
    "numpy": "2.4.6",
    "pandas": "3.0.5",
    "pyscf": "2.14.0",
    "pytest": "9.1.1",
    "PyYAML": "6.0.3",
    "scipy": "1.17.1",
}
EXPECTED_PYTHON = (3, 11, 15)
EXPECTED_LIBXC = "7.0.0"
EXPECTED_PROJECT_ROOT = Path(__file__).resolve().parents[2] / "coach"


def main() -> int:
    checks = {
        "python_version": sys.version_info[:3] == EXPECTED_PYTHON,
        "package_versions": all(metadata.version(name) == version for name, version in EXPECTED.items()),
        "libxc_version": dft.libxc.__version__ == EXPECTED_LIBXC,
    }

    distribution = metadata.distribution("coach-workflow")
    direct_url = Path(distribution._path) / "direct_url.json"
    direct = json.loads(direct_url.read_text(encoding="utf-8"))
    project_path = Path(direct["url"].removeprefix("file://")).resolve()
    checks["editable_project_install"] = direct.get("dir_info", {}).get("editable") is True
    checks["editable_project_root"] = project_path == EXPECTED_PROJECT_ROOT

    model = gp.Model("revwb97m2_environment_license_probe")
    model.Params.OutputFlag = 0
    variable = model.addVar(lb=0.0, ub=1.0, name="x")
    model.setObjective(variable, gp.GRB.MAXIMIZE)
    model.optimize()
    checks["gurobi_license_and_solver"] = (
        model.Status == gp.GRB.OPTIMAL and abs(variable.X - 1.0) <= 1.0e-12
    )

    report = {
        "passed": all(checks.values()),
        "checks": checks,
        "python": sys.version,
        "libxc": dft.libxc.__version__,
        "packages": {name: metadata.version(name) for name in EXPECTED},
        "editable_project_root": str(project_path),
        "gurobi": {
            "version": gp.gurobi.version(),
            "status": model.Status,
            "objective": model.ObjVal,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
