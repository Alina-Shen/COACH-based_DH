#!/bin/bash
#SBATCH --job-name=v7_synthetic_test
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --chdir=/clusterfs/mhg-data/yaoshen/coach-based_dh
#SBATCH --output=revwb97m2/results/v7_synthetic_%j.out
#SBATCH --error=revwb97m2/results/v7_synthetic_%j.err
set -euo pipefail
module load miniconda3
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m revwb97m2.scripts.test_v7_end_to_end --output "revwb97m2/results/v7_synthetic_${SLURM_JOB_ID}"
