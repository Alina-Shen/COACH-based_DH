from pathlib import Path
import argparse
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='09-coach-paper-workbook-reference.md'
CHAPTER='''# 2026-09-12 — COACH paper workbook reference resolved

## Contents

- [Workbook comparison](../../../../coach-based_dh/coach_mp2/results/step2_workbook_reference_v1.json)
- [Reproducible reader and check](../../../../coach-based_dh/coach_mp2/scripts/check_step2_workbook_reference.py)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step2, reference-data, workbook, repeatability

User identified /clusterfs/mhg-data/yaoshen/coach-based_dh/coach/paper/COACH_raw_data.xlsx
as the COACH reference. Read-only XLSX audit records SHA-256 and all sheet names.
raw_data contains reaction/property values, with distinct COACH and COACH(no 3B)
columns. No standalone absolute molecular-energy table is present.

raw_data!D298 (COACH, AE18_6) is -23748.38489725949 kcal/mol. Authoritative
GSCDB/Info/DatasetEval.csv maps AE18_6 to 1*16_C_AE18. Conversion by the frozen
627.50947406 kcal/mol per hartree gives -37.8454603141 Eh and matches pilot
job 25820274 at reported precision (7.1e-15 Eh floating-point difference).
The conversion is also consistent with the workbook Reference column and GSCDB
Analysis code. This closes the previously pending COACH reference-location issue
and validates carbon directly against paper data.

Water occurs in multicomponent SIE4x4_13–16 reactions, so its absolute pilot energy
cannot be compared directly with those values. Existing water fixture comparison
still passes; no claim of a water-to-workbook pass. No new jobs submitted.

Step 1 remains complete. Step 2 remains in progress only for a dedicated
zero-update parent-energy evaluation: the tested zero-cycle mode skips energy.
Historical generating build remains an acknowledged limitation, not a demand for
unavailable outputs. Updated mutable progress/protocol/report and live plan table.
All writes stay in coach_mp2 or project notes; workbook remains read-only.
'''
def main():
 a=argparse.ArgumentParser();a.add_argument('--publish',action='store_true');args=a.parse_args()
 ch=NOTES/'2026-09-12.chapters'/NAME;assert not ch.exists()
 p=NOTES/'COACH-based_mp2.md';s=p.read_text();lines=s.splitlines()
 matches=[i for i,l in enumerate(lines) if l.startswith('| 2 |')];assert len(matches)==1
 lines[matches[0]]='| 2 | COACH baseline and provenance | In progress — native repeatability and paper-reference PASS | Water/carbon fixture comparisons pass; carbon also matches COACH_raw_data.xlsx raw_data!D298. Reference location resolved. Dedicated zero-update energy reconstruction remains open. |'
 s='\n'.join(lines)+'\n';s=s.replace('## Contents\n','## Contents\n\n- [COACH paper workbook reference](./2026-09-12.chapters/'+NAME+')\n',1)
 s=s.replace('## Step 2 latest native results — 2026-09-12','''## Step 2 latest reference check — 2026-09-12

User supplied `coach/paper/COACH_raw_data.xlsx`. Carbon matches raw_data!D298
(COACH, AE18_6) after the established unit conversion, at reported precision.
Reference location is resolved. Water has no standalone absolute-energy entry
in this reaction/property workbook. Its fixture comparison still passes.
[Workbook audit](../../../coach-based_dh/coach_mp2/results/step2_workbook_reference_v1.json).
Step 2 remains open for dedicated zero-update energy reconstruction.

## Step 2 earlier native results — 2026-09-12''',1)
 idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:', '\n- [COACH paper workbook reference resolved](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for path,text in {p:s,idx:index,ch:CHAPTER}.items():
  assert path.resolve()==path
  if args.publish:
   with path.open('x' if path==ch else 'w') as f:f.write(text)
   assert path.read_text()==text
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
