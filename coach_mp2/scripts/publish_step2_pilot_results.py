from pathlib import Path
import json,argparse
ROOT=Path(__file__).resolve().parents[1]
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='08-step2-native-coach-repeatability.md'
REPORT='''# 2026-09-12 — Native COACH repeatability pilot

## Contents

- [Native results](../../../../coach-based_dh/coach_mp2/results/step2_pilot_v1.json)
- [Runtime/input/source hashes](../../../../coach-based_dh/coach_mp2/manifests/step2_pilot_v1.json)
- [Validation protocol](../../../../coach-based_dh/coach_mp2/configs/step2_validation_protocol_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step2, Q-Chem, repeatability, legacy-scratch

Job 25820274 completed, exit 0:0, elapsed 00:05:36, batch MaxRSS 1028704K.
Q-Chem 6.4.0, existing /clusterfs/mhg/yaoshen/qchem/trunk build; runtime and
relevant source registration hashed. User authorized the two-system diagnostic
SCF and accepted missing historical outputs/HDF5. Original generating build
remains unknown; reproduction does not establish that historical identity.

| System | Converged COACH energy (Eh) | Difference from existing COACH fixture (Eh) | Cycles |
| --- | ---: | ---: | ---: |
| SIE4x4_h2o | -76.4335179440 | -1.00002e-10 | 5 |
| 16_C_AE18 | -37.8454603141 | 0 at printed precision | 7 |

Both pass the predeclared 2e-6 Eh tolerance and terminate normally. GSCDB inputs
match fixture geometry, charge/spin, basis, grid, convergence and THRESH. Water's
first-cycle difference was 1.80000e-9 Eh; carbon's was 4.29200e-7 Eh. These
first-cycle observations are not yet a dedicated no-update evaluator validation.

Both zero-cycle cases read legacy scratch and terminate normally, without HDF5.
GEN_SCFMAN TRUE / MAX_SCF_CYCLES 0 prints 'Skip SCF calculation as requested'
and does not evaluate energy. Do not mark this as a fixed-orbital energy pass.
The production energy route still needs a verified evaluator; do not silently
replace zero SCF cycles with a converged SCF in production.

All ten current CSV headers in /clusterfs/mhg-data/yaoshen/GSCDB/Analysis lack
COACH. Asked the user for the matching COACH reference location. The reported
comparison uses existing FunctionalCOACH regression outputs, not Analysis.
Step 1 remains complete (50 checks); Step 2 is in progress with native
repeatability passed, pending reference clarification and dedicated fixed-orbital
energy reconstruction. Solver choice remains deferred and is not a blocker.

Added audit/prepare/check scripts, four pilot inputs, Slurm settings, provenance
and protocol manifests, five passing targeted tests, and result reports. All
source files remained read-only; legacy copies and runtime files stayed under
permitted coach_mp2 roots. No bulk production or solver installation. Live plan
table updated; retain this practice after every future progress increment.
'''
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
 chapter=NOTES/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 planpath=NOTES/'COACH-based_mp2.md';plan=planpath.read_text()
 lines=plan.splitlines();count=0
 for i,line in enumerate(lines):
  if line.startswith('| 2 |'):
   lines[i]='| 2 | COACH baseline and provenance | In progress — native repeatability PASS | Job 25820274: water/carbon converge and match COACH fixtures; legacy read passes. Analysis has no COACH column; reference clarification and dedicated zero-update energy reconstruction remain open. |';count+=1
 assert count==1;plan='\n'.join(lines)+'\n'
 plan=plan.replace('## Contents\n','## Contents\n\n- [Native COACH pilot results](./2026-09-12.chapters/'+NAME+')\n',1)
 plan=plan.replace('## Step 2 progress — 2026-09-12','''## Step 2 latest native results — 2026-09-12

Job 25820274 completed successfully in 5m36s. Water and carbon converge and
match existing COACH fixtures by -1.0e-10 Eh and zero at printed precision.
Both legacy scratch reads pass. Zero-cycle mode skips energy evaluation in this
build, so dedicated fixed-orbital energy reconstruction remains open. The requested
Analysis reference still needs clarification (no COACH column). Step 2 remains
in progress. [Detailed native results](../../../coach-based_dh/coach_mp2/results/step2_pilot_v1.json).

## Step 2 earlier progress — 2026-09-12''',1)
 idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:', '\n- [Native COACH repeatability pilot](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for p,s in {planpath:plan,idx:index,chapter:REPORT}.items():
  assert p.resolve()==p
  if args.publish:
   with p.open('x' if p==chapter else 'w') as f:f.write(s)
   assert p.read_text()==s
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(p))
if __name__=='__main__':main()
