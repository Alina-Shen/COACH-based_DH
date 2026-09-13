#!/usr/bin/env bash
#SBATCH --job-name=r2_scip_long
#SBATCH --partition=cm1
#SBATCH --account=lr_qchem
#SBATCH --qos=condo_qchem
#SBATCH --exclude=n0001.cm1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=02:20:00
#SBATCH --array=0-2
#SBATCH --no-requeue
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/scip_long_%A_%a.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/scip_long_%A_%a.err
set -euo pipefail
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
unset GRB_LICENSE_FILE
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
SCIP_PYTHON=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/environments/scip_pilot_v1/bin/python
case "${SLURM_ARRAY_TASK_ID:?}" in
  0) SCIP_CASE=discovery14; SCIP_START=original; SCIP_SECONDS=7200 ;;
  1) SCIP_CASE=discovery14; SCIP_START=incumbent; SCIP_SECONDS=7200 ;;
  2) SCIP_CASE=selected80; SCIP_START=incumbent; SCIP_SECONDS=600 ;;
  *) exit 2 ;;
esac
SCIP_OUTPUT=/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/fitting/scip_alternative_v1/long_${SLURM_ARRAY_JOB_ID}/${SLURM_ARRAY_TASK_ID}_${SCIP_CASE}_${SCIP_START}
git rev-parse HEAD
sha256sum revwb97m2/scip_alternative_v1/{backend,runner,runtime,tests}.py revwb97m2/scip_alternative_v1/run_long_comparison.sh
"$SCIP_PYTHON" -B -c 'from revwb97m2.scip_alternative_v1.runtime import bootstrap; bootstrap(); import pytest; raise SystemExit(pytest.main(["-q","-p","no:cacheprovider","revwb97m2/scip_alternative_v1/tests.py"]))'
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner run --output "$SCIP_OUTPUT" --reference "$SCIP_CASE" --start "$SCIP_START" --seconds "$SCIP_SECONDS" --threads 1 --memory-mib 8192
"$SCIP_PYTHON" -B -m revwb97m2.scip_alternative_v1.runner validate --output "$SCIP_OUTPUT"
# Turn scientific rejection into a failed job while preserving all diagnostics.
"$SCIP_PYTHON" -B -c 'import json,sys; from pathlib import Path; r=json.loads((Path(sys.argv[1])/"result.json").read_text()); raise SystemExit(0 if r["passed"] else 3)' "$SCIP_OUTPUT"
