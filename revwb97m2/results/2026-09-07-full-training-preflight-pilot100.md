# Full-training metadata audit and proposed pilot100

Planning only; no submissions authorized. Current snapshot:
[training_preflight_v2/audit.json](training_preflight_v2/audit.json).
v1 is an intermediate draft; v2 explicitly checks basis-bridge identity/status.

## Metadata versus numerical preflight

Metadata checks the recipe: reaction order/identity, signed stoichiometry,
reference energies/units, original weights, roles, species closure, input hashes,
basis/ECP metadata and recorded feature coverage. Numerical preflight checks the
assembled numbers: finite A (1498x292 for full training), fixed-subtracted target,
weights, grid differences, independent reaction reconstruction and numerical
scales/rank/correlations. It requires completed validated features. Metadata PASS
does not establish numerical readiness or solver optimality.

## Audit and exact proposal

Metadata passes:1498 unique ordered entries,49 Cycle-2 SI groups,seven property
classes,2799 species. All input hashes and basis-bridge source identities/runnable
statuses match. Original positive weights and fitting roles agree; final-assessment
entries excluded. Finite references use the existing DatasetEval Hartree convention,
not a new independent reference-energy or source-PDF validation.

| Coverage | Full training | Pilot |
|---|---:|---:|
| Entries | 1498 | 100 |
| Unique species | 2799 | 224 |
| Recorded v7 publication/recovery evidence hash-verified | 41 | 39 |
| Species needing generation or further validation | 2758 | 185 |
| Entries with evidence for every required species | 20 | 20 |

Full coverage also contains12 unvalidated/legacy candidates and2746 species with
no matching feature candidates. Recorded evidence is not fresh native/numerical
reparsing. D4 recovery sidecars are explicitly checked with policy/dependency hashes.
Canary stage markers are recorded as presence only, not approved partial-stage reuse.
All2799 conventional qarchive candidate paths exist; full restart-tree integrity,
compatibility and copy footprint remain launch gates. qarchive alone is not the
orbital restart tree. No new SCF is proposed.

- [Exact100 IDs, weights, references, stoichiometry and missing species](training_preflight_v2/pilot100_reactions.json)
- [Exact224 species, resource classes and evidence](training_preflight_v2/pilot100_species.json)
- [Full1498 metadata](training_preflight_v2/full1498_reactions.json)
- [Full species coverage](training_preflight_v2/species_coverage.json)
- [Snapshot checksums](training_preflight_v2/checksums.json)

Proposed selection retains existing20; covers every49 SI group; fills to100 by
lowest selected/full property-class fraction, then incremental maximum requested
memory, sum AO-count cubed, new-species count, original index. Evidence candidates
are zero new-generation cost for selection only, not exempt from reuse validation.
No reference values/residuals influence selection. Weights are unchanged.
This favors affordable examples; it is not an unbiased chemical accuracy sample.

Composition:BH8,EF13,ISO5,INC3,NC28,TC36,TM7. Basis metadata identifies70 nonzero-spin,
nine ECP and six one-electron species. Four memory classes are represented, not
allseven; the canaries separately cover the full resource range.

| Historical requested memory | Total species | Without accepted v7 evidence |
|---|---:|---:|
| 14GiB | 208 | 172 |
| 21GiB | 11 | 8 |
| 35GiB | 3 | 3 |
| 227GiB | 2 | 2 |

Large cases:PCONF21_444 and PCONF21_99,1833 orbital AOs each. Recommend keeping
all-group coverage, subject to resource review after large canaries. Alternative:
defer PCONF21 and explicitly lose49-group coverage. No resource choice presumed.

## TODO and gates

1. User reviews exact subset and PCONF21 resource tradeoff.
2. Finish/review canaries for runtime/memory calibration; historical requests
   are not predictions or live scheduler/account validation.
3. Version D4-aware production/reuse integration after active pinned work ends;
   tests and user commit before wider launches.
4. Audit full restart trees, basis/ECP and native-stage reuse for224species;
   split185 pending cases into exact missing versus reusable stages. Do not
   blindly rerun all stages. Do not zero-fill missing physical features;
   one-electron zero PT2 remains the explicit checked exception.
5. Prepare executable generation/resource/storage manifest for approval. Retained
   heavy data: `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2`;
   scratch: `/clusterfs/mhg-data/yaoshen/scf_read/revwb97m2`. Cost/core-hour/disk
   estimates await stage-reuse and canary evidence; no automatic cleanup or jobs.
6. Generate approved missing features and independently assemble/check100x292 A,
   fixed-subtracted target, original weights and both grid-difference matrices.
7. Bounded larger MIO pilot; optionally compare nested subsets for gap-size
   hypothesis with unchanged scientific settings. Report raw/recomputed gaps.
8. Finalize full-generation costs/approval, full numerical preflight and pre-bulk
   commit/resource checkpoint. Metadata organization is already available now.

## Implementation and verification

New `scripts/prepare_training_preflight.py` audits read-only inputs and writes a
new non-overwriting snapshot. New `tests/test_training_preflight.py` adds eight
tests: invalid stoichiometry, duplicate IDs, deterministic nested/group-covering
selection, weights, publication completion/hashes and stale spec rejection.
Full suite:131 passed. Independent snapshot/source hashes,100 unique IDs,49 groups,
20 retained seeds, selection reproducibility and active frozen-plan checks pass.
No original canary driver/spec/jobs modified. Initial systemPython3.6 invocation
failed before output publication; successful execution uses dh Python.

```bash
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m revwb97m2.scripts.prepare_training_preflight --output revwb97m2/results/training_preflight_new_snapshot
/global/home/users/yaoshen/.conda/envs/dh/bin/python -m pytest revwb97m2/tests -q
```

Coverage can change; regenerated proposals may differ. Review the exact v2 list,
not an unrecorded regeneration. v1 remains a superseded intermediate snapshot.
