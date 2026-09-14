# Multi-partition / 20-session launch update — pre-activation checkpoint

## LIVE — production dispatch activated, 2026-09-14

25895492 and independent compute_gate readback passed. Activated pending-only
mhg migration: discovery 25895832, selected 25895833/34/35, audit 25895836.
Original running fits untouched. Shared global20 admission and tmux monitor
are live; all selected tasks remain behind successful discovery/build/grid gates.
See [live mapping, verification and monitoring details](./LIVE_ACTIVATION_20260914.md).
Earlier non-activation checkpoints below are historical.

## Current checkpoint — WLS passed; adapter retest submitted, 2026-09-14

Sustained WLS job 25895401 passed with 16 additional concurrent environments
alongside two production fits. Adapter/shared-lock retest **25895492** is now
submitted on cm1 after lr8 hit its shared QOS CPU cap; compute outcome pending.
Added explicit initial activation `--partition` selection; 24 local tests pass.
No production migration or throttle changes. Route correction requires commit
before activation. See [current report](./REACTIVATION_CHECKPOINT.md).

The baseline-two rejection below is a historical checkpoint, superseded by the
sustained retest for tested access; remaining adapter/activation gates still apply.

## Latest outcome — activation stopped on license baseline, 2026-09-14

The server rejected job25884706 with **"Too many sessions, 5 active sessions
for a baseline of 2"**. Earlier brief concurrency success did not establish a
20-session entitlement. No migration/controller activation occurred. Restored
only existing array dispatch ceilings to2; running jobs and coach_mp2 unchanged.
Nineteen local tests pass; cross-node lock checks passed, but corrected real
adapter solve/readback is not yet fully validated. See [activation report](./ACTIVATION_REPORT.md).

The earlier pre-activation description below is historical. Current code now
includes a reservation-aware migration controller, chunked pending replacement
and a mandatory explicit baseline-confirmation gate. Those are **not live**.

Prepared 2026-09-14 following user approval. **Not released or activated.**
No live jobs held, cancelled, moved or resubmitted in this turn. Existing
10-fit throttles and original dependency jobs remain intact. All previous
tracked revwb97m2 files are unchanged. Only new files in this directory.

## Additive implementation

| File | Purpose |
| --- | --- |
| policy.py | Exact route/account/QOS validation; 16 CPUs/32GiB enforcement; pending-only task selection; phase dependency construction |
| leases.py | Shared POSIX-flock ledger, capacity20, atomic updates; count active plus 330-second cooling leases; reserve legacy jobs and retain crashed-owner slots |
| adapter.py | Validate additional launch authorization, acquire a slot before WLS, call frozen solve/audit functions, preserve scientific receipts and add actual-route provenance |
| audit.py | Validate migrated discovery route receipts and all138 scientific results before publishing a gate |
| run.sh | Separate 16-CPU/32GiB/2h30m wrapper; no changes to original scripts |
| tests.py | Fourteen unit/integration tests, including atomic contention, legacy occupancy, cooldown, mocked disposal on success/failure and dependency rejection |
| authorization_draft.json | Explicitly non-runnable template; production flags false, indices/hashes deliberately unfilled |

The adapter does not spoof SLURM variables, monkeypatch production checks or
edit the original cm1 release. The original release identifies scientific
settings; an additional hashed receipt records actual authorized execution
route. Existing scientific readers remain usable; the new discovery audit
also checks the additional routing receipts. Launch source hashes and pending
indices must be frozen before use.

## Routing review

| Partition | Account | QOS |
| --- | --- | --- |
| cm1 | lr_qchem | condo_qchem |
| lr7 | lr_mhg2 | condo_mhg_lr7 |
| lr8 | lr_mhg2 | mhg2_lr8_normal |
| mhg | mhg | normal |

No *_lowprio QOS accepted. Live association/node review and four test-only
submissions passed for 16 CPUs/32GiB. Scheduler predictions favored cm1
(00:28 on Sep14); other routes showed much later dates despite some idle-node
snapshots. These predictions are volatile, not guaranteed waits. Refresh all
four at activation; do not distribute work merely to use multiple partitions.
The bundled partition helper is unavailable; manual skill workflow was used.

## Required phase gates

1. Every original/replacement discovery job terminates; no selected fit starts.
2. New audit certifies all138 discovery candidates and migrated route receipts.
3. Maximum-row build preflight succeeds.
4. Grid job validates discovery again, creates its immutable snapshot and
   publishes the common selected rows.
5. Only then may selected-grid fits start. The adapter additionally reads the
   discovery gate and revalidates the entire grid snapshot before opening WLS.

Only the exhaustive audit barrier may use `afterany` on terminal jobs. This
accommodates cancellation of replaced pending array elements; it does NOT
declare their results successful. Missing/failed scientific results make that
audit fail. Build uses `afterok:audit`; grid uses `afterok:audit:build`; selected
uses `afterok:audit:build:grid`. No plain completion gate substitutes for success.

Current untouched chain: 25801134 -> 25802822 build; discovery+build ->
25802823 grid; grid -> 25802824 selected array. At final inspection tasks
38/39/40 were running, 41..123 (83) pending, and all414 selected fits pending.
coach_mp2 job25837199 was not modified.

## Token accounting and limits

Every new fit must use the SAME ledger across all routes. Legacy running jobs
must be reserved before activation and closed only after terminal accounting
and a conservative token-expiry allowance. New environments explicitly request
five-minute tokens; after disposal their slots remain occupied for330seconds.
Tokens belonging to external projects cannot be inferred from Slurm reliably;
the launch assumes the campaign's reserved entitlement and must account for any
other known WLS consumers. Never modify other projects to enforce the ledger.

An owner is not automatically expired based on elapsed solve time: a killed
process retains its lease until scheduler/operator reconciliation proves it
terminal. This stops admission safely but can require intervention. The
launcher must cap the aggregate queued/running admissions across partitions,
not independently allow20 per array. Adapter wait timeout600seconds is a final
guard, not a replacement for proper dispatch admission.

## Verified now

- Fourteen tests passed (1.90s); no real Gurobi environment used by these tests.
- Frozen discovery and selected release checks passed with gurobipy imports
  explicitly blocked.
- Shell syntax passed and Slurm accepted all four route/resource test-only requests.
- Existing files unchanged and live dependency chain inspected unchanged.

Not yet verified: cross-node shared-filesystem locking, real multi-route
adapter solve/readback, lease reconciliation against live accounting, and
transactional pending-job replacement. No production performance claim.

## Commit and remaining activation work

1. Commit this additive implementation.
2. Implement/test the bounded migration controller and source-hash release
   preparation. Validate shared-filesystem locking on compute nodes and a
   separate bounded adapter smoke solve/readback before touching the campaign.
3. Refresh exact expanded pending indices immediately before migration. Protect
   downstream pending jobs first. Prepare replacements held and preserve task
   IDs, seeds, outputs, CPU/memory/time limits; never replace running tasks.
4. Create the exhaustive audit barrier and change downstream dependencies to
   that barrier BEFORE cancelling replaced pending array elements. Otherwise
   `kill-on-invalid-dep` may cancel the original build/grid descendants.
5. Seed legacy WLS reservations, freeze/verify the dispatch authorization,
   cancel ONLY rechecked pending targets, verify the one-to-one replacement
   map, then release bounded admissions. Retain rollback receipts and stop on
   any state race or unexpected scheduler mutation.
6. Monitor without altering other projects; verify global20 accounting and
   positive scientific gates before selected dispatch. Publish final migration
   IDs and results to project notes. No activation is implied by this draft.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/multipartition_v1
git diff --cached --check
git diff --cached --stat
git commit -m "Add tested multi-partition routing and WLS admission foundation"
```
