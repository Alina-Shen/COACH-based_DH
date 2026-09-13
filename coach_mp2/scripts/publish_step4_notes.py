from pathlib import Path
import argparse
ROOT=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2')
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='12-step4-molecular-input-basis-authority.md'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
 chapter=NOTES/'2026-09-12.chapters'/NAME
 assert not chapter.exists()
 text='''# 2026-09-12 — Step 4 molecular input and basis authority

## Contents

- [Full work list and explanations](../../../../coach-based_dh/coach_mp2/results/step4_complete.md)
- [Validation evidence](../../../../coach-based_dh/coach_mp2/results/step4_validation.json)
- [Versioned reconciliation policy](../../../../coach-based_dh/coach_mp2/configs/step4_input_authority_v1.json)
- [Snapshot hashes](../../../../coach-based_dh/coach_mp2/manifests/step4_snapshot_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step4, completed, input-authority, basis, provenance, solver-neutral

Step 4 complete. All 17,452 energy-role inputs match pinned revwb97m2 geometry,
charge/spin, basis/auxiliary/ECP definitions and structural dimensions. Preserve
206 OPT exclusions and all ghost centers. Omega remains fixed at 0.27.

Resolved 12 source discrepancies locally: four concatenated rem lines, explicit
Yb auxiliary basis and seven explicit helium orbital bases/PURECART controls.
Inherited BigNC rimp2-def2-TZVPPD and GDB9-W1-F12 rimp2-def2-TZVP defaults in
3,446 external templates; no auxiliary generation. Changed 14,006 core METHOD
values to COACH. Frozen Step 1 files remain intact; Step 4 has a versioned overlay.

There are 593 embedded orbital bases, one embedded auxiliary basis, 97 embedded
ECPs, 367 implicit ECPs and 16,988 no-ECP species. All four pinned auxiliary
libraries also match current runtime files byte-for-byte. Independent archive
readback passes for all species; 15 tests pass. Source trees remain unchanged.

Original/derived inputs, detailed metadata and initial audit are hash-pinned under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step4_inputs_v1` (about
130 MB). Code/settings/manifests/results are under
`/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2`. Templates require later
stage-specific no-update SCF, grid, MP2 and resource controls before execution.

Next Step 5: inventory/import COACH archives and check actual basis compatibility,
especially helium/Yb. No orbitals read or copied, no quantum jobs, no solver use.
No clarification required for Step 4. Pause before backend-dependent work if
solver choice remains unresolved, expected Step 14. Updated both code/data
READMEs, mutable progress and live plan table; frozen step numbering unchanged.
'''
 planpath=NOTES/'COACH-based_mp2.md';plan=planpath.read_text();lines=plan.splitlines()
 matches=[i for i,l in enumerate(lines) if l.startswith('| 4 |')];assert len(matches)==1
 lines[matches[0]]='| 4 | Molecular input and basis authority | Complete — 17,452 inputs validated, 15 tests PASS, artifact hashes frozen | Exact molecular/basis authority staged; 12 source discrepancies reconciled locally and external auxiliary defaults explicit. Next Step 5: archive compatibility. |'
 plan='\n'.join(lines)+'\n'
 plan=plan.replace('Steps 1–3 complete. Next stable step: 4, molecular input and basis authority.','Steps 1–4 complete. Next stable step: 5, COACH-UKS archive inventory and import.')
 plan=plan.replace('## Contents\n','## Contents\n\n- [Step 4 molecular input and basis authority](./2026-09-12.chapters/'+NAME+')\n',1)
 addition='''## Step 4 completed — 2026-09-12

[Full work list and evidence](../../../coach-based_dh/coach_mp2/results/step4_complete.md).
All 17,452 energy-role inputs match the pinned molecular/basis authority, with
15 tests passing. Staged original and derived COACH templates in the project
heavy root; repaired four malformed rem lines and inherited authoritative Yb/He
basis blocks and external auxiliary defaults through a versioned overlay.
Source files and earlier frozen artifacts remain unchanged. Input templates
await stage-specific execution settings. Actual COACH archive compatibility
remains Step 5. Solver selection is unnecessary for Step 4 and stays deferred.

'''
 assert '## Objective and decision precedence' in plan
 plan=plan.replace('## Objective and decision precedence',addition+'## Objective and decision precedence',1)
 idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:', '\n- [Step 4 molecular input and basis authority](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 datareadme=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/README.md')
 readme=datareadme.read_text().replace('Current contents: this README only. Step 1 generated no heavy numerical data.','Step 1 generated no heavy numerical data. Step 4 adds `step4_inputs_v1/`: original/derived input tar, detailed metadata and historical initial audit (about 130 MB). See [snapshot manifest](../../coach-based_dh/coach_mp2/manifests/step4_snapshot_v1.json) for hashes. These are scientific templates; production execution and orbital compatibility remain later gates.')
 for path,content in {chapter:text,planpath:plan,idx:index,datareadme:readme}.items():
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(content)
   assert path.read_text()==content
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
