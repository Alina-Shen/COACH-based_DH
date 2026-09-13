#!/bin/bash
#SBATCH --job-name=coach_s5_audit
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step5_native_audit_v3_%j.log
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export TMPDIR=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/runtime
export OPENBLAS_NUM_THREADS=8 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B coach_mp2/scripts/check_step5_native_v3.py
