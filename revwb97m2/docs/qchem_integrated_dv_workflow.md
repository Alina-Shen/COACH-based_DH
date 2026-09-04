# Q-Chem fixed-orbital integratedDV workflow

Date: 2026-09-03

Status: implementation landed in the new Q-Chem trunk; build and native smoke
validation remain gates before production.

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
3. Derive one input per required feature grid. The orbital-reuse changes remain
   `MAX_SCF_CYCLES 0` and `GEN_SCFMAN FALSE`; set the requested Q-Chem XC grid
   for `250974`, `99590`, or `75302` without changing the omegaB97M-V method.
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

The driver recomputes Q-Chem's existing 10 meta-GGA density variables for each
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
- Build a pinned full Q-Chem executable and record its SVN revisions and binary
  hash.
- Run at least one restricted and one unrestricted imported-orbital smoke case
  on all three grids. Compare full matrices and selected rows to the maintained
  reference implementation within a declared tolerance.
- Implement and test the delimited-block extractor, atomic artifact publication,
  restart behavior, and missing/corrupt-archive refusal.
- Amend and revalidate the frozen scientific specification before changing the
  production generator. No bulk job submission is authorized until those gates
  pass and the user gives separate approval.

The active PySCF pilots may finish as comparative timing/stability evidence,
but their completion is no longer a prerequisite for choosing the production
density source.
