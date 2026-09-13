#!/bin/bash
#SBATCH --job-name=coach_s6_pt2
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step6_native_%j.log
set -euo pipefail
export QC=/clusterfs/mhg/yaoshen/qchem/trunk
export QCPROG=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/build/step5_no_orientation_v1/qcprog.exe
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
export QCSCRATCH=/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step6_v1
unset QCLOCALSCR
export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
project=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2
output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step6_v1
export TMPDIR=$output/tmp
cd "$output"
for name in SIE4x4_h2o 16_C_AE18; do
 for variant in MP2_FC RIMP2_FC RIMP2_0; do
  tag=${name}_${variant}
  test ! -e "$output/$tag.out"
  "$QC/bin/qchem" -save -nt 8 "$project/inputs/step6_v1/$tag.in" "$output/$tag.out" "$tag" > "$output/$tag.driver.log" 2>&1
 done
done
