#!/bin/bash
#SBATCH --job-name=r2_d12_l300
#SBATCH --partition=lr8
#SBATCH --account=lr_mhg2
#SBATCH --qos=mhg2_lr8_normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=557G
#SBATCH --time=336:00:00
#SBATCH --array=0-1%1
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step12_l300_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step12_l300_%A_%a.err
export STEP12_MEMORY_CLASS_MB=300000 STEP12_TIER=large_lr8 STEP12_BLOCK_SIZE=2000
exec /bin/bash /clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/slurm/run_step12_resource_pilot_task.sh
