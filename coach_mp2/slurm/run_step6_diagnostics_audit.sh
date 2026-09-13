#!/bin/bash
#SBATCH --job-name=coach_s6_audit
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step6_diagnostics_%j.log
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
export TMPDIR=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/runtime
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B coach_mp2/scripts/audit_step6_diagnostics.py
