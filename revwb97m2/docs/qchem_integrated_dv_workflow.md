# Q-Chem fixed-orbital integratedDV workflow

Date: 2026-09-03

Status: Q4 complete. The pinned Q3 native comparisons pass, and the strict
final-complete-block extractor, atomic no-overwrite publisher, and restart
validator pass fixtures plus all six real three-grid cases. Q6 resource and
Step-13 integration work remains before production review.

## Decision

Do not regenerate omegaB97M-V densities with PySCF for production. Reuse the
published Q-Chem omegaB97M-V orbitals already copied to
`/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2`, and ask Q-Chem to evaluate
and print integratedDV on those imported densities.

The 2026-08-28 canonical inventory audit found all 14,006 GSCDB molecular
records and all 14,006 corresponding `qarchive.h5` files in that project copy.
A fresh manifest-to-filesystem check on 2026-09-03 again returned
`canonical=14006 present=14006 missing=0`. A raw scan found 14,017 archives in
14,023 directories; the extras are the previously documented noncanonical
debug/backup records, so canonical-manifest membership—not the raw directory
count—is authoritative.

## Execution contract

1. Resolve each species through `manifests/gscdb137/species_manifest.csv` and
   require its copied `qarchive.h5` before preparing a job.
2. Copy the source orbital directory into a non-overwriting run directory. Keep
   the authoritative Q-Chem input immutable and record hashes/provenance.
3. Derive one input per required feature grid. Set `MAX_SCF_CYCLES 0` and
   `GEN_SCFMAN FALSE`, select the libks XC Fock engine with `XC_FXC 3`, and set
   the requested Q-Chem XC grid for `250974`, `99590`, or `75302` without
   changing the omegaB97M-V method or imported density.
4. Run the pinned build with `QCHEM_PRINT_INTEGRATED_DV=1`. The switch is
   opt-in and accepted only for an MGGA functional.
5. Require one final complete block delimited by `COACH integratedDV begin`
   and `COACH integratedDV end`, with the label `integratedDV` and shape
   96x180. If a Q-Chem execution produces multiple complete energy evaluations,
   retain the final complete block and record that count.
6. Transpose the printed matrix to the COACH 180x96 convention, select semantic
   rows `(64,154,166)`, and assemble the three-grid semilocal artifacts. Preserve
   full matrices until hashes and selected features have been validated.
7. Keep the existing scalar-feature and assembly boundaries independently
   resumable. Regenerate the Step-13 resource plan so no fresh PySCF parent-SCF
   boundary is on the production critical path.

## Q-Chem implementation boundary

Only `/clusterfs/mhg-data/yaoshen/qchem/trunk/libks` was changed. The historical
`/clusterfs/mhg/yaoshen/qchem/IDV_print` working copy is a read-only reference
and was not modified. The port does not inject a functional, alter omegaB97M-V,
or change SCF convergence behavior.

The active fixed-orbital route must use `XC_FXC 3`: Q-Chem's default legacy XC
Fock engine does not enter the libks dispatcher. The libks dispatcher performs
the ordinary XC Fock build, then invokes the energy driver for the opt-in
integratedDV emission. The driver recomputes Q-Chem's existing 10 meta-GGA density variables for each
screened grid batch, passes them to the isolated COACH integratedDV accumulator,
sums the full 96x180 result across OpenMP batches, and prints it only when the
environment switch is enabled.

The historical branch's same-spin compression parameter was `gamma_ss=0.2`.
The revised project's frozen scientific definition is `gamma_ss=0.01`, so the
new evaluator deliberately uses `0.01`; copying the historical constant would
silently make selected semantic row 154 incompatible with this project.

## Validation and remaining gates

- Both modified translation units pass `g++ -std=c++14 -fopenmp -fsyntax-only`
  against the current trunk headers.
- A deterministic selected-feature test against the frozen
  `revwb97m2/integrated_dv.py` definition passed after comparing printed columns
  `(64,154,166)` after transposition: shape 3x96, maximum absolute difference
  `3.4694469519536142e-18`, and `numpy.allclose=True` at
  `rtol=2e-13, atol=2e-14`.
- The pinned full Q-Chem build at revisions 48798/1666 passes: executable
  SHA-256 `0cfc9b426f71e9a7e8fd57990cd09d3241ec458742e319839bd7f05fae571084`,
  complete libks diff SHA-256
  `a7d9660e8fccc293691639cab38c4fe29a1496b1974383aa46ade92ba9eb92c3`,
  and zero unresolved dynamic dependencies.
- An unrestricted H2 archive-read probe with zero SCF cycles and `XC_FXC 3`
  emitted exactly one finite 96x180 block and terminated normally. This closes
  Q2 capability validation but does not substitute for Q3.
- Q3 passed after freezing `rtol=2e-12` and `atol=2e-12` hartree before results.
  `h2o_SW49` (closed-shell singlet UKS) and `12_NH2rad_HNBrBDE18`
  (open-shell doublet UKS) each passed on grids `250974`, `99590`, and `75302`.
  All six runs read the copied MO archive, terminated normally, emitted one
  finite 96x180 block, and agreed for the full matrix and selected rows. The
  largest absolute full-matrix error was `3.552713678800501e-15` hartree.
  See `../results/2026-09-04-q3-native-qchem-gateway-complete.md` and
  `../manifests/qchem_gateway/q3_validation_v1.json`.
- Q4 passed. The strict extractor rejects zero, malformed, truncated,
  wrong-shaped, nonnumeric, and nonfinite blocks; records and selects the final
  valid block when multiple complete blocks exist; and publishes 180x96, 3x96,
  and flattened 288 arrays through a validated atomic rename. Restart mode
  reuses only an independently valid immutable boundary. Missing, changed, or
  ambiguous archives and invalid existing boundaries stop without overwrite.
  See `../results/2026-09-04-q4-qchem-feature-publication-complete.md` and
  `../manifests/qchem_gateway/q4_validation_v1.json`.
- Amend and revalidate the frozen scientific specification before changing the
  production generator. No bulk job submission is authorized until those gates
  pass and the user gives separate approval.

The active PySCF pilots may finish as comparative timing/stability evidence,
but their completion is no longer a prerequisite for choosing the production
density source.
