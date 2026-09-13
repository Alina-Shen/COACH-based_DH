from pathlib import Path
import json,datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
def main():
 assert json.loads((R/'results/step6_completion_v1.json').read_text())['completion_authorized']
 date=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat();directory=N/(date+'.chapters');directory.mkdir(exist_ok=True);seq=max([int(p.name[:2]) for p in directory.glob('[0-9][0-9]-*.md')]+[0])+1
 names=[f'{seq:02d}-autoaux-reference-projects-and-orbital-copies-verbatim.md',f'{seq+1:02d}-coach-mp2-future-todos.md',f'{seq+2:02d}-step6-complete-carbon-accuracy-deferred.md']
 original=(R/'runtime/step6_previous_answer_verbatim.md').read_text()
 exact=f'# {date} — AutoAux, reference projects and orbital copies (verbatim)\n\n## Contents\n\n- [Project note index](../{date}.md)\n\nTags: COACH-based_mp2, verbatim, AutoAux, provenance\n\n'+original
 todos='''| ID | Future TODO | Timing / boundary |
| --- | --- | --- |
| F01 | Revisit carbon RI approximation error with approved AUG-CC-PCV5Z / rimp2-def2-QZVPPD: -0.092803 kcal/mol versus 0.015 target. Compare OS/SS and downstream property effects; audit similar AE18 basis combinations before extending any remedy. AutoAux +0.003729 is diagnostic only. | User explicitly defers this issue and retains approved basis; nonblocking for Step6/8. Review before final model/reporting; no automatic auxiliary substitution or blanket waiver. |
| F02 | Obtain or generate COACH orbitals for 3,371 GDB9-W1-F12 species, then validate import, features and assembly. | Required before Step17 final scoring, after model freeze; no new SCF generation authorized now. |
| F03 | Optional discrete outer omega scan after functional-design choices are fixed. | Disabled initially; omega remains 0.27. Reevaluate omega-dependent features and validate caches for each later approved trial. |
| F04 | Optional LMP2 acceleration and accuracy assessment. | Step7 stays deferred; canonical RI-MP2 does not depend on it. |
| F05 | Choose Gurobi or an open-source MIO backend and validate the schema/solver/readback interface. | Pause before backend-dependent work, expected Step14 or earlier if needed. Does not block Steps6/8. |
| F06 | Recover missing historical COACH generating-build/input provenance if it becomes available. | Preserve unknown provenance as unknown; numerical compatibility is not historical proof. Source directories remain read-only. |
| F07 | Review paired comparison diagnostics, scalar-bound saturation and residual grid violations; consider reduced scans/changed multistart budgets only as separately declared future experiments. | Preserve the frozen initial fitting/design protocol; review at model selection and before final claims. |
'''
 todochapter=f'# {date} — COACH MP2 future TODOs\n\n## Contents\n\n- [Maintained future-TODO chapter in the live plan](../COACH-based_mp2.md)\n- [Step 6 completion evidence](../../../../coach-based_dh/coach_mp2/results/step6_complete.md)\n\nTags: COACH-based_mp2, future-todos, carbon-RI, GDB9, omega, solver\n\n'+todos+'\nThis dated chapter records the current list; maintain the live plan chapter as work progresses. Stable step IDs are unchanged.\n'
 closed=f'''# {date} — Step 6 complete with carbon accuracy deferred

## Contents

- [Complete work list and explanations](../../../../coach-based_dh/coach_mp2/results/step6_complete.md)
- [Explicit carbon accuracy deferral](../../../../coach-based_dh/coach_mp2/configs/step6_carbon_accuracy_deferral_v1.json)
- [Runtime contract](../../../../coach-based_dh/coach_mp2/configs/step6_runtime_authority_v1.json)
- [Pilot features](../../../../coach-based_dh/coach_mp2/results/step6_pilot_features.csv)
- [Future TODOs](./{names[1]})

Tags: COACH-based_mp2, step6, complete-with-deferral, approved-basis

User explicitly chose to retain carbon's approved auxiliary basis and defer its
accuracy problem. Step6 is complete with this recorded exception; the original
0.015 kcal/mol criterion and failed carbon result are unchanged. AutoAux is
not adopted. The decision is confined to the measured carbon discrepancy.

Eight primary calculations pass orbital/density/native denominator checks.
Water RI accuracy passes; carbon remains -0.092803 kcal/mol. Reused checked
outputs, published approved-basis OS/SS/doubles pilot rows and the runtime
contract, and verified earlier frozen artifacts unchanged. Five exception-guard
tests pass, alongside the prior seven Step6 tests. No new jobs, SCF, solver use
or source-folder modifications. Stable Step7 stays optional/deferred; next
required step is 8. The previous answer is separately preserved verbatim.
'''
 for name,text in zip(names,[exact,todochapter,closed]):
  p=directory/name
  with p.open('x') as f:f.write(text)
  assert p.read_text()==text
 assert (directory/names[0]).read_text().endswith(original)
 index=N/(date+'.md')
 if not index.exists():index.write_text(f'# {date} — COACH project notes\n\n## Contents\n')
 s=index.read_text();links='\n'.join('- ['+label+'](./'+date+'.chapters/'+name+')' for label,name in zip(['Previous AutoAux answer — verbatim','COACH MP2 future TODOs','Step6 complete with carbon accuracy deferred'],names));s=s.replace('## Contents\n','## Contents\n\n'+links+'\n',1);index.write_text(s)
 p=N/'COACH-based_mp2.md';s=p.read_text();s=s.replace('## Contents\n','## Contents\n\n- [Future TODOs — consolidated chapter](./'+date+'.chapters/'+names[1]+')\n- [Step6 complete with carbon accuracy deferral](./'+date+'.chapters/'+names[2]+')\n',1)
 s='\n'.join('| 6 | MP2 and RI-MP2 feature gate | Complete with user-deferred carbon accuracy issue | Approved auxiliary retained. Orbital/density/denominator/core/spin checks pass; water RI passes. Carbon -0.092803 kcal/mol remains a recorded failure vs 0.015, deferred as F01. Next required Step8; solver-independent. |' if l.startswith('| 6 |') else l for l in s.splitlines())+'\n'
 s=s.replace('Next stable step: 6, MP2 and RI-MP2 feature gate.','Step6 complete with user-approved carbon accuracy deferral; Step7 optional/deferred. Next required step: 8, named semilocal/HF/dispersion/PT2 features.')
 s+='\n## Future TODOs — consolidated\n\n'+todos+'\nUser decision supersedes earlier pending AutoAux-proposal sections: retain the approved carbon auxiliary basis. Earlier dated findings remain historical evidence.\n';p.write_text(s)
 p=N/'STATUS.md';s=p.read_text();pos=s.index('\n')+1;s=s[:pos]+f'\n## COACH MP2 — Step6 complete with carbon accuracy deferral, {date}\n\nUser retains AUG-CC-PCV5Z / rimp2-def2-QZVPPD for carbon; AutoAux is not adopted. Its measured RI error remains a failed numerical check, explicitly deferred as F01. Other gateway checks pass. Step7 stays optional/deferred; next required Step8. [Completion report](../../../coach-based_dh/coach_mp2/results/step6_complete.md). [Future TODOs](./{date}.chapters/{names[1]}).\n\n'+s[pos:];p.write_text(s)
 p=R/'README.md';p.write_text(p.read_text()+'\n## Step6 complete with explicit carbon accuracy deferral\n\nApproved auxiliary basis retained by user; AutoAux not adopted. Use [runtime contract](configs/step6_runtime_authority_v1.json) and [completion report](results/step6_complete.md). Raw carbon numerical failure remains recorded. Next required Step8; Step7 optional.\n')
 p=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/README.md');p.write_text(p.read_text()+'\n## Step6 completion decision\n\nExisting `step6_v1/` outputs are reused without new jobs. User retains the approved carbon auxiliary and defers its RI error; AutoAux remains diagnostic. Step6 complete with this explicit limitation, next required Step8. See [completion report](../../coach-based_dh/coach_mp2/results/step6_complete.md).\n')
 print('\n'.join(str(directory/name) for name in names))
if __name__=='__main__':main()
