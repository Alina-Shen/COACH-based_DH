"""Publish only the explicitly permitted project notes; preserve past chapters."""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[1]
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='07-step2-baseline-and-provenance-audit.md'

def proposed():
    chapter='''# 2026-09-12 — Steps 1–2: baseline checks and source provenance gate

## Contents

- [Step 2 report](../../../../coach-based_dh/coach_mp2/results/step2_progress.md)
- [Source audit](../../../../coach-based_dh/coach_mp2/manifests/step2_provenance_audit_v1.json)
- [Baseline results](../../../../coach-based_dh/coach_mp2/results/step2_baseline_audit_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step1, step2, provenance, baseline, archive-format

User deferred the open-source solver choice; this does not block Steps 1–2.
Step 1 remains complete: all 50 validation checks pass and the 18-step index
and omega=0.27 specification remain unchanged. Step 2 is in progress, awaiting
native pilot validation and matching COACH reference energies.

Reference water/carbon printed component closure passes (1.10305e-10 and
-3.33742e-11 Eh residual). Independent L14_2a geometry-only D4-ATM agrees to
2.16261e-12 Eh. Five targeted parser/closure tests pass. These are preliminary
baseline checks, not a production-orbital reconstruction pass.

Three GSCDB137 scratch samples have empty 800-byte HDF5 containers but nonempty
legacy files; three BigNC qarchive.h5 samples each have 59 datasets including
MOs, density and basis metadata. Six sample directories have no immediate
.in/.out files. Hashes, dataset shapes/scalars, reference source/PDF/fixture
hashes and limitations are recorded. This is not a full Step 5 inventory.
Reference fixture Q-Chem versions differ (5.4.2 water/carbon; 6.3.1 L14), and
cannot establish the supplied scratch's generating build.

User clarified that GSCDB/qchem_inputs supplies input authority after replacing
METHOD with COACH, historical outputs are unavailable, and empty HDF5 files are
acceptable. User authorized testing one or two systems against GSCDB/Analysis.
All ten current Analysis CSV headers lack COACH; requested its reference location.
Historical outputs are no longer treated as a mandatory gate. Exact historical
build identity remains unknown and must not be inferred from a reproduction.

Prepared water SIE4x4_h2o and triplet carbon 16_C_AE18, each in zero-SCF and
separate SCF-repeatability modes. Staged verified copies of legacy files into
/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step2_pilot_v1. Inputs/scripts and
runtime hashes are in coach_mp2; output goes into the permitted heavy-data root.
Existing /clusterfs/mhg/yaoshen/qchem/trunk source registers the expected COACH
constants; no source changes. Pilot job 25820274 uses mhg/mhg/normal, 4 CPUs, 8 GB, one hour.
SCF is explicitly authorized for this diagnostic only; production remains fixed
orbitals. No solver switch or bulk production submission.

Standing user instruction: after every future progress increment, update
COACH-based_mp2.md, especially its plan table; retain frozen step IDs.
'''
    p=NOTES/'COACH-based_mp2.md';plan=p.read_text()
    old='| 2 | COACH baseline and provenance | Pending | Verify COACH source method/build/input provenance and parent energy reconstruction. |'
    new='| 2 | COACH baseline and provenance | In progress — source provenance gate open | Reference component closure/D4 and five tests pass; six scratch samples audited. User supplied GSCDB inputs and accepted missing historical outputs/HDF5; two-system native pilot prepared. Await pilot validation and COACH Analysis reference location. |'
    assert old in plan
    plan=plan.replace(old,new,1)
    plan=plan.replace('Next stable step: 2, COACH baseline and provenance.','Current stable step: 2, COACH baseline and provenance (in progress).',1)
    addition='''## Step 2 progress — 2026-09-12

[Audit report](../../../coach-based_dh/coach_mp2/results/step2_progress.md): reference
water/carbon printed energy-component closure and independent L14 D4-ATM pass;
five targeted tests pass. Three sampled GSCDB137 qarchive.h5 files are empty
containers with legacy scratch present; three sampled BigNC qarchive.h5 files
contain 59 datasets each. User supplied the GSCDB inputs (change METHOD to COACH), accepted absent original
outputs and empty HDF5, and authorized a two-system native reproducibility pilot.
The Analysis CSVs currently have no COACH column; reference location was requested.
Pilot results and reference comparison remain open. Historical generating build
identity is an explicit limitation, not a demand for unavailable outputs.
Step 2 is not complete.
The user deferred solver selection; it does not block Steps 1–2.

'''
    plan=plan.replace('## Objective and decision precedence',addition+'## Objective and decision precedence',1)
    plan=plan.replace('## Contents\n','## Contents\n\n- [Step 2 baseline and provenance audit](./2026-09-12.chapters/'+NAME+')\n',1)
    plan=plan.replace('This is the single live COACH-based_mp2 plan/status authority.','Standing user instruction: update this document, especially the plan table,\nafter every future progress increment.\n\nThis is the single live COACH-based_mp2 plan/status authority.',1)
    idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:', '\n- [Steps 1–2 baseline and provenance audit](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
    return {p:plan,idx:index,NOTES/'2026-09-12.chapters'/NAME:chapter}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
    assert not (NOTES/'2026-09-12.chapters'/NAME).exists()
    for path,text in proposed().items():
        assert path.resolve()==path
        if args.publish:
            with path.open('x' if path.name==NAME else 'w') as f:f.write(text)
            assert path.read_text()==text
        print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
