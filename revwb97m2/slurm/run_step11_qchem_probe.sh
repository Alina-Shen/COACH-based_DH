#!/bin/bash
#SBATCH --job-name=r2_s11_qc
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=72:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step11_qchem_probe_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step11_qchem_probe_%j.err

set -euo pipefail

repo=/clusterfs/mhg-data/yaoshen/coach-based_dh
probe=${STEP11_QCHEM_PROBE:-qchem_water_probe}
data_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step11/${probe}/${SLURM_JOB_ID}
input=${repo}/revwb97m2/fixtures/published_wb97m2/${probe}.in
output=${data_root}/qchem.out
scratch=${data_root}/qcscratch

if [[ ! -f "${input}" ]]; then
  echo "Missing fixture input ${input}" >&2
  exit 2
fi
if [[ -e "${output}" ]]; then
  echo "Refusing to overwrite ${output}" >&2
  exit 2
fi
mkdir -p "${data_root}" "${scratch}"

export QCSCRATCH="${scratch}"
export QC=/clusterfs/mhg/yaoshen/qchem/loco_os_yao
export QCPROG=/clusterfs/mhg/yaoshen/qchem/loco_os_yao/build/qcprog.exe
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
unset QCLOCALSCR

"${QC}/bin/qchem" -nt "${SLURM_CPUS_PER_TASK}" "${input}" "${output}"
