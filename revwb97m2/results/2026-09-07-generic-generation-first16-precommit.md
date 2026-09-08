# Generic generation/reuse implementation and first16 pre-commit checkpoint

Status: implemented and offline-tested; frozen first batch; NOT released or
submitted. All-seven-canary successful review, user commit and live resource
review remain required. No100-entry fitting started. User will report completion;
no scheduler polling/wait loop was started this turn.

## What changed

- `scripts/generate_training_features.py`: new generic inventory-based freeze,
  input/build/spec/source-tree pinning, source/derived-input checks, completed
  refresh/canary reuse audit, native-stage execution/resume, duplicate-execution
  file lock, D4-only1e-12Ha readback, publication validation and release gate.
  Existing native helpers are imported without monkey-patching their seven-case
  contract. No top-level package Python files changed; active canary hashes pass.
- `slurm/run_training_features_v1.sh`: new single-species launcher with required
  release argument, explicit8CPU/14GiB/72h defaults for this batch, approved module
  stack and external heavy-data log paths. It does not submit itself or other jobs.
- `tests/test_training_generation.py`:13 new test cases covering deterministic
  selection, unsafe paths, absent/incomplete release, stale reuse plan, D4-only
  tolerance, completed-stage reuse, partial-stage rejection and refreshed-energy
  normalization. Full suite144 passed in7.89s; shell syntax and diff checks pass.
- `manifests/production_generator/training_first16_v1.json`: exact first batch,
  full restart-file hash/size listings, derived inputs for every native stage,
  source/build/code/spec hashes, resource routes and proposed concurrency8.

Manifest SHA256:
`9103db43c94e4e70e485cdd0b9687310f39675010972161958ee4a89aa49842f`.
Spec SHA256:
`32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc`.

## Exact batch and work

Selection: first16 pilot species with no feature candidates in the v2 coverage
snapshot and14GiB resource class, ordered by orbital AO count then species name.
This is an inexpensive initial execution tranche, not a balanced accuracy test;
the complete100-entry proposal and its two PCONF21 members remain unchanged.

1. 189_h_W4-11
2. CUAGAU_H
3. 37_li_TA13
4. ALK8_li+
5. 33_be+_TA13
6. Pol130_Be
7. Pol130_Be0+
8. Pol130_Be0-
9. Pol130_He
10. Pol130_He0+
11. Pol130_He0-
12. ALK8_na+
13. MX35_Na
14. 133_c_W4-11
15. W4-17_b
16. W4-17_c

94 native stages:48 IDV (16 each250974/99590/75302),16 SR-HF/VV10 scalar,
16 fixed energy and14 PT2. Two one-electron cases skip PT2 explicitly; D4 is
separate. An intermediate commentary incorrectly said92 stages/four exemptions;
the manifest and this94-stage count are authoritative and the error was corrected.

Complete source trees total882236614bytes; per-stage isolated copies require at
least5184757659bytes (4.8287GiB), excluding new native scratch/output/failures.
Free space at freeze2504.37TiB, not reserved and shared across destinations.
72h is a cap, not a runtime prediction. Live allocation, concurrency enforcement
by the future submission procedure and duplicate-job review remain pending.

Planned retained root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/training_first16_v1`.
Planned scratch root:
`/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2/training_first16_v1`.
Neither created. Freeze reads/hashes restart files; their actual successful native
MO interpretation is still verified at execution, not claimed from hashing alone.

## Reuse and safety boundaries

Completed same-plan native stages are independently checked and skipped on resume.
Incomplete stage directories stop without overwriting. A complete publication
whose final marker was interrupted can be revalidated; partial ready directories
are preserved and stop for review. Published files remain hash-exact; only fresh
D4 numerical recomputation gets the approved tolerance. Other291 columns and
fixed/scalar/grid records remain exact. No SCF, cleanup or blind retry is added.

Completed cross-campaign reuse is available through `validate_reuse` and the
`audit-reuse` CLI, returning the vector/fixed/grid data for downstream use. A real
refreshed species11_Reactant1_EIE22 and recovered S22_06b passed this new wrapper's
read-only audits. No source files were changed. Arbitrary partial cross-campaign
stages are NOT automatically migrated; they need an explicit adapter and raw-stage
compatibility validation. The first16 deliberately avoid that unresolved case.

Release is separate from the frozen plan: absence fails before native execution
or filesystem mutation. The release must bind the manifest hash, explicit user
submission/resource approval, allseven canary reuse references (including recovery
evidence where applicable), and a commit containing the exact frozen code/plan.
Every release is rechecked against native canary evidence. No such release exists.
Future assembly must explicitly call the appropriate validated reuse interface;
the historical assembly was not silently generalized in this step.

## Next steps

1. User prelaunch commit of new files and outstanding pinned dependency changes.
2. User reports canaries finished; independently validate allseven, including
   accepted recovery evidence (a historical failed Slurm status need not erase
   valid recovered chemistry). Large canaries still require their prior review.
3. Live partition/account/memory/concurrency/storage/duplicate-job review; prepare
   the explicit reviewed release. Frozen historical routes are not approval.
4. Submit first16 only on release, max8 smaller jobs proposed. Review native
   results before expansion. No100-entry fitting until allseven and the assembled
   pilot matrix have passed. Pilot feature work itself is conservatively held
   behind allseven in this first manifest, per current user clarification.
5. Later expand class batches and integrate validated reuse into broader assembly;
   keep full generation independent of solver-gap closure.

Unfinished canaries do not block implementation, tests or freeze. They block this
batch's release by the chosen safety gate, not because fixed-orbital feature
values mathematically depend on them. If a canary reveals a scientific/driver
defect, update/test/refreeze explicitly before release.

## Read-only verification commands

```bash
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m pytest revwb97m2/tests -q
bash -n revwb97m2/slurm/run_training_features_v1.sh
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.generate_training_features check --plan revwb97m2/manifests/production_generator/training_first16_v1.json
```

Do not run freeze again on the existing manifest; it refuses overwrite. No Q-Chem
rebuild/new calculations/jobs/commits this turn. Initial syntax error during
development was fixed before the successful freeze and final144-test run.
