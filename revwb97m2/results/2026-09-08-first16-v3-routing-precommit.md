# First16 v3 routing and pilot preparation — pre-commit checkpoint

User approved one initial native execution checkpoint, preparation of the remaining
pilot in parallel, and partition selection for shorter waits. No `lr_lowprio` route
is permitted. No native jobs were submitted in this turn: changing the frozen
mhg-only runner requires a new user commit before its release gate can pass.

## Live resource review

The `$partition` helper path was absent, so the skill's manual Slurm workflow was
used: `sinfo`, `sacctmgr`, `scontrol`, user duplicate-job check, and non-submitting
`sbatch --test-only` estimates. No existing user jobs appeared at the review.

| Route | Evidence and choice |
|---|---|
| cm1 / lr_qchem / condo_qchem | Preferred for first16. Several idle nodes; n0001.cm1 has 48 CPUs, 241732 MiB real memory and zero allocated memory. Test-only estimated immediate start at 2026-09-08T16:32:37 (scheduler-reported time). |
| lr8 / lr_mhg2 / mhg2_lr8_normal | Valid fallback, test-only estimated immediate start at 2026-09-08T16:36:00. Large physical memory fits later resource classes too. |
| mhg / mhg / normal | Substantial priority backlog; test-only estimate 2026-10-05T10:56:00. This is a changing scheduler estimate, not a promised delay. |
| lr7 / lr_mhg2 / condo_mhg_lr7 | Association confirmed and allowed by routing policy; no first16 launch preference over currently available cm1/lr8. |

Test-only numbers 25713389, 25713431 and 25713432 are NOT submitted job IDs.
Both approved data/scratch roots share the same filesystem, reporting about 2.5 PiB
available (`df -h`); do not add their available capacities together or infer a
reservation. First16 restart-copy lower bound remains 5,184,757,659 bytes (~4.83
GiB), excluding generated scratch. Requests remain 8 CPUs, 14 GiB and 72 h per task.

## Implementation and evidence

- `scripts/generate_training_features_v2.py`: reviewed per-species release routing
  permits only the four listed partition/account/QOS combinations. Exact species
  coverage and only those three route fields are accepted. Runtime allocation and
  environment must match. No memory/CPU/science override; commit and evidence gates
  remain. Adds bounded array-index selection and hashes the new launcher.
- `slurm/run_training_features_array_v3.sh`: cm1 defaults and one `0-15%8` array,
  ensuring at most eight active tasks within this array. This is not a global
  throttle across multiple independent arrays; review total concurrency before
  splitting later work across partitions. All 16 tasks can be queued together.
- `training_first16_v3.json`: new namespace and code hashes, preserving exact
  species, all derived inputs, basis/source trees, resources, scientific spec and
  94 native stages from v2. V2 manifest/launcher files are unchanged historical
  artifacts; v2's old code hashes no longer match the current runner, so launch v3.
- `scripts/prepare_pilot_execution_v3.py`: fresh corrected-canary readback and
  pilot input hashes; reports remaining resource classes, artifact candidates,
  restart tree metadata, and unsupported derived-input gates without promoting
  legacy files to validated numerical evidence. No bulk restart-content hashing
  in this planning audit; full content hashes remain required at execution freeze.
- `tests/test_corrected_generation_release.py`: routing, forbidden QOS/account,
  extra resource override, incomplete species maps, array-index, allocation and
  conservative legacy-category regressions. Full suite: **168 passed (10.74 s)**.
  Shell syntax and `git diff --check` passed. New and old first16 scientific/input/
  resource fields independently compared equal; new output/scratch roots absent.

The release draft records user approval but retains `USER_COMMIT_REQUIRED` and
`resource_review_passed=false`. Refresh live resources and create an actual release
with the resulting commit after the user commits. Never submit the draft directly.

## Pilot scope and next actions

All 100 selected entries and 224 species are preserved. After first16, resource
classes comprise 192 species at 14 GiB/8 CPU, 11 at 21 GiB/8 CPU, three at
35 GiB/8 CPU, and two at 227 GiB/16 CPU (these counts include reuse candidates).
Completed preparation output: `results/pilot_execution_v3/remaining_pilot_preparation.json`.
Its categories are 16 first16 species, one fresh corrected-canary species in this
pilot, 39 legacy migration candidates, and 168 new-generation candidates (two of
which are blocked by explicit ECP). All 224 source input hashes and derived-input
gates were checked; only those two gates failed. All seven corrected canary
readbacks passed again. This is not full legacy numerical acceptance.
The PCONF21 pair keeps its separate resource review. Explicit `$ecp` inputs for
`3d4dIPSS_Y_GS` and `3d4dIPSS_Y_GS+` are rejected by the current generator: do not
strip/replace those blocks by assumption. Review a faithful supported path before
their execution. This does not block first16 or other supported ready species.

Next: user commit; refresh live routes; enable an actual release; submit the single
first16 array; validate representative native results; then release ready remaining
work together under resource-class controls. Finish legacy stage migration and the
explicit-ECP implementation review before claiming the entire pilot executable.
No scientific settings, tolerances, orbitals, native Q-Chem code or historical
canary data changed. No Q-Chem rebuild, scratch cleanup, fitting or submission.
