# Separate SCIP pilot installed — 2026-09-13

## Work performed

1. Saved the prior answer verbatim in project notes, including its original final read-only statement (historical context, not this turn's action). Checked exact text equality with the project-owned source copy.
2. Created an isolated Python3.11 venv at `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/environments/scip_pilot_v1`. Existing environments and the frozen production specification were not changed.
3. Downloaded and retained binary wheels, then installed offline from them: PySCIPOpt6.2.1, NumPy2.4.6 and SciPy1.17.1. Runtime reports SCIP10.0.2 and SoPlex8.0.2. No license application/key/server was needed.
4. Recorded pinned requirements, hash-checked reinstall requirements, wheel/library hashes, interpreter identity and dependency/version output. `pip check` passes. The Python wheel loader resolves bundled Fortran libraries; a direct standalone ldd initially lacked that loader path, and a second recorded ldd with the wheel library path resolves all dependencies. The external-library list includes SoPlex, CppAD, zlib, TinyCThread, AMPL/MP, Nauty, sassy and Ipopt; no Gurobi backend used. Full redistribution packaging of third-party notices is future release work.
5. Configured the separate pilot envelope to mirror current Gurobi: 16 CPUs and32GiB per fit,7200s solver time,2h30m scheduler limit, at most2 concurrent fits (32 CPUs/64GiB total). The concurrency cap is a resource policy, not a license restriction. These are recorded defaults for future job/adapter implementation, not an active submitted fitting array.
6. Verified SCIP accepts the pilot time/memory/relative-gap1e-4/absolute-gap1e-10/feasibility1e-9/thread-ceiling parameters. `parallel/maxnthreads=16` does not make ordinary optimize automatically use16 threads; parallel strategy needs benchmarking later. Existing independent Step9 acceptance remains authoritative.
7. Ran a tiny mixed-integer quadratic epigraph test with a known optimum: binary z=1, x≈2, independently recomputed objective0.1. Tightened gap targets to zero for this tiny certification test only. Earlier smoke attempts exposed an API method-name mismatch and an overly strict optimal-status assertion under pilot gap stopping; both are documented in retained logs. Final smoke passes with status optimal. Reported objective≈0.09999999910 differs by about9e-10, reinforcing the need for independent feasibility/objective audits.
8. Verified hashes and loaded all ten existing Step8 292-column feature/grid-difference arrays in the new environment. No Q-Chem reruns or production fits were performed. No Gurobi comparison was run; the user will compare with revwb97m(2) later.
9. Updated project notes, STATUS, progress and plan annotations while preserving step numbering. Installation is complete; the full fitting adapter/backend validation remains Step14 work. Step10 resource measurements remain separately tracked.

## Usage and evidence

Python executable: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/environments/scip_pilot_v1/bin/python`.

Smoke command from workspace root: `<python> -B coach_mp2/scripts/check_scip_pilot.py` (tiny installation test, not production).

[Budget/config](../configs/scip_pilot_v1.json) · [Validation](scip_pilot_install_validation.json) · [Installation manifest](../manifests/scip_pilot_install_v1.json) · [Hashed requirements](../configs/scip_pilot_requirements_hashed_v1.txt)
