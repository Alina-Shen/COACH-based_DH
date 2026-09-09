# Remaining 166 pilot species — resource-group freeze checkpoint

Scope: prepare the supported new-generation portion of the unchanged 100-entry
pilot. No new native jobs, fitting, SCF, cleanup or scientific changes. First16
has independently passed; do not repeat an initial checkpoint for every group.
Stop for the user's frozen-manifest commit before release/submission.

## Selection and resource review

| Group | Species | CPUs each | Memory each | Wall limit | Proposed partition/account/QOS |
|---|---:|---:|---:|---:|---|
| m14 | 153 | 8 | 14 GiB | 72 h | cm1 / lr_qchem / condo_qchem |
| m21 | 8 | 8 | 21 GiB | 72 h | cm1 / lr_qchem / condo_qchem |
| m35 | 3 | 8 | 35 GiB | 72 h | cm1 / lr_qchem / condo_qchem |
| m227 | 2 | 16 | 227 GiB | 336 h | lr8 / lr_mhg2 / mhg2_lr8_normal |

The m227 pair is PCONF21_444 and PCONF21_99. Every CPU/memory/wall request comes
unchanged from the approved pilot inventory. These are resource groups, not four
serial scientific tests: ready reviewed groups can all enter the queue together.
No percent array throttle and no lr_lowprio. Scheduler/site limits still apply.
If all166 could run together, aggregate requests would be1344 CPUs/2869 GiB;
this is not a reservation or a claim of current simultaneous capacity.

Used `$partition` manual Slurm workflow (helper previously missing): fresh sinfo,
sacctmgr, user squeue, df and sbatch --test-only. cm1 had five idle nodes with
241732 MiB physical memory each; lr8 nodes have773569 MiB. Both exceed their
proposed requests strictly. Account/QOS associations confirmed, no user duplicates.
Individual test-only estimates at16:59:51–53 September8 were immediate for all
four groups on their proposed routes and for the PCONF21 pair on either cm1 or
lr8. Prefer lr8 for the pair to separate high-memory work from cm1's small-job
queue and provide more node headroom. This is a scheduling recommendation, not
a measured hardware-speed comparison. Refresh after commit; estimates do not
predict all tasks starting at once. Test-only25713935–25713939 are NOT jobs.

The two approved storage roots share one filesystem with about2.5 PiB available.
Expected minimum restart copies from the inventory total94,951,439,318 bytes
(about88.43 GiB), excluding new native scratch/logs; capacity is not reserved.
Retained data and disposable scratch remain separated under the user's roots.

## Implementation and checks

- Added `scripts/freeze_remaining_pilot_v3.py`: selects only supported new
  candidates, excludes first16/accepted-canary/legacy/ECP-blocked species, rejects
  duplicate names and unreviewed resource tuples, checks first16 acceptance and
  pilot identity, and invokes the existing tested native freeze implementation.
- Each freeze hashes full restart contents (not metadata alone), authoritative
  input, source/basis/electron/spin identities, derived native inputs, code/build
  and specification. New namespaces prevent mixing previous outputs. Existing
  generator and launcher are untouched, preserving first16 validation contracts.
- New manifests in `manifests/production_generator/pilot_remaining_v3/` contain
  four plans, four disabled release drafts and four summaries. Each summary
  records exact sbatch overrides: full array range without %8, CPU, memory, wall
  time and route, plus the plan argument for the existing tested array launcher.
  Do not invoke the first16 launcher with its defaults for these larger groups.
- Plans explicitly set concurrency_proposal=null to supersede the historical
  generator's default proposal8. This is a generated planning-field change only;
  no runtime code/science change. Actual release remains a separate approved gate.
- Added four tests in `tests/test_remaining_pilot_freeze.py`; full suite
  **172 passed (11.75 s)**. Tests cover excluded categories, preserved grouping,
  duplicate rejection and unknown resource rejection.

Post-freeze checks PASS:166 distinct species,994 native stages (916/48/18/12 for
m14/m21/m35/m227), all four plans load under the unchanged runtime, preparation
authority hashes match, all four release drafts reject execution, all output/
scratch namespaces remain absent. Minimum copy total agrees with the inventory.
Plan hashes:

- m14:8e3a4f9ce7f8852a47f4ddcffcfd7a66c37e43145e2ba9521bc6486441b59263
- m21:b88650aa00c87023c2617413da368fafac32cb99c0ad18332d2c2d677eb7da3a
- m35:87c2df1c40e0a1baf9b735566a190b3d9765c89306c505bf2f75782997422203
- m227:6f90692cf129f152e3929d2593a60f74516db17eb7d6b1854cbb29ec449d9fc7

## Deliberately excluded / next

39 legacy candidates need explicit numerical/stage migration validation; do not
blindly regenerate or silently accept them. Two explicit-ECP Y_GS/Y_GS+ inputs
need faithful generator support; preserve original blocks. They remain in the
100-entry training scope, merely outside this supported execution manifest.
With16 first16 and1 corrected-canary pilot species, these categories cover224.

Commit these new artifacts together with the previous actual first16 release and
independent readback report. Then recheck live resources/storage/duplicates,
create actual releases bound to that commit and submit all ready resource groups
without an eight-task cap. Keep legacy/ECP work separate. Full100-row numerical
assembly must pass before bounded MIO fitting; this freeze does not certify it.
