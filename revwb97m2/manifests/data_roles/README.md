# Data-role manifests

This directory freezes the data roles used by `revwb97m2` before any fitting.
The policy is COACH-faithful: the exact 1,498 final/Cycle-2 entries determine
coefficients, while all 137 GSCDB137 datasets may influence model/design
selection through dataset-level normalized error ratios (NERs). This deliberate
overlap is recorded rather than described as an independent validation split.

The COACH overfitting diagnostic is the mean NER of `AE11`, `MB08-165`, and
`MB16-43`. `MB16-43` also belongs to the fitting set, so the diagnostic is not
fully independent and must not be presented as an untouched test.

Final energy assessment is restricted to the appended `SC74`/`OEEFD` reaction
groups, BigNC (`L14`/`vL11`), and GDB9-W1-F12 after model and sparsity are
frozen. GDB9-W1-F12 is the genuinely untouched robustness test in the COACH
paper. COACH itself tuned D4-ATM parameters on BigNC; this project may call
BigNC untouched only while no model or dispersion parameter is tuned on it.
OPT is tracked separately as a geometry-optimization assessment.

Geometry, charge, multiplicity, orbital-basis, auxiliary-basis, ECP, and ghost
center metadata are parsed from verified, hash-pinned Q-Chem inputs. The core
snapshot supplies 14,006 inputs; the official GSCDB `AdditionalSets` snapshot
supplies 75 BigNC, 3,371 GDB9-W1-F12, and 206 OPT inputs. Q-Chem orbital files,
`qarchive.h5`, and scratch orbital directories are not read. BigNC counterpoise
monomer inputs retain their `@` ghost centers.

Build and validate with:

```bash
python revwb97m2/scripts/build_data_role_manifests.py
python revwb97m2/scripts/validate_data_role_manifests.py
```

Generated files:

- `dataset_roles.csv`: dataset-level role declarations and counts.
- `reaction_roles.csv`: every pinned GSCDB/auxiliary reaction with explicit role flags.
- `species_roles.csv`: exact unique species required by each energy role.
- `qchem_input_metadata.csv`: parsed, hash-pinned non-orbital input metadata for
  17,452 energy-role inputs plus 206 OPT geometry-assessment inputs.
- `provenance.json` and `validation.json`: source/output hashes and independent checks.
