from pathlib import Path
import json,argparse
R=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2');N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args();audit=json.loads((R/'results/step5_import_audit.json').read_text());assert audit['passed']
 directory=N/'2026-09-12.chapters';seq=max(int(p.name[:2]) for p in directory.glob('[0-9][0-9]-*.md'))+1;name=f'{seq:02d}-step5-import-complete-native-final-case-running.md';chapter=directory/name
 text='''# 2026-09-12 — Step 5 import complete; final native case running

## Contents

- [Import audit](../../../../coach-based_dh/coach_mp2/results/step5_import_audit.json)
- [Refreshed inventory](../../../../coach-based_dh/coach_mp2/results/step5_inventory_v2.json)
- [Local executable build provenance](../../../../coach-based_dh/coach_mp2/manifests/step5_no_orientation_build_v1.json)
- [Native validation protocol](../../../../coach-based_dh/coach_mp2/configs/step5_native_v2_protocol.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step5, import-complete, native-gate-pending

All 14,081 supplied species are imported: 178,586 top-level files,
805,644,039,802 bytes. Staging is empty. Each file had source-stream SHA256 and
destination-readback verification before atomic publication. Independent final
receipt/coverage/permission/dimension audit passes. A pre-completion audit
correctly stopped on an unfinished copy; that failure log is retained separately.
Full refreshed 17,452-species inventory passes for 14,078 ordinary cases plus
three known He3 trailing-byte cases. GDB9 3,371 species remain deferred.

Isolated Q-Chem build job 25827268 passed. The project-local source patch skips
post-SCF orimo when NoSCF only; shared source/build were unchanged. Binary,
commands and 276 shared dependency hashes recorded. Six input/copy tests pass;
earlier frozen Step 3/4 artifacts unchanged.

Native job 25827314: water, carbon and He3_47/48/49 pass exact MO-file bytes,
density closure, native overlap compatibility and unchanged parent energy.
This fixes the He3 invariant failure without relaxing tolerances or truncating
trailing bytes. ISOL24_i8e is still running at this update, with approved
1,884-AO def2-QZVPP, retained 4,819-function auxiliary and omega 0.27. No new SCF.
Audit job 25827432 is queued after successful native completion. Step 5 remains
in progress until all six cases pass. Prepared completion publisher refuses to
finalize without the native and import gates. Solver choice is not required.
'''
 section='''## COACH MP2 — Step 5 import complete; native gate pending, 2026-09-12

All 14,081 available species / 178,586 files / 805.6 GB are imported and audited.
Isolated no-SCF orientation-fix build 25827268 passed; water/carbon/three He3
native regressions pass. ISOL24 evaluation 25827314 is running; audit 25827432
follows it. Step 5 remains in progress until the six-case gate passes. GDB9 stays
deferred before Step 17. [Evidence](./2026-09-12.chapters/'''+name+''').

'''
 status=N/'STATUS.md';s=status.read_text();k=s.index('\n')+1;s=s[:k]+'\n'+section+s[k:]
 plan=N/'COACH-based_mp2.md';q=plan.read_text().replace('## Contents\n','## Contents\n\n- [Step 5 imports complete; native gate pending](./2026-09-12.chapters/'+name+')\n',1);lines=q.splitlines()
 for i,l in enumerate(lines):
  if l.startswith('| 5 |'):lines[i]='| 5 | COACH-UKS archive inventory and import | All 14,081 supplied imports audited; native gate in progress | Water/carbon/three He3 PASS with isolated orientation fix; ISOL24 running, final audit queued. GDB9 deferred before Step 17. |'
 q='\n'.join(lines)+'\n';idx=N/'2026-09-12.md';index=idx.read_text().replace('\nTags:','\n- [Step 5 import complete; native final case running](./2026-09-12.chapters/'+name+')\n\nTags:',1)
 for path,content in {chapter:text,status:s,plan:q,idx:index}.items():
  if a.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(content)
  print(('PUBLISHED ' if a.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
