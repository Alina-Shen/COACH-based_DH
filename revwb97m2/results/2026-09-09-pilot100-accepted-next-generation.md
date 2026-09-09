# Accepted bounded100-entry MIO pilot and next-generation readiness

## Independent post-job acceptance

Job25727562 COMPLETED0:0,30m17s,16CPUs,peak batch RSS1621832KiB (~1.55GiB)
against16GiB requested. Empty stderr; all six fit stages and final completion
record present. Fresh separate-process `pilot100_mio_v1 validate` passes commit/
release/test/code/input/publication hashes, all six numerical objective/constraint/
grid audits and no-solve/no-write resumes. Synthetic control12/12 passed.
No optimization, native calculation or source modification in this results audit.

| Fit | Regularized objective(Ha²) | Raw/recomputed relative gap | Maximum99590(kcal/mol) | Maximum75302(kcal/mol) |
| --- | --- | --- | --- | --- |
| Discovery14 | 0.001928739885 | 97.4274% | 0.06985619 | 0.24868753 |
| Discovery40 | 0.000135120327 | 96.1025% | 0.04144207 | 0.55665872 |
| Constrained14 | 0.001636246715 | 96.6664% | 0.01498500 | 0.20027606 |
| Restart14 | 0.001494514891 | 96.5730% | 0.01498500 | 0.11693325 |
| Constrained40 | 0.000157435727 | 96.3070% | 0.01498500 | 0.29233188 |
| Restart40 | 0.000131610792 | 95.7259% | 0.01498500 | 0.27243959 |

All solves status9/TIME_LIMIT with audited incumbents, selected support14/40,
Gurobi13.0.3.99590 public0.015 threshold passes all constrained/restart fits;
both discovery fits violate it. Thus this real pilot demonstrates active grid
enforcement, unlike prior20-row incumbents.75302 is diagnostic and not stable at
0.015; no coarse-grid stability claim or new constraint.

Both restarts improved their constrained incumbent objective. A constrained14
incumbent improving over discovery14 does not mean constraints lower the optimum:
these are time-limited searches with additional search time and different paths.
FinalK40 SSE0.000131390299911934Ha², ridge2.2049248022136362e-7Ha².
FinalK14 SSE0.0014944463269677293Ha², ridge6.856427874568014e-8Ha².

Raw gaps are finite and consistent with recomputed gaps in all6 cases. The prior
positive-infinity discrepancy did not recur, but this does NOT establish its
internal cause or attribute the change solely to data size (time/data differ).
Large remaining gaps mean no optimality certificate or reliable final K ranking.
K40 VV10 reached the lower interior bound1e-8; final D4 coefficients reached the
upper interior bound0.99999999. These are legal pilot results, not a reason to
change scientific bounds or conclude a term unnecessary from100 entries.

Full numerical results/telemetry/scalars saved in
`revwb97m2/results/2026-09-09-pilot100-mio-independent-readback.json`.

## Next step performed: refreshed full-training readiness screen

Read-only audit verified original training-preflight checksums/source hashes and
derived prospective inputs from authoritative source files, without launching
Q-Chem or changing inputs. Full scope remains1498 entries/2799 species. The
accepted100-entry export supplies224 species; conservative remainder2575.
2554 remaining species pass current generic input derivation,21 are explicitly
blocked by embedded-ECP scope. Passing this input screen is not a frozen manifest,
orbital-tree proof or native success.15322 derived stages before additional reuse.

Remaining resource inventory:14GiB1937,21GiB287,35GiB183,62GiB107,117GiB29,
227GiB24,557GiB8. These are existing conservative requested-memory classes, not
fresh scheduler routes or authorization. Large cases retain resource review.

21 explicit-ECP cases: Ag/Cd/Mo/Nb/Rh/Ru/Tc neutral+cation pairs; Pd ES/GS/GS+;
Y_ES; Zr ES/GS/GS+. Current two-case Y gateway intentionally excludes them.
Review each authoritative embedded basis/ECP/core/spin against successful user
production calculations before extending support; do not infer core counts or
copy exploratory basis reductions. See exact species in
`revwb97m2/results/2026-09-09-full-training-next-generation-audit.json`.

## Newly identified compatibility blocker

Calling the older corrected-canary registry validator now fails `code identity
changed`. Exact map comparison proves: missing files0, changed pinned files0,
one added file `/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/pilot100_inputs.py`.
Its introduction during MIO implementation expanded the old `ROOT.glob('*.py')`
hash list. This is a workflow integration regression; the file was additive and
none of the old chemical implementation bytes changed. The current pilot's own
frozen validator passes. Do not erase the new file, alter old manifests, dismiss
the error, or claim old registry revalidation passed.

Six additional prior canary artifacts remain reuse candidates pending compatible
validation: UracilPentane dimer,BSR36_c4,HR46_N-methylacetamide,HR46_toluene,
MOR16_ed33,S22_06b. They are not blindly counted as freshly accepted beyond224.
Remainder2575 is conservative, not a demand to rerun all these species.

## Recommended next approval/checkpoint

1. Implement a versioned generation/evidence compatibility layer with explicit
   dependency sets and immutable historical hashes. It must distinguish the
   known additive nonchemical adapter from any changed/missing chemical dependency;
   test both acceptance and tamper refusal. Do not weaken old validators globally.
2. Review21 ECP cases against production references and propose bounded native
   gateways for any newly supported core/spin representation. Ask for unresolved
   scientific choices; keep supported ordinary generation separate.
3. Revalidate/reuse accepted224 and additional canaries, refresh exact remaining
   resource/storage/stage counts, then freeze first full-training execution
   manifests. User pre-test/pre-generation commit and live partition/resource
   review precede submissions. No global eight-task cap and neverlr_lowprio.
4. Assemble/validate full1498x292 and both grid matrices, then bounded full-matrix
   MIO/resource preflight before the pre-bulk scan checkpoint. Do not treat the
   1.55GiB pilot measurement as proof of full-scale branch-and-bound memory needs.

Default recommendation: proceed toward full-training features with these gates,
not spend longer trying to certify100-row fits. Optional longer100-row solves can
study search/gap behavior but would need explicit resources and are not required
for feature generation. No new generation, MIO or bulk jobs submitted this turn.
