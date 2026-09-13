# Step 6 — native PT2 gate findings (2026-09-12)

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
| SIE4x4_h2o | approved rimp2-def2-QZVPPD | 0.00726669 | PASS |
| 16_C_AE18 | approved rimp2-def2-QZVPPD | -0.09280332 | FAIL |
| carbon diagnostic | augQZ | -0.05895972 | FAIL |
| carbon diagnostic | autoaux_v2 | 0.00372860 | PASS |

## Next decision and scope

The tested 525-function AutoAux basis passes at +0.00372860 kcal/mol.
[Carbon-only exception proposal](../configs/step6_carbon_auxiliary_exception_proposal_v1.json)
and its exact proposed input are prepared for user review. The result is
diagnostic evidence, not an approved input exception. Retaining strict mirroring and simultaneously passing this carbon
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
