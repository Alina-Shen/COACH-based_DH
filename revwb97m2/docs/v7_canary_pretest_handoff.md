# Approved canary implementation — pre-test commit checkpoint

## Subsequent approved correction and execution

The original pre-test stop below is historical. Commit b8736a7 passed110tests;
freeze exposed implicit Ru ECP in MOR16_ed33 (the original no-ECP claim was
incorrect). User approved basis-bridge-aware electron counting and separated
storage. Corrected suite now passes114tests. New schema2 plan pins the bridge
and code; MOR16 has200explicit+28ECP electrons without changing its input.
Five smaller jobs25680429/25680433/25680434/25680435/25680436 submitted.
The two larger cases remain unsubmitted pending smaller-case review.

User storage policy supersedes the old unresolved-quota gate: retained inputs,
outputs, feature arrays and logs under coach-based_dh_data/revwb97m2; working
archives and Q-Chem cwd/temp under scf_read/revwb97m2. Stage qcscratch links
point to that external scratch namespace; route identity is validated. Atomic
Q4 publication staging remains beside retained arrays because it becomes the
retained output, not disposable Q-Chem scratch. No old files moved or deleted.
Current readback requires working qarchive evidence: do NOT delete scratch
until an explicit evidence-preserving cleanup procedure is approved.
Shared filesystem free capacity is the user-authorized limit; checks do not
sum free space from two paths on the same filesystem. New scratch growth is
not predicted by the24.314GiB copy-only lower bound.

Corrections are uncommitted, explicitly hash-pinned in the frozen plan. A
follow-up commit is needed before broader expansion; no silent code identity
substitution or bulk authorization is implied.

## Original implementation handoff (historical)

User approved the seven-case plan and removed the maximum-two-jobs-overall cap.
No global two-job cap is implemented. Memory/CPU/wall allocations and review
before the two large cases remain. This turn implements the prerequisite new
scientific path; user pre-test commit remains as specified in the approved plan.
No tests, freeze, Q-Chem runs, Slurm submissions or rebuild were performed.

## New files

- `v7_canary.py`: seven-species freeze/load contract; all-electron Cartesian
  electron/spin checks; v7 scalar input; three Q4 grids; isolated scalar/PT2/fixed
  jobs; field-aware fixed parsing; total SS+OS recovery; pure D4ATM; final292
  feature/grid publication and raw-output readback.
- `scripts/v7_canary.py`: explicit freeze/run/validate CLI; no batch submission.
- `tests/test_v7_canary.py`: electron-count/PT2-zero, v7-vs-v6 input controls,
  unsupported input refusal, output spin/read evidence, partial-stage refusal,
  artifact tamper, no-overwrite and large-case review tests. Added, NOT RUN.
- `slurm/run_v7_canary_v1.sh`: explicit species launcher, no global concurrency
  cap. Defaults describe14GiB class only; other cases MUST override allocation.
  Runtime driver checks CPUs/memory against the frozen species.

Historical drivers/defaults/specification and previous38species artifacts remain
unchanged. New code is intentionally scoped to seven known real-atom, no-ECP
canaries. It does NOT claim support for general ECP/ghost-center fresh generation.
One-electron PT2 zero is derived from authoritative electron count and confirmed
by Q-Chem output, not from the string W4-17_h. D4 is recalculated from geometry.

Each completed Q-Chem stage has input/output/preparation hashes and independent
spin/archive/termination checks. Only completed matching stages can be reused;
partial stages/publications fail closed and remain on disk. Q4 publisher reuses
only validated artifacts. No silent deletion or automatic retry. No new SCF.
Fresh total PT2 is calculated for multi-electron canaries, unlike VV10-only reuse.

## After user commit

Run full unit/configuration suite first, then freeze a new manifest (these are
future commands, not tests already performed):

```bash
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m pytest -q revwb97m2/tests
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.validate_scientific_spec --json
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.v7_canary freeze \
  --plan revwb97m2/manifests/production_generator/v7_canary_v1.json \
  --root /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/v7_canary_v1
```

Freeze hashes all seven full orbital trees and records the minimum retained-copy
footprint (five copies for H, six otherwise). This excludes new Q-Chem temporary
growth and failures, so it is NOT a sufficient quota check by itself. Before
launch, inspect quota/headroom, existing compatible stages, live partitions/
account/QOS/wall limits, and memory. Ask user if quota/capacity is unresolved.
The launcher is not runnable until the plan is frozen and these gates pass.

User removed the overall two-job cap. Do not infer changed memory, permission
for unlimited dataset expansion, or waiver of the post-small-case large review.
Keep the approved smaller-first sequence for this seven-case execution; any
parallel small-case scheduling should be settled at resource preflight without
reintroducing a maximum-two-overall condition. No large submission until small
case review; `--large-reviewed` is an explicit execution gate, not auto approval.

After completed cases: separate `validate` readback, resource/timing review and
publication audit. Then propose100complete training reactions and exact species
closure/cost before any larger cohort submission. No bulk fitting implied.
