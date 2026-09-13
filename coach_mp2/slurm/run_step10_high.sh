#!/bin/bash
#SBATCH --job-name=coach_s10_high
#SBATCH --partition=lr8
#SBATCH --account=lr_mhg2
#SBATCH --qos=mhg2_lr8_normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=557G
#SBATCH --time=48:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step10_high_%j.log
set -euo pipefail
export OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16
export PYTHONDONTWRITEBYTECODE=1
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B /clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/scripts/run_step10.py high
