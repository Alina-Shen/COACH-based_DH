# Exact100-entry numerical pilot complete — 2026-09-08

## Release and native results

Verified user commit `c588b5a574166244256fdff780e1c52ce8439919` and clean worktree
before release. Frozen code/plans, water sidecar, source trees, build/scientific
authorities and corrected seven-canary registry passed fresh checks. Live Slurm
review found idle cm1 nodes (241732MiB), approved lr_qchem/condo_qchem association,
no duplicate user jobs and approximately2.5PiB available on the shared filesystem.
The partition helper was absent, so manual live queries were used.

Created separate approved release JSONs without modifying committed plans or
disabled drafts. Submitted unchanged8CPU/14GiB/72h tasks on cm1; no artificial
concurrency cap and no lr_lowprio. Test-only IDs25726456/25726457 are not real jobs.

| Species | Real job | State/exit | Elapsed | Peak RSS | HF identity error(Ha) |
| --- | --- | --- | --- | --- | --- |
| 11_H2O_TA13 | 25726543 | COMPLETED0:0 | 00:00:19 | 823764KiB | 4.0000145e-9 |
| 3d4dIPSS_Y_GS | 25726544_0 | COMPLETED0:0 | 00:06:48 | 1578164KiB | 2.5000020e-9 |
| 3d4dIPSS_Y_GS+ | 25726544_1 | COMPLETED0:0 | 00:07:19 | 1584212KiB | 2.9999825e-10 |

All stderr files empty. Separate post-job validation reconstructed components
and checked source/native/publication provenance: all3 species/13 stages pass.
HF tolerance remains2e-8Ha. Water VV10 changed0.0207884461 to0.0480091250Ha;
SR reuse difference0 and other291 features unchanged. Y retained authoritative
embedded ECP/basis blocks and existing orbitals. No new SCF, Q-Chem rebuild,
scientific change, historical overwrite or scratch deletion.

## Integration and verification

Added `revwb97m2/scripts/assemble_pilot100_v1.py`:

- `collect`(line8) consumes audited generic publications with current hash checks,
  corrected legacy38 fixed energies, corrected canary evidence and fresh water/Y
  native validators. Handles first16 top-level versus remaining166 per-case plan
  hash schemas explicitly. Historical drivers remain unchanged.
- `assemble_checked`(line61) requires exact100 reactions and224 species; preserves
  original references/weights. Independently multiplies a100x224 stoichiometry
  matrix against species features/fixed energies/both grid differences and checks
  agreement (rtol1e-12,atol2e-10 for summation roundoff, not changed native tolerances).
- `main`(line86) exports arrays and metadata, reads arrays back, records provenance
  hashes and writes a completion marker only after checks pass.

Added `revwb97m2/tests/test_pilot100_assembly.py`: four tests for exact scope and
weights, missing-species refusal, partial-pilot refusal and nonfinite-data refusal.
Full suite186passed in6.49s; git diff --check passes. Added reusable standalone
`revwb97m2/scripts/audit_final_three.py` for the completed post-job readback (refuses
to overwrite its report). No existing source code was modified.

Export: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/matrices/pilot100_v1`.
Contains100x292 feature matrix;100-length fixed/reference/target/weight arrays;
two100x292 grid-difference matrices for99590 and75302; ordered reactions/species;
validation manifest and MATRIX_COMPLETE. All finite, original100 reactions and
all49 selected groups retained. Corrected legacy fixed values are now explicitly
integrated into this production-consumable numerical export (not a blanket change
to the legacy generic reuse API).

Separate process verifies every exported artifact hash and completion marker.
Removing the seven newly unblocked rows reproduces the earlier93-row diagnostic
feature matrix byte-for-byte. Newly included rows are TA13_1/2/3/5/6/7 and
3d4dIPSS_11. Validation manifest SHA256:
`4e22fc55ed9c78609865463c5e08fdef0283abc07d07112dfb508b3fe4791f18`.

Release, submission and readback records reside under
`revwb97m2/manifests/production_generator` and `revwb97m2/results/pilot_execution_v3`.
Heavy numerical/native data remain in the approved data tree; scratch remains in
the approved scf_read tree. No cleanup performed.

## Next checkpoint

The exact100-entry chemical/numerical matrix gate is complete. This is NOT a
100-entry MIO run, optimality certificate, full1498 matrix or bulk fit.
Commit the new integration/tests/releases/reports, then prepare/review the bounded
real100-entry grid-constrained MIO plan (K14 plus an approved representative largerK,
time/memory, ridge objective, starts/restarts and raw/recomputed gaps). Do not infer
solver-gap resolution from successful feature generation. No fitting submitted.
