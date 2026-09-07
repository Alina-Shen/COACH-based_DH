# Step 14 recovery and real-reaction assembly complete

All 38 species and the unchanged 20-reaction cohort pass. Recovery array
25634381 completed seven tasks with exit 0:0 in 13–26 seconds, maximum batch
MaxRSS 943368 KiB (0.900 GiB). No Q-Chem rebuild or iterative SCF was needed.

## Changes and rationale

- The user's label mapping is correct: TOTAL SS RI-MP2_ENERGY denotes total
  same-spin energy; TOTAL OS RI-MP2_ENERGY denotes total opposite-spin energy.
  Both are already scaled in these legacy outputs. New versioned helpers in
  `step14_recovery_v2.py` accept that dialect and preserve the original frozen
  parser for reproducibility. Modern output delegates to the original parser.
- Legacy recovery uses a_ss/a_os=0.340960 from the coefficient summary, not
  rounded 0.34 printing. It checks SS+OS+singles against the legacy RIMP2 total
  to 5.2e-9 Ha (its 8-decimal display precision). The inconsistent final
  scE_PT2c remains a diagnostic instead of being used as a source of raw PT2.
- All six Dip146 cases were independently run with EXCHANGE wB97M-V,
  CORRELATION RIMP2, SCS=3, SSS_FACTOR=SOS_FACTOR=1000000, zero SCF cycles,
  MP2_RESTART_NO_SCF TRUE, the same orbitals, basis/frozen-core settings and
  applied field. Output confirms the unchanged wB97M-V parent and unit factors.
  Maximum spin error against recovered raw values: 1.7363e-10 Ha, versus a
  frozen 2e-8 Ha limit. This experimentally verifies the scaling interpretation.
- Hydrogen PT2 is explicitly zero only after verifying one alpha and zero
  beta electrons. Its successful existing scalar/grid outputs are reused; only
  a fresh fixed-energy HF print job is run. No synthetic PT2 output is made.
- Legacy VV10 is labeled DFT Correlation Energy; the recovery parser supports
  this label in the established pure-VV10 scalar job.
- Fixed energy uses the final Nuclear Repu. Energy, which includes the nuclear
  applied-field contribution, instead of the earlier bare nuclear repulsion.
  Maximum pure-HF reconstruction error is 4.5001e-9 Ha versus 2e-8 Ha allowed.
- `run_step14_recovery_v2.py` uses new isolated scratch directories, verifies
  copies and source archives, runs unit/fixed jobs, and publishes only passing
  recovered vectors. `complete_step14_recovery.py` checks every source tree,
  all 114 Q4 grid artifacts, recovery output, scalar values, direct D4 values,
  and grid differences; independently recomputes reaction sums via a 20x38
  stoichiometric matrix; then atomically publishes the full reaction artifact.
- The resubmission skill informed duplicate-job and resource checks. Its
  destructive scratch-cleaning helper was inapplicable to this approved
  isolated-archive workflow; all original calculation evidence was retained.

## Attempt history

Initial recovery v1 / job 25634305 failed all seven tasks at scalar parsing
because the newly added helper omitted the legacy VV10 label fallback. A
real-output preflight caught this; a stop request was issued, but all tasks
had already failed. The failed code, frozen contract, and output directories
are retained. Version 2 adds the fallback and field-aware fixed-energy parsing
with regression tests. The original 31 successful species and all grid runs
were reused unchanged.

## Evidence and artifacts

- `manifests/reaction_features/step14_recovery_v2.json`: frozen recovery code,
  cohort, cases, unit comparison tolerance and hydrogen policy.
- `manifests/reaction_features/step14_recovery_complete_v2.json`: independent
  aggregate validation and actual Slurm accounting; SHA-256
  c0a921691e098732c7ba83d2b9e80541a4096b516d0abbeb625fba13ec6c3c58.
- Output directory:
  `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/reactions_recovery_v2`.
  Contains feature_matrix.npy (20x292), fixed_energy.npy, reference_energy.npy,
  target.npy, objective_weight.npy, both grid-difference matrices, reaction
  names, validation, and ASSEMBLY_COMPLETE. Matrix SHA-256:
  37fd3ac909820e04a0ce21c1d3185a0b276f736443d91641cc9ed7805053ae32.
- 64 repository tests pass; git diff --check and published artifact readback
  hashes pass. Three recovery tests cover spin precision/identity refusal,
  the one-electron guard/VV10 label, and nuclear applied-field energy.

Step 14 is complete for the frozen R2 292-feature cohort. Next recommended
work is Step 15 preparation: named R1/R2 optimizer inputs and a bounded MIO
pilot with independent VV10/PT2/D4 coefficient bounds. Q7 bulk authorization
remains separate. The frozen v1 launcher still pins its original parser;
general production integration of the versioned recovery helpers must be
explicitly reflected in a new production contract.
