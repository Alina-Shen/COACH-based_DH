# Full1498 bounded MIO tested and submitted — September 11, 2026

## Checks and release

- Verified clean implementation commit `ccfcad8a2d4f0c748d492cf8a98bdbe3451f0ae2`.
- Full suite: **267 passed in13.07s**, including11 new full-data orchestration
  cases. Frozen plan/code check passed. No fixes or production source edits needed.
- Fresh full1498 numerical/input preflight passed: all sources and identities,
  original weights/targets/roles, finite arrays and exact100 pilot rows. Evidence:
  [preflight](./2026-09-11-full1498-mio-preflight.json) and
  [test record](./2026-09-11-full1498-mio-tests.json).
- `$partition` helper was absent at its documented scripts/partition_helper.py
  path. Used direct live sinfo/sacctmgr/scontrol and sbatch --test-only instead.
  cm1 had five fully idle48CPU/241732MiB nodes; mhg also had idle nodes; lr8
  was mostly allocated with some mixed nodes. Chosecm1's available allocation
  and existing matching committed route, not a promised globally optimal wait.
  Confirmed lr_qchem/condo_qchem association, partition UP/unlimited walltime,
  and idle n0001.cm1 with217713MiB reported free.32GiB request fits physical
  memory strictly. Never used lr_lowprio; launcher unchanged.
- Scheduler dry-run predicted immediatecm1 placement. User queue was empty
  immediately before submission; below998 active-task limit. Storage reported
  ~2.5PiB available and existing log directory. Slurm socket sandbox denials
  were handled by approved escalated calls, not by changing job settings.
- Created separate enabled operational release
  `manifests/full1498_mio_v1/release_20260911.json` pointing to committed code/plan
  and passing test evidence. check_release verified every frozen file against
  the commit. Preserved disabled draft and historical proposal unchanged.

## Submission and scope

Submitted **25778194** at00:11:12PDT, started00:11:13 on **n0001.cm1**.
Routecm1/lr_qchem/condo_qchem;16CPUs/32GiB/90min. Slurm deadline01:41:13PDT.
The dry-run's displayed job number was only a test prediction, not a second job.

The job first runs matrix checks and synthetic control, then six serial real
solves K14/K80 discovery/constrained/restart with600s caps. It stops on failed
incumbent/audit or constrained full-training99590 advancement check. No automatic
retries or scientific changes. This is not production bulk-fitting authorization.
No optimum, gap resolution or full-grid feasibility is claimed from RUNNING.

Output root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/full1498_mio_v1/25778194`.
Logs: heavy-data `logs/full1498_mio_25778194.out` and `.err`.
Startup confirmed: synthetic integration report passed all12 checks (including
active-grid response, restart, immutable resume and tamper refusal). First real
discovery14 contract/output directory exists; error log remains empty. Compute
WLS/solver access is demonstrated by successful synthetic solves; credentials
were not read into or printed in this conversation.
Nominal real solver budgets total60min plus setup/readback overhead;90min is the
allocation limit, not predicted convergence time. No need to wait for all six
solves during this submission turn; inspect final results before advancing.

Only test/preflight/release/report artifacts were added this turn; no production
code modification, Q-Chem job/rebuild, source overwrite or cleanup.
