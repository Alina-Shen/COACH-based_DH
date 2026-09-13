# Step 2 baseline and provenance — 2026-09-12

Step 1 remains complete (50 freeze/semantic checks revalidated this session).
Step 2 is now **complete**. See results/step2_complete.md; earlier entries below preserve the work history. The frozen
18-step index and scientific specification, including fixed omega=0.27, are unchanged.
Solver selection is deferred by the user and does not block these steps.

Completed:
- Added a reproducible read-only audit script and source SHA-256 manifest covering
  reference COACH Python implementation, documentation, paper PDFs, fixture geometries
  and outputs, and all listed files in six predeclared source scratch samples.
- Parsed original COACH water and triplet-carbon regression outputs. Printed
  component sums agree with printed SCF totals by +1.10305e-10 and -3.33742e-11 Eh.
  Carbon uses kinetic + nuclear attraction + SEOQF instead of water's one-electron
  columns; the audit handles both explicitly and rejects missing components.
- Independently evaluated geometry-only D4-ATM for L14_2a with the reference
  parameters; discrepancy 2.16261e-12 Eh (tolerance 1e-10 Eh). No SCF was run.
  The geometry container basis is irrelevant to this D4 calculation.
- Five targeted tests pass, including missing-component and corrupted-energy rejection.
- Read and hashed three source samples per dataset. GSCDB137 G2RC_39,
  Pol130_BeH20+, Pol130_PS0+ each have empty 800-byte qarchive.h5/archive.h5
  containers and nonempty legacy scratch 53.0/54.0/58.0/819.0/99.0.
  BigNC L14_PHE, vL11_3a, L14_2b_monA each have 59 datasets in qarchive.h5,
  including two spin sets of MOs/densities, basis metadata and stored energy.
  Dataset shapes and scalar values are captured; numerical orbital validity is untested.
- No .in/.out files appear immediately inside these six scratch directories.
  Fixture banners show Q-Chem 5.4.2 for water/carbon and 6.3.1 for L14_2a.
  These do NOT identify the builds that generated the supplied scratch.

Remaining Step 2 exit requirements:
1. Obtain original generating input/output locations and exact COACH source/build
   identity for both supplied roots. Verify omega, functional coefficients, basis,
   spin, grid, SCF convergence and dispersion conventions against those records.
2. Verify a native legacy-scratch reading route for GSCDB137. Empty HDF5 containers
   are not evidence that the legacy orbitals are absent or corrupt.
3. Reconstruct parent COACH energy from representative supplied orbitals with
   no orbital update and compare against matching original output. Printed fixture
   arithmetic and independent D4 alone do not satisfy this requirement.

All source files remain read-only. No orbitals copied, production jobs submitted,
new SCF performed, or solver installed. Full coverage/import remains Step 5.

Artifacts: `scripts/audit_step2_baseline.py`, `tests/test_step2_baseline.py`,
`manifests/step2_provenance_audit_v1.json`, `results/step2_baseline_audit_v1.json`,
`results/step2_tests.log`, `results/step2_audit.log`, and mutable `manifests/progress.json`.
Run with the existing dh Python environment, `-B`, `OMP_NUM_THREADS=1` and
`OPENBLAS_NUM_THREADS=1`; the script sets TMPDIR to coach_mp2/runtime.

## Subsequent user clarification and native pilot

User supplied GSCDB/qchem_inputs as input authority (replace METHOD with COACH),
accepted absent historical outputs and empty HDF5, and authorized one or two
system reproducibility tests. This supersedes the demand above for unavailable
historical outputs: original outputs are useful but are not mandatory. Historical
generating build remains unknown. All ten Analysis CSV headers lack COACH; a
matching reference location has been requested. Existing COACH fixtures provide
a provisional matched-geometry/basis/grid comparison for water and carbon.

Prepared/staged four distinct scratch cases for SIE4x4_h2o and 16_C_AE18:
zero-SCF saved-density evaluation and separate SCF repeatability per species.
Only METHOD, SCF_GUESS READ, SCF_FINAL_PRINT 1, and (fixed mode) MAX_SCF_CYCLES 0
change. All other source input settings remain unchanged. Small legacy files are
hash-verified on staging; no empty HDF5 copied. Runtime wrapper/executable/source
identity is hashed in manifests/step2_pilot_v1.json. Existing trunk COACH source
has expected omega/HF/VV10/D4 constants. Source tree is read-only.

Job 25820274 submitted on mhg/mhg/normal: 4 CPUs, 8 GB, one hour; observed running.
Outputs: /clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step2_pilot_v1.
Scratch: /clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step2_pilot_v1.
Diagnostic SCF now explicitly authorized; production fixed-orbital rule unchanged.
No solver switch or bulk production submission. Completion awaits pilot results
and the accepted reference comparison.

## Final pilot outcome

Job 25820274 COMPLETED 0:0, 5m36s, MaxRSS 1028704K. Water converged in
5 cycles (-76.4335179440 Eh; difference -1.00002e-10 Eh), carbon in 7
(-37.8454603141 Eh; zero difference at printed precision). Both pass 2e-6 Eh
against existing COACH fixtures. Zero-cycle runs successfully read legacy scratch
but skip energy evaluation: not a fixed-orbital energy pass. Step 2 remains open
for dedicated no-update energy reconstruction and COACH Analysis reference
clarification. See results/step2_pilot_v1.json for machine-readable evidence.

## Paper workbook reference resolved

User supplied /clusterfs/mhg-data/yaoshen/coach-based_dh/coach/paper/COACH_raw_data.xlsx.
The raw_data sheet reports reaction/property values. Cell D298 (COACH, AE18_6)
is -23748.38489725949 kcal/mol. DatasetEval maps AE18_6 to 1*16_C_AE18.
Using the existing 627.50947406 conversion yields -37.8454603141 Eh, matching
the carbon pilot at reported precision (floating-point difference 7.1e-15 Eh).
Workbook Reference-column conversion was cross-checked against DatasetEval.
Water occurs in SIE4x4_13–16 multicomponent reactions and has no direct absolute
energy entry; its fixture comparison remains PASS. No additional jobs required
for the carbon paper-data cross-check. Reference location is resolved; the
dedicated zero-update energy evaluator remains the open Step 2 gate. Source
workbook is read-only and SHA-256 recorded in step2_workbook_reference_v1.json.

Final completion: job 25821657 passes fixed-orbital energy validation (44 checks), six tests pass, Step 1 recheck passes. Next step 3. See step2_complete.md for the density-roundoff acceptance clarification and scope.
