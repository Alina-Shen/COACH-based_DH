#!/bin/bash
#SBATCH --job-name=coach_s10_small
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=02:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step10_small_%j.log
set -euo pipefail
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
export PYTHONDONTWRITEBYTECODE=1
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B /clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/scripts/run_step10.py small
