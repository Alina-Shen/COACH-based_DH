# Adapter validation and initial-route checkpoint — 2026-09-14

## Scope and status

Following successful sustained WLS probe 25895401, the user approved adapter
readback validation followed by safe activation if checks pass. No production
migration, cancellations, holds, throttle changes or dispatcher activation have
occurred at this checkpoint. Original running fits and other projects are untouched.

## Work performed

1. Confirmed clean initial worktree at commit `772b1e4`. Reviewed the additive
   adapter, smoke model/readback, shared ledger, migration controller, dependency
   audit and frozen discovery/selected readers. Original scientific source and
   release files were not edited.
2. Reran the existing pytest suite: 19 tests passed. An initial unittest command
   discovered zero tests and was not counted as validation. Shell syntax passed.
3. Reviewed live cm1/lr8/lr7/mhg physical memory and scheduling. All exceed the
   unchanged 32 GiB/node request. The partition helper is absent, so manual
   Slurm queries and test-only submissions were used. No lowprio QOS was used.
4. Submitted isolated two-node adapter test **25895492**: two tasks on separate
   nodes, 16 CPUs/task, 32 GiB/node, 20-minute allocation. Each task runs a
   120-second real-data solve and validates publication hashes, starts, model
   dimensions/parameters, coefficients and independently evaluated objective.
   Both nodes contend on one capacity-20 shared lock ledger. Test results are
   isolated from production; this does not create a production discovery candidate.
5. lr8 / lr_mhg2 / mhg2_lr8_normal was blocked by QOSGrpCpuLimit (shared QOS
   cap cpu=768). Moved only this pending diagnostic to cm1 / lr_qchem /
   condo_qchem. Its submitted script remains unchanged; the scheduler override
   is the authoritative actual route. cm1 has 241732 MiB/node and a 14-node QOS cap.
6. Found that controller activation hard-coded all replacement arrays and its
   scientific audit to lr8. Added explicit `--partition` selection, validated
   before scheduler mutation, using the existing approved route/account/QOS
   map. Default remains lr8 for compatibility; the reviewed cm1 activation
   must explicitly pass `--partition cm1`. The chosen initial route is recorded
   in state. Resources, fitting budgets, seeds and scientific dependencies are
   unchanged. This is initial-route selection, not automatic dynamic rerouting.
7. Added four parameterized route tests and one invalid-route rejection test:
   **24 tests passed**. Tests check all replacement/audit submissions use the
   selected route and running/other-project jobs remain unchanged.

## Live test result

25895492 is pending on cm1 for Resources at report preparation. No compute
solve/readback pass is claimed. Once running, allow two minutes for each solve
(concurrent), plus setup and independent audits. Scheduler start predictions
are estimates only, not guarantees.

Logs:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/multi_smoke_25895492.out`
and matching `.err`.
Artifacts:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/dispatch/activation_checks_v1/25895492/`.

## Remaining activation gates

- Successful terminal accounting for the two-node smoke; both passed.json files;
  independent real-artifact readback via controller.compute_gate; code hashes match.
- Commit the route correction before freezing a production controller hash.
- Refresh live pending indices and resources. At inspection, discovery 47/48
  ran unchanged, indices 49..123 (75) remained pending, and all 414 selected
  fits were dependency-pending; both original array throttles remain 2.
- Activate exact pending-only replacement with global 20-slot reservations,
  conservative legacy-token retirement and held replacements. Preserve running
  tasks and repair descendants before cancelling any replaced pending task.
- Require exhaustive 138-candidate discovery audit -> build -> successful grid
  selection before releasing any selected fit. Then monitor the ledger and
  scheduler; stop admissions on failed accounting or scientific checks.

## Commit commands

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/multipartition_v1/controller.py \
           revwb97m2/multipartition_v1/test_activation.py \
           revwb97m2/multipartition_v1/README.md \
           revwb97m2/multipartition_v1/REACTIVATION_CHECKPOINT.md
git diff --cached --check
git diff --cached --stat
git commit -m "Validate explicit activation routing and rerun adapter gateway"
```
