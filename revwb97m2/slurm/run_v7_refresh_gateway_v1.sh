#!/usr/bin/env bash
#SBATCH --job-name=r2_v7_gateway
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --array=0-4%2
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=04:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_gateway_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_gateway_%A_%a.err
set -euo pipefail
# Bounded coverage only: singlet, ordinary doublet, one electron, and
# recovered singlet/triplet electric-field cases. Never submit all 38 here.
cases=(48_hcn_BH76 58_hn2_BH76 W4-17_h Dip146_HF2+ Dip146_LiN2+)
index=${SLURM_ARRAY_TASK_ID:?Slurm array index required}
[[ "$index" =~ ^[0-4]$ ]] || exit 2
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
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=1
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
printf 'Gateway species: %s\n' "${cases[$index]}"
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u -m revwb97m2.scripts.v7_refresh species \
  --plan revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json \
  --species "${cases[$index]}" --cpus 8
