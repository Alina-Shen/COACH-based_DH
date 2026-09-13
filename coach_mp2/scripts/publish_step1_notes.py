"""Publish the requested Step 1 notes and root README updates, within explicit scope.

Default is a read-only preview. --publish requires filesystem permission for the
notes/heavy/scratch roots. Previous dated chapters are never overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
HEAVY=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2')
SCRATCH=Path('/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2')
CHAPTER='05-step1-scientific-specification-frozen.md'

def proposed():
    plan_path=NOTES/'COACH-based_mp2.md';plan=plan_path.read_text()
    if './2026-09-12.chapters/'+CHAPTER in plan:raise ValueError('Step 1 already published')
    index=json.loads((ROOT/'configs/step_index_v1.json').read_text())
    table='''## Frozen step index and progress

The 18 step IDs were frozen first on 2026-09-12 in
[step_index_v1.json](../../../coach-based_dh/coach_mp2/configs/step_index_v1.json).
Never renumber or reuse IDs; add substeps or append new IDs with versioned
change control. Step 5 now explicitly names archive import, Step 9 names
constraint implementation, and Step 16 names final model selection/freeze.
Step 7 remains optional and nonblocking. IDs are tracking identifiers, not a
strict chronology: Step 13/14 pilots can precede Step 12 bulk production;
full-domain assembly still requires the production outputs.

| Step | Frozen objective | Status | Exit criterion / next action |
|---:|---|---|---|
'''
    for item in index['steps']:
        status='Complete — Step 1 validation PASS' if item['id']==1 else 'Deferred, optional' if item['id']==7 else 'Pending'
        table+='| {id} | {title} | {status} | {exit_criterion} |\n'.format(status=status,**item)
    start=plan.index('## Stable project steps');end=plan.index('## Recommended improvements',start)
    plan=plan[:start]+table+'\n'+plan[end:]
    plan=plan.replace('## Objective and decision precedence','''## Step 1 completed — 2026-09-12

[Scientific specification v1](../../../coach-based_dh/coach_mp2/configs/scientific_spec_v1.json)
and the 18-step index are hash-frozen. All 17 adversarial tests and 50 post-freeze
checks pass. The scientific contract is authoritative; the earlier mirror
contract is preparation history. [Completion report](../../../coach-based_dh/coach_mp2/results/step1_complete.md)
and [dated evidence](./2026-09-12.chapters/05-step1-scientific-specification-frozen.md)
record artifacts, checks and remaining gates. Source path remains pending;
no native chemistry, orbital coverage or execution authorization is claimed.
Next stable step: 2, COACH baseline and provenance.

## Objective and decision precedence''',1)
    plan=plan.replace('- [Preparation contract and source snapshot]', '- [Step 1 scientific freeze](./2026-09-12.chapters/05-step1-scientific-specification-frozen.md)\n- [Preparation contract and source snapshot]',1)
    plan=plan.replace('Editing this\nplanning contract does not implement or validate the chemistry port.','The Step 1 scientific freeze defines these settings; the native chemistry\nport and its numerical validation remain later implementation gates.')
    plan=plan.replace('Both root READMEs describe the preparation state and storage purposes.','Q-Chem scratch root: `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2`.\nWrites are restricted to these three project roots, except project notes.\nOriginal COACH, revwb97m2 and `/clusterfs/mhg-data/yaoshen/GSCDB` are read-only.\nAll three root READMEs document their purposes; no task staging writes outside\nthese roots are allowed.')
    plan=plan.replace('Prepared now: a reviewable mirror contract, source hash inventory, and this\nupdated plan. No operational runner or production scientific spec is claimed.','Completed now: scientific specification v1, frozen 18-step index, source\nidentity inventory, semantic validator, adversarial tests and freeze evidence.\nThe earlier mirror contract is superseded. No operational chemistry/fitting\nrunner or runtime release is claimed.')
    dated=NOTES/'2026-09-12.md';dated_text=dated.read_text().replace('\nTags:', '\n- [Step 1 scientific specification and index frozen](./2026-09-12.chapters/'+CHAPTER+')\n\nTags:',1)
    chapter='''# 2026-09-12 — Step 1 scientific specification and index frozen

## Contents

- [Live project plan](../COACH-based_mp2.md)
- [Complete change report](../../../../coach-based_dh/coach_mp2/results/step1_complete.md)
- [Frozen specification](../../../../coach-based_dh/coach_mp2/configs/scientific_spec_v1.json)
- [Frozen index](../../../../coach-based_dh/coach_mp2/configs/step_index_v1.json)
- [Freeze hashes](../../../../coach-based_dh/coach_mp2/manifests/scientific_spec_v1.freeze.json)
- [Validation evidence](../../../../coach-based_dh/coach_mp2/results/step1_validation.json)
- [Test evidence](../../../../coach-based_dh/coach_mp2/results/step1_tests.json)

Tags: COACH-based_mp2, step-1, scientific-specification, frozen-index, omega-0.27, validation, storage-scope

User authorized Step 1 and index freeze, with all writes limited to code root
`/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2`, heavy root
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2`, Q-Chem scratch root
`/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2`, plus project notes.
Read-only database authority is `/clusterfs/mhg-data/yaoshen/GSCDB`.

Froze all 18 IDs first, preserving numbers. Clarified Step 5 as archive import,
Step 9 as constraint implementation and Step 16 as final model selection/freeze.
Optional Step 7 LMP2 is nonblocking; assembly/optimizer pilots may precede bulk.
Mutable progress is separate from the frozen index.

Completed authoritative scientific specification v1: COACH UKS source,
fixed target omega=0.27, zero new SCF, 292 features with explicit degree order,
consistent exchange/Nofit, total frozen-core RI-UMP2, VV10 b=5.5/ATM,
C0/UEG/independent bounds, exact mirrored roles/weights/grids and current
expanded-quadratic K14–82 campaign. Optional later omega scan is disabled until
design choices are fixed; no future scan grid/budget selected.

Recorded 35 source hashes; GSCDB Info DatasetEval/Datasets/Standard_errors are
byte-identical to reference (8448/142/137 rows). Independent inherited-science
comparison passes. 17 adversarial tests and 50 validator checks PASS. Tests
cover scientific contamination, holdout leakage, changed optimizer/grid policies,
nonfinite/duplicate JSON, content hashes and output path/symlink escapes.

Specification SHA-256:
`f4977550a9905cb630aaeea1039bffab0ae500f4ee86c627ecb10d3fb62e5aae`.
Index SHA-256:
`29383d65b257fa04d5b1d56cd4d75800aa0f8a335a9116aabcd281ca4ae590fa`.
14-artifact scientific hash freeze published; no Git commit performed.

Updated scientific/storage docs, three root READMEs, live plan and dated index.
No writes to reference projects or /tmp; Python -B prevented reference bytecode
writes. No chemistry, orbital copying, heavy numerical generation, solver use,
Slurm submission or inherited runtime-pass claims. Orbital source path remains
pending; Step 1 is scientifically complete without it. Next: Step 2 provenance;
source-dependent portions need the user-provided archives/associated inputs.

Recheck with `python3.9 -B coach_mp2/scripts/validate_scientific_spec.py` and
`python3.9 -B -m unittest discover -s coach_mp2/tests -p 'test_*.py' -v`.
'''
    heavy='''# COACH MP2 heavy numerical data

## Contents

- [Storage contract](../../coach-based_dh/coach_mp2/docs/storage_layout.md)
- [Scientific specification](../../coach-based_dh/coach_mp2/configs/scientific_spec_v1.json)

Root: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2`.
Current contents: this README only. Step 1 generated no heavy numerical data.

Future numerical artifacts belong in species/ (validated stages/checkpoints),
processed/ (reaction matrices), optimization/ (bulk solver output), logs/ (full
logs) and build/ (heavy project-local builds) when those stages are implemented.
Q-Chem working scratch belongs under `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2`.
Scripts, settings, manifests and important lightweight results belong in the
code root `/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2`.

Initial scientific contract is fixed COACH orbitals, target omega=0.27,
zero new SCF and total RI-UMP2. Source path/identity and native feature gates
remain pending. Use explicit spec/source/archive/omega hashes and non-overwriting
atomic publication. Scratch must not hold the only reproducibility evidence.
Never reuse reference-project orbital-dependent artifacts as COACH data.
Keep this README and the code/scratch documentation current together.
'''
    scratch='''# COACH MP2 Q-Chem scratch

## Contents

- [Storage contract](../../coach-based_dh/coach_mp2/docs/storage_layout.md)
- [Scientific specification](../../coach-based_dh/coach_mp2/configs/scientific_spec_v1.json)

Root: `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2`.
Current contents: this README only. No orbital archives have been copied.
The user will supply the read-only source orbital path later.

Place isolated per-job Q-Chem working directories and verified archive copies
here. Compare source/copy hashes before use and preserve the source. Require
COACH provenance and zero new SCF cycles, with target energy omega=0.27.
Do not run from authoritative source scratch or silently overwrite successful
stages. Publish durable numerical results and provenance to the project heavy
root; keep scripts/configuration/important summaries in the code root.
Reference projects and shared Q-Chem source/build trees are read-only.
'''
    return {plan_path:plan,dated:dated_text,NOTES/'2026-09-12.chapters'/CHAPTER:chapter,
            HEAVY/'README.md':heavy,SCRATCH/'README.md':scratch}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    files=proposed()
    allowed={NOTES/'COACH-based_mp2.md',NOTES/'2026-09-12.md',NOTES/'2026-09-12.chapters'/CHAPTER,HEAVY/'README.md',SCRATCH/'README.md'}
    assert set(files)==allowed
    assert not (NOTES/'2026-09-12.chapters'/CHAPTER).exists()
    assert not (SCRATCH/'README.md').exists()
    for path,text in files.items():
        if path.resolve()!=path:raise ValueError('Unexpected destination symlink')
        if args.publish:
            mode='x' if path==NOTES/'2026-09-12.chapters'/CHAPTER or path==SCRATCH/'README.md' else 'w'
            with path.open(mode) as handle:handle.write(text)
        print(json.dumps({'path':str(path),'bytes':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest(),'published':args.publish}))
    if args.publish:
        for path,text in files.items():assert path.read_text()==text

if __name__=='__main__':main()
