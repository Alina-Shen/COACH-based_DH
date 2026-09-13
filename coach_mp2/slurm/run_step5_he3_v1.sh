#!/bin/bash
#SBATCH --job-name=coach_s5_he3
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_he3_v1/slurm_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_he3_v1/slurm_%j.err
set -euo pipefail
export QC=/clusterfs/mhg/yaoshen/qchem/trunk
export QCPROG=$QC/build/qcprog.exe
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
export QCSCRATCH=/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_he3_v1
unset QCLOCALSCR
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
project=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2
output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_he3_v1
export TMPDIR=$output/tmp
cd "$output"
for species in He3_47 He3_48 He3_49; do
 for mode in fixed; do
  name=${species}
  test ! -e "$output/$name.out"
  "$QC/bin/qchem" -save -nt 4 "$project/inputs/step5_he3_v1/$name.in" "$output/$name.out" "$name" > "$output/$name.driver.log" 2>&1
 done
done
