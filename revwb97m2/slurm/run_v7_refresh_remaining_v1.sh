#!/usr/bin/env bash
#SBATCH --job-name=r2_v7_remaining
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=8
#SBATCH --mem=14G
#SBATCH --time=04:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_remaining_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_remaining_%A_%a.err
set -euo pipefail
# Explicit remaining indices supplied at submission, with %2 concurrency.
# Submit 21-GiB class with --mem=21G and afterok dependency on 14-GiB class.
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
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u - <<'PY'
import os
from pathlib import Path
from revwb97m2.v7_refresh import load_plan,refresh_species
p=Path('revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json')
plan,_=load_plan(p)
index=int(os.environ['SLURM_ARRAY_TASK_ID'])
assert 0 <= index < len(plan['cases'])
c=plan['cases'][index]
assert int(os.environ['SLURM_CPUS_PER_TASK'])==c['resources']['cpus']
assert int(os.environ['SLURM_MEM_PER_NODE'])==1024*c['resources']['requested_memory_gib']
print('Frozen case',index,c['species'],flush=True)
refresh_species(p,c['species'],c['resources']['cpus'])
print('Validated refresh complete',c['species'],flush=True)
PY
