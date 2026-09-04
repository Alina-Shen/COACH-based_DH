#!/bin/bash
#SBATCH --job-name=r2_d12_m30000
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=62G
#SBATCH --time=72:00:00
#SBATCH --array=0
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step12_m30000_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step12_m30000_%A_%a.err
export STEP12_MEMORY_CLASS_MB=30000 STEP12_TIER=small_mhg STEP12_BLOCK_SIZE=10000
exec /bin/bash /clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/slurm/run_step12_resource_pilot_task.sh
