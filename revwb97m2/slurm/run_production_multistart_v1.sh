#!/usr/bin/env bash
#SBATCH --job-name=r2_production
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:30:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/production_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/production_%A_%a.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.production_multistart_v1 run --release "${1:?release required}" --phase "${2:?phase required}" --index "${SLURM_ARRAY_TASK_ID:-0}"
