from pathlib import Path
import argparse
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='10-step2-fixed-orbital-baseline-complete.md'
CHAPTER='''# 2026-09-12 — Step 2 fixed-orbital baseline complete

## Contents

- [Complete work list and explanation](../../../../coach-based_dh/coach_mp2/results/step2_complete.md)
- [44-check native audit](../../../../coach-based_dh/coach_mp2/results/step2_fixed_v3_validation.json)
- [Completion artifact hashes](../../../../coach-based_dh/coach_mp2/manifests/step2_completion_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step2, completed, fixed-orbitals, provenance, Q-Chem

Step 2 complete; next stable step 3. Step 1 rechecked (50 checks), unchanged
scientific specification and step IDs. Solver choice remains deferred.

Found a native fixed-energy route using METHOD COACH, GEN_SCFMAN FALSE,
MAX_SCF_CYCLES 0, MP2_RESTART_NO_SCF TRUE and NO_ORTHO TRUE. The restart flag
suppresses diagonalization; NO_ORTHO suppresses GDM read-in reorthonormalization.
No Q-Chem source modifications, new compilation or SCF optimization required.

Job 25821443 completed but failed MO/density integrity; preserved as rejected.
Corrected job 25821657 completed 0:0 in 59 seconds, MaxRSS 592736K. Both ran
mhg/mhg/normal, 4 CPUs, 8 GB, one-hour limit, with fresh isolated source copies.

Final MO files 53.0 (coefficients and orbital energies) are bitwise unchanged.
Q-Chem recomputes 54.0: differences are at most 2.77556e-17. Explicitly replaced
the overly strict density-byte expectation with an independent occupied-MO
outer-product check; exact MO equality stays required. Both source and output
densities agree with math.fsum reconstruction within the normwise roundoff bound
16*epsilon*||C_occ||_F^2; observed errors use less than 0.52% of the bound.
The earlier reorthonormalizing attempt does not pass this final MO requirement.

Fixed-energy water -76.4335179420 Eh differs by +1.90001e-9 Eh from its COACH
fixture. Carbon -37.8454590857 Eh differs by +1.22840e-6 Eh from both fixture
and paper raw_data!D298 (AE18_6). Both pass the existing 2e-6 Eh tolerance.
Component closure residuals are 0 and 1.00009e-10 Eh, within 2e-8 Eh. Older-driver
DFT Correlation includes VV10; use final Nuclear Repu. print precision.
All 44 native audit checks and six targeted tests pass. Failure tests cover
truncated output, missing evidence/components, nonfinite data and density changes.

Current build/input/source hashes, original-source invariance and workbook
comparison are recorded. Historical generating build remains unknown under the
user's accepted no-original-output policy. This is a two-system baseline, not
full inventory, BigNC native validation, PT2/feature release or bulk production.
Step 5 and later gates remain pending. All writes stayed in the three allowed
coach_mp2 roots plus project notes. Updated progress, protocol, README, live plan
table, and new dated chapter; preserved previous chapters and failed evidence.
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args()
 ch=NOTES/'2026-09-12.chapters'/NAME;assert not ch.exists()
 planpath=NOTES/'COACH-based_mp2.md';plan=planpath.read_text();lines=plan.splitlines()
 found=[i for i,l in enumerate(lines) if l.startswith('| 2 |')];assert len(found)==1
 lines[found[0]]='| 2 | COACH baseline and provenance | Complete — fixed-orbital baseline PASS | Job 25821657: unchanged MOs, independently verified density, parent-energy/fixture/paper checks; 44 audit checks and six tests pass. Historical generating build remains unknown under accepted provenance policy. |'
 plan='\n'.join(lines)+'\n';plan=plan.replace('Current stable step: 2, COACH baseline and provenance (in progress).','Steps 1 and 2 complete. Next stable step: 3, immutable data roles and metrics.')
 start=plan.index('## Step 2 latest reference check');end=plan.index('## Objective and decision precedence',start)
 plan=plan[:start]+'''## Step 2 completed — 2026-09-12

[Completion report and full work list](../../../coach-based_dh/coach_mp2/results/step2_complete.md).
Native no-update COACH evaluation passes for water and carbon using the older
SCF driver, MP2_RESTART_NO_SCF TRUE and NO_ORTHO TRUE. MO coefficients and
orbital energies remain byte-identical. Independently reconstructed source/output
densities differ only at roundoff (2.77556e-17); the density-byte expectation was
explicitly superseded by the documented normwise reconstruction bound.

Job 25821657 completed 0:0; all 44 native audit checks and six tests pass.
Fixed-energy differences from COACH references: water +1.90001e-9 Eh; carbon
+1.22840e-6 Eh, both within the pre-existing 2e-6 Eh tolerance. Carbon also
matches the paper workbook within that tolerance. Historical generating build
remains unknown and is not inferred from this reproduction. Full archive/BigNC/
feature/MP2 validation remains in later steps. Earlier attempts and decisions
are preserved in dated chapters 07–09 and the completion report.

'''+plan[end:]
 plan=plan.replace('## Contents\n','## Contents\n\n- [Step 2 fixed-orbital completion](./2026-09-12.chapters/'+NAME+')\n',1)
 idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:', '\n- [Step 2 fixed-orbital baseline complete](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for path,text in {planpath:plan,idx:index,ch:CHAPTER}.items():
  assert path.resolve()==path
  if args.publish:
   with path.open('x' if path==ch else 'w') as f:f.write(text)
   assert path.read_text()==text
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
