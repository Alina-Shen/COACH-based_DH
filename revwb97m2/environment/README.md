# Reproducible `coach` environment

This directory records the verified environment for the PySCF-native
`revwb97m2` workflow. Always load Conda through the cluster module first.

## Standard creation

From the repository root at the recorded baseline commit:

```bash
module load miniconda3
conda env create --file revwb97m2/environment/environment.yml
conda run -n coach python -m pip install --editable './coach[functional,workflow,test]'
```

If `coach` already exists, inspect it first and update it non-destructively:

```bash
module load miniconda3
conda env update --name coach --file revwb97m2/environment/environment.yml
conda run -n coach python -m pip install --editable './coach[functional,workflow,test]'
conda run -n coach python -m pip check
```

The editable install must resolve to this checkout's `coach/` directory. Do
not use `--prune` automatically on a shared existing environment.

## Exact Linux recreation

For the exact Conda builds captured on Rocky Linux 8, create the Conda layer
and then install the exact Python package set:

```bash
module load miniconda3
conda create --name coach --file revwb97m2/environment/conda-linux-64.explicit.txt
conda run -n coach python -m pip install --requirement revwb97m2/environment/pip-linux-64.lock.txt
conda run -n coach python -m pip install --editable ./coach --no-deps
```

`conda-linux-64.explicit.txt` is platform/build-specific. `environment.yml` is
the readable direct-dependency specification. `pip-linux-64.lock.txt` captures
the full installed Python dependency closure but deliberately excludes the
editable project itself; the exact project source is the Git commit recorded
in `baseline.json`.

## Verification

Run:

```bash
module load miniconda3
conda run -n coach python -m pip check
conda run -n coach python revwb97m2/scripts/validate_environment.py
conda run -n coach python revwb97m2/scripts/validate_scientific_spec.py
conda run -n coach pytest -q coach/FunctionalCOACH/tests
```

The Gurobi check solves a bounded one-variable optimization problem. A package
import alone does not establish that a usable license is available.

## Captured validation status

The machine-readable record is [`baseline.json`](baseline.json), with a
human-readable action log in
[`../results/2026-08-29-reproducible-code-environment-baseline.md`](../results/2026-08-29-reproducible-code-environment-baseline.md).

Environment, Gurobi, scientific-specification, stored species-smoke, and
stored reaction-smoke checks pass. The upstream FunctionalCOACH suite currently
has three passing tests and one known carbon AE18 failure caused by invalid
values reaching the SCF DIIS eigensolve. This recorded code regression is not
an environment recreation failure.
