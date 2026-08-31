# Scientific specification version 4: stability diagnostics

## Decision

Version 4 changes only the stability policy. A converged parent checkpoint
that passes energy reconstruction, immutable-authority hashes, and bitwise
density/selected-feature reload identity is authoritative independently of a
PySCF stability calculation.

Stability is now a separate timed diagnostic for gateway/model-critical or
flagged species. Each selected diagnostic records `stable`, `unstable`,
`indeterminate`, or `unavailable`; an alternative orbital solution is never
adopted automatically. Species not selected for the diagnostic record
`unavailable` with the reason rather than silently implying stability.

## Rationale

The Step-8 `h2o_SW49` internal UKS stability response stayed CPU-bound for
more than 30 minutes and warned that PySCF's response omitted NLC. It was
therefore neither a complete omegaB97M-V stability test nor an acceptable
blocking dependency for checkpoint publication. The validated checkpoint was
recovered without restarting SCF and passed every independent identity check.

## Unchanged science

The parent functional, all-UKS reference policy, molecular inputs, basis/ECP
and auxiliary definitions, fixed-orbital cycle, grids, 291-column layout,
nonlinear parameters, energy partition, weights, and data roles are unchanged
from version 3. The exact version-3 file is archived as
`revwb97m2/configs/archive/scientific_spec.v3.yaml`.

The version-4 independent specification validator passes all checks.
