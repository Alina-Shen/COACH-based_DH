# Published omegaB97M(2) executable probes

`qchem_water_probe.in` is a deliberately small executable-authority probe. It
tests whether the pinned local Q-Chem 6.1 development build recognizes native
`wB97M(2)` and reports a converged xDH energy using an all-UKS omegaB97M-V
parent, frozen-core RI-MP2, and explicit numerical grids. The def2-SVP basis is
for method/fixture mechanics only; it does not reproduce the paper's
def2-QZVPPD assessment convention.

The non-overwriting Slurm runner writes each attempt under its job ID below
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step11/qchem_water_probe`.
Its result cannot become a trusted regression fixture until the output method,
parent/reference, component, and terminal-success records have been audited.

`qchem_h2o_sw49_probe.in` uses the exact geometry, def2-QZVPPD orbital basis,
RI auxiliary basis, all-UKS policy, and grids of the existing `h2o_SW49`
checkpoint fixture. Select it by submitting with
`--export=ALL,STEP11_QCHEM_PROBE=qchem_h2o_sw49_probe`.
