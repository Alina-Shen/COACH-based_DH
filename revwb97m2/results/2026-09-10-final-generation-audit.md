# Full generation completion and scientific readback — September 10, 2026

## Outcome

**PASS: all 2,575 remainder species accepted; zero unfinished species and zero
audit failures.** All 15,412 generated native stages passed full readback.
The audit completed at 23:34:45 PDT on September 10 in 1,601 seconds.
Maximum HF and PT2 consistency errors were 5.10e-9 Ha and 1.00e-10 Ha,
respectively; both passed the existing validator tolerances.

The 2,575-species remainder consists of 2,569 generated species and six reused
canary species. The 2,569 generation tasks include 2,548 ordinary species and
21 ECP gateway species. Together with the previously accepted 224 pilot species,
these cover all 2,799 unique species required by the 1,498 fitting entries.

## Checks performed

- Reconciled every species against the controller's final job journal, including
  both pending-job migrations. Required COMPLETED/0:0 for every replacement or
  original task still responsible for a species. Intentional removed originals
  were not counted as failed chemistry or duplicated species.
- Checked final campaign and all 11 frozen plan hashes. Reloaded each plan through
  the production validator, checking code, build, specification, inventory,
  basis bridge, authoritative inputs and derived stage inputs.
- For every generated species, independently checked publication markers,
  identity and artifact hashes, and rehashed the original saved-orbital tree.
- Revalidated every native stage: source/stage identities, input/output artifacts,
  working qarchive hashes and scratch routes, normal Q-Chem termination, saved-MO
  readback and correct electron/spin counts.
- Revalidated native integratedDV/Q4 publications and reconstructed all 292
  features, including D4 ATM, fixed energy, scalar terms and both grid-difference
  vectors. Compared the reconstructed values against the saved publications;
  required finite arrays and the existing scientific tolerances.
- Fresh corrected seven-canary raw readback covers all six extra reused species.
  Independently rechecked the existing 100-entry pilot matrix's authorities,
  hashes, shapes, finite values, reaction identities, references and weights.
- Compared the union of generation, pilot and extra reuse species against all
  1,498 reaction metadata entries: exactly 2,799 unique species, no omissions,
  duplicates or extras. This is coverage validation, not full numerical assembly.

This audit uses two bounded readback workers. No Q-Chem/SCF job, Gurobi fit,
rebuild, scientific parameter change or data cleanup was performed. D4 and
feature postprocessing were reevaluated as part of readback. Original artifacts
and historical reports were preserved.

## Last jobs and controller

| Species / task | Final state | Runtime | Finished (PDT) |
| --- | --- | --- | --- |
| MOR32_pr24 / 25731104_5 | COMPLETED, 0:0 | 44h 02m 28s | September 10, 22:25:11 |
| PCONF21_SER_ab / 25751667_20 | COMPLETED, 0:0 | 2h 21m 26s | September 9, 21:11:54 |
| PCONF21_SER_b / 25751667_21 | COMPLETED, 0:0 | 3h 34m 51s | September 9, 22:25:19 |
| PCONF21_SER_pII / 25731143_22 | COMPLETED, 0:0 | 5h 02m 40s | September 10, 00:36:22 |

MOR32_pr24 was the final calculation, not a hung job. Slurm reported its batch
MaxRSS as 257,961,584 KiB (approximately 246 GiB), below its 557-GiB allocation.
The controller recorded `finished: true`, 2,569 completed, zero active tasks,
no unresolved intent and no halt at September 10, 22:25:59 PDT. No further
automatic submission or monitoring is needed for this completed campaign.

## What is and is not complete

Species feature generation and the requested remainder's result checks are
complete. The existing 100-entry matrix
remains validated. The full **1,498 × 292 numerical training matrix has not yet
been assembled or validated**, and no full-data optimization has run.

Recommended next step: implement/review the full-data integration manifest and
assembly adapter, explicitly binding the 2,569 generated publications, six
canary reuse sources and 224 accepted pilot sources. Assemble original COACH
entries and weights, fixed/reference targets and both grid matrices; validate
stoichiometry, coverage, units, hashes, finiteness and agreement with the accepted
pilot rows. Then prepare the separate pre-bulk fitting commit/specification/code
freeze and user-approved model-size/resource scan. No missing-feature zero fill,
new scientific settings, or bulk-fitting authorization is inferred here.

Final machine-readable evidence: [full audit JSON](./2026-09-10-final-generation-audit.json).

Keep the existing scratch and qarchive evidence for now: the native validation
path still uses it. Completion does not authorize deleting restart or audit data.
