"""Close Step6 only with the exact user-deferred carbon accuracy exception."""
from pathlib import Path
import json,hashlib,csv
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(v,d,decision):
 if decision['species']!='16_C_AE18' or decision['retained_auxiliary_basis']!='rimp2-def2-QZVPPD':raise ValueError('Unexpected exception scope')
 if not d['passed'] or len(d['cases'])!=8 or not all(c['passed'] for c in d['cases']):raise ValueError('Unresolved orbital/denominator gate')
 if len(v['cases'])!=6:raise ValueError('Incomplete primary evaluation')
 if {c['species'] for c in v['comparisons']}!={'SIE4x4_h2o','16_C_AE18'}:raise ValueError('Unexpected comparison scope')
 failed=[c for c in v['comparisons'] if not c['passed']]
 if len(failed)!=1 or failed[0]['species']!='16_C_AE18':raise ValueError('Exception cannot cover another failure')
 if abs(failed[0]['ri_minus_conventional_hartree']-decision['observed_error_hartree'])>1e-14:raise ValueError('Exception not valid for changed result')
 if any(c['all_electron_minus_frozen_core']>=0 for c in v['comparisons']):raise ValueError('Core control failed')
 return True

def main():
 v=json.loads((R/'results/step6_validation.json').read_text());d=json.loads((R/'results/step6_denominator_audit.json').read_text());carbon=next(c for c in v['comparisons'] if c['species']=='16_C_AE18')
 decision=dict(date='2026-09-12',authority='User: stick to approved carbon basis, record discrepancy as future TODO, complete Step6',species='16_C_AE18',retained_orbital_basis='AUG-CC-PCV5Z',retained_auxiliary_basis='rimp2-def2-QZVPPD',observed_error_hartree=carbon['ri_minus_conventional_hartree'],observed_error_kcalmol=carbon['ri_minus_conventional_kcalmol'],accuracy_tolerance_kcalmol=.015,numerical_accuracy_pass=False,disposition='user_accepted_deferral_of_this_accuracy_gate_only',autoaux_proposal='not_adopted; diagnostic evidence retained',scope='This measured carbon RI approximation discrepancy only; not blanket acceptance of other failures',validation_sha256=sha(R/'results/step6_validation.json'),denominator_sha256=sha(R/'results/step6_denominator_audit.json'),todo='F01 in COACH-based_mp2.md future TODO chapter')
 check(v,d,decision);assert v['denominator_audit_sha256']==sha(R/'results/step6_denominator_audit.json')
 for n,key in [(3,'sha256'),(4,'artifacts'),(5,'sha256')]:
  for f,h in json.loads((R/f'manifests/step{n}_freeze_v1.json').read_text())[key].items():assert sha(R/f)==h,f
 # Check all previously snapshotted native/input/result artifacts before reuse.
 snapshot=json.loads((R/'manifests/step6_evidence_snapshot_v1.json').read_text())
 for f,h in snapshot['sha256'].items():assert sha(R/f)==h,f
 for f,h in snapshot['native_outputs'].items():assert sha(Path(f))==h,f
 (R/'configs/step6_carbon_accuracy_deferral_v1.json').write_text(json.dumps(decision,indent=2)+'\n')
 contract=dict(status='gateway_complete_with_carbon_accuracy_deferral',scope='two-species feature gateway, not full production readiness',runtime_manifest='manifests/step5_no_orientation_build_v1.json',basis_authority='configs/input_basis_amendments_v1.json',carbon_deferral='configs/step6_carbon_accuracy_deferral_v1.json',controls=dict(EXCHANGE='COACH',CORRELATION='RIMP2',N_FROZEN_CORE='FC',N_FROZEN_VIRTUAL=0,SCS=3,SSS_FACTOR=1000000,SOS_FACTOR=1000000,SCF_GUESS='READ',SCF_GUESS_MIX=0,GEN_SCFMAN='FALSE',MAX_SCF_CYCLES=0,MP2_RESTART_NO_SCF='TRUE',NO_ORTHO='TRUE'),remove_METHOD=True,omega=.27,auxiliary_basis='authoritative per-species basis, no AutoAux substitution',feature='unscaled OS+SS doubles; printed singles excluded',singles='SCS3 libgmbpt printed singles multiplier .3211; record separately',denominators='native COACH Fock occupied/virtual block spectra, no regularization or attenuation',scratch='separate working copies under scf_read/coach_mp2',solver_dependency=False)
 (R/'configs/step6_runtime_authority_v1.json').write_text(json.dumps(contract,indent=2)+'\n')
 with (R/'results/step6_pilot_features.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['species','OS_hartree','SS_hartree','total_doubles_hartree','printed_singles_excluded_hartree','accuracy_status'])
  for c in v['cases']:
   if c['core']=='FC' and c['pt2']['engine']=='RIMP2':
    x=c['pt2'];w.writerow([c['species'],x['opposite_spin'],x['same_spin'],x['doubles'],x['printed_singles'],'user_deferred_error' if c['species']=='16_C_AE18' else 'pass'])
 report='''# Step 6 complete with user-approved carbon accuracy deferral — 2026-09-12

## Work performed in this completion turn

1. Logged the preceding answer verbatim in a new dated project-note chapter.
2. Recorded the user's decision to retain carbon AUG-CC-PCV5Z / rimp2-def2-QZVPPD.
   The AutoAux proposal is not adopted. No input/basis authority changed.
3. Added an explicit, result-hash-bound completion exception for the measured
   carbon RI error (-0.0928033174 kcal/mol). The 0.015 kcal/mol threshold and
   original failed numerical report remain unchanged. This is a deferred
   accuracy issue, not a numerical pass or a waiver for other systems/errors.
4. Reused the completed native calculations; checked all snapshotted input,
   result and output hashes, and verified prior Step 3/4/5 freezes unchanged.
   The eight primary runs pass orbital, density and native-denominator checks;
   the six accepted primary energy evaluations provide conventional/RI/core
   controls. Water's RI error passes (+0.0072666852 kcal/mol). No new jobs needed.
5. Published two pilot OS/SS/doubles rows from the APPROVED auxiliary basis,
   with an explicit carbon accuracy status and printed singles excluded.
   Recorded the solver-independent COACH RI-MP2 runtime/input contract.
6. Tested the exception guard against unrelated failures, altered carbon
   results, failed denominator checks and failed frozen-core controls.
7. Added a consolidated future-TODO chapter to COACH-based_mp2.md and a linked
   standalone notes chapter. Updated the stable plan table, STATUS, progress
   and READMEs; froze Step 6 completion evidence without renumbering steps.

## Scope and next work

Step 6 is complete WITH the explicit user-approved carbon accuracy deferral.
Its original raw aggregate numerical flag is still false. No new SCF,
AutoAux adoption, source archive modification, solver use or bulk production
occurred. Step 7 remains optional/deferred; next required step is 8 (named
semilocal/HF/dispersion/PT2 features). GDB9 stays deferred before Step 17.

## Evidence

- [Full earlier calculations/investigation](./step6_findings.md)
- [Unchanged raw numerical validation](./step6_validation.json)
- [Native denominator/orbital audit](./step6_denominator_audit.json)
- [Carbon accuracy deferral](../configs/step6_carbon_accuracy_deferral_v1.json)
- [Runtime/input contract](../configs/step6_runtime_authority_v1.json)
- [Approved-basis pilot features](./step6_pilot_features.csv)
- [Completion tests](./step6_completion_tests.log)
- [Completion freeze](../manifests/step6_freeze_v1.json)
'''
 (R/'results/step6_complete.md').write_text(report)
 result=dict(step=6,status='complete_with_user_deferred_accuracy_issue',scientific_checks_pass_except_recorded_carbon_RI_error=True,raw_numerical_pass=v['passed'],completion_authorized=True,deferral='configs/step6_carbon_accuracy_deferral_v1.json',solver_required=False)
 (R/'results/step6_completion_v1.json').write_text(json.dumps(result,indent=2)+'\n')
 files=['scripts/complete_step6.py','scripts/publish_step6_closed_notes.py','tests/test_step6_completion.py','results/step6_completion_tests.log','configs/step6_carbon_accuracy_deferral_v1.json','configs/step6_runtime_authority_v1.json','results/step6_pilot_features.csv','results/step6_complete.md','results/step6_completion_v1.json','manifests/step6_evidence_snapshot_v1.json','runtime/step6_previous_answer_verbatim.md']
 (R/'manifests/step6_freeze_v1.json').write_text(json.dumps(dict(step=6,status=result['status'],prior_evidence_transitively_pinned=True,sha256={f:sha(R/f) for f in files}),indent=2)+'\n')
 p=R/'manifests/progress.json';x=json.loads(p.read_text());x['steps'][5].update(status=result['status'],remaining_gate=None,deferred_issue='F01 carbon RI accuracy; approved auxiliary retained by user',proposal_disposition='AutoAux not adopted',evidence=['results/step6_complete.md','manifests/step6_freeze_v1.json']);x['next_step']=8;x['runtime_readiness_scope']='Step5 fixed-parent and Step6 two-species RI-MP2 gateway, with explicit carbon accuracy deferral; bulk validation pending';p.write_text(json.dumps(x,indent=2)+'\n');print(result)
if __name__=='__main__':main()
