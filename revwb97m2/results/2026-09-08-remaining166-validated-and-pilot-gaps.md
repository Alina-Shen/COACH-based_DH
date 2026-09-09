# Remaining166 validated; next-step legacy audit and exact pilot gaps

All four arrays completed0:0:25714429(153),25714430(8),25714431(3),25714463(2).
Independent post-job readback accepted166/166 species and994 native stages.
Maximum HF reconstruction error5.000001301880275e-9 Ha, within unchanged2e-8.
Raw native outputs, original restart hashes, code/build/input/specification,
published hashes,292-feature vectors, fixed/scalar terms and both grid differences
were checked through the unchanged production validator. No native reruns.

PCONF21_444:5:18:33, MaxRSS100930572 KiB (~96.3 GiB).
PCONF21_99:2:36:32, MaxRSS105908028 KiB (~101.0 GiB).
Both succeeded within their16 CPU/227 GiB allocations; no resource reduction made.

## Work beyond job readback

Added three read-only audit/diagnostic scripts, leaving frozen runtime unchanged:

- `scripts/audit_remaining166.py`: release checks and parallel post-job validation;
  saves per-species success/failure/provenance and numerical identity metrics.
- `scripts/audit_legacy_pilot_candidates.py`: revalidates the38-species refresh
  cohort, source restart hashes, historical artifacts, current geometry-only D4,
  and corrected final-nuclear fixed-energy parsing.38/38 pass; vectors unchanged,
  max absolute fixed-energy correction9.499899533693679e-9 Ha. Historical files
  were not rewritten. Generic v2's legacy reuse rejection remains unchanged.
- `scripts/pilot_coverage_after_readback.py`: checks audited artifact hashes,
  explicitly consumes corrected legacy fixed values, revalidates canary evidence
  and assembles only covered rows as a diagnostic, preserving original weights.
 221/224 species covered;93x292 diagnostic matrix finite. The diagnostic arrays
  are calculated in memory; only coverage/shapes/hash report saved. No training
  subset replacement, fitting release, zero-filled features or full100-row claim.

Reports under `results/pilot_execution_v3/`:
`remaining166_independent_readback_20260908.json`,
`legacy38_corrected_audit_20260908.json`,
`pilot_coverage_after_readback_20260908.json`.
Regression suite172passed9.50s; git diff whitespace check passed. These are new
audit tools, not changed production algorithms; the audit uses existing validators,
not a separately implemented quantum-chemical numerical method.

## Exact remaining gaps and recommended next implementation

| Missing species | Evidence / reason | Affected pilot entries | Next action |
|---|---|---|---|
|11_H2O_TA13|Old scalar input has NL_VV_B1000 (b10), not approved b5.5. Not in38-species v7 refresh.|TA13_1,2,3,5,6,7|Refresh the scalar term with approved settings and validate/migrate compatible remaining stages; do not blindly accept old292 vector.|
|3d4dIPSS_Y_GS;3d4dIPSS_Y_GS+|Embedded GEN basis/ECP bridge already hash-validated; current canary-derived driver explicitly rejects $ecp/embedded ECP resolution.|3d4dIPSS_11|Versioned explicit-ECP support preserving original blocks and orbitals; use validated28 removed core electrons (11/spin1 and10/spin0 valence cases); bounded native verification before acceptance.|

The ECP limitation is in this workflow, not evidence that Q-Chem cannot run the
inputs or that orbitals are missing. Do not remove ECP blocks, substitute a basis,
change electron/spin labels, or run newSCF by assumption. No Q-Chem rebuild is
currently established as necessary. Formal corrected-legacy ingestion and final
100-row matrix export still need integration; diagnostic success alone is not a
production matrix release. Continue those implementations, freeze/test any new
native execution plans, then user commit before submission. No added commit gate
is required merely to retain these read-only audit reports.

User policy remains no eight-task cap and no lr_lowprio for future submissions.
No new jobs, source/data overwrites, cleanup, science/tolerance changes or fitting
were performed. Updated project STATUS and chapter13 with accepted results/gaps.
