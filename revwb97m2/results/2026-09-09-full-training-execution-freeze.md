# Compatibility tests, seven-canary readback and execution freeze

## Why revalidate the seven canaries?

This is a software-migration regression check, NOT seven new Q-Chem calculations.
The old reader intentionally rejected the expanded top-level dependency list.
The new explicit reader must demonstrate both that only the known additive
module is accepted and that real source/raw-output/Q4/publication evidence still
reconstructs the accepted features, corrected fixed energies and grid differences.
Unit tests alone cannot establish this on the actual chemistry artifacts.

Revalidation rereads existing input/output/orbital files and checks hashes and
numerical reconstruction under unchanged tolerances. It does not regenerate
orbitals, rerun SCF or rerun native feature stages. It is needed for this reader
transition and evidence release, not a new scientific canary campaign.

## Completed checks

- Verified clean commit `0a22faff23b6251a4e384b7e5abcd44eff433b88`.
- Full suite **228 passed in20.17s**, including31 new compatibility/ECP cases.
- Shell syntax and git diff --check pass; no committed runtime fixes required.
- New corrected reader: **7/7 native/source/artifact/numerical readbacks PASS**.
  Existing matrix validation also passes. Six additional canaries are now
  accepted reuse outside the224 pilot species: total230 accepted species.
- Test/readback evidence:
  `revwb97m2/results/2026-09-09-generation-compat-tests-readback.json`.
- Kept native ECP validation distinct:21 input derivation/reference tests pass,
  but their new native feature jobs have not run. They remain a gateway cohort.

## Manifest preparation

Added the reproducible orchestration helper
`revwb97m2/scripts/freeze_full_training_execution_v1.py`. It uses the committed
generator with two hashing workers, writes exclusive new manifests, checks each
through its loader and confirms each disabled release is rejected. It does not
alter production/scientific code, copy orbitals, execute Q-Chem or submit jobs.

Target folder: `revwb97m2/manifests/full_training_execution_v1`.
Each execution manifest pins authoritative and derived inputs, complete source
orbital trees and qarchive hashes, basis/spin metadata, code/spec/build/evidence,
isolated data/scratch roots, native stages and existing resource requirements.

| Cohort | Species | CPUs/task | Requested GiB | Wall cap(hours) |
| --- | --- | --- | --- | --- |
| Ordinary14 |1916|8|14|72|
| Ordinary21 |286|8|21|72|
| Ordinary35 |182|8|35|72|
| Ordinary62 |106|8|62|72|
| Ordinary117 |28|8|117|72|
| Ordinary227 |23|16|227|336|
| Ordinary557 |7|16|557|336|
| Embedded-ECP gateway |21|8|14|72|

At most500 species per manifest is an indexing/review grouping, NOT a concurrent
running-task limit or mandatory serial submission policy. Four14GiB ordinary
manifests plus six other ordinary classes and one ECP gateway comprise11 plans.
The common launcher has an array0-0 placeholder; release/submission must use the
actual plan's array range and CPU/memory/walltime. No `%8` cap and no lr_lowprio.
Routes in frozen plans are inventory defaults, not a current queue recommendation;
reviewed release overrides select actual partition/account/QOS without rewriting
scientific inputs. Large-memory classes remain subject to resource review.

Retained outputs under approved data-tree species namespaces;
disposable scratch under `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2`.
Copy-byte totals count source copies per stage only, not new native scratch,
logs, retained failures or existing storage. No cleanup occurred.

## Final freeze acceptance

**PASS:**11 manifests,2569 generation species,230 validated reuse species,
complete2799-species partition with no duplicates/overlap/omission.15412 native
stages (15286 ordinary +126 ECP gateway). Minimum source-copy bytes2757002202056,
approximately2.51TiB; available shared filesystem bytes2755506161582080 at audit,
comfortably above copy lower bound plus557GiB headroom. This is not a reservation
or final scratch-space estimate. All execution namespaces absent and all release
drafts disabled. Each frozen plan's recorded input/tree/qarchive hashes agree.

Added `revwb97m2/scripts/audit_full_training_execution_v1.py` to preserve the
independent cross-manifest check. The freeze and audit orchestration helpers are
the only new code files this turn; committed scientific/generation runtime files
were not changed. These helpers ran the actual preparation/audit; the228-test
suite was run against the committed implementation before manifest preparation.

Artifacts: `summary.json` in the execution folder and
`revwb97m2/results/2026-09-09-full-training-execution-freeze-audit.json`.
Summary SHA2566efff05a8c88f52ab7616d2d53cfb32c66dc8cdb8cc324aa7334e3d1cac7cd11.
Execution folder is approximately64MiB of versioned JSON contracts/drafts,
not native outputs or orbital copies. Manifest set is complete and ready to commit.

## Next gate

After final freeze acceptance: user execution-manifest commit, then live
partition/account/QOS/array limits/storage/duplicate review and explicit approved
release. ECP gateway release flag stays false until authorized for that cohort.
No jobs are submitted by freezing. Validate native results and assemble exact
1498x292 plus both grid matrices before bounded full-matrix MIO/pre-bulk gates.
