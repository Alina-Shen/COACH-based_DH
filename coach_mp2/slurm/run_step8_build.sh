#!/bin/bash
#SBATCH --job-name=coach_s8_build
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=01:00:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step8_build_%j.log
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
/global/home/users/yaoshen/.conda/envs/dh/bin/python -B coach_mp2/scripts/build_step8.py
