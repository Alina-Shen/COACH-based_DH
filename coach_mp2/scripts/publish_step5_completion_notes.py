from pathlib import Path
import json,argparse
R=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2');N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args();freeze=json.loads((R/'manifests/step5_freeze_v1.json').read_text());assert freeze['status']=='complete_available_scope'
 directory=N/'2026-09-12.chapters';seq=max(int(f.name[:2]) for f in directory.glob('[0-9][0-9]-*.md'))+1;name=f'{seq:02d}-step5-available-source-import-and-native-gate-complete.md';chapter=directory/name
 text='''# 2026-09-12 — Step 5 available-source import and native gate complete

## Contents

- [Complete work list and explanations](../../../../coach-based_dh/coach_mp2/results/step5_complete.md)
- [Import audit](../../../../coach-based_dh/coach_mp2/results/step5_import_audit.json)
- [Six-case native audit](../../../../coach-based_dh/coach_mp2/results/step5_native_v4_validation.json)
- [Runtime contract](../../../../coach-based_dh/coach_mp2/configs/step5_runtime_authority_v1.json)
- [Artifact freeze](../../../../coach-based_dh/coach_mp2/manifests/step5_freeze_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step5, available-scope-complete, immutable-imports, native-gate

Step 5 complete for 14,081 supplied species (14,006 core/auxiliary plus 75 BigNC).
GDB9 3,371 species remain explicitly deferred before Step 17; full final-domain
readiness is not claimed. Next stable step is 6, MP2/RI-MP2 feature validation.

Finished verified immutable source import and four supplemental records, then
independently audited coverage, receipt hashes, permissions and legacy dimensions.
Each source file was stream-hashed and destination-readback verified before
publication. Full refreshed inventory passes, including the approved ISOL24
1,884-AO def2-QZVPP exception and three preserved He3 trailing-byte cases.
An early receipt audit stopped correctly on a still-unpublished archive; only
the post-completion audit is used for the final gate. Previous evidence preserved.

Built isolated Q-Chem no-SCF post-orientation bypass; build job 25827268 passed.
Original shared source/build and source archives unchanged. Build manifest pins
276 shared dependencies, patched source, commands and binary. The patch skips
orimo only when NoSCF; normal SCF orientation logic is retained. Use the project
runtime authority rather than the shared executable for strict frozen-MO work.

Audit25827432 stalled on a live COACH3 header read and was cancelled with
its pending finalizer25828053. Replacement audit25828892 uses immutable project
imports and verifies agreement with both import receipts and native-staging
source hashes. No scientific criterion is relaxed; live originals are not
rehashed after execution.

Six-case native job 25827314 and audit 25828892 passed: water, carbon,
He3_47/48/49 and ISOL24_i8e. Entire MO files (including excess bytes) and source
hashes unchanged; density closure and energy closure pass; prior parent energies
agree where available. Native overlap verifies source-orbital orthonormality
within the declared 1e-6 compatibility tolerance. The He3 byte gate is fixed
without weakening its contract. ISOL24 uses the user-approved orbital basis;
RIMP2-def2-QZVPPD auxiliary retained. No new SCF optimization and no solver use.

Eight tests pass (six input/copy and two dispersion-closure tests); Step 3/4 frozen files unchanged.
The seven printed components close against native SCF-cycle energy, with
printed D4 recorded separately and VV10 inside DFT correlation. Audit v3 failed
only because it incorrectly added D4; v4 corrects bookkeeping without changing
tolerances or rerunning Q-Chem. Froze Step 5 evidence and updated
progress, both READMEs, STATUS.md and plan table. Unknown historical generating
build/basis provenance remains unknown; numerical compatibility is not proof
of that history. Full-domain feature and MP2 validation remain later gates.
'''
 section='''## COACH MP2 — Step 5 available-source scope complete, 2026-09-12

All 14,081 supplied orbital archives are imported with verified hashes and
published receipts. The six-case patched native gate passes, including exact
He3 MO bytes and ISOL24's approved def2-QZVPP basis. Build/native/audit jobs:
25827268 / 25827314 / 25828892. Use the project-local no-SCF orientation bypass
runtime; the shared executable still rewrites degenerate MOs after SCF.
Next Step 6. GDB9 3,371 remains deferred before Step 17; full-domain numerical
production and MP2 are not yet validated. [Complete work list](../../../coach-based_dh/coach_mp2/results/step5_complete.md).

'''
 status=N/'STATUS.md';s=status.read_text();pos=s.index('\n')+1;s=s[:pos]+'\n'+section+s[pos:]
 plan=N/'COACH-based_mp2.md';q=plan.read_text().replace('## Contents\n','## Contents\n\n- [Step 5 available-source scope complete](./2026-09-12.chapters/'+name+')\n',1);lines=q.splitlines()
 for i,l in enumerate(lines):
  if l.startswith('| 5 |'):lines[i]='| 5 | COACH-UKS archive inventory and import | Complete for 14,081 supplied species; GDB9 deferred | Verified imports, refreshed inventory and six-case native byte/density/energy/overlap gate PASS. Next Step 6; 3,371 GDB9 remain a pre-Step17 TODO. |'
 q='\n'.join(lines)+'\n';q=q.replace('Steps 1–4 complete. Next stable step: 5, COACH-UKS archive inventory and import.','Steps 1–4 complete; Step 5 complete for available sources, with GDB9 explicitly deferred. Next stable step: 6, MP2 and RI-MP2 feature gate.');q+='\n'+section
 idx=N/'2026-09-12.md';index=idx.read_text().replace('\nTags:','\n- [Step 5 available-source scope complete](./2026-09-12.chapters/'+name+')\n\nTags:',1)
 data=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/README.md');readme=data.read_text()+'''\n## Step 5 available-source completion\n\nAll 14,081 source imports are published in `step5_import_v1/species/`; receipt audit and per-file copy hashes are frozen in code-root evidence. GDB9 remains deferred. `build/step5_no_orientation_v1/` contains the isolated patched Q-Chem executable; `step5_native_v2/` holds six-case passing native outputs. Keep immutable imports separate from runtime scratch. See [completion report](../../coach-based_dh/coach_mp2/results/step5_complete.md). MP2/full production remains pending.\n'''
 code=R/'README.md';codereadme=code.read_text()+'''\n## Step 5 available-source scope complete\n\nAll 14,081 supplied species are imported and audited; six native regressions pass with the project-local no-SCF orientation bypass. Use [runtime authority](configs/step5_runtime_authority_v1.json) and [completion evidence](results/step5_complete.md). Next Step 6. GDB9 3,371 remains deferred before Step 17; no full-domain/MP2 production pass is claimed.\n'''
 for path,content in {chapter:text,status:s,plan:q,idx:index,data:readme,code:codereadme}.items():
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(content)
   assert path.read_text()==content
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
