# Safe activation attempt — 2026-09-14

## Outcome and correction

Activation is blocked by the actual WLS service response:

> Too many sessions, 5 active sessions for a baseline of 2

This came from env.start() on n0023.lr8 in job25884706 using
`/global/home/users/yaoshen/tools/gurobi.lic`. The user reported maximum20, but
the service still reports baseline2 for this credential set. The earlier
three-session short probe only demonstrated temporary concurrent access; the
prior inference that it proved sustained expanded access was not justified.
Whether Support changed a different license, requires refreshed credentials,
or changed a different dashboard limit remains unresolved. No credentials are
printed or included here.

Gurobi explains that exceeding the baseline for an extended period can trigger
this error, and tokens can remain counted until their lifespan expires:
[official guidance](https://support.gurobi.com/hc/en-us/articles/34567582787345-How-do-I-resolve-the-error-Too-many-sessions).

## Work performed

1. Recorded user preference for lr8 hardware over mhg, with cm1 also preferred.
   Reviewed live resources; two-node lr8 jobs started promptly even though
   scheduler test-only estimates were implausibly late. No lowprio QOS used.
2. Extended leases.py with pre-dispatch reservations and worker handoff. The
   controller counts queued reservations, active environments and cooling
   leases globally rather than allowing20 independently per partition.
   Legacy/build environments use a conservative3600s retirement allowance
   because their existing default token configuration is not changed.
3. Extended adapter.py with reserved-slot admission, stable array-owner keys,
   isolated smoke execution and explicit baseline-confirmation requirement.
   Production still calls the unchanged frozen solve/reader with7200s/16threads.
4. Added controller.py: exact pending targeting, descendant protection,
   held replacement arrays, chunked selected-task replacement to keep temporary
   queue occupancy below999, dependency repair before discovery cancellation,
   original-running-job reservations, accounting reconciliation and persistent
   admission. Activation requires complete compute/readback gates and a
   separately confirmed baseline20. It has NOT been run against production.
5. Added audit_job.sh and array-index forwarding in run.sh. Later phases require
   successful exhaustive discovery audit -> build -> grid -> selected. Only
   the exhaustive audit may depend on terminal status with afterany.
6. Added smoke.py/smoke.sh/smoke_model.py and regression tests. The test outputs
   are isolated under the data dispatch root, not the production fit roots.
7. Added test_activation.py. Simulated migration protects running/coach_mp2,
   maintains one-for-one pending replacements, stays below999 queue entries,
   repairs dependencies before parent cancellation, reserves before release
   and refuses selected fits after failed discovery audit. All19 tests passed.
8. Following the explicit baseline2 rejection, stopped new license tests and
   restored ArrayTaskThrottle=2 on25801134 and25802824 (previously10). No
   running task was cancelled, suspended, moved or changed in allocation.
   Build25802822/grid25802823 dependencies unchanged; coach_mp2 untouched.

## Compute tests (all on lr8 / lr_mhg2 / mhg2_lr8_normal)

Each requested two nodes, one16-CPU task/node,32GiB/node,20-minute wall limit.
No existing inputs/outputs were overwritten; failed diagnostics are retained.

| Job | Nodes | Outcome |
| --- | --- | --- |
| 25884490 | n0007.lr8, n0012.lr8 | Shared lock passed; smoke readback rejected120s because the frozen production reader correctly requires7200s |
| 25884605 | n0016.lr8, n0024.lr8 | Shared lock passed; new smoke reader hit tupledict-key iteration bug after solving; fixed indexed readout and added regression test |
| 25884706 | n0016.lr8, n0023.lr8 | Shared lock passed; WLS rejected startup with baseline2; no complete real adapter/readback pass |

First two errors were test-harness bugs, not changes to scientific requirements.
The third is an external license blocker, not a solver model error. Do not
interpret successful unit tests or cross-node locking as production activation.

Artifacts:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/dispatch/activation_checks_v1/<job>/`.
Logs:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/multi_smoke_<job>.out` / `.err`.

## Current production state and next gate

At the post-safety-change check, tasks25801134_38/39/40 remained running on
n0003.cm1; pending41..123 and selected0..413 now have ceiling2. The throttle
does not stop an existing third running fit. No replacement fitting arrays,
audit jobs or tmux dispatcher were launched. No frozen original source,
scientific release or production artifact was edited.

Ask Support to confirm **baseline concurrent sessions=20 for the exact license
referenced by the current file**, and whether a replacement license file is
required. Share only confirmation or a securely stored replacement file path,
not secrets. Then rerun the corrected compute/readback test, refresh/freeze the
pending inventory and sources, and activate only after all gates pass.

Suggested support follow-up:

> You approved an increase to20 concurrent sessions, but our compute-node
> gurobipy application still receives "Too many sessions, 5 active sessions
> for a baseline of 2" on September14. It uses our existing WLS license file.
> Could you confirm that the baseline (not only a maximum/burst limit) is20 for
> that license, and whether we need a newly downloaded license/API credential?

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/multipartition_v1
git diff --cached --check
git diff --cached --stat
git commit -m "Add guarded migration controller and record WLS baseline activation blocker"
```
