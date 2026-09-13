#!/usr/bin/env bash
#SBATCH --job-name=r2_scip_pilot
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --exclude=n0001.cm1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --no-requeue
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/scip_pilot_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/scip_pilot_%j.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
unset GRB_LICENSE_FILE
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
SCIP_PYTHON=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/environments/scip_pilot_v1/bin/python
SCIP_OUTPUT=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/scip_alternative_v1/${SLURM_JOB_ID}
"$SCIP_PYTHON" -B -c 'from revwb97m2.scip_alternative_v1.runtime import bootstrap; bootstrap(); import pytest; raise SystemExit(pytest.main(["-q","-p","no:cacheprovider","revwb97m2/scip_alternative_v1/tests.py"]))'
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner run --output "$SCIP_OUTPUT/discovery14_original" --reference discovery14 --start original --seconds 60
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner validate --output "$SCIP_OUTPUT/discovery14_original"
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner run --output "$SCIP_OUTPUT/discovery14_incumbent" --reference discovery14 --start incumbent --seconds 60
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner validate --output "$SCIP_OUTPUT/discovery14_incumbent"
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner run --output "$SCIP_OUTPUT/selected80_incumbent" --reference selected80 --start incumbent --seconds 60
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner validate --output "$SCIP_OUTPUT/selected80_incumbent"
