#!/usr/bin/env bash
#SBATCH --job-name=r2_training_features
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=72:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/training_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/training_%j.err
set -euo pipefail
species=${1:?Frozen species required}
release=${2:?Reviewed release JSON required; absent until seven canaries and commit pass}
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
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.scripts.generate_training_features run \
  --plan revwb97m2/manifests/production_generator/training_first16_v1.json \
  --species "$species" --release "$release" --cpus "$SLURM_CPUS_PER_TASK" \
  --memory-gib "$((SLURM_MEM_PER_NODE / 1024))"
