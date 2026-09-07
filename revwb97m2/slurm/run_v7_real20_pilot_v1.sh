#!/usr/bin/env bash
#SBATCH --job-name=r2_v7_real20
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=16
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_real20_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_real20_%j.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
export GRB_LICENSE_FILE=/global/home/users/yaoshen/tools/gurobi.lic
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
dh_python=/global/home/users/yaoshen/.conda/envs/dh/bin/python
pilot_root="revwb97m2/results/v7_real20_${SLURM_JOB_ID}"
manifest=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/v7_vv10_refresh_v1/reactions/inputs.json
# Fresh corrected synthetic control, isolated from chemical fit evidence.
"$dh_python" -m revwb97m2.scripts.test_v7_end_to_end --output "${pilot_root}_synthetic"
base=(-m revwb97m2.scripts.run_v7_fit --manifest "$manifest" --budget 14 --seconds 120 --threads 16)
"$dh_python" "${base[@]}" --output "$pilot_root/pass1"
"$dh_python" "${base[@]}" --output "$pilot_root/pass2" --start "$pilot_root/pass1" --grid-candidates "$pilot_root/pass1"
"$dh_python" "${base[@]}" --output "$pilot_root/restart" --start "$pilot_root/pass2" --grid-candidates "$pilot_root/pass1"
# Resume is readback only, not another solve; verifies unchanged run contracts.
"$dh_python" "${base[@]}" --output "$pilot_root/pass2" --start "$pilot_root/pass1" --grid-candidates "$pilot_root/pass1" --resume
"$dh_python" "${base[@]}" --output "$pilot_root/restart" --start "$pilot_root/pass2" --grid-candidates "$pilot_root/pass1" --resume
printf 'Bounded real20 passes, restart and readbacks complete\n'
