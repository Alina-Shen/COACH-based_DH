# COACH-based MP2 code and lightweight artifacts

This is the version-controlled working root for the `COACH-based_mp2`
project. Put source code, scripts, small configuration files, manifests,
tests, documentation, Slurm wrappers, and lightweight result summaries here.

Heavy numerical data belongs under:

`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2`

## Current structure

```text
coach_mp2/
└── README.md   # This structure and storage-policy document
```

No scientific implementation has been added yet. Directories will be created
only when their first real artifact is added.

## Planned structure

```text
coach_mp2/
├── README.md
├── configs/       # Versioned scientific specifications and run configurations
├── docs/          # Model equations, methods, storage layout, and user guidance
├── manifests/     # Lightweight immutable input/data-role/provenance manifests
├── scripts/       # Reproducible command-line workflow entry points
├── slurm/         # Reviewed Slurm submission wrappers
├── tests/         # Unit, regression, identity, and gateway tests
└── results/       # Small validation reports and scientific summaries
```

The final layout may change as the implementation is designed. Planned
directories are not considered present until they are actually created.

## Storage rules

- Keep all project scripts and scientifically important lightweight files in
  this tree.
- Do not store SCF checkpoints, molecular feature arrays, PT2 intermediates,
  large processed matrices, solver bulk output, scratch, or full production
  logs here.
- Every artifact must identify the scientific-specification version and its
  input/code provenance where applicable.
- Never reuse `revwb97m2` orbitals or checkpoints as COACH-orbital data.
  Reusable code or metadata must be imported through an explicit audit and a
  project-owned manifest.
- Update this README in the same change whenever a file or directory is added,
  removed, renamed, or assigned a different purpose.

## Active model scope

- Initial model: `M2-total`, a full COACH-form energy refit on fixed
  self-consistent COACH orbitals.
- Use selected integratedDV rows `(64,154,166)`; row `154` gives the documented
  final-COACH monomial-`u`/Legendre-`v` same-spin expansion.
- Store opposite-spin and same-spin MP2 contributions separately, but impose
  one shared fitted coefficient so the initial PT2 energy is
  `c_PT2 * (E_PT2_OS + E_PT2_SS)`.
- `M1-total` and `M1-SCS` are out of scope.
- `M2-SCS` is a future option.
- RI-MP2 is the intended efficient canonical-MP2 backend after validation.
- LMP2 is a future acceleration option based on
  `qchem/lmp2_zfp/libgmbpt/libgmbpt/localmp2`; its approximation error and
  numerical smoothness must be validated before substitution.
- Retain both original COACH dispersion components while adding PT2: VV10 with
  fixed nonlinear parameters `b=5.5,C=0.01`, and D4-ATM with fixed damping
  parameters. Add linear scalar coefficients `c_VV10` and `c_ATM`; their
  bounds and relationship to `c_PT2` remain a pre-fit TODO.
- Initial functional capability is energy-only.
- Target domain is the full COACH molecular domain, executed through staged
  feasibility/resource tiers.
