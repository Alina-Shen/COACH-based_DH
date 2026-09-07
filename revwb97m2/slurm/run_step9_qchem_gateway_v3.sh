#!/usr/bin/env bash
#SBATCH --job-name=r2_s9_qc
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --array=0-1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step9_qchem_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/step9_qchem_%A_%a.err

set -euo pipefail

module purge
module load gcc/10.5.0
module load ucx/1.14.1
module load openmpi/4.1.6
module load boost/1.83.0

qchem_root=/clusterfs/mhg-data/yaoshen/qchem/trunk
run_root=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/step9_same_archive_v3
cases=(h2o_SW49 12_NH2rad_HNBrBDE18)
species=${cases[$SLURM_ARRAY_TASK_ID]}
case_root=$run_root/$species

test -f "$case_root/PREPARED.json"
test ! -e "$case_root/qchem.out"
test ! -e "$case_root/qchem.pt2.out"
export QC=$qchem_root
export QCPROG=$qchem_root/exe/qcprog.exe
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
export QCSCRATCH=$case_root/qcscratch
unset QCLOCALSCR
unset QCHEM_PRINT_INTEGRATED_DV
unset QCHEM_DUMP_INTEGRATED_DV_INPUTS

"$qchem_root/bin/qchem" -save -nt "$SLURM_CPUS_PER_TASK" \
  "$case_root/input.step9.in" "$case_root/qchem.out" step9_scalar

"$qchem_root/bin/qchem" -save -nt "$SLURM_CPUS_PER_TASK" \
  "$case_root/input.step9.pt2.in" "$case_root/qchem.pt2.out" step9_scalar

touch "$case_root/QCHEM_COMPLETE"
