#!/usr/bin/env bash
#SBATCH --job-name=r2_full_features_v3
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=72:00:00
#SBATCH --array=0-0
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/full_training_v3_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/training_v3_%A_%a.err
set -euo pipefail
release=${1:?Reviewed release JSON required}
plan=${2:?Frozen reviewed full-training plan required}
module purge
module load python/3.11.6-gcc-11.4.0
module load gcc/10.5.0
module load ucx/1.14.1
module load openmpi/4.1.6
module load intel-oneapi-tbb/2021.10.0
module load intel-oneapi-mkl/2023.2.0
module load cmake
module load hdf5
module load boost/1.83.0
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:?} OPENBLAS_NUM_THREADS=1
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.scripts.generate_training_features_v3 run \
  --plan "$plan" --species-index "${SLURM_ARRAY_TASK_ID:?}" --release "$release" \
  --cpus "$SLURM_CPUS_PER_TASK" --memory-gib "$((SLURM_MEM_PER_NODE / 1024))"
