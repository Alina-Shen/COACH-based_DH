#!/bin/bash
#SBATCH --job-name=coach_s8_validate
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step8_validate_%j.log
set -euo pipefail
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B /clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/scripts/validate_step8.py
