from pathlib import Path
import argparse
N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh');NAME='17-isol24-i8e-approved-def2-qzvpp-exception.md'
SECTION='''## COACH MP2 — ISOL24_i8e basis exception approved, 2026-09-12

User explicitly approved **orbital BASIS def2-QZVPP** for `ISOL24_i8e`, replacing
def2-QZVPPD to accommodate the existing COACH archive. The new basis has **1,884
AOs**, matching its legacy 819.0 dimensions; the amended structural audit passes.
This is an intentional single-species departure from revwb97m2, wb97m_os_rimp2
and XYG-OS5 (2,085-AO def2-QZVPPD). Record the exception in reproducibility and
benchmark reporting. It supersedes the earlier ISOL24_i8e basis-mismatch blocker.

**AO-count agreement does not prove the generating basis.** Full basis identity
and native fixed-orbital/MP2 compatibility remain pending; no production-ready
claim or new SCF is authorized. Existing **RIMP2-def2-QZVPPD auxiliary basis is
retained**; geometry, charge/spin, frozen-core controls and omega=0.27 are unchanged.

The [versioned amendment](../../../coach-based_dh/coach_mp2/configs/input_basis_amendments_v1.json)
and [active input](../../../coach-based_dh/coach_mp2/inputs/basis_exceptions_v1/ISOL24_i8e.in)
are authoritative for this species. Earlier frozen Step 4 records remain historical.
Future metadata reads use `coach_mp2/scripts/active_input_authority.py`; input
extraction must apply the amendment's `input_overrides`. [Structural check](../../../coach-based_dh/coach_mp2/results/step5_isol24_basis_exception_validation.json).

'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args();chapter=N/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 text='''# 2026-09-12 — Approved ISOL24_i8e def2-QZVPP exception

## Contents

- [Project status](../STATUS.md)
- [Amendment and input hashes](../../../../coach-based_dh/coach_mp2/configs/input_basis_amendments_v1.json)
- [Active input](../../../../coach-based_dh/coach_mp2/inputs/basis_exceptions_v1/ISOL24_i8e.in)
- [Structural validation](../../../../coach-based_dh/coach_mp2/results/step5_isol24_basis_exception_validation.json)

Tags: COACH-based_mp2, ISOL24_i8e, basis-exception, user-approved, step5

User explicitly selects def2-QZVPP for ISOL24_i8e. Changed only orbital BASIS in
a versioned copy of the Step 4 COACH template; retained RIMP2-def2-QZVPPD auxiliary
basis and all other settings. Resolved 584 shells/1,884 spherical AOs, matching
legacy 1,884 AOs/MOs. Geometry and archive file-size checks pass. No new SCF.

The prior 2,085-AO mismatch is superseded by this approved scientific exception;
full generating-basis identity/native compatibility remain pending. Matching AO
counts alone are not proof. Document the departure from the reference projects.
Original inputs and frozen Step 4 evidence are unchanged. Active metadata loader
applies the amendment, and future input extraction must use its input_overrides.
Updated STATUS.md, live plan, progress and README. Historical full Step 5 inventory
still records the previous mismatch; the new single-species audit supersedes it
for basis selection, without falsely declaring a completed full-domain rerun.
'''
 status=N/'STATUS.md';s=status.read_text();pos=s.index('\n')+1;s=s[:pos]+'\n'+SECTION+s[pos:]
 plan=N/'COACH-based_mp2.md';q=plan.read_text().replace('## Contents\n','## Contents\n\n- [Approved ISOL24_i8e basis exception](./2026-09-12.chapters/'+NAME+')\n',1)
 lines=q.splitlines()
 for i,l in enumerate(lines):
  if l.startswith('| 5 |'):lines[i]='| 5 | COACH-UKS archive inventory and import | In progress — available-source copy and compatibility gates | ISOL24_i8e user-approved def2-QZVPP exception passes dimensions; full basis/native validation pending. He3 strict MO gate pending; GDB9 deferred before Step 17. |'
 q='\n'.join(lines)+'\n\n'+SECTION
 idx=N/'2026-09-12.md';index=idx.read_text().replace('\nTags:','\n- [Approved ISOL24_i8e def2-QZVPP exception](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for path,content in {status:s,chapter:text,plan:q,idx:index}.items():
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(content)
   assert path.read_text()==content
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
