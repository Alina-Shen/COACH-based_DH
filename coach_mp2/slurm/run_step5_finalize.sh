#!/bin/bash
#SBATCH --job-name=coach_s5_finalize
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step5_finalize_%j.log
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
python3 -B coach_mp2/scripts/finalize_step5.py
python3 -B coach_mp2/scripts/publish_step5_completion_notes.py --publish
