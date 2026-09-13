from pathlib import Path
import json,datetime,hashlib
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
def main():
 d=json.loads((R/'configs/step6_carbon_auxiliary_exception_proposal_v1.json').read_text());assert d['status']=='proposed_not_active_requires_user_decision';date=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat();directory=N/(date+'.chapters');seq=max(int(p.name[:2]) for p in directory.glob('[0-9][0-9]-*.md'))+1;name=f'{seq:02d}-step6-tested-carbon-autoaux-exception-proposal.md'
 text=f'''# {date} — Step 6 tested carbon AutoAux exception proposal

## Contents

- [Concrete exception proposal](../../../../coach-based_dh/coach_mp2/configs/step6_carbon_auxiliary_exception_proposal_v1.json)
- [Exact proposed parent input](../../../../coach-based_dh/coach_mp2/inputs/basis_exception_candidates_v1/16_C_AE18_autoaux.in)
- [Full work list and results](../../../../coach-based_dh/coach_mp2/results/step6_findings.md)

Tags: COACH-based_mp2, step6, AutoAux, proposed-exception, decision-pending

Carbon's tested 525-function AutoAux basis passes the unchanged 0.015 kcal/mol
gate: RI minus four-center doubles = +0.00372860 kcal/mol. The approved
rimp2-def2-QZVPPD gives -0.09280332; rimp2-aug-cc-pVQZ gives -0.05895972.
The AutoAux run preserves source MO bytes, COACH energy and native Fock spectra.

Recommend reviewing a carbon-only auxiliary exception. Exact proposed input
changes AUX_BASIS_CORR to GEN and adds the tested basis block; orbital basis
AUG-CC-PCV5Z, geometry, spin and COACH parent remain unchanged. This exception
is NOT active and has NOT been applied to any other species. Similar AE18
combinations need separate testing before broadening its scope.

Step 6 remains open pending this scientific-input decision; Gurobi versus other
MIO solvers has no bearing on it. Original input/basis authority remains intact.
The proposal-writing attempt first used the old system Python and failed before
writing; rerunning with the project dh environment produced the reviewed files.
''';(directory/name).write_text(text)
 p=N/(date+'.md');p.write_text(p.read_text().replace('## Contents\n','## Contents\n\n- [Step 6 tested carbon AutoAux exception proposal](./'+date+'.chapters/'+name+')\n',1))
 for fn in ['STATUS.md','COACH-based_mp2.md']:
  p=N/fn;s=p.read_text();section='\n## Step 6 — tested carbon auxiliary exception awaits decision\n\nAutoAux passes (+0.00372860 kcal/mol); current auxiliary fails (-0.09280332), with 0.015 allowed. [Concrete carbon-only proposal](../../../coach-based_dh/coach_mp2/configs/step6_carbon_auxiliary_exception_proposal_v1.json). No authority change applied; solver choice is unrelated.\n'
  if fn=='STATUS.md':pos=s.index('\n')+1;s=s[:pos]+section+s[pos:]
  else:
   s='\n'.join('| 6 | MP2 and RI-MP2 feature gate | In progress; auxiliary exception decision pending | Water PASS; carbon current auxiliary FAIL (-0.092803 kcal/mol), tested AutoAux PASS (+0.003729; limit 0.015). Concrete carbon-only proposal ready; authority unchanged. Solver-independent. |' if l.startswith('| 6 |') else l for l in s.splitlines())+'\n';s+=section
  p.write_text(s)
 p=R/'manifests/progress.json';v=json.loads(p.read_text());v['steps'][5]['proposal']='configs/step6_carbon_auxiliary_exception_proposal_v1.json';v['steps'][5]['remaining_gate']='User decision on tested carbon-only auxiliary exception; current authority fails accuracy gate';p.write_text(json.dumps(v,indent=2)+'\n')
 p=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/README.md');p.write_text(p.read_text()+'\n## Step 6 pilot and diagnostic outputs\n\n`step6_v1/` preserves eight primary outputs, failed legacy/AutoAux-format attempts, and alternate auxiliary/AutoAux diagnostics. Step 6 remains open: the current carbon auxiliary fails accuracy, while the tested AutoAux candidate passes. No production input authority changed. See [findings](../../coach-based_dh/coach_mp2/results/step6_findings.md).\n')
 print(directory/name)
if __name__=='__main__':main()
