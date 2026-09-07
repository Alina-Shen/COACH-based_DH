# v7 cohort validated; bounded real-data fitting pilot

## Final pilot outcome (supersedes submission status below)

Job25679856 COMPLETED0:0 in6m10s; empty stderr. Corrected synthetic control
passes all12 checks, including grid enforcement, restart/resume and tamper refusal.
Allthree real fits pass fresh independent post-job readback. Each returned
status9 (120s TIME_LIMIT), not an optimality certificate. Pass2/restart are
identical incumbents; first-pass incumbent already meets the chosen grid limit.
The real cohort therefore does not itself demonstrate an active grid constraint;
the separate synthetic fixture does.

Pass2/restart weightedSSE=2.0958641022824694e-7Ha²,
ridgepenalty=2.2708743411019994e-8Ha²,
total=2.3229515363926694e-7Ha² (matches solver objective within audit tolerance).
99590 max=0.001481086045066296kcal/mol, below0.015 public threshold.
75302 max=0.04922288191342823kcal/mol: diagnostic only, NOT coarse-grid stable
at0.015. Raw solver gap remains positive infinity, serialized as null with
explicit state; recomputed relative gap0.9986519366137236 (~99.865%). Bound
3.1314859143052587e-10Ha². This is an audited feasible workflow result, not
convergence, solver-gap resolution or final model selection.

Next recommendation: review/commit these execution wrappers and validation
reports, then prepare the approved-scale feature-generation canary plan for
larger/full-data validation. Do not launch bulk fitting from only20 rows.
Keep the raw-gap issue and75302 diagnostic limitation explicit.

## Completed chemical/assembly validation

All30 tasks in25676786 and all3 tasks in25677457 COMPLETED0:0. The14GiB
tasks took19s–5m45s;21GiB tasks took13m25s–13m41s. Assembly25677566
COMPLETED0:0 in2m26s and reported independent fitter readback PASS.

A fresh read-only audit using the committed scientific implementation:

- Passed frozen plan/source/code/Q-Chem build hash verification.
- Reparsed and validated all38 species, including ordinary and recovered cases,
  unchanged291 reused columns, fixed energy and both grid differences.
- Loaded and hash-checked the published fitter manifest and completion marker.
- Independently reconstructed all20 reactions from38 species with a
  stoichiometric matrix and checked published arrays at1e-12 absolute tolerance.
- Rechecked historical baseline hashes and unchanged fixed/reference energies,
  target and Cycle2 objective weights.

Validated feature matrix:20x292; target/weights:20; both grid matrices:20x292.
Published input manifest:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/v7_vv10_refresh_v1/reactions/inputs.json`
SHA256 `4bb27b1bfac3fdf1eb739783581652a2c1ec9225bb4899e31dc0660dc3693b4f`.
VV10 b5.5/C.01 and omega.3/gamma_ss.01 are retained. VV10 usesSG1 only;
its zero grid-difference column does not prove both-grid VV10 stability.

## Next authorized bounded test

New orchestration only: `slurm/run_v7_real20_pilot_v1.sh`. No scientific core,
specification, parser, solver or tolerance edits. Existing untracked reports,
launchers and logs preserved. No commit/push or Q-Chem build.

Used partition skill/live mhg capacity and association checks; chose16CPUs,
8GiB,15minute job cap. Bash syntax, diff whitespace and sbatch test-only pass.
Submitted **25679856**:

1. Fresh corrected synthetic integration control in a separately named root.
2. Real20-row K14 initial fit, approved ridge SSE+1e-10||beta||².
3. Warm-started grid-constrained fit using first-pass candidate selection.
4. Restart from the grid-constrained incumbent with the same selected-row policy.
5. Readback-only resume of constrained and restarted fits.

Real solves each capped at120s and16Gurobi threads: at most360s of real solver
time, not a full K scan. Synthetic solves retain their10s caps. Fail-fast shell
prevents later stages after failed control/fit. WLS credentials read privately,
never copied into reports or printed. Purpose is feasibility/objective/grid/
restart validation, not production ranking or an optimality certificate.

Logs: `results/v7_real20_25679856.out/.err`; isolated results root:
`results/v7_real20_25679856`, synthetic suffix `_synthetic`.
At submission the pilot has no claimed outcome. Verify Slurm and result.json,
independent objective/readback and public0.015kcal/mol grid limit after completion.
Only20of1498 fitting entries are covered; larger/full-data generation and
pre-bulk approval/commit gates remain. No full-dataset generation or bulk fit.
