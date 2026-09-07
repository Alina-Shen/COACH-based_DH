# Approved science and proposed test-to-production sequence

Date: 2026-09-07. Planning/documentation only; no test, implementation, commit,
Q-Chem rebuild or submission performed in this turn.

## Approved decisions

- Fixed omegaB97M-V orbitals; target omega=0.3, gamma_ss=0.01; VV10 b=5.5,
  C=0.01; independent VV10/PT2/D4 amplitudes and existing C0.
- Follow maintained COACH ridge: half*SSE + 5e-11*||beta||^2, equivalently
  SSE + 1e-10*||beta||^2. Recommendation for implementation: retain our explicit
  residual representation with the latter objective, preserving current SSE
  units; save unregularized SSE and penalty separately. This does not import
  unrelated COACH SOS1 bookkeeping. Ridge covers the fitted coefficient vector,
  not residual or binary variables.
- Internal grid threshold 0.999*0.015=0.014985 kcal/mol; independently audit
  public 0.015. Two grid passes, no new orbital cycles.
- Final selection follows COACH's lowest overall mean error/NER among eligible
  candidates under chosen constraints/stability requirements, plus approved
  user-review gate before protected final assessment.
- No-ridge comparison becomes a FUTURE TODO, not a gate before first fitting.
- Undocumented near ties, trade-offs and exact historical final-selection trace
  are deferred user decisions, not prerequisites for generating candidates.

## Readiness distinction

Science is settled sufficiently to implement and validate fitting. Existing
code is NOT yet a production implementation of these approvals: v6 YAML/scalar
input uses b=10; mio.py is unregularized and uses no 0.999 margin. Production
spec-to-code wiring, scan/resume/failure behavior and general recovery integration
remain. No native omega change/rebuild is needed.

The recorded 38 species /20 entries are v6 reuse candidates. New b=5.5 VV10
must be evaluated and vectors republished without overwriting old results. Other
components can be reused after identity checks. Full fit still requires all
2799 species /1498 entries; the earlier feature audit did not report missing
orbital archives. Step16 exact ranking details can wait, but metric implementation
and broader 13907-species development coverage are needed before final selection.
Neither final tie handling nor the Gurobi support response blocks initial fits.

## Recommended stages and commit gates

0. Optional immediate checkpoint of current code/history using the scoped Git
   commands below. This captures old implementation, NOT new-science readiness.
1. Implement versioned v7 (archive v6 intact), spec-driven ridge/C0/grid controls,
   b=5.5 scalar derivation/provenance, reusable reaction-ready publication,
   production scan/start/resume manifests and failure states. Add tests without
   executing them. Keep parent/R0 constants and old artifact namespaces intact.
2. **Pre-test commit:** inspect staged diff and commit the exact code/config/tests
   intended for validation. Then run the following approved-scope tests. No
   tests/jobs until user has made this checkpoint. Fixes discovered during tests
   need follow-up commits and affected reruns; do not hide dirty code identities.
3. After gateway tests, review resources and approve fixed-orbital feature
   generation. If 'bulk' includes feature production, make a pre-generation
   commit here too. Begin seven representative canaries; review, then approve
   wider batches using the existing resource-class plan updated for v7.
4. Validate/reuse all fitting-species components and assemble full 1498x292 A,
   b, weights, fixed terms, D99590 and D75302 with immutable manifests. Run
   a larger pilot and full-matrix bounded preflight.
5. **Pre-bulk-MIO commit:** record tested implementation, passing validation,
   full data hashes, resolved scan/parameters/resources and authorization. User
   reviews/commits before submission. No scientific changes after this commit
   without affected validation and another checkpoint.

## Test plan (proposed; none run yet)

| Layer | Tests | Acceptance |
|---|---|---|
| Unit/config | Parse v7, reject unsupported/stale options; ridge algebra, sqrt weights, bounds/UEG/binaries, interior scalars, unit conversion, 0.999 margin | Correct analytical toy values and all tests pass; old v6 evidence preserved |
| Serialization/restarts | Hash identities, resume idempotence; stale b=10 rejection, missing/failed feature, infeasible/no-incumbent/time-limit states | No invalid publication; explicit diagnostics and no overwrite |
| Grid selection | >200-row multi-candidate independent fixture; stable ties/dedup; selected constraints and independent public-limit audit | Correct row union and no hidden coarse-grid constraint |
| Chemical gateway | Existing closed/open-shell gateways plus recovered one-electron, spin-scaling and field cases; b=5.5 VV10; reuse unchanged columns | Same orbitals/zero SCF, validated new VV10, field/fixed identities, correct total-PT2 recovery |
| Real small MIO | Refresh 20-entry cohort; K14, ridge, both grid passes, restart, independent residual/objective/penalty readback | Feasible audited incumbent or explicit failure; no claim of optimum from TIME_LIMIT |
| Resource/scale | 100-300 real entries when available, then bounded full1498-row pilot; representative larger K; planned16threads | Measure RSS/runtime, strict output and start/resume controls; no arbitrary time-to-solution claim |
| Selection pipeline | Dataset-specific NER/weights/aggregates on hand-computed fixtures; role isolation | Needed before scientific ranking, not before initial coefficient fitting |

## Bulk proposals (require later resource approval)

Feature generation first: update the prior seven-class canary plan for v7;
revalidate reuse rather than regenerate every term. Preserve conservative memory
assignments, inspect storage quota/copy footprint and live Slurm availability;
stop systemic failures and diagnose before resubmission. No source archive edits,
no blind retries. Existing prior proposal is not a new submission permission.

Initial MIO scan proposal retains existing seven K values [14,24,32,40,48,64,80].
Propose two solves per K per grid pass (initial + one warm-started restart),
16threads,7200seconds per solve; pass2 starts from pass1. This explicit repeat
interpretation needs validation in the driver; seed/start lineage must be saved.
That schedule is 28 solves with a MAXIMUM nominal solver allowance of 56 wall
hours serial /896 core-hours, excluding I/O/setup/queue/retries. It is not a
completion-time or convergence prediction. Recommend initial solver concurrency1,
provisional16GiB memory and3h Slurm limit for one2h solve, to be revised from
measured full-matrix/larger-K RSS and partition policies before launch.

COACH general paper scan is every integer24-80, whereas our seven-K scan is a
coarse project proposal. It does not establish the best K over the full integer
range. After the coarse scan, user can authorize refinement near promising sizes
or full24-80: 57K*2solves*2passes=228 solves, maximum456 solver-hours/7296
core-hours under uniform2h16thread limits. Final-cycle SI22-89 was a separate
polynomial screen, not an instruction to silently expand our run. Freeze the
chosen execution grid before the production commit; exact final tie handling
can remain deferred. Keep all candidates and rank using declared development
metrics when available; no final-test-driven refinement.

## Git commands

No currently staged changes were shown by `git diff --cached --stat`. There are
many uncommitted implementation files, output artifacts and unrelated root-level
Q-Chem scratch deletions. Do not use `git add .` or `git commit -a`.

Run these from the project root; inspect every staged diff before committing.
The following scope includes project code/config/tests/lightweight manifests and
Markdown reports, not raw result logs/arrays or private reproducer input JSON.

```bash
cd /clusterfs/mhg-data/yaoshen/coach-based_dh
git status --short
git diff --cached --stat
git add -- ':(glob)revwb97m2/*.py' revwb97m2/configs revwb97m2/scripts revwb97m2/tests revwb97m2/slurm revwb97m2/environment revwb97m2/manifests revwb97m2/docs ':(glob)revwb97m2/results/*.md'
git add -- revwb97m2/diagnostics/gap_reproducer/.gitignore revwb97m2/diagnostics/gap_reproducer/reproduce.py revwb97m2/diagnostics/gap_reproducer/prepare_local_data.py revwb97m2/diagnostics/gap_reproducer/README.md revwb97m2/diagnostics/gap_reproducer/SUPPORT_DRAFT.md
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Review for unintended files/private research data/credentials; do not commit
unless scope is correct. Optional immediate checkpoint:

```bash
git commit -m "Checkpoint revwb97m2 implementation and approved fitting plan"
git rev-parse HEAD
```

After implementation and BEFORE executing tests, repeat staging/review and use:

```bash
git commit -m "Implement revwb97m2 v7 COACH ridge and validation workflow"
git rev-parse HEAD
```

After tests/data readiness/resource approval and BEFORE production MIO, repeat
staging/review (also explicitly stage newly created lightweight validation/run
manifests once their exact paths are known), then:

```bash
git commit -m "Validate revwb97m2 v7 and freeze production fitting manifest"
git rev-parse HEAD
git status --short
```

Future commands are conditional templates, not claims that v7 or validation
exists now. Do not commit raw arrays/logs or research_inputs.local.json, and do
not force-add ignored files. No push requested. External project notes are not
included in this repository commit; the decisions are mirrored in this report.
