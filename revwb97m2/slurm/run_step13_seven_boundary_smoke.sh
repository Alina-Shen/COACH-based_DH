#!/bin/bash
#SBATCH --job-name=r2_s13_7b_smoke
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=72:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step13_7b_smoke_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step13_7b_smoke_%j.err

set -euo pipefail
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

cd /clusterfs/mhg-data/yaoshen/coach-based_dh
exec /global/home/users/yaoshen/.conda/envs/coach/bin/python \
  revwb97m2/scripts/run_step13_species.py \
  --species 3d4dIPSS_Ag_GS \
  --output-root /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step13/smoke/v1 \
  --spec revwb97m2/configs/scientific_spec.yaml \
  --max-memory-mb 3750 --block-size 10000
