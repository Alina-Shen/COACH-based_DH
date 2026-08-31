# Closed-shell reference-policy audit

## Decision

Use an unrestricted Kohn-Sham reference for closed-shell singlets as well as
open-shell species. This is a computational-reference policy, not an instruction
to seek a broken-symmetry solution: a spin-zero UKS calculation can converge to
equal alpha and beta densities. Spin contamination and stability must still be
recorded.

## Evidence

- The COACH paper and its 38-page SI contain no explicit `RKS`, `UKS`,
  `restricted`, or `unrestricted` reference-policy statement. They therefore do
  not independently establish the choice.
- The maintained training-data generator
  `coach/1_data_generation/pyscf_integrated_dv.py` constructs `dft.UKS(mol)`
  unconditionally.
- The maintained end-user driver defaults to UKS and offers RKS only through an
  explicit `--rks` option for closed-shell inputs.
- Every one of the 14,006 verified core Q-Chem inputs and every one of the 3,652
  pinned official AdditionalSets inputs sets `UNRESTRICTED True`.

Therefore the assumption “UKS for all inputs” is correct for the released
workflow and input corpus, with the terminology caveat that the Q-Chem files
express this as `UNRESTRICTED True` rather than the PySCF class name `UKS`.
