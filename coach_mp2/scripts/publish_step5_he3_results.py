from pathlib import Path
import json
R=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2');N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh');NAME='15-step5-he3-native-investigation-results.md'
def main():
 d=json.loads((R/'results/step5_he3_native_validation.json').read_text());assert d['completed_cases']==3
 chapter=N/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 text='''# 2026-09-12 — Three He3 native read results

## Contents

- [Native validation](../../../../coach-based_dh/coach_mp2/results/step5_he3_native_validation.json)
- [Coefficient/orientation analysis](../../../../coach-based_dh/coach_mp2/results/step5_he3_orientation.json)
- [GDB9 scheduling and input comparison](./14-step5-quarantine-investigation-and-gdb9-deferral.md)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step5, He3, native-test, frozen-orbitals

Job 25826223: all three outputs terminate normally with a single fixed-density
Fock evaluation and COACH omega 0.27. Source hashes remain unchanged; active
orbital-energy bytes and excess trailing bytes remain unchanged. Source/output
densities independently reconstruct from occupied source MOs within the established
normwise bound. Component energy closure passes. Fixed energies in Eh:
He3_47 -8.3001208857; He3_48 -8.1442233631; He3_49 -7.9113273194.

The strict MO-byte gate FAILS for all three, correctly reported by the validator.
Changed columns per spin: 34, 30 and 22, respectively. Maximum coefficient
errors after sign alignment: 1.75e-9, 2.02e-9 and 8.42e-9. Current scfman.C
calls orimo after SCF; libsym/oriorb.F reorients degenerate MOs and writes the
coefficients back. This explains why zero SCF and NO_ORTHO are not sufficient
for strict saved-coefficient invariance in these cases. Do not weaken the gate.

Existing He3 sources are readable and appear recoverable without new SCF.
Next implementation task: a project-local bypass of the post-SCF reorientation,
or validated feature extraction before it, then repeat byte/energy/density checks.
Keep quarantine until that fix passes. No source/build files outside the approved
roots were modified. ISOL24_i8e remains a separate 1,884-vs-2,085 basis mismatch.
GDB9 remains explicitly deferred to before Step 17 as recorded in chapter 14.
'''
 chapter.write_text(text)
 idx=N/'2026-09-12.md';s=idx.read_text().replace('\nTags:','\n- [Three He3 native read results](./2026-09-12.chapters/'+NAME+')\n\nTags:',1);idx.write_text(s)
 p=N/'COACH-based_mp2.md';s=p.read_text().replace('## Contents\n','## Contents\n\n- [Three He3 native read results](./2026-09-12.chapters/'+NAME+')\n',1)
 s+='\n## He3 native investigation completed — 2026-09-12\n\nAll three native fixed-parent reads finish; energy bytes and density closure pass, but strict MO-byte invariance fails due to coefficient changes consistent with post-SCF orbital reorientation. Keep quarantine pending a project-local workflow fix; new He3 SCF is not indicated. See [results](./2026-09-12.chapters/'+NAME+').\n'
 p.write_text(s)
 print('Published chapter 15 and updated plan/index')
if __name__=='__main__':main()
