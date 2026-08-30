# Storage and version-control layout

All lightweight, reviewable project material belongs under:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2
```

All heavy or reproducible generated data belongs under:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2
```

## Version-controlled tree

```text
revwb97m2/
├── configs/       authoritative and experiment-specific YAML files
├── docs/          decisions, methods, and data-layout documentation
├── inputs/        small hand-written smoke and gateway inputs
├── manifests/     lightweight species/run manifests; no large payloads
├── results/       concise result summaries and tables suitable for review
├── scripts/       maintained command-line tools
├── slurm/         submission scripts
└── legacy root scripts/configs retained for accepted smoke compatibility
```

Source code, validators, configuration, small inputs, Slurm scripts, summary
tables, and Markdown reports are version controlled. Generated `.npy`, HDF5,
checkpoint, scratch, environment, full log, and solver-result files are not.

## Heavy-data tree

The intended production layout is:

```text
coach-based_dh_data/revwb97m2/
├── orbitals/
│   ├── wb97m_v_qchem_scratch/   verified immutable working copy
│   └── copy_validation/         heavy copy reports if needed
├── species/
│   ├── gateway/
│   ├── pilot/
│   └── production/
├── processed/
│   ├── pilot/
│   └── production/
├── optimization/
│   ├── pilot/
│   └── production/
├── logs/
├── runtime_cache/
├── failed/
├── smoke/                       accepted H2O smoke artifacts
└── reaction_smoke/              accepted synthetic reaction artifacts
```

Directories are created only when a workflow needs them. Every generated
artifact must record the specification version and SHA-256, code commit,
source manifest, and completion state. Heavy artifacts are never silently
overwritten.
