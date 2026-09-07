#!/bin/bash
#SBATCH --job-name=dh_wls_check
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --chdir=/clusterfs/mhg-data/yaoshen/coach-based_dh
#SBATCH --output=revwb97m2/results/dh_wls_%j.out
#SBATCH --error=revwb97m2/results/dh_wls_%j.err

set -euo pipefail
module load miniconda3
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONNOUSERSITE=1
python -m pip check
python revwb97m2/scripts/validate_dh_wls.py
