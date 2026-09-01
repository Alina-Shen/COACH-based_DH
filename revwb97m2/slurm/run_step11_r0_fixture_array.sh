#!/bin/bash
#SBATCH --job-name=r2_s11_r0
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=72:00:00
#SBATCH --array=0-5%3
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step11_r0_fixture_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step11_r0_fixture_%A_%a.err

set -euo pipefail

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

repo=/clusterfs/mhg-data/yaoshen/coach-based_dh
python_bin=/global/home/users/yaoshen/.conda/envs/coach/bin/python
species_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species
output_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step11/paper_precision_r0/${SLURM_ARRAY_JOB_ID}

species=(h2o_SW49 12_NH2rad_HNBrBDE18 BH9_08_1R2 CUAGAU_Au01N0_H AE11_Yb DAPD_B)
specs=(
  revwb97m2/configs/archive/scientific_spec.v3.yaml
  revwb97m2/configs/scientific_spec.yaml
  revwb97m2/configs/scientific_spec.yaml
  revwb97m2/configs/scientific_spec.yaml
  revwb97m2/configs/scientific_spec.yaml
  revwb97m2/configs/scientific_spec.yaml
)

name="${species[${SLURM_ARRAY_TASK_ID}]}"
spec="${specs[${SLURM_ARRAY_TASK_ID}]}"
output="${output_root}/${name}.json"
if [[ -e "${output}" ]]; then
  echo "Refusing to overwrite ${output}" >&2
  exit 2
fi
mkdir -p "${output_root}"

cd "${repo}"
"${python_bin}" revwb97m2/scripts/evaluate_published_wb97m2_fixture.py \
  --species "${name}" \
  --parent-dir "${species_root}/gateway/${name}" \
  --scalar-dir "${species_root}/scalar/gateway/${name}" \
  --spec "${spec}" \
  --output "${output}"
