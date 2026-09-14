#!/usr/bin/env bash
#SBATCH --job-name=r2_multi_audit
#SBATCH --partition=lr8
#SBATCH --account=lr_mhg2
#SBATCH --qos=mhg2_lr8_normal
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --no-requeue
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/multi_audit_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/multi_audit_%j.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
unset GRB_LICENSE_FILE
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
exec /global/home/users/yaoshen/.conda/envs/dh/bin/python -B -u -m revwb97m2.multipartition_v1.audit "$@"
