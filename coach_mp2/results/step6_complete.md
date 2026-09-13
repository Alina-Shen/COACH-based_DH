# Step 6 complete with user-approved carbon accuracy deferral — 2026-09-12

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
