# Job25792248 — solver recovery succeeds; exact-float readback defect identified

## Outcome

Slurm COMPLETED0:0/20m28s,16CPU,peakRSS1757556KiB (~1.68GiB). Both600-second solves produced candidates and job-local independent readback passed. stderr empty;no resource failure. Publication/completion artifacts present.

| Stage | Direct SSE+ridge | Gap | Semilocal nonzero | Selected99590 max kcal/mol | Full99590 max | Unselected violations |
|---|---:|---:|---:|---:|---:|---:|
| constrained80 |0.6300221237699382|30.8739%|76|0.0149850000000772|0.03238715244784875|9|
| restart80 |0.6142645145935063|28.4065%|76|0.0149850000000029|0.05898767711024431|11|

Both select80coefficients and impose349grid rows. Restart coefficient/start identities exact;restart initial candidate selected-grid-feasible. First run's imported discovery start not grid-feasible;solver obtained a passing candidate. Restart improves objective2.50111997%,but increases unselected99590 sensitivity. Retain both candidates for review;do not equate lower training objective with final-model superiority. Gaps remain finite/consistent;no global optimum claim. All public99590violations are unselected. Worst initial3d4dIPSS_17=0.03238715;worst restart3d4dIPSS_6=0.05898768kcal/mol. Full entry lists/values in audit JSON.75302monitoring max0.85941382→0.66044913kcal/mol;counts above0.015 are541→494 (diagnostic,not new enforcement).

## Independent audit and reader defect

Called committed selective_recovery_v1.validate on login node. Release/test/commit/plan/source/publication checks proceeded,but exact report equality at `revwb97m2/scripts/selective_recovery_v1.py:142` rejected candidate/report mismatch. Detailed recursive comparison identifies only ridge penalty float change: saved2.793524061652957e-6 vs recomputed2.7935240616529565e-6Hartree²,difference4.235164736271502e-22. Same scalar occurs in restart start audit (exact comparison atline134). This is a last-bit reproducibility discrepancy;underlying hardware/BLAS mechanism not isolated. No scientific decision,violation identity,coefficient or source hash changed.

Read-only diagnostic `/tmp/audit25792248.py` repeated direct objectives,coefficient/selection/scientific checks,349-row reconstruction,parameters/model dimensions,start vectors,restart import,gaps and all-entry grid reports. Numeric report values compared with diagnosticrtol=atol=1e-12;all nonfloat report structure/IDs/counts/flags exact. All comparisons pass. This tolerance is an analysis-only comparison,NOT a modification of scientific feasibility thresholds or released implementation. Existing direct objective tolerance retained. Result:independent numerical audit passes,but official cross-node reader still needs correction;do not report official reader PASS.

Hashed all run artifacts before/after inspection:unchanged. Detailed evidence `2026-09-11-selective-recovery-25792248-audit.json` includes all outliers and exact differing fields. No WLS session/new solver run required for readback.

## Next recommendation

Fix/version numeric report comparisons (including start audit),keeping hashes/row IDs/selections/booleans exact and recomputing scientific feasibility with unchanged limits. Add last-bit-difference and meaningful-change rejection tests;rerun readback on THESE existing artifacts. No expensive fit rerun indicated by this defect. Preserve old frozen source hashes via a versioned reader rather than silently modifying released files.

Then prepare production expanded/COACH-selective scan with explicit candidate pool,starts,resources/dependencies and pre-bulk commit/release. No need to add all1498constraints or investigate SOS1 as a launch prerequisite. Grid outliers remain user-review information under approved policy,not an automatic block. Final model review and production launch remain unapproved. This turn changed no implementation code/configuration and submitted no jobs;only analysis reports and project notes/status.
