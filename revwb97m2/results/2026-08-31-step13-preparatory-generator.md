# Step 13 resource-independent preparatory implementation

Step 13 is now in progress at the boundary that does not depend on the final
Step-12 resource decision. No chemistry job was run or submitted, no live
artifact was changed, and no resource value was inferred.

## Delivered implementation

1. `production_generator.py` joins the locked fixed-geometry energy-role union
   to the validated basis bridge and immutable record index. It refuses
   duplicate identities, missing joins, record-hash disagreement, non-runnable
   basis rows, and unsafe path components. The joined count is exactly 17,452.
2. Seven independently resumable future boundaries are explicit: parent;
   semilocal grids `250974`, `99590`, and `75302`; VV10; RI-MP2; and final
   species assembly. This prevents a failure in one grid or scalar calculation
   from invalidating another completed result. Existing combined Step-9/10
   gateway artifacts remain untouched and authoritative as gateway fixtures.
3. The production layout is deterministic:
   `production_root/<scope>/<species>/<boundary>`. Scope is retained to avoid
   cross-source ambiguity, even though the current locked species names are
   globally unique.
4. Every species receives an authority fingerprint covering the source-record
   hash, basis/ECP-definition hashes, role table, basis table, record index,
   scientific specification, and planner implementation.
5. Read-only state discovery classifies each boundary as missing, complete and
   reusable, failed, partial, corrupt, stale-authority, or interrupted
   temporary. Failed and questionable trees are preserved and force explicit
   review; the planner never deletes, repairs, or overwrites them silently.
6. Reuse requires a completion marker, matching manifest identity/status,
   current source and authority fingerprint, an independent passing validation
   record pinned to the manifest hash, and matching hashes for every declared
   non-symlink artifact.
7. The dependency plan makes parent the prerequisite for all component stages
   and requires all three semilocal grids plus VV10 and RI-MP2 before assembly.
   Missing work is marked eligible only after dependencies and Step-12 resource
   sign-off; invalid work is marked stop-and-report.
8. The CLI `scripts/plan_step13_production.py` supports the full population or
   deterministic species/limit subsets. It atomically publishes a JSON plan,
   refuses an existing output path, and contains no execution or submission
   operation.
9. The checked-in `step13_preparatory_v1.yaml` freezes the source hashes,
   boundary graph, reusable-artifact requirements, preservation policy, and
   explicit Step-12 gate. Production subset, tiers, resources, concurrency,
   retries, direct/out-of-core routes, and quantitative AO stops are null.
10. `validate_step13_preparatory.py` independently checks the authorities,
    exact population, boundary graph, full dry-run action counts, unset
    resource fields, and global submission prohibition.
11. Six focused tests cover population identity, path/boundary layout, complete
    artifact reuse, hash corruption, failure/partial/stale/interrupted states,
    dependency-aware resource gating, deterministic plan identity, atomic
    output, and overwrite refusal.

## Validation evidence

- Focused Step-13 tests: `6 passed`.
- Full empty-root inventory: 17,452 species x 7 boundaries = 122,164 missing
  boundary records, with 17,452 parent actions and 104,712 dependent actions;
  every action remains gated on Step 12 and submission is globally false.
- Seven-species CLI dry run: plan ID `a804e6fabad7c5b2`, 49 missing boundaries,
  7 parent actions, 42 dependency-gated actions, and zero authorized
  submissions. The disposable plan was written to
  `/tmp/revwb97m2-step13-preparatory-dry-run-20260831-v2.json`.

## Intentionally deferred

Step 13 cannot yet choose the feasible production subset, size tiers,
partition/account/QOS, CPU/memory/walltime, array concurrency, retry limits,
direct/out-of-core routes, or AO/auxiliary-AO stops. It cannot render or submit
production arrays. Those actions require job `25431773` to terminate, the
terminal Step-10/12 measurement to be evaluated, and explicit Step-12 resource
sign-off.
