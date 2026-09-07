# Step 14 terminal audit — 2026-09-06

Step 14 remains in progress: array 25615636 finished with 31 successful tasks
and seven failures. No reaction matrix was published.

- Audited every task's terminal accounting and all 38 source input/orbital
  trees; source hashes remain unchanged. All 114 Q4 grid publications validate,
  including those belonging to the seven incomplete species.
- All 31 completed species pass eight boundary validations, reaction-ready
  hashes/identity, scalar and fixed-energy reparsing, finite 292-vector checks,
  and exact comparison-grid difference reconstruction.
- Tasks 26–31 (Dip146_HF2+/−, Dip146_LiN2+/−, Dip146_NaLi2+/−) terminated Q-Chem
  normally but failed scalar publication. The alternate RI-MP2 driver prints
  `TOTAL SS RI-MP2_ENERGY` / `TOTAL OS RI-MP2_ENERGY`, which the current parser
  does not accept. It also rounds printed spin scaling factors to 0.34;
  recovery must establish the full-precision scaling semantics, not merely
  add regex aliases. For HF2+, printed SS+OS is -0.1195365443 Ha whereas the
  final scaled PT2 component is -0.1192469573 Ha. Existing identity checks
  cannot be bypassed to promote this result.
- Task 36 (W4-17_h) failed in Q-Chem's generalized perturbation code with
  `std::bad_alloc`, after reporting one alpha and zero beta electrons. Batch
  MaxRSS was 711960 KiB, so the record does not indicate a Slurm OOM. The
  one-electron doubles-zero case needs an explicit validated recovery route.
- The missing species block Dip146_101, Dip146_131, Dip146_140, and
  TAE_W4-17_110. The frozen 20-reaction gate cannot be completed with the
  remaining 16 reactions.
- Correction to prior explanatory notes: these Dip146 +/− suffixes are
  applied-field cases (the input contains `$multipole_field`), not molecular
  charge changes. Recovery must preserve the applied field and check the
  fixed-energy field contribution. Actual ionization entries elsewhere in the
  cohort do change charge.
- Added `revwb97m2/scripts/audit_step14_cohort.py` to perform the read-only
  artifact audit and retain actual Slurm accounting in
  `revwb97m2/manifests/reaction_features/step14_terminal_audit_20260906.json`.
- Verification: 61 tests pass. Existing scientific code, frozen contracts,
  failed outputs, and completed artifacts were preserved. No reruns, Q-Chem
  rebuild, or partial reaction publication were performed.

Recommended next action: prepare a versioned recovery for the six field-case
scalar outputs and the one-electron PT2 case, retaining original evidence and
requiring independent scalar/fixed-energy validation before reaction assembly.
