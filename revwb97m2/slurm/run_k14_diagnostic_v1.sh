#!/usr/bin/env bash
#SBATCH --job-name=r2_k14_diag
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=01:30:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/k14_diagnostic_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/k14_diagnostic_%j.err
set -euo pipefail
release=${1:?Reviewed committed tested release required}
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.scripts.k14_diagnostic_v1 run --release "$release"
