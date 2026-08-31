#!/bin/bash
#SBATCH --job-name=r2_s10_ghost
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=240G
#SBATCH --time=12:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step10_ghost_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step10_ghost_%j.err

set -euo pipefail

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

repo=/clusterfs/mhg-data/yaoshen/coach-based_dh
python_bin=/global/home/users/yaoshen/.conda/envs/coach/bin/python
data_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species
name=L14_GGG_monB
spec=revwb97m2/configs/scientific_spec.yaml
parent_dir="${data_root}/gateway/${name}"
semilocal_dir="${data_root}/semilocal/gateway/${name}"
scalar_dir="${data_root}/scalar/gateway/${name}"
validation_dir="${data_root}/validation/gateway/${name}"

cd "${repo}"
mkdir -p "${validation_dir}"

if [[ ! -f "${parent_dir}/PARENT_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_parent_scf.py \
    --species "${name}" --spec "${spec}" --output-dir "${parent_dir}" \
    --max-memory-mb 240000 --verbose 4
else
  echo "restart-skip parent ${name}: validated completion marker exists"
fi

if [[ ! -f "${semilocal_dir}/SEMILOCAL_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_semilocal_features.py \
    --species "${name}" --spec "${spec}" --parent-dir "${parent_dir}" \
    --output-dir "${semilocal_dir}" --max-memory-mb 240000 --block-size 2000
else
  echo "restart-skip semilocal ${name}: validated completion marker exists"
fi

if [[ ! -f "${scalar_dir}/SCALAR_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_scalar_features.py \
    --species "${name}" --spec "${spec}" --parent-dir "${parent_dir}" \
    --output-dir "${scalar_dir}" --max-memory-mb 240000
else
  echo "restart-skip scalar ${name}: validated completion marker exists"
fi

"${python_bin}" revwb97m2/scripts/validate_parent_scf.py \
  --parent-dir "${parent_dir}" --spec "${spec}" \
  --output "${validation_dir}/parent_validation.json"
"${python_bin}" revwb97m2/scripts/validate_semilocal_features.py \
  --semilocal-dir "${semilocal_dir}" --spec "${spec}" \
  --output "${validation_dir}/semilocal_validation.json" \
  --max-memory-mb 240000 --block-size 2000
"${python_bin}" revwb97m2/scripts/validate_scalar_features.py \
  --scalar-dir "${scalar_dir}" --spec "${spec}" \
  --output "${validation_dir}/scalar_validation.json"

date -u +%Y-%m-%dT%H:%M:%SZ > "${validation_dir}/GATEWAY_COMPLETE"
