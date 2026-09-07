#!/usr/bin/env bash
#SBATCH --job-name=revwb97m2_q6_med_r1
#SBATCH --partition=lr8
#SBATCH --account=lr_mhg2
#SBATCH --qos=mhg2_lr8_normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=62G
#SBATCH --time=08:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/q6_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/q6_%j.err

set -euo pipefail
module purge
module load gcc/10.5.0
module load ucx/1.14.1
module load openmpi/4.1.6
module load boost/1.83.0

cd /clusterfs/mhg-data/yaoshen/coach-based_dh
/global/home/users/yaoshen/.conda/envs/coach/bin/python \
  revwb97m2/scripts/recover_q6_resource_pilot.py \
  --species TMB28_C1 --cpus "$SLURM_CPUS_PER_TASK" --attempt retry1
