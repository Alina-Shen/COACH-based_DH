#!/usr/bin/env bash
#SBATCH --job-name=r2_s13_fresh
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=02:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step13_fresh_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step13_fresh_%j.err

set -euo pipefail

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

cd /clusterfs/mhg-data/yaoshen/coach-based_dh
/global/home/users/yaoshen/.conda/envs/coach/bin/python \
  -m revwb97m2.scripts.run_step13_fresh_species \
  --species 11_H2O_TA13 \
  --cpus "$SLURM_CPUS_PER_TASK"
