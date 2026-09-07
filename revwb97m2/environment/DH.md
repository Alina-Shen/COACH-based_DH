# Shared `dh` environment

The shared COACH-based double-hybrid environment is installed at
`/global/home/users/yaoshen/.conda/envs/dh`. Its initial package versions match
the existing `coach` baseline; that environment and existing production
scripts are unchanged.

## Activate

```bash
module load miniconda3
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate dh
```

Conda environment configuration sets `GRB_LICENSE_FILE` to the private file
`/global/home/users/yaoshen/tools/gurobi.lic`. Only the path is stored there;
never commit or print the license contents. Do not enable shell tracing around
credentials. Direct invocation of `dh/bin/python` without activation does not
apply Conda environment variables; export the license path explicitly then.

## Reproduce the installed package set

For an empty `dh` environment, from the repository root:

```bash
module load miniconda3
conda install -n dh --file revwb97m2/environment/conda-linux-64.explicit.txt --yes
conda run -n dh python -m pip install -r revwb97m2/environment/pip-linux-64.lock.txt
conda run -n dh python -m pip install --editable ./coach --no-deps --no-build-isolation
conda env config vars set -n dh GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
```

These locks include Python 3.11.15, Gurobi 13.0.3, PySCF 2.14.0, NumPy 2.4.6,
SciPy 1.17.1, pandas 3.0.5, h5py 3.16.0, DFT-D4 4.2.0, Basis Set Exchange 0.12,
PyYAML 6.0.3 and pytest 9.1.1, plus their pinned dependency closure.

## Compute-node check

```bash
sbatch revwb97m2/slurm/validate_dh_wls.sh
```

The job checks package consistency, pinned versions, LibXC, editable source
location, and private license permissions. It explicitly uses WLS credentials
in a single output-suppressed environment and solves a 300-variable quadratic
problem with known optimum zero. This exceeds the restricted license's
[200-variable quadratic limit](https://support.gurobi.com/hc/en-us/articles/360051597492-How-do-I-resolve-a-Model-too-large-for-size-limited-Gurobi-license-error).
Both model and environment are disposed on exit. No raw license values or
exception messages are logged.

Successful execution establishes WLS access from the tested node at that time,
not every partition or sustained multi-hour token renewal. Full-R2 scientific
fitting and bulk submissions are separate from this environment check.
