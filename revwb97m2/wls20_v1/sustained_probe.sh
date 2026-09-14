#!/usr/bin/env bash
#SBATCH --job-name=r2_wls20_sustained
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --cpus-per-task=16
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --no-requeue
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/wls20_sustained_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/wls20_sustained_%j.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
exec /global/home/users/yaoshen/.conda/envs/dh/bin/python -B -u revwb97m2/wls20_v1/sustained_probe.py
