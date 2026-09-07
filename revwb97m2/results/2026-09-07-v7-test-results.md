# v7 tests: committed baseline and bounded synthetic integration

Baseline: bf641f651b82fa9f1a854c6cee391d6710ae4898; clean worktree verified
before tests. Specification hash:
32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc.
No existing implementation file was changed during this test turn.

## Completed checks

1. Full committed suite: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
   /global/home/users/yaoshen/.conda/envs/dh/bin/python -m pytest -q revwb97m2/tests`.
   Result: **95 passed in 6.97s**. Log: `2026-09-07-v7-pytest.log`.
   Covers old regressions plus new v7 settings/ridge algebra/margin, 700-row
   independent selector, stale inputs, failure records and small solver models.
2. `python -m revwb97m2.scripts.validate_scientific_spec --json --output
   revwb97m2/manifests/scientific_spec/scientific_spec_v7_validation.json` passes
   supported v7 configuration validation. This checks configuration only; it
   does NOT certify chemical features, bulk readiness or all old gateway hashes.
3. Added `scripts/test_v7_end_to_end.py`, a synthetic four-row/292-feature CLI
   harness exercising the real v7 runner, and `slurm/test_v7_end_to_end.sh`.
   Actual WLS environment on a compute node; no synthetic data is represented
   as chemistry or used for scientific model selection.
4. Partition skill: checked live mhg/lr8/cm1 and account associations. Chose
   mhg/mhg/normal: idle CPU nodes available, physical memory >4GiB. Script requests
   oneCPU,4GiB,10minutes; no resource class or scientific production change.
5. Job **25674271**, n0030.mhg0, elapsed10s, batch MaxRSS48956K. Slurm result
   **FAILED1:0** from an incorrect test-harness assertion, NOT failed solver calls.
   Pass1/pass2/restart all returned audited incumbents; resume preserved outputs;
   tampered input was refused. Both pass1 and pass2 solver status2.
6. Diagnosed assertion: expecting SR-HF alone to shift was invalid because other
   exchange coefficients can satisfy UEG and the grid bound. Corrected the new
   harness to require a changed coefficient vector plus the independently checked
   grid condition. No solver/model/spec code changed. Initial failure report is
   preserved. No job resubmission or fresh solve after this correction.
7. Independently reloaded hashed inputs and pass1/pass2/restart through `readback`.
   Corrected readback has all12 checks true; max coefficient change0.57528089885.
   Grid99590 error drops0.018049710714 ->0 kcal/mol on this deliberately synthetic
   fixture. Objective was independently recomputed including ridge. This is a
   corrected readback PASS, not a claim that Slurm job25674271 succeeded or that
   the corrected harness has completed a fresh full rerun.
8. Ran the actual v7 input-preparation CLI for h2o_SW49 and
   12_NH2rad_HNBrBDE18. Both generated no-overwrite preparation records and inputs
   with NL_VV_B550, OMEGA/OMEGA2 300, SCF_GUESS READ, MAX_SCF_CYCLES0 and
   UNRESTRICTED TRUE. No Q-Chem run/archive mutation. Artifacts under
   `results/v7_input_preparation_20260907`.

The synthetic pass1 reports raw gap0 with a derived discrepancy around7e-10
relative from an absolute bound difference7.11e-20; strict reporting preserves
that discrepancy. This is roundoff-scale evidence on this instance, not a
resolution of the historical raw-infinite-gap issue.

## Test-plan coverage and remaining blockers

| Plan layer | Outcome |
|---|---|
| Unit/config | Passed95 tests + configuration check |
| Serialization/restart/grid | Unit coverage passes; synthetic real-runner steps and corrected readback pass; fresh corrected-harness rerun remains |
| Chemical gateway | Actual closed/open-shell INPUT PREPARATION passes; b5.5 Q-Chem evaluation/recovery/republication NOT done |
| Real20-entry MIO | Not run: no validated v7 b5.5 reaction manifest/assembly producer yet |
| 100-300/full1498 resource tests | Not run: larger validated feature data unavailable |
| Selection pipeline | Paper-specific revised analysis implementation/tests still pending; not a blocker to initial coefficient fits |

The committed v7 input loader deliberately requires a new independently validated
assembly manifest. The previous implementation handoff already identified its
chemical producer/recovery integration as follow-up work; input preparation
alone cannot produce that evidence. Old b10 vectors cannot safely substitute.
Thus the entire test plan is NOT complete and bulk fitting is NOT ready.

Next recommendation: commit the new harness/report and correct its assertion;
then implement/version a bounded b5.5 refresh and independent assembly publication
for the existing gateways/20-entry cohort, preserving hashes/reuse/recovery logic.
Review/commit that new implementation before its chemical tests, consistent with
the user's checkpoint requirement. After chemical validation, run real20-row
ridge/two-pass MIO. Wider feature generation and bulk MIO retain separate gates.

## Files added this turn

- `scripts/test_v7_end_to_end.py`: new synthetic test harness; SR-only expectation
  corrected to general coefficient change after the failed test.
- `slurm/test_v7_end_to_end.sh`: bounded CPU/WLS launcher.
- `manifests/scientific_spec/scientific_spec_v7_validation.json`: configuration result.
- This report, pytest log, generated input-preparation and synthetic job artifacts.
- External STATUS and project chapter11 updated with results/remaining gates.

No existing production source fix, spec edit, Q-Chem build, chemical job, bulk
submission, commit or push. New harness is uncommitted; baseline and result
provenance are not silently presented as the same commit.
