#!/bin/bash
#SBATCH --job-name=r2_s11_h2
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=72:00:00
#SBATCH --array=0-1
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step11_h2_reaction_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step11_h2_reaction_%A_%a.err

set -euo pipefail

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

repo=/clusterfs/mhg-data/yaoshen/coach-based_dh
python_bin=/global/home/users/yaoshen/.conda/envs/coach/bin/python
root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step11/h2_reaction/${SLURM_ARRAY_JOB_ID}
spec=revwb97m2/configs/scientific_spec.yaml
species=(W4-17_h W4-17_h2)
name="${species[${SLURM_ARRAY_TASK_ID}]}"
parent_dir="${root}/parent/${name}"
scalar_dir="${root}/scalar/${name}"
r0_output="${root}/r0/${name}.json"

cd "${repo}"
"${python_bin}" revwb97m2/scripts/run_parent_scf.py \
  --species "${name}" --spec "${spec}" --output-dir "${parent_dir}" \
  --max-memory-mb 8000 --verbose 4
"${python_bin}" revwb97m2/scripts/run_scalar_features.py \
  --species "${name}" --spec "${spec}" --parent-dir "${parent_dir}" \
  --output-dir "${scalar_dir}" --max-memory-mb 8000
"${python_bin}" revwb97m2/scripts/evaluate_published_wb97m2_fixture.py \
  --species "${name}" --spec "${spec}" --parent-dir "${parent_dir}" \
  --scalar-dir "${scalar_dir}" --output "${r0_output}" --max-memory-mb 8000
