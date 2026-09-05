#!/usr/bin/env bash
#SBATCH --job-name=revwb97m2_q3
#SBATCH --partition=lr8
#SBATCH --account=lr_mhg2
#SBATCH --qos=mhg2_lr8_normal
#SBATCH --array=0-5
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/q3_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/q3_%A_%a.err

set -euo pipefail

module purge
module load gcc/10.5.0
module load ucx/1.14.1
module load openmpi/4.1.6
module load boost/1.83.0

project=/clusterfs/mhg-data/yaoshen/coach-based_dh
run_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q3_native_v1
python=/global/home/users/yaoshen/.conda/envs/coach/bin/python
qchem_root=/clusterfs/mhg-data/yaoshen/qchem/trunk

cases=(
  h2o_SW49/250974
  h2o_SW49/99590
  h2o_SW49/75302
  12_NH2rad_HNBrBDE18/250974
  12_NH2rad_HNBrBDE18/99590
  12_NH2rad_HNBrBDE18/75302
)
case_rel=${cases[$SLURM_ARRAY_TASK_ID]}
case_root=$run_root/$case_rel

test -f "$case_root/PREPARED.json"
test ! -e "$case_root/qchem.out"
test ! -e "$case_root/integrated_dv_inputs.bin"

export QC=$qchem_root
export QCPROG=$qchem_root/exe/qcprog.exe
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
export QCSCRATCH=$case_root/qcscratch
unset QCLOCALSCR
export QCHEM_PRINT_INTEGRATED_DV=1
export QCHEM_DUMP_INTEGRATED_DV_INPUTS=$case_root/integrated_dv_inputs.bin

"$qchem_root/bin/qchem" -save -nt "$SLURM_CPUS_PER_TASK" \
  "$case_root/input.q3.in" "$case_root/qchem.out" q3_gateway

"$python" "$project/revwb97m2/scripts/validate_q3_qchem_case.py" "$case_root"
touch "$case_root/Q3_CASE_PASS"
