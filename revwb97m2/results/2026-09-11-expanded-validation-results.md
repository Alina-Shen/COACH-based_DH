# Job25790995 — expanded validation partial success; K80 grid coverage failure

Slurm FAILED1:0 after50m37s; peakRSS2301860KiB (~2.20GiB),16CPUs. Not OOM or allocation timeout. Five600s solves completed with incumbents, valid direct objectives/constraints and consistent gaps. Runner stopped at constrained80 full99590 advancement gate; restart80 not run. No publication/completion record, so no complete-workflow acceptance.

## Independent review

Verified release/test/commit/plan hashes, full-data input hashes, historical source publication and actual source coefficients/selection. Rebuilt starts and selected rows, ran fresh audit_case for every existing stage, compared stored audits exactly, recomputed all1498 grid differences and violating entry IDs. Hashed all existing run artifacts before/after: unchanged. Read-only analysis requires no WLS session. Evidence: `2026-09-11-expanded-validation-25790995-audit.json`; newly recorded hashes are a snapshot, not a substitute for an original completion publication.

| Stage | Direct SSE+ridge | Gap | Nonzero semilocal | Max99590 kcal/mol | Violations |
|---|---:|---:|---:|---:|---:|
| discovery14 |1.9078853302|16.10%|10|0.1449649521|106|
| discovery80 |0.4164166140|11.31%|76|2.2514023414|628|
| constrained14 |2.2619917535|25.33%|10|0.014985|0|
| restart14 |2.2619917535|26.48%|10|0.014985|0|
| constrained80 |0.6154784364|30.35%|76|0.03488872785|14|
| restart80 |not run|||||

Discovery stages had no grid constraints and pass their intended acceptance, not final eligibility. K14 restart imported a feasible candidate but made no objective improvement; fresh-search bound/gap can differ. All constrained stages enforced the same242-row union. K80 selected maximum0.0149850000000551kcal/mol; all14 public-limit failures were UNSELECTED. Worst3d4dIPSS_17:0.03488872785, thenTMD10_8:0.03081591173,TMD10_7:0.02958204998. Full list with values in JSON: PCONF21_15,CT20_10,CT20_15,RG10N_105,RG10N_189,RG10N_249,ALK8_1,BDE99_78,G21IP_2,3d4dIPSS_6,3d4dIPSS_7,3d4dIPSS_17,TMD10_7,TMD10_8.

75302 monitoring maxima: constrained14/restart14=0.2810084;constrained80=0.7296782kcal/mol. Not a newly imposed eligibility condition. This does not certify unseen-data performance or global optimality.

## Recommendation and blockers

Recommend approval to enforce all1498 existing99590 rows in a versioned recovery K80 solve plus restart, retaining expanded objective,big-M,ridge,0.999 margin and public0.015 limit. This changes the selected-row implementation policy and must be explicitly approved/versioned; it does not alter target weights, chemistry or the declared full-training acceptance limit. Model584vars/3586constraints vs1074 currently; no performance guarantee. Reuse accepted K14 as a feasible K80 warm-start candidate after explicit re-audit under new rows; K14 fits within K80 budget. Preserve K80 failed-grid candidate for diagnostics, not as an already feasible start. Use one bounded K80+restart check, then production release if successful, rather than repeating discovery/K14 or a new broad diagnostic ladder.

Alternative closer to existing selection protocol: add the14 violations to242rows (256), re-solve and audit all1498; potentially iterate because newly sensitive rows can emerge. Merely adding search time on unchanged242rows cannot enforce omitted inequalities. Do not weaken thresholds, silently add75302, or discard data. No recovery implemented/submitted this turn.

Production launch blockers: (1) approved/versioned grid-coverage policy and successful full99590 K80 result; (2) untested K80 restart and revised-path numerical/artifact validation; (3) committed/tested production expanded execution path and exact scan/start/row policy, reviewed resources/dependencies, pre-bulk commit and explicit release. Proposed production7K x2solves x2passes=28solves,7200s each. Existing base spec remains explicit residual; validated overlay must be deliberately carried into production, not changed without provenance/versioning.

Not launch blockers: missing orbitals/features (complete), WLS access, observed memory use, zero semilocal coefficients (working), zero solver gap (not required), unresolved detailed Gurobi-internal cause, SOS1/fixedCOACH-seed experiments,75302 threshold, deferred final ranking details before initial fitting. Final candidate eligibility/selection still needs the declared assessment and user review; not a demand to finish that before search.

This turn changed no implementation source/configuration and submitted no jobs; added result reports and project-note/status updates only.
