# revwb97m2

This directory contains the isolated code and configuration for the revised
omegaB97M(2) practice. The upstream `../coach/` checkout is treated as read-only.

## Authoritative scientific specification

The frozen version-4 specification is
[`configs/scientific_spec.yaml`](configs/scientific_spec.yaml), with rationale
in [`docs/scientific_specification.md`](docs/scientific_specification.md). Run
its independent validation gate with:

```bash
python scripts/validate_scientific_spec.py
```

The storage policy and organized version-controlled/heavy-data trees are
defined in [`docs/storage_layout.md`](docs/storage_layout.md).

The reproducible Conda/Python baseline, exact Linux locks, and verification
commands are documented in [`environment/README.md`](environment/README.md).

The root-level `revwb97m2.yaml` and smoke scripts are retained as the legacy
configuration used by the already accepted plumbing tests. New scientific
work must use `configs/scientific_spec.yaml`.

## Experiment registry

Every created experiment receives an immutable config and a short,
hash-qualified ID. The current human-readable list is
[`EXPERIMENTS.md`](EXPERIMENTS.md), backed by
[`experiments/registry.csv`](experiments/registry.csv). Creation, status
updates after every run attempt, and validation are handled by
[`scripts/experiment_registry.py`](scripts/experiment_registry.py). See
[`experiments/README.md`](experiments/README.md) for the naming convention and
commands.

## Authoritative GSCDB137 manifest

The pinned species, dataset, provenance, and scratch-coverage records are under
[`manifests/gscdb137/`](manifests/gscdb137). The construction and the COACH SI
weighting evidence are explained in
[`docs/gscdb137_species_manifest.md`](docs/gscdb137_species_manifest.md).

```bash
python scripts/validate_gscdb137_manifest.py
```

Specification version 4 follows the manifest's per-species GSCDB basis
assignments and translates verified named/generated basis, ECP, and auxiliary
basis metadata into PySCF definitions. The earlier Q-Chem comparison utility
remains available for provenance auditing:

```bash
python scripts/validate_gscdb_basis_policy.py
```

## Accepted legacy smoke baseline

The first implemented target was `R2_coach291`. The smoke calculation uses
omegaB97M-V/def2-QZVPPD orbitals for water, frozen-core RI-MP2, VV10 with
`b=10` and `C=0.01`, and the three COACH feature grids. It selects integratedDV
rows `(64, 153, 166)` and writes a 291-element feature vector. The frozen
scientific model instead uses semantic rows `(64, 154, 166)`; see the
row-153/154 decision in the scientific specification. Existing smoke artifacts
remain plumbing and algebra regression fixtures and are not production
training data.

## Production semilocal feature kernel

[`integrated_dv.py`](integrated_dv.py) implements the three frozen semilocal
rows `(64,154,166)` with `gamma_x=0.004`, `gamma_ss=0.01`, and
`gamma_os=0.006`. It follows the COACH feature-construction protocol on fixed
omegaB97M-V densities but deliberately contains no final COACH coefficients:
the 288 semilocal columns are inputs to a new omegaB97M(2)-form fit. See the
Step 7 [validation record](manifests/integrated_dv/validation.json).

## Manifest-driven parent SCF

[`parent_scf.py`](parent_scf.py) combines immutable molecular records with the
validated basis bridge and runs omegaB97M-V using UKS for every species. It
publishes non-overwriting checkpoint/density directories atomically and proves
checkpoint density and selected-feature identity before making the checkpoint
read-only. The Step 8 `h2o_SW49` gateway and its recorded PySCF stability/NLC
limitation are documented in the
[parent-SCF manifest](manifests/parent_scf/README.md).

## Checkpoint-only scalar double-hybrid features

[`scalar_features.py`](scalar_features.py) consumes a validated parent
checkpoint without rerunning SCF. It appends unscaled SR-HF, fixed-grid VV10
at `b=10,C=0.01`, and total frozen-core canonical DF-UMP2 as columns
`288:291`, while preserving same-spin/opposite-spin PT2 diagnostics and the
complete fixed-energy partition. Atomic artifacts, direct-energy identities,
resource measurements, and validation commands are described in the
[Step 9 manifest](manifests/scalar_features/README.md).

## Three-grid scientific gateways

[`semilocal_features.py`](semilocal_features.py) consumes a validated parent
checkpoint and independently publishes the selected `(64,154,166)` `3 x 96`
matrix on each frozen COACH grid: `250974`, `99590`, and `75302`. It records
per-grid point counts, wall time, peak memory, hashes, and reference-grid
differences without rerunning SCF. The Step-10 matrix definition and static
resource preflight are in
[`step10_gateway_matrix_v1.yaml`](manifests/gateway_matrix/step10_gateway_matrix_v1.yaml).
The non-overwriting Slurm arrays preserve the parent, semilocal, and scalar
restart boundaries separately. Aggregate the measured stage costs and the
exact role-minimal fixed-geometry population, then validate every gateway with:

```bash
python scripts/summarize_step10_resources.py
python scripts/validate_step10_gateway_results.py
```

The summary is intentionally an early Step-12 measurement, not a production
resource authorization. In particular, it refuses to infer CPU-hours from
only the small gateways while the high-cost counterpoise case is incomplete.

## Published omegaB97M(2) R0 comparator

Step 11 treats the uploaded 2018 omegaB97M(2) paper as a hash-pinned authority
only for the conventions and five-decimal coefficients it states explicitly.
[`published_wb97m2.py`](published_wb97m2.py) implements the resulting named
component algebra as an immutable, non-fitted `R0` comparator; it cannot
silently reinterpret the project's distinct 291-column `R2` feature vector.
The source boundary, coefficients, unresolved authorities, and validation
status are recorded in the
[`published_wb97m2` manifest](manifests/published_wb97m2/README.md).

```bash
python scripts/validate_published_wb97m2.py
```

The full R0 density evaluator and trusted molecular/reaction fixtures remain
open until authoritative semilocal definitions and implementation-level
conventions are supplied. This is an explicit Step-11 authority gate, not a
failure of the coefficient-algebra scaffold.

## Reaction-level smoke test

`reaction_smoke.yaml` defines three closed-shell species and two balanced
hydrogen-only reactions. The test exercises a unit stoichiometric difference
and a coefficient of two without introducing open-shell-reference ambiguity.

The reaction builder uses the configured fixed terms

```text
Nofit = E_nuclear + E_one-electron + E_Coulomb + E_LR-HF
```

and constructs, for every reaction,

```text
A_reaction       = sum_s nu_s A_species
Nofit_reaction   = sum_s nu_s Nofit_species
Reference        = sum_s nu_s (Nofit_species + A_species beta_oracle)
b                = Reference - Nofit_reaction
```

The reference is deliberately synthetic and is only an algebra/data-plumbing
oracle. It is not a scientific benchmark and must not be used for fitting.

Run the complete calculation through Slurm with:

```bash
sbatch slurm/run_reaction_smoke.sh
```

The script uses the `coach` Conda environment and writes species and processed
artifacts only under:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/reaction_smoke
```

Successful completion creates `processed/REACTION_SMOKE_PASS`. No MIO solver is
called by this workflow.

All generated environments, logs, checkpoint files, matrices, and reports live
under:

```text
/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2
```

Submit the smoke job with:

```bash
mkdir -p /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs
sbatch /clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/slurm/run_r2_smoke.sh
```

The run directory is intentionally non-overwriting. A successful calculation
contains both `CALCULATION_COMPLETE` and `SMOKE_PASS`.

## Archived Q-Chem fixed-orbital gateway

The Q-Chem-orbital route is retired from production and preserved under
`../coach/qchem_orbital_route` and
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/qchem_orbital_route`. Its
historical disposable gateway can be prepared with:

```bash
python3.9 scripts/prepare_qchem_gateway.py prepare \
  --case-root /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/tmp/qchem_gateway/h2o_SW49-fixed-orbitals-v1
```

The preparation tool refuses to overwrite an existing case. It copies the
published `h2o_SW49` orbital scratch into separate baseline and working trees,
preserves an exact copy of the authoritative input, and creates a derived input
whose only semantic changes are `MAX_SCF_CYCLES 0` and `GEN_SCFMAN FALSE`.
`PREPARED.json`, `source_manifest.json`, `qchem_identity.json`, and
`input.diff` record the provenance. Run `run_qchem.sh` only after reviewing the
derived input and pinned Q-Chem build. It is reference/provenance material
only. Production parents must be generated self-consistently in PySCF under
specification version 4.
