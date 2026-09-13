#!/bin/bash
#SBATCH --job-name=coach_s8_native
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step8_native_%j.log
set -euo pipefail
export QC=/clusterfs/mhg/yaoshen/qchem/trunk
build=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/build/step8_features_v1
export QCPROG=$build/qcprog.exe
export LD_LIBRARY_PATH=$build:${LD_LIBRARY_PATH:-}
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
export QCSCRATCH=/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step8_v1
unset QCLOCALSCR
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
project=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2
output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step8_v1
export TMPDIR=$output/tmp
cd "$output"
ldd "$QCPROG" > "$output/loaded_libraries.txt"
for name in SIE4x4_h2o 16_C_AE18; do
 for mode in 250974 99590 75302 sr_vv full_hf lr_hf; do
  tag=${name}_${mode}
  unset QCHEM_PRINT_INTEGRATED_DV QCHEM_DUMP_INTEGRATED_DV_INPUTS
  if [[ $mode =~ ^[0-9]+$ ]]; then
   export QCHEM_PRINT_INTEGRATED_DV=1
   export QCHEM_DUMP_INTEGRATED_DV_INPUTS=$output/$tag.bin
  fi
  test ! -e "$output/$tag.out"
  "$QC/bin/qchem" -save -nt 8 "$project/inputs/step8_v1/$tag.in" "$output/$tag.out" "$tag" > "$output/$tag.driver.log" 2>&1
 done
done
