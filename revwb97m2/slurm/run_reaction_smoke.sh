#!/bin/bash
#SBATCH --job-name=revwb97m2_rxn_smoke
#SBATCH --partition=lr7
#SBATCH --account=lr_mhg2
#SBATCH --qos=condo_mhg_lr7
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=04:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/reaction_smoke_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/reaction_smoke_%j.err

set -euo pipefail

PROJECT_ROOT=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2
DATA_ROOT=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/reaction_smoke
COACH_CONDA_ENV=/global/home/users/yaoshen/.conda/envs/coach

export PATH="${COACH_CONDA_ENV}/bin:${PATH}"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

mkdir -p "${DATA_ROOT}/species"

for species_name in h2_eq h2_stretched h4_dimer; do
    species_dir="${DATA_ROOT}/species/${species_name}"
    xyz_path="${PROJECT_ROOT}/inputs/reaction_smoke/${species_name}.xyz"
    if [[ -f "${species_dir}/SMOKE_PASS" ]]; then
        echo "Reusing validated species ${species_name}"
        continue
    fi
    if [[ ! -d "${species_dir}" ]]; then
        python "${PROJECT_ROOT}/run_r2_smoke.py" \
            --config "${PROJECT_ROOT}/revwb97m2.yaml" \
            --xyz "${xyz_path}" \
            --output-dir "${species_dir}" \
            --max-memory-mb 40000 \
            --block-size 10000 \
            --verbose 4
    fi
    python "${PROJECT_ROOT}/validate_r2_smoke.py" \
        --config "${PROJECT_ROOT}/revwb97m2.yaml" \
        --run-dir "${species_dir}"
done

processed_dir="${DATA_ROOT}/processed"
if [[ ! -f "${processed_dir}/REACTION_SMOKE_PASS" ]]; then
    if [[ -d "${processed_dir}" ]]; then
        echo "Processed directory exists without REACTION_SMOKE_PASS: ${processed_dir}" >&2
        exit 1
    fi
    python "${PROJECT_ROOT}/build_reaction_smoke.py" \
        --config "${PROJECT_ROOT}/revwb97m2.yaml" \
        --reaction-spec "${PROJECT_ROOT}/reaction_smoke.yaml" \
        --output-dir "${processed_dir}"
    python "${PROJECT_ROOT}/validate_reaction_smoke.py" \
        --reaction-spec "${PROJECT_ROOT}/reaction_smoke.yaml" \
        --run-dir "${processed_dir}"
fi

echo "Reaction smoke test passed: ${processed_dir}"
