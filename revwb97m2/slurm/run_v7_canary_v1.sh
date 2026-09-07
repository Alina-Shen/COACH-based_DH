#!/usr/bin/env bash
#SBATCH --job-name=r2_v7_canary
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=72:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_canary_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_canary_%j.err
set -euo pipefail
# One explicit frozen species per job. No global concurrency cap or auto-submit.
# Override allocation to the frozen case at submission; the driver verifies it.
# Large cases require post-small-case review and explicit --large-reviewed.
species=${1:?Provide a frozen canary species}
shift
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
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.scripts.v7_canary run \
  --plan revwb97m2/manifests/production_generator/v7_canary_v1.json \
  --species "$species" --cpus "$SLURM_CPUS_PER_TASK" \
  --memory-gib "$((SLURM_MEM_PER_NODE / 1024))" "$@"
