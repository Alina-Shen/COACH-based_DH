from pathlib import Path
import argparse
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='13-step5-archive-inventory-and-import-progress.md'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true');args=parser.parse_args()
 chapter=NOTES/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 text='''# 2026-09-12 — Step 5 archive inventory and import progress

## Contents

- [Full work list and remaining gates](../../../../coach-based_dh/coach_mp2/results/step5_progress.md)
- [Inventory summary](../../../../coach-based_dh/coach_mp2/results/step5_inventory_v1.json)
- [Numerical samples](../../../../coach-based_dh/coach_mp2/results/step5_sample_numerics.json)
- [Restart policy](../../../../coach-based_dh/coach_mp2/configs/step5_restart_policy_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step5, in-progress, orbitals, provenance, quarantine, solver-neutral

Step 5 is not complete. The full source-directory/structural inventory covers
17,452 species: 14,077 structural passes, four quarantined, 3,371 missing GDB9
final-assessment archives. All 2,799 fitting and 249 diagnostic species pass
structurally; four model-selection species are quarantined. No dataset is dropped.

Source ISOL24_i8e has 1,884 AOs versus 2,085 in frozen authority. User asked for
a compatible replacement and the missing GDB9-W1-F12 source root. He3_47/48/49
have 315 AOs/314 MOs but 5,056 extra bytes in 53.0. Packed occupied-density
closure passes; square beta interpretation fails. Current Q-Chem warns on length
and reads packed offsets; native no-update validation of these cases is pending.
Do not truncate or rewrite source files. No replacement SCF is authorized.

Five numerical samples (carbon, water, Yb, helium, L14_2a) pass finite-value and
occupied-density closure checks, including BigNC reduced orbital rank. Six tests
pass for geometry/dimensions and safe copy/resume/corruption handling. Full basis
identity and AO ordering remain unproven for legacy-only records.

Started a verified import of 14,077 eligible records (about 805 GB) into
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/step5_import_v1`.
The copy remains running at this update. Each species publishes atomically with
source-stream/destination-readback hashes and read-only files; nested fragment
jobs are excluded and listed. Resume checks both source/copy hashes. Imported
records remain structural-only, not production-ready. Monitor from workspace:
`python3 -B coach_mp2/scripts/step5_status.py`; log is
`/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2/results/step5_import_v1.log`.
No final campaign success is claimed. A final hardened inventory rerun is pending.

Inspected revwb97m2 copy policy and XYG-OS5 working input. Retain COACH's Step 2
READ/zero-cycle/old-driver/NO_ORTHO/MP2_RESTART_NO_SCF controls; do not transfer
XYG-OS5's method or 200-cycle allowance. Omega remains 0.27. No quantum jobs or
solver use. Pause before a backend choice is needed. Earlier frozen files and
step numbering remain unchanged; live plan and both READMEs updated.
'''
 pp=NOTES/'COACH-based_mp2.md';plan=pp.read_text();lines=plan.splitlines();indices=[i for i,l in enumerate(lines) if l.startswith('| 5 |')];assert len(indices)==1
 lines[indices[0]]='| 5 | COACH-UKS archive inventory and import | In progress — inventory complete; copy running; unresolved source gates | 14,077 structural passes, four quarantined, 3,371 GDB9 missing. Verified import underway; full basis compatibility remains pending. Solver-neutral. |'
 plan='\n'.join(lines)+'\n';plan=plan.replace('## Contents\n','## Contents\n\n- [Step 5 archive inventory/import progress](./2026-09-12.chapters/'+NAME+')\n',1)
 addition='''## Step 5 in progress — 2026-09-12

[Full work list and remaining gates](../../../coach-based_dh/coach_mp2/results/step5_progress.md).
Inventoried 17,452 species: 14,077 structural passes, four quarantined and 3,371
missing GDB9 archives. Available-source verified copy is running in the project
heavy-data root. ISOL24_i8e needs a compatible 2,085-AO archive; three He3
file-length cases need native read validation. Five numerical samples and six
tests pass. Full basis compatibility, final copy audit and hardened inventory
rerun remain pending. No solver selection or production-readiness claim.

'''
 plan=plan.replace('## Objective and decision precedence',addition+'## Objective and decision precedence',1)
 idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:','\n- [Step 5 archive inventory and import progress](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 rp=Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2/README.md');readme=rp.read_text()+'''\n## Step 5 import in progress\n\n`step5_import_v1/species/` holds atomically published, read-only source copies with per-species hashes. `step5_import_v1/staging/` is incomplete work and must never be consumed. Records are structural-only, pending numerical/full basis validation; four cases are quarantined and 3,371 GDB9 species are missing. See [work list](../../coach-based_dh/coach_mp2/results/step5_progress.md). Preserve these immutable imports and use separate runtime scratch copies.\n'''
 for path,content in {chapter:text,pp:plan,idx:index,rp:readme}.items():
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(content)
   assert path.read_text()==content
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
