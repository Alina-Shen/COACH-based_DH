#!/usr/bin/env bash
#SBATCH --job-name=r2_fixed_checkpoint
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=2
#SBATCH --mem=14G
#SBATCH --time=01:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/fixed_checkpoint_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/fixed_checkpoint_%j.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.fixed_energy_checkpoint \
  --contract revwb97m2/manifests/production_generator/fixed_energy_checkpoint_v1.json \
  --output "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/fixed_energy_checkpoint_${SLURM_JOB_ID:?}" --verify-only
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m pytest revwb97m2/tests -q
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.scripts.fixed_energy_checkpoint \
  --contract revwb97m2/manifests/production_generator/fixed_energy_checkpoint_v1.json \
  --output "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/fixed_energy_checkpoint_${SLURM_JOB_ID:?}"
