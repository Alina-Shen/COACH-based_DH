# Step 2 complete — COACH baseline and provenance

Completed 2026-09-12. Step IDs and scientific specification remain unchanged.
Next step: 3, immutable data roles and metrics. Solver choice remains deferred.

## What was done and why

1. Inspected the reference project's fixed-energy route and the existing Q-Chem
   6.4.0 source. The general SCF driver skips all energy evaluation at zero cycles;
   the older driver can evaluate a fixed density with MP2_RESTART_NO_SCF TRUE.
   This flag suppresses diagonalization; METHOD remains COACH, with no MP2 job.
2. Prepared fresh water and triplet-carbon scratch copies with verified source
   hashes. Changed GEN_SCFMAN to FALSE and added MP2_RESTART_NO_SCF TRUE to the
   earlier zero-cycle inputs, preserving basis, grid, spin, and omega=0.27.
3. Ran job 25821443 (completed 0:0, 1m03s). Its energy calculation worked, but
   the initial GDM guess reorthonormalized the MOs. Rejected this route's integrity
   check and preserved the failed evidence; scheduler success is not validation.
4. Traced the transformation to gesman/GuessMan.C. Prepared fresh v3 cases with
   NO_ORTHO TRUE and ran job 25821657 (completed 0:0, 59s, MaxRSS 592736K).
   No Q-Chem source edits or compilation were necessary. Each job requested
   mhg/mhg/normal, 4 CPUs, 8 GB, 1 hour, after checking live capacity.
5. Validated exact SHA-256 invariance of 53.0 (both MO coefficients and orbital
   energies), all original source files, runtime/source identities and inputs.
   Q-Chem rebuilds 54.0 from those unchanged MOs: density serialization differs
   by at most 2.77556e-17. Thus the initial byte-identical-density expectation is
   superseded explicitly by independent mathematical reconstruction, while the
   exact MO requirement remains unchanged. This is not orbital optimization.
6. Independently reconstructed each spin density as occupied-MO outer products,
   using math.fsum. Both the source and output density must satisfy a normwise
   floating-point bound 16*epsilon*||C_occ||_F^2. The largest errors are under
   0.52% of that bound. A per-entry relative bound was unsuitable for near-zero
   entries; the final bound measures rounding on the whole density's scale.
7. Reconstructed total energy from the printed components. The older driver's
   DFT Correlation term already includes VV10; no double counting. Used its
   final Nuclear Repu. value rather than the less precise geometry printout.
8. Compared with the existing COACH fixtures and carbon's paper-workbook entry.
   Verified normal termination, one Fock evaluation, no-update controls/messages,
   and absence of failure indicators. Added six tests rejecting truncated output,
   missing controls/components, nonfinite input and density perturbation.
9. Rechecked Step 1 (all 50 checks pass), published the completion evidence,
   updated mutable progress/protocol/README and the live notes plan table.
   Prior dated notes and rejected attempts remain intact.

## Results

| System | Fixed-orbital energy (Eh) | Difference from COACH fixture (Eh) | Component-sum residual (Eh) |
| --- | ---: | ---: | ---: |
| SIE4x4_h2o | -76.4335179420 | +1.90001e-9 | 0 at printed precision |
| 16_C_AE18 | -37.8454590857 | +1.22840e-6 | +1.00009e-10 |

Both pass the pre-existing 2e-6 Eh baseline tolerance; closure passes 2e-8 Eh.
Carbon's paper reference is raw_data!D298, AE18_6, COACH column in
/clusterfs/mhg-data/yaoshen/coach-based_dh/coach/paper/COACH_raw_data.xlsx.
The paper comparison gives the same carbon difference. It is a tolerance pass,
not a claim of numerical identity. The earlier separately converged pilots agreed
more closely, but their optimized orbitals were not used for this fixed test.
All 44 native validation checks and six targeted tests pass. Earlier component/
D4 baseline tests and paper-reference checks are retained as supporting evidence.

## Accepted scope and limitations

This completes the two-system Step 2 baseline under the user's accepted policy:
original historical outputs are unavailable and not mandatory; current COACH
method/input/runtime provenance and reproducibility are recorded. The historical
COACH3/BigNC generating build is still unknown. BigNC archive sample provenance
and geometry-only D4 validation exist; no claim of a BigNC fixed-energy pilot or
full archive inventory. Step 5 handles full inventory/import; later feature/MP2
steps still require their own gates. NO_ORTHO must accompany this read-in route.
No bulk production, backend switch, or new SCF optimization in this completion
run. All code/results here, heavy output and scratch in their dedicated permitted
coach_mp2 roots; all reference trees remain read-only.

Primary evidence: results/step2_fixed_v3_validation.json, results/step2_fixed_tests.log,
results/step1_recheck_after_step2.json, manifests/step2_fixed_v3.json,
results/step2_workbook_reference_v1.json, results/step2_fixed_v2_rejected.json.
Recheck: python3.9 -B coach_mp2/scripts/validate_step2_fixed.py
