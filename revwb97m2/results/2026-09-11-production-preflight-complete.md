# Committed production model/start preflight passed

## Actions and evidence

1. Verified clean starting commit `488dba7ac0129b375797ed8057a00ba210ab6063`. Full regression suite passed: **405 tests in 17.74 seconds**. Recorded the commit and frozen plan hash in `2026-09-11-production-committed-tests.json`.
2. Followed the partition skill's manual fallback because its bundled `partition_helper.py` does not exist. Live Slurm showed idle cm1 nodes with 48 CPUs/241732 MiB each; the user's cm1/lr_qchem/condo_qchem association was present. lr8 and mhg also had available capacity. Chose cm1 for this small preflight; no memory changes or low-priority route. The user had no active jobs at that snapshot.
3. Added an operational build-only harness and 15-minute Slurm wrapper in `revwb97m2/results/production_execution_preflight_20260911.{py,sh}`. Production code and frozen manifests were not changed. The harness verifies committed source identities, full inputs, graph and source25792248 readback before opening one quiet WLS session. No license values are printed.
4. Scheduler test-only check accepted the allocation. Submitted **25795805**, cm1/n0001.cm1, 16 CPUs/32 GiB. It **COMPLETED 0:0 in 56 seconds**. Batch sampled MaxRSS was92680K; this brief construction measurement is NOT an estimate of two-hour search memory.
5. Built eight models: K14/K80, ungridded/existing349-row grid, original/noisy simple starts. All retained584variables,292binaries,zeroSOS,590 or1288constraints,7200-second time limit and16threads. Assigned starts exactly, exported models and MST starts, reloaded them and verified coefficient roundtrip within serialization tolerance (rtol1e-14/atol1e-15), with exact binary start equality. This serialization check changes no scientific acceptance threshold.
6. Both ungridded original seeds were feasible. The noisy seeds and the original seeds on the existing selected grid were diagnostically infeasible, but all suggestions imported successfully. This is permitted by the approved COACH policy. No optimizer was called: solver repair/acceptance or fitting quality is not established by this test.
7. Verified completion/publication hashes, harness identity and all eight case summaries after completion. Gurobi version13.0.3. Kept reports/models/start files under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/production_preflight_v1/25795805`. No source artifacts changed.
8. Updated project notes and STATUS forward table. Production release draft remains unchanged with every release gate false.

## Scope and next action

The349rows are historical test fixtures, NOT the future production row set. Production still selects from all14 new discovery candidates. This preflight does not exercise the entire Slurm dependency chain or the future matching-K source publications; regression tests cover those guards.

Commit the new harness/evidence files. Before production release, confirm the WLS concurrent-session entitlement in the user's dashboard. A September6 note recommends at most two sessions but is not authoritative proof of license capacity. No capacity stress-test or assumption of42simultaneous licenses was made. The user was asked to provide only the limit, never credentials.

After capacity confirmation, prepare a resource-reviewed release and any required license-based array throttle, preserving the approved56solves,7200seconds/solve,16CPUs/32GiB per task,2h30m job limit,under999active tasks and no lr_lowprio. Any code change for throttling requires its own frozen identity/commit before launch. Explicit production authorization remains required. There is no need to repeat feature generation or introduce another scientific fitting experiment to resolve this administrative resource question.
