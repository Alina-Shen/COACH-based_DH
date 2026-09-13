#!/bin/bash
#SBATCH --job-name=coach_s5_native
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=02:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2/slurm_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2/slurm_%j.err
set -euo pipefail
export QC=/clusterfs/mhg/yaoshen/qchem/trunk
export QCPROG=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/build/step5_no_orientation_v1/qcprog.exe
export QCAUX=/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux
export QCSCRATCH=/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step5_native_v2
unset QCLOCALSCR
export OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32
project=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2
output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_native_v2
export TMPDIR=$output/tmp
cd "$output"
for name in SIE4x4_h2o 16_C_AE18 He3_47 He3_48 He3_49 ISOL24_i8e; do
 test ! -e "$output/$name.out"
 "$QC/bin/qchem" -save -nt 32 "$project/inputs/step5_native_v2/$name.in" "$output/$name.out" "$name" > "$output/$name.driver.log" 2>&1
done
