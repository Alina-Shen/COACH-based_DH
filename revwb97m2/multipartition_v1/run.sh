#!/usr/bin/env bash
#SBATCH --job-name=r2_multi_fit
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:30:00
#SBATCH --no-requeue
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/multi_fit_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/multi_fit_%j.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
if [[ -n "${SLURM_ARRAY_TASK_ID:-}" ]]; then
    set -- "$@" --index "$SLURM_ARRAY_TASK_ID"
fi
exec /global/home/users/yaoshen/.conda/envs/dh/bin/python -B -u -m revwb97m2.multipartition_v1.adapter "$@"
