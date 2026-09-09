# Full-training generation: approved automatic submission

## Scope and checks

Production commit: `50e3b7a56fc9f18cf38b31812c1704305bb7e45d`.
The original 11 execution plans, chemistry source files, launchers and disabled
drafts remain unchanged. All plan/code identities were checked against this
commit, all plan input/build/specification checks passed, and the seven-canary
corrected evidence registry passed fresh readback. Source orbital trees were
hashed during the preceding freeze; each compute task checks them again before
running. No new SCF, Q-Chem rebuild, scientific setting or tolerance change.

Coverage remains 230 accepted reuse + 2,569 generation = 2,799 species for the
1,498-entry training set. Generation comprises 21 ECP gateway species and 2,548
ordinary species, 15,412 native stages, minimum source copies 2.51 TiB.
Both approved data/scratch roots share a filesystem with approximately 2.755e15
bytes available at release. No unrelated or original data was deleted.

## New operational code and tests

- `scripts/full_training_feeder_v1.py`: persistent singleton controller, durable
  pre-submission intent and job-ID journal; all-user expanded queue accounting;
  visibility-lag reservations; live route estimates; completed-publication hashes;
  ECP-first automatic gate; no blind retries or automatic Slurm requeue.
- `scripts/prepare_full_training_campaign_v1.py`: validates committed production
  authorities, namespace absence, exact coverage, physical memory/CPU capacity
  and storage, then creates new route-specific releases and a hashed campaign.
- `tests/test_full_training_feeder_v1.py`: 17 offline regressions for caps,
  expanded arrays, duplicates, unresolved intent, uncertain submission responses,
  accounting lag/failures, completion checks, stop requests and resource binding.

Tests: 17/17 new cases passed (0.36 s); full suite **245 passed (21.55 s)**.
`git diff --check` passed. These operational additions are outside the frozen
chemistry dependency glob. They are tested and hash-bound but not yet committed;
the production calculation code and execution plans are committed. The user
explicitly authorized continuous submission in this turn.

## Release, routing and first submission

Campaign directory:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/campaigns/full_training_20260909_v1`.
It contains `campaign.json`, 41 immutable route-specific releases, and durable
`controller/state.json` / `controller/controller.lock`.

Campaign SHA256:
`77fba9c62b2c440b79807dc3f201683331b68ebbab171c290311458f8da3b289`.

Live `$partition` manual review (bundled helper unavailable) checked partition
time limits, user account/QOS associations, node capacities, array limits and
QOS limits. All four reviewed partitions have unlimited partition walltime;
actual task limits remain 72 h or 336 h as frozen. `MaxArraySize=1001` accommodates
all indices (maximum 499). Physical memory must exceed the frozen request.

| Resource class | Eligible reviewed routes | Selection policy |
| --- | --- | --- |
| 8 CPU, 14/21/35/62/117 GiB, 72 h | cm1, mhg, lr7, lr8 | Compare fresh `sbatch --test-only` start estimates for each array transaction. |
| 16 CPU, 227 GiB, 336 h | cm1, mhg, lr7, lr8 | Same; never reduce requested memory or time to force a route. |
| 16 CPU, 557 GiB, 336 h | lr8 only | Other reviewed partitions lack sufficient physical memory. |

First actual array: **25730889**, tasks **0–20**, all RUNNING at the initial check
on n0001/n0003/n0005/n0007.cm1. Each requests 8 CPU, 14 GiB, 72 h under
`cm1/lr_qchem/condo_qchem`. Started 2026-09-09 02:07:11 PDT. No `%8` running cap.
`Requeue=0`, no restart, correct allocation; all 21 stderr logs initially empty.
This confirms scheduler startup, not completed chemical validation.

Follow-up at 02:10 PDT: controller heartbeat advancing across multiple polls;
21 submitted / 21 active / 0 accepted complete, no halt or unresolved intent.
Native fixed/PT2 stage output files are progressing. A sampled `sstat` batch
record reports approximately 1.49 GiB MaxRSS; final per-task resource accounting
remains a post-completion check.

The controller selected cm1 from live dry-run estimates; mhg estimated a much
later start (September 29), while cm1/lr7/lr8 estimated immediate starts. These
are scheduler estimates, not guaranteed waits. Dry-run job numbers are NOT
actual submitted jobs; only successful actual IDs enter the controller journal.

Representative actual override (committed launcher itself is unchanged):

```text
--partition=cm1 --account=lr_qchem --qos=condo_qchem
--nodes=1 --ntasks=1 --cpus-per-task=8 --mem=14G --time=72:00:00
--array=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20 --no-requeue
```

## Automatic progression and safeguards

1. Wait for all 21 ECP tasks to finish `COMPLETED/0:0`, with the native driver's
   own full validation, completion markers, matching publication identity and
   controller artifact-hash readback. A successful process alone is insufficient.
2. Automatically release the 2,548 remaining species, larger-memory groups
   first. No further manual submission is needed along the successful path.
3. Poll every 60 seconds; submit at most 32 tasks per transaction/poll. This is
   a submission rate and atomic quota check, not a 32-running-task limit.
4. Count **all yaoshen active tasks across all projects**, arrays expanded;
   include pending/running and other active states. Maximum **998**, never 999.
   Account for submitted tasks temporarily absent from queue/accounting.
5. Immediately before each actual submission, read the queue again. Scheduler
   errors, malformed/uncertain responses, exceeded capacity, changed authorities,
   failed/cancelled/timed-out jobs or invalid publications stop further submission.
   Already-running jobs are not cancelled. No automatic retry of failed work.
6. Continue tracking after the last submission until every species is published,
   or stop with a durable reason for review. Full numerical matrix assembly and
   fitting are NOT performed by this controller.

The controller cannot atomically control simultaneous unrelated submissions
outside its lock. Avoid another independent bulk submitter if the global limit
must be strict; external jobs are counted, and a detected over-limit queue halts
new submissions. It never cancels unrelated jobs to enforce the limit.

## Monitoring and stopping

Host: **n0001.scs00**. Tmux session: **r2_full_training_20260909**.
Initial controller PID: 3021682. This is a lightweight login-host monitor,
not a reserved compute node. Q-Chem runs only in the Slurm compute allocations.

On the same host:

```bash
tmux attach -t r2_full_training_20260909
# Detach without stopping: Ctrl-b, then d
squeue -u yaoshen -h -r -o '%i|%T|%j|%P|%M|%R'
```

To stop future submissions only:

```bash
touch /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/campaigns/full_training_20260909_v1/controller/STOP
```

Inspect `controller/state.json` for the heartbeat, actual job IDs, individual
indices, route-test evidence, completed counts, or `halted`/unresolved `intent`.
Tmux survives client disconnection, **not host reboot/failure**. State survives
in the data directory. Resume after a host failure requires checking the journal;
an unresolved intent or halt deliberately prevents blind automatic restart.
Do not edit pinned calculation/controller files while this campaign is active.

## Next checkpoint

Let the controller progress; inspect any halt before retrying. After all species
finish, independently audit raw results/resources and assemble/validate the full
1,498 × 292 numerical training matrix, preserving COACH entries and weights.
Only then prepare the separate pre-bulk fitting checkpoint and model-size scan.
No full-data fit or final model-selection claim is made here.
