"""Record a failed scientific gate without publishing completed features."""
from pathlib import Path
import json,hashlib,datetime
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];N=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 v=json.loads((R/'results/step6_validation.json').read_text());d=json.loads((R/'results/step6_diagnostics.json').read_text());assert not v['passed'];date=datetime.datetime.now(ZoneInfo('America/Los_Angeles')).date().isoformat();lines=[]
 for c in v['comparisons']:lines.append(f"| {c['species']} | approved rimp2-def2-QZVPPD | {c['ri_minus_conventional_kcalmol']:.8f} | {'PASS' if c['passed'] else 'FAIL'} |")
 for c in d['cases']:
  if c['status']=='normal':lines.append(f"| carbon diagnostic | {c['tag'].replace('16_C_AE18_RIMP2_','')} | {c['ri_minus_conventional_kcalmol']:.8f} | {'PASS' if c['within_predeclared_accuracy'] else 'FAIL'} |")
 report=f'''# Step 6 — native PT2 gate findings ({date})

Step 6 remains open: the approved carbon auxiliary basis fails the predeclared
RI-versus-conventional 0.015 kcal/mol accuracy criterion. This is independent
of MIO solver selection. No basis authority, scientific threshold or production
engine has been changed, and no completed Step 6 feature set is published.

## Work performed and explanation

1. Read the frozen Step 6/scientific contract and the latest revwb97m2 native
   scalar/recovery implementation. Retained COACH omega=0.27, canonical
   unregularized PT2, frozen core and the matching authoritative orbital bases.
2. Prepared water (closed-shell UKS) and carbon (triplet UKS) from hash-verified
   local imports. Created isolated inputs/scratch/output directories; kept
   original archives and reference projects read-only. Used the Step 5 patched
   Q-Chem executable, READ, zero SCF cycles, NO_ORTHO, zero guess mixing and
   EXCHANGE COACH with CORRELATION MP2/RIMP2. No SCF optimization was performed.
3. Ran six initial pilots, job 25829462: nominal MP2/RI frozen-core pairs plus
   all-electron RI controls. Set FC explicitly (one occupied orbital per spin
   for O/C), zero frozen virtuals, and unit OS/SS scales. Carbon's parent-only
   input omitted FC; adding it implements the already-frozen PT2 policy.
4. Detected Q-Chem's automatic conversion of MP2 to RI-MP2 when an auxiliary
   basis is present. Confirmed it in read-only rem_setup.C and excluded both
   nominal MP2 outputs as conventional references. Ran two actual four-center
   references without an auxiliary basis, job 25829605. The orbital basis,
   parent and frozen-core policy stayed unchanged.
5. Implemented strict actual-engine and spin-component parsing. Checked
   aa+bb=SS, ab=OS and OS+SS+printed singles=printed PT2 total; the candidate
   fitted feature is OS+SS only. Documented that SCS3 unit doubles factors
   still leave a .3211 printed singles multiplier in libgmbpt; conventional
   singles are unscaled. Singles are excluded, never mistaken for doubles.
6. Audited denominator semantics from native source. Q-Chem pseudocanonicalizes
   COACH Fock occupied/virtual blocks, without occupied-virtual mixing. This
   clarifies the initial protocol's incorrect assumption that saved eigenvalues
   alone define native denominators; the versioned v2 protocol records the
   correction. Checked native 58.0 Fock spectra against Step 5 COACH-only spectra
   to 2e-8 Eh, strict negative finite denominator bounds, exact complete 53.0
   byte identity, source hashes, densities and electron/virtual populations.
   All eight primary runs pass these checks (audit job 25829648); maximum native
   spectrum difference from the COACH baseline is below 8.1e-11 Eh. Saved
   eigenvalues differ from reconstructed spectra by up to 0.000165 Eh (water)
   and 0.011456 Eh (carbon), confirming why the native definition matters.
7. Water passes RI accuracy, carbon fails. All-electron RI doubles are more
   negative than FC by 0.0276556042 Eh (water) and 0.0514497492 Eh (carbon),
   confirming a nontrivial core-correlation control. These are diagnostics,
   not replacements for the frozen-core feature.
8. Investigated carbon with the legacy RI route (job 25829818), which failed
   before PT2 because COACH with USE_LIBQINTS FALSE hits get_id_dft_path error.
   Tested rimp2-aug-cc-pVQZ (job 25829827); it reduces but does not eliminate
   the discrepancy. Neither diagnostic changes the approved auxiliary basis.
9. Generated a diagnostic AutoAux basis with PySCF 2.14.0 from the exact native
   AUG-CC-PCV5Z carbon basis (181 orbital AOs): 95 auxiliary shells, 525 spherical
   functions, maximum l=6. The first input (25829897) failed before calculation
   because Q-Chem rejects integer-formatted primitive coefficients. Preserved it
   and corrected only real-number formatting (25829953). The diagnostic audit
   25829954 checks source/MO/Fock/parent identity and numerical accuracy.
10. Passed seven targeted tests, including rejection of wrong engine labels,
    nonunit scaling, broken total identities and invalid denominators; checked
    frozen-core windows and occupied/virtual separation. Kept failures and
    corrections as evidence. Verified prior Step 3/4/5 code freezes unchanged.
    Updated progress, plan table, STATUS, README and dated project notes.

## Accuracy results

Signed RI doubles minus four-center doubles, using the same COACH parent.
The unchanged acceptance threshold is 0.015 kcal/mol.

| System | Auxiliary basis / diagnostic | Difference (kcal/mol) | Result |
| --- | --- | ---: | --- |
'''+ '\n'.join(lines)+'''

## Next decision and scope

The available AutoAux result is diagnostic evidence, not an approved input
exception. Retaining strict mirroring and simultaneously passing this carbon
RI gate may require a reviewed auxiliary-basis or PT2-engine exception. Do not
relax the threshold or silently substitute a different basis. Audit similar
AUG-CC-PCV5Z/AE18 cases before broadening any exception.

Step 8 has not started; Step 7 remains optional. GDB9 3,371 species remain
user-deferred before Step 17. No full-domain PT2 validation is claimed. All
writes are within authorized COACH MP2 code, heavy-data, scratch and notes roots.

## Evidence

- [Primary validation, including failed carbon gate](./step6_validation.json)
- [Denominator/space checks](./step6_denominator_audit.json)
- [Carbon diagnostic audit](./step6_diagnostics.json)
- [Initial protocol](../manifests/step6_protocol_v1.json)
- [Routing and denominator clarification](../manifests/step6_conventional_v2.json)
- [AutoAux basis provenance](../manifests/step6_autoaux_diagnostic_v2.json)
- [Read-only source audit](../manifests/step6_source_audit_v1.json)
- [Tests](./step6_tests.log)
'''
 (R/'results/step6_findings.md').write_text(report)
 for step,key in [(3,'sha256'),(4,'artifacts'),(5,'sha256')]:
  for f,h in json.loads((R/f'manifests/step{step}_freeze_v1.json').read_text())[key].items():assert sha(R/f)==h,f
 p=R/'manifests/progress.json';x=json.loads(p.read_text());x['steps'][5].update(status='in_progress_accuracy_gate_failed',remaining_gate='Carbon approved auxiliary basis fails 0.015 kcal/mol RI/conventional criterion; review diagnostic results before any input exception',evidence=['results/step6_findings.md','results/step6_validation.json','results/step6_denominator_audit.json','results/step6_diagnostics.json'],conventional_job_id='25829605',denominator_job_id='25829648',diagnostic_jobs=['25829818','25829827','25829897','25829953','25829954']);x['next_step']=6;p.write_text(json.dumps(x,indent=2)+'\n')
 directory=N/(date+'.chapters');directory.mkdir(exist_ok=True);seq=max([int(p.name[:2]) for p in directory.glob('[0-9][0-9]-*.md')]+[0])+1;name=f'{seq:02d}-step6-carbon-ri-accuracy-gate-findings.md';text=f'''# {date} — Step 6 carbon RI accuracy gate findings

## Contents

- [Complete work list and numerical results](../../../../coach-based_dh/coach_mp2/results/step6_findings.md)
- [Primary validation](../../../../coach-based_dh/coach_mp2/results/step6_validation.json)
- [Carbon diagnostics](../../../../coach-based_dh/coach_mp2/results/step6_diagnostics.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step6, RI-MP2, accuracy-gate, auxiliary-basis, solver-independent

Step 6 remains open. Eight primary native runs pass source/MO/density/COACH
Fock-spectrum checks, and seven tests pass. Water's RI error is 0.007266 kcal/mol;
carbon's approved rimp2-def2-QZVPPD error is -0.092803 kcal/mol, exceeding the
unchanged 0.015 limit. Alternative auxiliary and AutoAux results are in the
linked report; these are diagnostics only, not approved basis exceptions.

Key implementation findings: remove AUX_BASIS_CORR for a genuine conventional
reference (otherwise Q-Chem silently routes MP2 to RI); use EXCHANGE COACH to
retain the parent Fock; native denominators come from its occupied/virtual
blocks, not blindly from saved eigenvalues. Source MO bytes remain unchanged.
Record and exclude printed singles; SCS3 has a .3211 singles scale in libgmbpt.

Primary jobs 25829462/25829605; denominator audit 25829648. Legacy-route failure
25829818; alternate auxiliary 25829827; AutoAux formatting failure 25829897 and
corrected run 25829953; diagnostic audit 25829954. All failures retained.
No solver choice, new SCF optimization or authority/tolerance change. Prior
Step 3/4/5 freezes unchanged; GDB9 remains deferred before Step 17. Review a
concrete basis/engine exception before marking Step 6 complete or advancing.
''';(directory/name).write_text(text)
 p=N/(date+'.md');s=p.read_text().replace('## Contents\n','## Contents\n\n- [Step 6 carbon RI accuracy gate findings](./'+date+'.chapters/'+name+')\n',1);p.write_text(s)
 p=N/'COACH-based_mp2.md';s=p.read_text();s='\n'.join('| 6 | MP2 and RI-MP2 feature gate | In progress; carbon accuracy gate fails | MO/density/native-denominator checks PASS; water RI PASS, carbon -0.092803 kcal/mol exceeds 0.015. Auxiliary diagnostics recorded; authority exception requires review. Solver-independent. |' if l.startswith('| 6 |') else l for l in s.splitlines())+'\n';s+='\n## Step 6 native PT2 findings — '+date+'\n\n[Work list, failed gate and diagnostic results](../../../coach-based_dh/coach_mp2/results/step6_findings.md). Step 6 remains current; no basis or threshold change.\n';p.write_text(s)
 p=N/'STATUS.md';s=p.read_text();pos=s.index('\n')+1;s=s[:pos]+f'\n## COACH MP2 — Step 6 carbon accuracy gate open, {date}\n\nWater RI/conventional comparison passes; carbon with approved auxiliary basis fails (-0.092803 kcal/mol versus 0.015 allowed). Source/MO/density/native Fock spectra pass. Auxiliary diagnostics are recorded without changing authority. Solver-independent; next step remains 6. [Work list and numerical results](../../../coach-based_dh/coach_mp2/results/step6_findings.md).\n\n'+s[pos:];p.write_text(s)
 p=R/'README.md';p.write_text(p.read_text()+'\n## Step 6 accuracy gate open\n\nSee [findings](results/step6_findings.md): water passes; carbon approved auxiliary fails the RI accuracy criterion. Diagnostic auxiliary inputs are not production authority. Source/MO/COACH Fock checks and seven tests pass. Next step remains 6; no solver decision required.\n')
 print('Published findings:',directory/name)
if __name__=='__main__':main()
