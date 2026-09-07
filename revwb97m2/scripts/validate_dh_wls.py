#!/usr/bin/env python3
"""Compute-node environment/WLS check; never emit license values or errors."""
from __future__ import annotations

import importlib.metadata as metadata
import json
import os
from pathlib import Path
import socket
import sys

import gurobipy as gp
from pyscf import dft

from validate_environment import (
    EXPECTED, EXPECTED_LIBXC, EXPECTED_PROJECT_ROOT, EXPECTED_PYTHON,
)


def main() -> int:
    report = {"hostname": socket.gethostname(), "job_id": os.getenv("SLURM_JOB_ID"),
              "python_executable": sys.executable, "checks": {}}
    checks = report["checks"]
    try:
        checks["compute_allocation"] = bool(report["job_id"])
        checks["dh_prefix"] = Path(sys.prefix) == Path("/global/home/users/yaoshen/.conda/envs/dh")
        checks["python_version"] = sys.version_info[:3] == EXPECTED_PYTHON
        versions = {name: metadata.version(name) for name in EXPECTED}
        report["packages"] = versions
        checks["package_versions"] = versions == EXPECTED
        checks["libxc_version"] = dft.libxc.__version__ == EXPECTED_LIBXC
        direct = json.loads(metadata.distribution("coach-workflow").read_text("direct_url.json"))
        checks["editable_project"] = (
            direct.get("dir_info", {}).get("editable") is True
            and Path(direct["url"].removeprefix("file://")).resolve() == EXPECTED_PROJECT_ROOT
        )
        license_path = Path(os.environ["GRB_LICENSE_FILE"])
        checks["private_license"] = license_path.stat().st_mode & 0o077 == 0
        # Read only the necessary WLS fields; never print values or raw exceptions.
        fields = {}
        for line in license_path.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() in {"WLSACCESSID", "WLSSECRET", "LICENSEID"}:
                fields[key.strip()] = value.strip()
        checks["wls_fields_present"] = set(fields) == {"WLSACCESSID", "WLSSECRET", "LICENSEID"}
        if not all(checks.values()):
            raise ValueError("preflight failed")
        # Explicit credentials prevent fallback to a local size-restricted license.
        with gp.Env(empty=True) as env:
            env.setParam("OutputFlag", 0)
            env.setParam("WLSACCESSID", fields["WLSACCESSID"])
            env.setParam("WLSSECRET", fields["WLSSECRET"])
            env.setParam("LICENSEID", int(fields["LICENSEID"]))
            env.start()
            with gp.Model("dh_wls_quadratic_probe", env=env) as model:
                model.Params.Threads = 1
                model.Params.TimeLimit = 30
                x = model.addVars(300, lb=0.0, ub=2.0)
                model.setObjective(gp.quicksum((x[i] - 1.0) ** 2 for i in range(300)))
                model.optimize()
                checks["wls_quadratic_solve"] = (
                    model.Status == gp.GRB.OPTIMAL
                    and abs(model.ObjVal) < 1e-6
                    and max(abs(x[i].X - 1.0) for i in range(300)) < 1e-5
                )
                report["solver"] = {"version": gp.gurobi.version(), "variables": 300,
                                    "status": model.Status, "objective": model.ObjVal}
    except Exception as exc:
        # Gurobi startup errors may include sensitive information: report only type/code.
        report["error_type"] = type(exc).__name__
        if isinstance(exc, gp.GurobiError):
            report["gurobi_error_code"] = exc.errno
        checks["execution"] = False
    report["passed"] = all(checks.values())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
