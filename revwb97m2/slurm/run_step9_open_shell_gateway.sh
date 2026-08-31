#!/bin/bash
#SBATCH --job-name=r2_s9_nh2
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=04:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step9_nh2_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step9_nh2_%j.err

set -euo pipefail

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

repo=/clusterfs/mhg-data/yaoshen/coach-based_dh
python_bin=/global/home/users/yaoshen/.conda/envs/coach/bin/python
species=12_NH2rad_HNBrBDE18
parent_dir=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/gateway/${species}
scalar_dir=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/scalar/gateway/${species}

mkdir -p /clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs
cd "${repo}"

if [[ ! -f "${parent_dir}/PARENT_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_parent_scf.py \
    --species "${species}" \
    --stage gateway \
    --output-dir "${parent_dir}" \
    --max-memory-mb 40000 \
    --verbose 4
fi

if [[ ! -f "${scalar_dir}/SCALAR_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_scalar_features.py \
    --species "${species}" \
    --parent-dir "${parent_dir}" \
    --output-dir "${scalar_dir}" \
    --max-memory-mb 40000
fi
