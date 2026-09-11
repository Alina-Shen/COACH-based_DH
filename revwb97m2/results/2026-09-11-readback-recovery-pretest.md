# Readback recovery and real-fitting gates — pre-test checkpoint

## Implemented, not yet executed

New `scripts/continuous_readback_v2.py` independently validates original continuous_v1 identity, committed producer hashes, complete required artifact hashes, model/parameter identity and acceptance. It compares only SSE/ridge/objective with rtol1e-12/atol1e-15; other audit fields stay exact. It preserves the original producer/plan/release and outputs. No monkey-patching or refreezing historical runs.

The same tool prepares a full-primal fixed-support MIO start only after exact four-scalar selection, unchanged continuous gates and an independent MIO audit. It recomputes residuals from unchanged coefficients; no clipping or rounding. Output is source/matrix/reader-hash bound, explicitly not submission-authorized and not grid-audited. Relaxed results cannot become this start. The real-data export remains pending execution after user commit.

Added18 regression cases for roundoff acceptance, nonfinite/changed objective rejection, exact Boolean/count/schema fields and invalid/fractional/UEG/residual start rejection. Tests are prepared, not yet run, at this pre-test commit gate. No solver or Slurm jobs submitted this turn; scientific specification and acceptance tolerances unchanged.

## After commit

1. Run full pytest suite, then new reader on job25783741 to a new results JSON; expect fixed=true/relaxed=false, with independently audited candidate start. A successful reader execution does NOT mean all diagnostic gates passed.
2. Prepare a separately frozen precision-focused relaxation run: same full1498 matrix, objective, ridge, constraints,600s/16CPU/32GiB/90min envelope. Proposed controlled variants: first retain algorithm/presolve defaults and tighten only BarConvTol to1e-12; second use the same tighter barrier criterion plus NumericFocus=3. Record effective parameters, solver quality, coefficients, residuals, hashes and independent acceptance. These are explicit diagnostic solver settings, not production changes or relaxed scientific thresholds. No success promised; if still failing, examine scaling/presolve/unscaled residuals before further changes. Exact launcher/manifest and resource review remain to be prepared before submission.
3. With audited start and reliable readback, prepare a bounded MIO confirmation using the improved start, then complete K80, grid-constrained and restart gates. A production-length7200s K14 confirmation is a reasonable next proposed resource choice, but is NOT authorized by this preparation or implemented here.
4. Freeze production starts/candidate union, full scan and resource plan; user pre-bulk commit and explicit launch approval. Production spec remains7200s per solve.

## Is ten minutes the cause?

It may limit MIO improvement/proof: job25778785 hit600s with its supplied start unchanged. It cannot explain the current relaxed rejection: job25783741 stopped OPTIMAL in0.907s, far below600s. Simply raising TimeLimit does not force a solver to keep working after its convergence criteria are met. Its UEG/residual violations and the separate exact-float reader defect are not evidence of insufficient wall time. The successful four-scalar optimization took0.066s and improved32.1915 to4.42974. This narrows the diagnosis but does not establish the MIO solver's internal cause.

Gurobi distinguishes barrier convergence from time limits; tightening BarConvTol may improve accuracy. NumericFocus increases numerical care but may cost time. These are experiments, not guaranteed repairs. Sources: [parameters](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html), [numerical guidance](https://docs.gurobi.com/projects/optimizer/en/current/concepts/numericguide/numeric_parameters.html).

## What blocks real fitting?

- **Not blocked by chemistry:** accepted full1498 numerical matrix already exists; no orbital/feature regeneration needed.
- **Readback reliability:** new fix must pass tests and real-artifact validation.
- **Numerical acceptance:** relaxed point fails existing gates; solver OPTIMAL alone is insufficient. A relaxed diagnostic is not itself a final-fit requirement, but its failure requires resolution or explicit evidence that accepted MIO candidates are unaffected.
- **Full-data workflow gates:** larger support, grid constraints and restart path are not yet validated through the approved bounded full-data sequence. Current MIO incumbent has not improved; the new start still requires audited import and solver acceptance.
- **Release gate:** exact production starts/candidate union/resources, pre-bulk commit and launch approval remain. No requirement to prove global optimality or obtain zero gap is added; gaps remain reported and considered in model review.

Recommendation: finish this short correctness checkpoint first, then test a longer improved-start MIO run instead of attributing all symptoms to short search time or launching28 production solves now.
