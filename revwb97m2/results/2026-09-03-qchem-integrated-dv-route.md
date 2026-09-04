# Q-Chem integratedDV route decision

Date: 2026-09-03

Decision: replace fresh production PySCF omegaB97M-V SCF with reuse of the
complete copied Q-Chem orbital archives and native Q-Chem integratedDV output.

Evidence:

- canonical copied inventory: 14,006/14,006 molecular records have
  `qarchive.h5`;
- the old `IDV_print` working copy was inspected read-only;
- the maintained full COACH layout is 96x180, not the old branch's truncated
  96x100 print;
- the new trunk implementation is opt-in, preserves the selected XC functional,
  and prints all 180 columns;
- syntax checks passed for the evaluator and driver;
- the historical `gamma_ss=0.2` is intentionally replaced by the frozen
  revwb97m2 value `0.01`; selected columns `(64,154,166)` are validated against
  the project-owned NumPy implementation (`max_abs=3.4694469519536142e-18`,
  `allclose=True` at `rtol=2e-13, atol=2e-14`).

Production remains gated on a pinned full Q-Chem build, imported-orbital native
smokes, extraction/provenance validation, specification amendment, regenerated
resource planning, and explicit submission approval.
