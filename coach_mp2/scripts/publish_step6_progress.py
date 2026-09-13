from pathlib import Path
import json,datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
def main():
 date=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat();directory=N/(date+'.chapters');directory.mkdir(exist_ok=True);seq=max([int(p.name[:2]) for p in directory.glob('[0-9][0-9]-*.md')]+[0])+1;name=f'{seq:02d}-step6-native-pt2-gate-started.md'
 text=f'''# {date} — Step 6 native PT2 gate started

## Contents

- [Step 6 protocol](../../../../coach-based_dh/coach_mp2/manifests/step6_protocol_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step6, PT2, same-orbital, solver-independent

Step 6 is in progress. Job 25829462 runs six isolated no-SCF pilots on mhg,
8 CPUs, 16 GB: water and triplet carbon with nominal conventional MP2/RI-MP2
frozen-core pairs and all-electron RI controls. EXCHANGE COACH retains the
parent operator; unit spin factors expose OS/SS separately. Inputs and copied
source files are hash-pinned. No new SCF optimization or solver is used.

Initial water output shows Q-Chem routes CORRELATION MP2 with an auxiliary
basis to RI-MP2. That nominal MP2 run cannot count as a conventional reference;
a distinct four-center reference is required before Step 6 can pass.
The predeclared RI-versus-conventional tolerance is 0.015 kcal/mol. Exact
MO-file identity, denominator definition, core counts and singles separation
remain mandatory gates. Step 5 freeze stays unchanged. GDB9 remains deferred.
'''
 (directory/name).write_text(text)
 idx=N/(date+'.md')
 if not idx.exists():idx.write_text(f'# {date} — COACH project notes\n\n## Contents\n\nTags: COACH-based_mp2\n')
 s=idx.read_text().replace('## Contents\n','## Contents\n\n- [Step 6 native PT2 gate started](./'+date+'.chapters/'+name+')\n',1);idx.write_text(s)
 p=N/'COACH-based_mp2.md';s=p.read_text();s='\n'.join('| 6 | MP2 and RI-MP2 feature gate | In progress | Six native pilots, job 25829462; conventional-engine routing and denominator/core/spin audits pending. Solver-independent. |' if l.startswith('| 6 |') else l for l in s.splitlines())+'\n';p.write_text(s)
 p=N/'STATUS.md';s=p.read_text();pos=s.index('\n')+1;s=s[:pos]+f'\n## COACH MP2 — Step 6 in progress, {date}\n\nNative PT2 job 25829462 underway; conventional-engine routing must be verified. Solver choice does not block this step. [Protocol](../../../coach-based_dh/coach_mp2/manifests/step6_protocol_v1.json).\n\n'+s[pos:];p.write_text(s)
 p=R/'manifests/progress.json';d=json.loads(p.read_text());d['steps'][5].update(status='in_progress',native_job_id='25829462',evidence=['manifests/step6_protocol_v1.json'],remaining_gate='Conventional-engine reference and denominator/core/spin checks');p.write_text(json.dumps(d,indent=2)+'\n');print(directory/name)
if __name__=='__main__':main()
