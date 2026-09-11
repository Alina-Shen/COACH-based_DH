# Approved full1498 bounded workflow — pre-test checkpoint

User approved the September10 recommendation on September11: K14/K80, six
600s solves,16CPUs/32GiB/90min and all-training99590 public-grid advancement
gate. This approves the bounded scope, not production bulk fitting. Base commit
12080b8 and accepted full1498 matrix/scientific settings remain unchanged.

## Implemented, not yet tested

- `scripts/full1498_mio_v1.py`: separate orchestration; schedule at26, frozen
  plan/release/commit gates34/47, exact matrix identity70, full-row violation
  reporting77, allocation checks88, license-free resume95, independent per-solve
  audit113, immutable final validation134, serial fail-stop execution157 and
  guarded per-solve subprocess entrypoint200.
- Reuses the frozen row-generic `run_pilot100_fit_v1` mathematical implementation.
  No changes to historical pilot, objective, bounds, grid selector or scientific
  specification. Every start remains bound to the full input identity; pilot100
  starts cannot be silently reused. Candidate rows are reconstructed from both
  discovery coefficients rather than assuming every training row is selected.
- Independent readback checks saved objective/constraint/gap/start telemetry and
  preserves existing output bytes. New per-solve reports list all99590/75302
  violations with reaction IDs and selected/unselected membership. Discovery is
  unconstrained; constrained/restart full99590 failure is saved before stopping
  dependent stages. No automatic row additions, relaxations or retries.
- `slurm/run_full1498_mio_v1.sh`: separate16CPU/32GiB/90min launcher, private WLS
  path, controlled BLAS threads and heavy-data logs. Template routecm1 is NOT a
  live resource decision; release route must match actual scheduler allocation.
- `tests/test_full1498_mio_v1.py`:11 offline cases covering schedule/start lineage,
  disabled release, wrong matrix identity, license-free resume, pilot-start
  refusal,400-row selector fixture/unselected violation reporting, allocation
  mismatches, no-incumbent fail-stop and changed schedule rejection. Existing
  solver/pilot tests remain regression coverage for objective and readback.
- `scripts/freeze_full1498_mio_v1.py`: hash-only freeze, does not import the new
  runner or execute tests. Generated `manifests/full1498_mio_v1/plan.json` and
  `release_draft.json`; the latter has submission/tests/resource flags false and
  no selected route/commit/test report. Historical proposal.json is preserved.

## Checks actually performed

Read/source inspection, worktree review and hash-only freeze completed. No new
tests, synthetic solves, Gurobi environment, license access, native chemistry or
Slurm submissions occurred. New code is **untested pending user pre-test commit**;
the previous256-test result is not acceptance of this implementation.

## Next gate

After commit: run complete unit/configuration tests and real full-data identity
readback; address failures without weakening gates. Then use live `$partition`
review to select approved account/QOS (neverlr_lowprio; <999 active user tasks),
check memory/walltime/environment and release only against committed passing
test evidence. On compute node: synthetic control, six bounded real solves and
immutable independent audits. No production scan is authorized here.

The proposed full production scan and later scientific ranking remain separate
review/commit gates. Short bounded success is neither proof of optimality nor a
guarantee that longer search will fit the same memory allowance.

## Pre-test commit commands

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git add -- revwb97m2/scripts/full1498_mio_v1.py revwb97m2/scripts/freeze_full1498_mio_v1.py revwb97m2/scripts/preflight_full1498_mio_v1.py revwb97m2/slurm/run_full1498_mio_v1.sh revwb97m2/tests/test_full1498_mio_v1.py revwb97m2/manifests/full1498_mio_v1/proposal.json revwb97m2/manifests/full1498_mio_v1/plan.json revwb97m2/manifests/full1498_mio_v1/release_draft.json revwb97m2/results/2026-09-10-full1498-mio-preflight.json revwb97m2/results/2026-09-10-full1498-optimizer-validation-plan.md revwb97m2/results/2026-09-11-full1498-mio-pretest-checkpoint.md
git diff --cached --stat
git diff --cached --check
git commit -m "Implement approved bounded full1498 MIO workflow before tests"
```
