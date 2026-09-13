# Step 4 complete — molecular input and basis authority

Date: 2026-09-12. Solver-neutral; next frozen step is 5. Omega remains 0.27.

## Work performed and rationale

1. Audited all 17,452 energy-role species against current GSCDB inputs and the pinned revwb97m2 molecular/basis records: 14,006 core, 75 BigNC and 3,371 GDB9-W1-F12. The 206 OPT entries remain excluded. Geometry, charge, multiplicity, ghost centers and role membership are preserved.
2. Resolved the 12 initial discrepancies in project-local derived inputs. Split concatenated SCF_GUESS/SCF_CONVERGENCE lines for BH9_05_17TS and BH9_05_7TS, and SCF_GUESS/MEM_STATIC lines for FH51_n-nonane and ISOL24_i8e. These are syntax repairs, preserving both intended settings.
3. Inherited the pinned explicit auxiliary basis for AE11_Yb (AUX_BASIS_CORR GEN), retaining its original all-electron orbital basis, N_FROZEN_CORE 0 and absence of ECP. The named source auxiliary basis lacks Yb. Inherited the pinned explicit orbital basis and PURECART 111 for seven O24x5_he2 entries (0.9, 1.0, 1.2, 1.5, 2.0, monA, monB), matching the reference authority instead of relying on their source named-basis spelling.
4. Made the reference project's explicit auxiliary defaults visible in all 3,446 external templates: rimp2-def2-TZVPPD for BigNC and rimp2-def2-TZVP for GDB9-W1-F12. No auxiliary basis was generated or newly selected. Recorded these reconciliations in a versioned overlay without changing the frozen Step 1 specification.
5. Changed METHOD to COACH in 14,006 core templates; external inputs already specify COACH. Preserved other input blocks/settings except the enumerated repairs. These are scientific input templates, not runnable production inputs: later stages must apply validated no-update SCF, grids, MP2 and resource controls.
6. Resolved orbital, auxiliary and ECP definitions using the pinned reference bridge and compared all definition hashes, shell/AO counts and electron counts. All 17,452 match. There are 593 embedded orbital bases, one embedded auxiliary basis, 97 embedded ECPs and 367 implicit named-basis ECPs; 16,988 species have no ECP. Electron/spin parity also passes. The four reference auxiliary library files match their frozen hashes and the current Q-Chem runtime copies byte-for-byte.
7. Staged original and derived input bytes in a deterministic 34,904-member tar, with detailed metadata and the historical initial audit, under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step4_inputs_v1` (about 130 MB). Kept a lightweight CSV, source pins and artifact hashes in the code root. Original GSCDB, reference inputs and libraries were only read.
8. Added an independent archive readback validator that checks current source hashes, allowed transformations, exact geometry/basis blocks, role order, structural dimensions and library identity. All 17,452 inputs pass. Added 15 tests covering malformed input, unauthorized geometry/grid/ECP edits, auxiliary assignments, ghost preservation and rem-key matching; all pass.
9. Froze Step 4 artifacts and updated mutable progress, code/data READMEs, the live project plan table and a new dated project-note chapter. Earlier step artifacts and the 18 frozen step IDs remain unchanged.

## Evidence and remaining boundary

- [Reconciliation policy](../configs/step4_input_authority_v1.json)
- [Snapshot and source hashes](../manifests/step4_snapshot_v1.json)
- [Species manifest](../manifests/step4_inputs_v1.csv)
- [Validation](./step4_validation.json)
- [15 tests](./step4_tests.log)
- [Artifact freeze](../manifests/step4_freeze_v1.json)

No orbitals were imported or changed, no Q-Chem/Slurm jobs ran, and no solver was selected or used. Matching the supplied COACH archives to these authoritative basis definitions remains Step 5, particularly for the repaired helium/Yb cases. Definition/count agreement here does not establish archive AO ordering or numerical integral agreement. Pause before backend-dependent work, expected Step 14, if no solver has been chosen.
