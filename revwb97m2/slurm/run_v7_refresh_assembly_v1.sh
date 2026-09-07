#!/usr/bin/env bash
#SBATCH --job-name=r2_v7_assembly
#SBATCH --partition=mhg
#SBATCH --account=mhg
#SBATCH --qos=normal
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_assembly_%j.out
#SBATCH --error=/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/v7_assembly_%j.err
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
/global/home/users/yaoshen/.conda/envs/dh/bin/python -u - <<'PY'
from pathlib import Path
from revwb97m2.v7_refresh import assemble,load_plan
from revwb97m2.fit_inputs import load_inputs,digest
p=Path('revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json')
plan,settings=load_plan(p)
assemble(p)  # Revalidates all 38 species before any publication.
manifest=Path(plan['output_root'])/'reactions/inputs.json'
arrays,record=load_inputs(manifest,settings)
assert arrays['feature_matrix'].shape==(20,292)
assert (manifest.parent/'ASSEMBLY_COMPLETE').is_file()
print('Independent fitter readback PASS',flush=True)
print('Manifest',manifest,'SHA256',digest(manifest),flush=True)
for name,array in arrays.items():print(name,array.shape,flush=True)
PY
