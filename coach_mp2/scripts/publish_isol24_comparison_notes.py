from pathlib import Path
import argparse
N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh');NAME='16-isol24-i8e-reference-project-handling.md'
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args();chapter=N/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 text='''# 2026-09-12 — ISOL24_i8e handling in reference projects

## Contents

- [Full comparison and implications](../../../../coach-based_dh/coach_mp2/results/step5_isol24_reference_comparison.md)
- [Source hashes and output evidence](../../../../coach-based_dh/coach_mp2/results/step5_isol24_reference_comparison.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step5, ISOL24_i8e, basis-authority, provenance, reference-comparison

User asked how revwb97m2, wb97m_os_rimp2 and xyg_os5 handle ISOL24_i8e.
All require def2-QZVPPD (2,085 AOs) and RIMP2-def2-QZVPPD (4,819 auxiliary
functions). Successful wb97m_os_rimp2 output explicitly runs wB97M-V parent
SCF (omega 0.3, SR HF 0.15) for 15 cycles, then RI-MP2. XYG-OS5 runs B3LYP
parent SCF for three cycles. Both terminate normally. SCF_GUESS READ is only
initialization here: MAX_SCF_CYCLES 200 permits orbital optimization.
Their current legacy scratch dimensions are 2,085 AOs and 2,053 retained MOs.

Current revwb97m2 authority is
`/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/manifests/qchem_orbitals/qchem_orbital_authority_v1.yaml`.
It selects `/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2`, including the
correct-basis ISOL24_i8e source. This is source-policy evidence, not proof of a
completed revwb97m2 species feature calculation. Historical original-archive
and PySCF-parent policies should not be substituted for the current authority.

Both original shared archives, `/global/scratch/users/jsliang/COACH3/ISOL24_i8e`
and `/global/scratch/users/jsliang/wB97M-V/ISOL24_i8e`, instead have 1,884 AOs/MOs.
The successful benchmark outputs do not establish how their correct-basis read
guesses were obtained or whether an earlier job repaired/projected/regenerated
the original archive. Do not claim proven automatic repair of the 1,884-AO file.
A commented XYG-OS5 copy command points at xygj_os but is not an execution record.

COACH remains quarantined under its zero-update/2,085-AO contract. Obtaining
or generating correct-basis COACH orbitals would match the reference basis;
using wB97M-V/B3LYP orbitals, changing basis or zero-padding is not an equivalent
substitution. No new SCF or basis exception authorized by this investigation.
Reference inputs, outputs and source directories only read; evidence/scripts
written under coach_mp2, with this project-note exception. Step numbering and
status unchanged; added the finding to the live plan without relaxing Step 5.
'''
 pp=N/'COACH-based_mp2.md';s=pp.read_text().replace('## Contents\n','## Contents\n\n- [ISOL24_i8e reference-project handling](./2026-09-12.chapters/'+NAME+')\n',1)
 s+='\n## ISOL24_i8e reference comparison — 2026-09-12\n\nCurrent revwb97m2 selects the 2,085-AO wb97m_os_rimp2 scratch source. The successful wb97m_os_rimp2 and XYG-OS5 jobs performed 15/3 parent SCF cycles in def2-QZVPPD. Both original shared wB97M-V and COACH archives have only 1,884 AOs. Earlier repair history is unproven; the current COACH basis gate remains unchanged. See [comparison](./2026-09-12.chapters/'+NAME+').\n'
 idx=N/'2026-09-12.md';index=idx.read_text().replace('\nTags:','\n- [ISOL24_i8e reference-project handling](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for path,content in {chapter:text,pp:s,idx:index}.items():
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(content)
   assert path.read_text()==content
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
