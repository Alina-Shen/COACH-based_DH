# Q4 Q-Chem integratedDV extraction and publication complete

Date: 2026-09-04

Status: complete; the strict extractor, atomic publisher, restart policy, and
six real Q3-derived feature boundaries pass validation.

## Implementation

`qchem_feature_publisher.py` is the production-facing Q-Chem integratedDV
boundary. Its parser recognizes marked blocks, requires the declared and
observed 96x180 shape, exact `integratedDV` label, numeric finite values, and
balanced non-nested delimiters. It rejects zero-block, malformed, wrong-shaped,
nonfinite, and truncated output. Multiple valid complete blocks are allowed;
the last is selected and the total count and selected ordinal are recorded.

Before extraction, the source preflight requires a regular nonempty Q-Chem
output, preparation record, authoritative input copy, derived input, source
`qarchive.h5`, and exactly one isolated copied `qarchive.h5`. It reproduces the
prepared source/copy archive hashes, input hashes, species/grid identity,
alpha/beta MO-read evidence, normal Q-Chem termination, and the controls
`METHOD wB97M-V`, `UNRESTRICTED TRUE`, `SCF_GUESS READ`,
`MAX_SCF_CYCLES 0`, `GEN_SCFMAN FALSE`, `XC_FXC 3`, and the recorded grid.
Missing or changed archives stop publication; there is no PySCF or SCF
fallback.

The publisher writes into a uniquely named sibling staging directory. It
stores the transposed 180x96 full matrix, selected rows `(64,154,166)` as 3x96,
and their C-order flattened 288-vector. It then writes hashes, provenance,
source identity, a validation record, and a completion marker. The staged
boundary is independently reloaded and checked before one directory rename
publishes it. Existing destinations are never overwritten. A failed staging
attempt remains unpublished and receives `FAILURE.json` for diagnosis.

`publish-or-resume` implements the restart rule: an absent boundary is
published, a complete boundary is independently revalidated and reused without
mutation, and an incomplete, corrupt, source-mismatched, or hash-mismatched
existing boundary stops instead of being repaired or overwritten.

## Real-data evidence

The six Q3 source cases were published under
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/qchem_gateway/q4_published_v1`.
They cover `h2o_SW49` and `12_NH2rad_HNBrBDE18` on grids `250974`, `99590`,
and `75302`. Each boundary has all three arrays plus manifest, validation, and
completion marker; the collection occupies 867 KiB. Each source output hash
matches the passed Q3 record and each source/archive hash was reproduced.

A second `publish-or-resume` pass reported `reused` for all six cases, proving
that restart inspection does not rewrite complete results. The aggregate
`q4_validation_v1.json` reports all seven Q4 gateway checks true and all 20
per-boundary checks true. Its SHA-256 is
`10d4a84b7f2173963cec84143c71114fcd68f2ec4e728ccff2f909b8d560c501`.

## Tests and handoff

The Q4 tests cover one block, final selection from multiple blocks, zero
blocks, truncation, malformed/nested/unmatched markers, wrong labels, wrong
shape, nonnumeric/nonfinite data, exact transpose/selection/flattening,
artifact hashes, direct overwrite refusal, valid restart reuse, corrupt
existing-boundary refusal, and both missing and changed archive refusal. The
complete repository suite passes: 43 tests.

The final cross-gate audit initially found one stale provenance hash: Q3 had
extended the maintained integratedDV series helper with Chebyshev evaluation,
while `manifests/integrated_dv/validation.json` still named the earlier module
hash. Rerunning the independent kernel validator refreshed that record with all
17 checks passing; the complete scientific-specification validator then passed
189/189 checks. No scientific parameter or result was changed.

Q4 is complete without a Q-Chem rebuild or new Q-Chem calculation. Q6 is now
ready: integrate this boundary into the non-submitting Step-13 plan and measure
representative archive-copy, grid, extraction, memory, output-size, and restart
costs. Bulk production remains unauthorized.
