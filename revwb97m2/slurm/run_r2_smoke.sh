#!/bin/bash
#SBATCH --job-name=revwb97m2_smoke
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/%x-%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/%x-%j.err

set -euo pipefail

PROJECT_ROOT=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2
DATA_ROOT=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2
PYTHON_BIN=${DATA_ROOT}/venv/bin/python
RUN_DIR=${DATA_ROOT}/smoke/h2o

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=${DATA_ROOT}/tmp/${SLURM_JOB_ID}

mkdir -p "${DATA_ROOT}/logs" "${DATA_ROOT}/smoke" "${TMPDIR}"

"${PYTHON_BIN}" "${PROJECT_ROOT}/run_r2_smoke.py" \
  --config "${PROJECT_ROOT}/revwb97m2.yaml" \
  --xyz "${PROJECT_ROOT}/inputs/smoke_h2o.xyz" \
  --output-dir "${RUN_DIR}" \
  --max-memory-mb 40000 \
  --block-size 10000

"${PYTHON_BIN}" "${PROJECT_ROOT}/validate_r2_smoke.py" \
  --config "${PROJECT_ROOT}/revwb97m2.yaml" \
  --run-dir "${RUN_DIR}"
