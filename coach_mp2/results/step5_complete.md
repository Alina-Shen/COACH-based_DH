# Step 5 available-source scope complete — 2026-09-12

Step 5 is complete for the 14,081 supplied species. The user-deferred 3,371
GDB9-W1-F12 species remain a future Step 5/feature/assembly prerequisite before
Step 17 assessment. This does not claim full final-domain readiness.

## Work performed and explanations

1. Finished the original 14,077-species immutable import and preserved four
   supplemental sources (He3_47/48/49 and ISOL24_i8e). All 14,081 available
   species are published: 178,586 files, 805,644,039,802 bytes. Each top-level source file was SHA256 hashed while
   streaming, checked by destination readback, checked for source size/mtime
   drift, and published by per-species rename with read-only files. Nested
   fragment directories are explicitly listed as excluded parent-restart data.
2. Refreshed the entire 17,452-species structural inventory with the hardened
   parser and active basis amendment. 14,078 ordinary passes plus three known
   He3 trailing-byte cases; 3,371 GDB9 absent/deferred. Previous inventory retained.
3. Applied the user-approved ISOL24_i8e def2-QZVPP orbital basis (1,884 AOs),
   preserving RIMP2-def2-QZVPPD auxiliary basis. Native compatibility now tested;
   this remains a documented single-species departure from the reference projects.
4. Built an isolated Q-Chem executable that skips post-SCF orimo only for NoSCF.
   The shared source, libraries and executable were read-only; the project-local
   source patch, compile/link commands, binary hash and 276 shared dependency
   hashes are recorded. Normal SCF paths retain their original orientation logic.
   Build job 25827268 passed. No new SCF optimization was performed.
5. Ran six native fixed-parent regressions (job 25827314): water, carbon,
   He3_47/48/49 and ISOL24_i8e. Explicit READ, zero cycles, old driver,
   MP2_RESTART_NO_SCF, NO_ORTHO and zero guess mixing preserve source orbitals.
   All use omega 0.27; the patched orientation marker must appear.
6. Native audit job 25828892 passed all six cases: all 53.0 bytes unchanged,
   immutable imported-source hashes unchanged against staging provenance, finite data, independent source/output
   occupied-density reconstruction within the Step 2 normwise bound, component
   energy closure, and unchanged parent energies where prior comparisons exist.
   Native overlap matrices also validate source Ctranspose S C against identity
   within the declared 1e-6 compatibility tolerance. No He3 trailing bytes were
   truncated; the earlier MO-byte failures are resolved without relaxing the gate.
7. Independently audited import receipts, scope, source roots, read-only files
   and legacy dimensions. An early audit correctly stopped at a still-unpublished
   archive; only the post-completion audit is used as the passing gate. Per-file
   hash readback occurred before publication; no redundant full 805GB rehash is
   claimed. Receipt hashes bind the complete imported set.
The first full native audit (25827432) stalled on an external COACH3 header
   read; it and its pending finalizer were cancelled. The replacement audit
   uses verified project imports, requires receipt and staging-hash agreement,
   and retains all numerical tests. It does not rehash live external originals.
8. Reran six input/copy/corruption tests and two nonzero-dispersion/double-counting
   tests; all eight pass. The seven printed components close against the native SCF-cycle energy;
   printed D4 is recorded separately. The v3 audit incorrectly added D4 and failed;
   v4 corrects that bookkeeping without changing the tolerance or native outputs. Confirmed Step 3/4 frozen
   artifacts unchanged. Froze the new Step 5 evidence, recorded the validated
   runtime contract, and updated progress, READMEs, STATUS.md, live plan and notes.

## Boundaries

These checks establish available-source import integrity and six-case native
compatibility, not full-domain numerical validation or proof of the unknown
historical generating build/basis. Legacy dimensions alone cannot prove basis
identity. MP2, virtual-space/denominator/frozen-core checks and full feature
production remain their own steps. Next stable step is 6. GDB9 stays deferred.
Solver choice is not needed for this work; pause before backend-dependent work.

All writes were confined to coach_mp2 code, its heavy-data/scratch roots and
project notes. Original archives, GSCDB and other projects were not modified.

## Evidence

- [Inventory](./step5_inventory_v2.json)
- [Import audit](./step5_import_audit.json)
- [Native six-case audit](./step5_native_v4_validation.json)
- [Runtime build provenance](../manifests/step5_no_orientation_build_v1.json)
- [Native validation protocol](../configs/step5_native_v2_protocol.json)
- [Tests](./step5_tests_v2.log)
- [Freeze](../manifests/step5_freeze_v1.json)
