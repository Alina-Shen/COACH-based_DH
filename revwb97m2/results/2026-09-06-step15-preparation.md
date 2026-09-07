# Step 15 named inputs and bounded optimizer diagnostics

Step 15 is in progress. The generalized C0 model and named R2 inputs are ready.
The full R2 solve is blocked by Gurobi's size-restricted license (error 10010).
R1 has a named 79-column schema but no matching real cohort feature matrix.

- Added `revwb97m2/mio.py` with named R1-79/R2-292 layouts, generalized C0
  best-subset weighted least squares, coefficient bounds +/-25, mandatory four
  scalar selections counted against the support budget, SR-HF bounds [0,1],
  independent VV10/PT2/D4 bounds [1e-8,0.99999999], and gx(0,0)+c_sr_hf=1.
  R2's exchange uses monomials in u and Legendre polynomials in its companion
  coordinate; its UEG vector is evaluated accordingly. No VV10+PT2 equality,
  ridge penalty, one-electron bound, or sampled enhancement bound is added.
- Optional practical-grid inequalities use the frozen 0.015 kcal/mol limit.
  The initial real-data pilot omits grid constraints, as required for pass 1.
- Explicit support semantics: at most K selected slots, four mandatory scalar
  slots always charged to K. Selection does not force an arbitrary nonzero
  minimum on signed semilocal coefficients or on SR-HF, whose lower bound is 0.
- Added `run_step15_pilot.py`. It verifies Step 14 artifact hashes, prepares
  the 20x292 matrix and target/weight/fixed/reference/grid arrays, creates named
  schemas, freezes a pilot contract, exports full/reduced LP models, and records
  status, incumbent, bound, gap and independently audited weighted SSE.
- R1 cannot be sliced from R2: its same-spin nonlinear gamma is 0.2 whereas
  R2 uses 0.01. Existing original78/coach291 comparison-schema metadata is
  historical; this pilot follows v6 independent scalar bounds and 79/292
  feature counts. It explicitly marks R1 feature data pending.
- Two full R2 attempts (K=14, 2-second cap, 1 thread, seed 0) returned Gurobi
  error 10010, model too large for size-limited license. No full-R2 coefficient
  result is claimed. The current Gurobi 13.0.3 environment reports a restricted
  non-production license expiring 2027-11-29.
- A separate 10-column restricted-support engineering diagnostic (K=7, two
  repeats) solved optimally twice with zero gap and identical coefficients.
  Weighted SSE was 0.00011442617701032907 Ha^2. All bound/UEG/support checks and
  independent objective reconstruction passed. This is not full R2 model
  selection or a scientific performance assessment.
- The first pilot finished solving but failed JSON serialization of NumPy
  booleans. Source snapshots and partial artifacts are preserved in
  `results/step15_pilot_v1`; corrected serialization and results are in v2.
- Three new tests verify named layouts and the UEG vector, mandatory-scalar
  budget/bounds, and an actual solve with independent scalar values and an
  active grid constraint. All 67 repository tests and git diff --check pass.

Artifacts: `/clusterfs/mhg-data/yaoshen/coach-based_dh/revwb97m2/results/step15_pilot_v2/`:
named_models.json, reaction_names.json, arrays, pilot_contract.json,
pilot_results.json, full_R2.lp, reduced_support_diagnostic.lp, and two reduced
diagnostic coefficient vectors.

Next: provide an unrestricted Gurobi environment/license path for the full
R2 pilot. Generate separately validated R1 features on the same imported
densities/grids before the R1 comparison. Two-second diagnostic limits do not
replace v6 production settings (16 threads, 7200 seconds); no production scan,
grid-row selection, or bulk Q-Chem job was run.
