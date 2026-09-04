#!/bin/bash
# Common task body. Invoke only through a reviewed memory-class SBATCH script.

set -euo pipefail

: "${STEP12_MEMORY_CLASS_MB:?wrapper must set STEP12_MEMORY_CLASS_MB}"
: "${STEP12_TIER:?wrapper must set STEP12_TIER}"
: "${STEP12_BLOCK_SIZE:?wrapper must set STEP12_BLOCK_SIZE}"
: "${SLURM_ARRAY_TASK_ID:?must run as a Slurm array task}"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

repo=/clusterfs/mhg-data/yaoshen/coach-based_dh
python_bin=/global/home/users/yaoshen/.conda/envs/coach/bin/python
selection=${repo}/revwb97m2/manifests/step12/step12_pilot_selection_v1.csv
inventory=${repo}/revwb97m2/manifests/step12/step12_fitting_inventory_v1.csv
spec=revwb97m2/configs/scientific_spec.yaml
pilot_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step12/pilots/v1

name=$(awk -F, -v memory="${STEP12_MEMORY_CLASS_MB}" -v tier="${STEP12_TIER}" \
  -v task_id="${SLURM_ARRAY_TASK_ID}" \
  'NR > 1 && $3 == memory && $4 == tier && $1 == task_id {print $2}' "${selection}")
if [[ -z "${name}" ]]; then
  echo "No pilot row for class=${STEP12_MEMORY_CLASS_MB}, tier=${STEP12_TIER}, index=${SLURM_ARRAY_TASK_ID}" >&2
  exit 2
fi

inventory_row=$(awk -F, -v species="${name}" 'NR > 1 && $2 == species {print; exit}' "${inventory}")
if [[ -z "${inventory_row}" ]]; then
  echo "Pilot species absent from frozen inventory: ${name}" >&2
  exit 2
fi
IFS=, read -r scope inventory_name inventory_tier memory_class qchem_mem_total \
  qchem_mem_static requested_memory_gib pyscf_max_memory_mb partition account qos \
  wall_hours cpus remainder <<< "${inventory_row}"
if [[ "${inventory_name}" != "${name}" || "${inventory_tier}" != "${STEP12_TIER}" \
      || "${memory_class}" != "${STEP12_MEMORY_CLASS_MB}" ]]; then
  echo "Pilot/inventory identity mismatch for ${name}" >&2
  exit 2
fi
if [[ "${SLURM_CPUS_PER_TASK}" != "${cpus}" ]]; then
  echo "CPU allocation mismatch for ${name}: Slurm=${SLURM_CPUS_PER_TASK}, inventory=${cpus}" >&2
  exit 2
fi

if [[ "${STEP12_PREFLIGHT_ONLY:-0}" == "1" ]]; then
  echo "preflight passed: species=${name} tier=${inventory_tier} memory_class_mb=${memory_class} requested_memory_gib=${requested_memory_gib} cpus=${cpus}"
  exit 0
fi

species_root=${pilot_root}/${scope}/${name}
parent_dir=${species_root}/parent
semilocal_dir=${species_root}/semilocal_combined_measurement
# Keep the original amplitude-retaining pilot artifacts immutable.  Failed
# species have preserved temporary directories under the legacy name, while
# new/retried work uses the energy-only DF-UMP2 implementation and a new path.
legacy_scalar_dir=${species_root}/scalar_combined_measurement
energy_only_scalar_dir=${species_root}/scalar_energy_only_measurement_v2
if [[ -f "${legacy_scalar_dir}/SCALAR_COMPLETE" ]]; then
  scalar_dir=${legacy_scalar_dir}
else
  scalar_dir=${energy_only_scalar_dir}
fi
assembly_dir=${species_root}/assembly_measurement
validation_dir=${species_root}/validation
mkdir -p "${validation_dir}"

refuse_partial() {
  local directory=$1
  local marker=$2
  if [[ -e "${directory}" && ! -f "${directory}/${marker}" ]]; then
    echo "Preserved partial/failed directory requires review: ${directory}" >&2
    exit 3
  fi
}

cd "${repo}"
refuse_partial "${parent_dir}" PARENT_COMPLETE
if [[ ! -f "${parent_dir}/PARENT_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_parent_scf.py \
    --species "${name}" --spec "${spec}" --stage pilot \
    --output-dir "${parent_dir}" --max-memory-mb "${pyscf_max_memory_mb}" \
    --block-size "${STEP12_BLOCK_SIZE}" --verbose 4
fi

refuse_partial "${semilocal_dir}" SEMILOCAL_COMPLETE
if [[ ! -f "${semilocal_dir}/SEMILOCAL_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_semilocal_features.py \
    --species "${name}" --spec "${spec}" --stage pilot \
    --parent-dir "${parent_dir}" --output-dir "${semilocal_dir}" \
    --max-memory-mb "${pyscf_max_memory_mb}" --block-size "${STEP12_BLOCK_SIZE}"
fi

refuse_partial "${scalar_dir}" SCALAR_COMPLETE
if [[ ! -f "${scalar_dir}/SCALAR_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_scalar_features.py \
    --species "${name}" --spec "${spec}" --stage pilot \
    --parent-dir "${parent_dir}" --output-dir "${scalar_dir}" \
    --max-memory-mb "${pyscf_max_memory_mb}"
fi

refuse_partial "${assembly_dir}" ASSEMBLY_COMPLETE
if [[ ! -f "${assembly_dir}/ASSEMBLY_COMPLETE" ]]; then
  "${python_bin}" revwb97m2/scripts/run_r1_r2_assembly.py \
    --semilocal-dir "${semilocal_dir}" --scalar-dir "${scalar_dir}" \
    --output-dir "${assembly_dir}"
fi

"${python_bin}" revwb97m2/scripts/validate_parent_scf.py \
  --parent-dir "${parent_dir}" --spec "${spec}" \
  --output "${validation_dir}/parent_validation.json"
"${python_bin}" revwb97m2/scripts/validate_semilocal_features.py \
  --semilocal-dir "${semilocal_dir}" --spec "${spec}" \
  --output "${validation_dir}/semilocal_validation.json" \
  --max-memory-mb "${pyscf_max_memory_mb}" --block-size "${STEP12_BLOCK_SIZE}"
"${python_bin}" revwb97m2/scripts/validate_scalar_features.py \
  --scalar-dir "${scalar_dir}" --spec "${spec}" \
  --output "${validation_dir}/scalar_validation.json"
date -u +%Y-%m-%dT%H:%M:%SZ > "${validation_dir}/PILOT_COMPLETE"
