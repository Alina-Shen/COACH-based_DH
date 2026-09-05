# Step 1 completion: scientific specification version 5

Date: 2026-09-03

## Decision

The production orbital source is the existing self-consistent Q-Chem
omegaB97M-V `qarchive.h5`, reused without a new orbital optimization. Q-Chem
must run with zero SCF cycles from an isolated, hash-verified copy. IntegratedDV,
short-range HF exchange, VV10, and frozen-core RI-MP2 must all be evaluated
from the same imported archive. PySCF remains an explicitly authorized
fallback and cross-engine regression route, but it is never selected silently.

The unchanged version-4 specification is archived at
`revwb97m2/configs/archive/scientific_spec.v4.yaml` with SHA-256
`420ca198e7374144db20ae6737f83cf999ad6a36ae06ea034aeca85314bf4dc5`.

## Orbital inventory and scope

- Canonical GSCDB plus auxiliary-only scope: 14,006/14,006 regular, nonempty
  archives; zero missing, empty, or nonregular entries.
- BigNC: 75/75 source archives available; a project-owned non-overwriting copy
  and source/copy hash validation are required before execution.
- GDB9-W1-F12: input metadata exists, but no validated Q-Chem orbital archive
  authority was found. This final-assessment scope is explicitly blocked.
- OPT: outside this fixed-geometry energy and training workflow.

The validator uses the pinned species manifests. It does not infer authority
from raw directory counts or from unrelated extra directories.

## Frozen execution contract

- Preserve the matching Q-Chem geometry, charge, multiplicity, unrestricted
  reference, orbital basis, ECP, and auxiliary-basis definitions.
- Use `MAX_SCF_CYCLES 0`, `GEN_SCFMAN FALSE`, and
  `QCHEM_PRINT_INTEGRATED_DV=1`; orbital updates are forbidden.
- Require a meta-GGA and a finite final complete delimited 96x180 integratedDV
  block. Transpose to 180x96, then select rows `(64,154,166)`.
- Use grids `250974`, `99590`, and `75302`; grid `250974` supplies fitting
  features and the other two supply grid-difference constraints.
- Retain revised-model `gamma_c,ss=0.01`; do not inherit the historical
  `IDV_print` value `0.2`.
- Record source/copy archive hashes, Q-Chem input/output hashes, source
  revisions and diff, executable hash, and full/selected integratedDV hashes.

## Validation

The following commands pass:

```bash
python revwb97m2/scripts/validate_qchem_orbital_authority.py \
  --output revwb97m2/manifests/qchem_orbitals/validation.json
python revwb97m2/scripts/validate_scientific_spec.py --json \
  --output revwb97m2/manifests/scientific_spec/scientific_spec_v5_validation.json
```

This closes the scientific-definition gate. It does not claim that the Q-Chem
binary or native archive-reuse calculation has passed: those remain downstream
Steps 7, 9, and 10 gates.

## Next action

Build and provenance-pin the modified current Q-Chem trunk. Record main and
libks SVN URLs/revisions, local-diff SHA-256, executable SHA-256, compiler, and
linked libraries. That binary is required before the bounded restricted and
unrestricted three-grid archive-reuse smoke matrix can test the frozen
scientific contract.
