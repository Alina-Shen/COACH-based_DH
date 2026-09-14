# Live activation — 2026-09-14

## Validated gateway

25895492 completed on n0037.mhg0/n0038.mhg0 in 3m26s, exit 0:0, empty stderr.
Both nodes passed cross-node capacity-20 locking and isolated real-data
adapter/readback. Independently reran controller.compute_gate against the real
artifacts and current source hashes; passed. Local regression suite: 24 passed
in 7.35 seconds. Initial worktree clean; committed implementation d16acea.
The sustained WLS test 25895401 had already passed; no new license-only probe.

## Activated mapping

State root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/dispatch/production_20260914_v1/`.
Its `state.json`, `authorization.json`, `events.jsonl`, `ledger/leases.json`
and per-task receipts retain exact mapping, source hashes and scheduler actions.

| New job | Purpose / task indices | Route | Resources |
| --- | --- | --- | --- |
| 25895832_[49-123] | 75 replacement discovery fits | mhg / mhg / normal | 16 CPUs, 32 GiB, 2h30 allocation; 7200s solve |
| 25895833_[0-199] | 200 selected fits | mhg / mhg / normal | Same |
| 25895834_[200-399] | 200 selected fits | mhg / mhg / normal | Same |
| 25895835_[400-413] | 14 selected fits | mhg / mhg / normal | Same |
| 25895836 | Exhaustive discovery/scientific-route audit | mhg / mhg / normal | 16 CPUs, 32 GiB, 30m |

Preserved original running discovery 25801134_47/48 on n0003.cm1. Cancelled
only the 75 freshly verified held/pending originals 25801134_[49-123] and all
414 pending leaves of 25802824, after one-to-one held replacements existed.
No scientific inputs/results were deleted or overwritten. This retires old
scheduler entries, not their task definitions; all replacements retain task
indices, seeds, K values, output targets and frozen solver settings.

Build 25802822 and grid 25802823 were held before parent replacement. Repaired
dependencies before cancelling original discovery tasks. Slurm throttled some
cancellation RPCs, but the activation command completed successfully; no
manual bypass/recovery was required. Selected replacements were created in
200/200/14 chunks to keep expanded queue occupancy below 999 (initial 493;
planned transient maximum 768; final observed 494).

## Scientific gates, independently inspected in Slurm

1. 25895836: afterany on original 25801134 and replacement 25895832 arrays;
   terminal accounting alone does NOT pass the audit. All 138 scientific
   discovery candidates and migrated route receipts must validate.
2. Build 25802822: afterok:25895836.
3. Grid 25802823: afterok:25895836:25802822.
4. Every selected replacement array: afterok:25895836:25802822:25802823,
   plus controller-held until the successful grid stage.

Build/grid retain their frozen cm1 route and resources. Added only scheduler
ExcNodeList=n0002.cm1,n0004.cm1,n0006.cm1 to these two pending jobs. Treat those
nodes as unavailable until verified recovery; do not trust optimistic estimates
that rely on them. No running job or other project was modified.

## Global admission and initial health

First controller iteration released 18 new discovery tasks, indices 49..66,
with two legacy running reservations: 20 occupied ledger slots. Sixteen new
fits (49..64) started on n0037..n0040.mhg0, two released tasks waited for
resources, and 57 further discovery tasks remained held. All 414 selected fits
remained unreleased. New task reservations count even while pending; expiry
cooldown is 330s after disposal. Legacy-token retirement uses 3600s conservatively.

Checked all 16 initial running receipts: mhg/mhg/normal, empty stderr. All 16
had model.json with TimeLimit=7200 and Threads=16, nonempty progress.jsonl and
no failure.json. Representative sstat showed substantial accumulated CPU and
about 1.1 GiB RSS. These are healthy startup checks, not final scientific passes
or proof of optimality.

Persistent monitor started in tmux **r2_dispatch_20260914** on **n0001.scs00**.
It checks every 45s, shares the one capacity-20 ledger, advances only on success
gates, and stops admissions on detected failures/source changes. Confirmed
live status output at stage discovery, occupied20, released18. It is a login-node
process, not a durable service guaranteed to survive host/session failures.

```bash
# On n0001.scs00:
tmux attach -t r2_dispatch_20260914
```

## Changes and next steps

No Python/solver code, frozen releases or original job scripts changed this
turn. Only this report, README, external project notes and scheduler/dispatch
state changed. Do not edit hash-frozen live dispatch source without planning a
safe checkpoint. Monitor first production completions, independent scientific
audits, token retirement and dispatcher liveness. No additional user submission
is needed while the controller is healthy; any failure stops admission for review.
Final scientific model review is still required after selected fits finish.
