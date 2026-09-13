from pathlib import Path
import json,argparse
R=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2');N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh');NAME='14-step5-quarantine-investigation-and-gdb9-deferral.md'
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args()
 native=R/'results/step5_he3_native_validation.json';passed=native.exists() and json.loads(native.read_text())['passed']
 state='PASS: all three fixed-parent reads complete with unchanged MO/energy file bytes and density closure.' if passed else 'Submitted/running job 25826223; native read validation remains pending.'
 if native.exists() and not passed:
  report=json.loads(native.read_text());state=str(report['completed_cases'])+' native case(s) finished; strict MO byte-invariance gate failed. Densities close and orbital energies are unchanged in the completed orientation diagnostic. Other cases may still be running.'
 chapter=N/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 content='''# 2026-09-12 — Step 5 quarantine investigation and GDB9 deferral

## Contents

- [Input comparison and basis-count evidence](../../../../coach-based_dh/coach_mp2/results/step5_quarantine_investigation.json)
- [GDB9 deferral policy](../../../../coach-based_dh/coach_mp2/configs/step5_gdb9_deferral_v1.json)
- [He3 diagnostic inputs and source hashes](../../../../coach-based_dh/coach_mp2/manifests/step5_he3_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step5, He3, ISOL24, GDB9, deferred-assessment

User has no replacement COACH orbitals for the four cases and asked whether the
existing files can work. Compared all four GSCDB and XYG-OS5 inputs/outputs.
Geometries agree. He3 basis blocks/PURECART agree; all three XYG-OS5 outputs
show the same excess-length warning and normal termination. COACH source has
315 AOs and 314 MOs; packed occupied-density closure passes. Extra 5,056 bytes
are preserved, not truncated. Native diagnostic uses COACH omega 0.27, READ,
GEN_SCFMAN FALSE, MAX_SCF_CYCLES 0, MP2_RESTART_NO_SCF TRUE and NO_ORTHO TRUE
on isolated copies, job 25826223 (mhg, four CPUs, 8 GB).

Native status: '''+state+'''

The current scfman.C calls orimo after SCF even on the no-update path;
libsym/oriorb.F reorients degenerate orbitals and writes coefficients back.
He3_47 retains all orbital-energy bytes and trailing bytes but changes 34
columns per spin. After sign alignment maximum coefficient differences are
about 1.75e-9; density closure passes. Do not weaken the frozen-MO gate. A
project-local bypass or validated extraction before postprocessing is a future
implementation task. Original archives remain unchanged. See the code-root
results/step5_he3_orientation.json and step5_he3_native_validation.json.

ISOL24_i8e: both inputs select def2-QZVPPD and XYG-OS5 prints 2,085 orbital AOs.
COACH source instead has 1,884. Independent element/basis counts reproduce
2,085 for def2-QZVPPD and 1,884 for non-diffuse def2-QZVPP/QZVP. This suggests
a non-diffuse generating basis, but counts alone do not establish identity.
Memory/SCF-guess differences do not fix it. Do not silently switch basis or pad
orbitals: the missing virtual space matters to MP2. Remains quarantined under
current mirrored protocol. No replacement SCF is authorized by this investigation.

User explicitly deferred the unavailable 3,371 GDB9-W1-F12 COACH orbitals.
These species are final-assessment-only: excluded from coefficient fitting,
model selection and diagnostics. Needed for Step 17 after Step 16 model freeze.
Future TODO: obtain or generate orbitals, then complete deferred Step 5 import,
relevant molecular feature gates/production and Step 13 assembly before scoring.
No generation now. Preserve frozen assessment membership and step IDs. This
future scope does not block current development; full final-domain readiness
remains false. Available-source import continues separately. Solver choice is
still deferred and was not required for this work.
'''
 pp=N/'COACH-based_mp2.md';plan=pp.read_text();plan=plan.replace('## Contents\n','## Contents\n\n- [Quarantine investigation and GDB9 deferral](./2026-09-12.chapters/'+NAME+')\n',1)
 lines=plan.splitlines()
 for i,l in enumerate(lines):
  if l.startswith('| 5 |'):lines[i]='| 5 | COACH-UKS archive inventory and import | In progress — available-source copy and compatibility gates | GDB9 3,371 species explicitly deferred to before Step 17; not a development blocker. ISOL24_i8e remains incompatible; He3 native diagnostic tracked in chapter 14. |'
  if l.startswith('| 17 |'):lines[i]=l.rstrip('|')+' Deferred TODO: obtain/generate 3,371 GDB9 COACH orbitals and validate features/assembly before final scoring. |'
 plan='\n'.join(lines)+'\n';plan+='\n## GDB9 scheduling clarification — 2026-09-12\n\nThe 3,371 GDB9-W1-F12 species are final-assessment-only (Step 17, after Step 16 model freeze). User deferred their unavailable COACH orbitals to a future acquisition/generation TODO. Complete their deferred import, feature and assembly gates before scoring; preserve membership and do not block current development. No new SCF is authorized now. See [decision record](./2026-09-12.chapters/'+NAME+').\n'
 idx=N/'2026-09-12.md';index=idx.read_text().replace('\nTags:','\n- [Quarantine investigation and GDB9 deferral](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for path,text in {chapter:content,pp:plan,idx:index}.items():
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(text)
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
