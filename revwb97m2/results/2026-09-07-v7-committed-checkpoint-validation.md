# Committed v7 checkpoint validation

Validated commit: `1cbe45b67ca3c0ab2de677b7018df2cccc931281`.
Worktree was clean at start. No implementation or scientific settings changed.

- Full committed suite: **100 passed in 5.30 seconds**, with dh Python and
  OMP_NUM_THREADS=1 / OPENBLAS_NUM_THREADS=1.
- Scientific configuration validator: passed, configuration scope only.
- Frozen plan source/code/Q-Chem build hash checks: passed.
- Plan and every pinned code file: byte-identical to Git HEAD.
- Separate independent readback of all five existing gateway artifacts: passed
  (48_hcn_BH76, 58_hn2_BH76, W4-17_h, Dip146_HF2+, Dip146_LiN2+).
- All 38 species: reuse dependency hashes and legacy ordinary/recovered energy,
  scalar, semilocal and grid validation passed again.
- Gateway launcher shell syntax and git diff whitespace checks: passed.

Plan SHA256 remains
`bb0da88f3ddea0ef724a6fcbf03e5b7c5224c648e71d927c9acfcdd4e0d6dffd`;
specification SHA256 remains
`32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc`.
The configuration validator still prints historical pretest-commit metadata;
the concrete commit/hash checks here supply the checkpoint evidence without
mutating the frozen specification or invalidating its existing artifacts.

The original five chemical calculations were not rerun: their tested code is
identical to the now-committed code and their saved artifacts passed fresh
readback. Authoritative full orbital-tree hashes will be checked by each new
species execution; this turn did not reread all 38 full orbital trees.

Exactly 33 species lack refreshed completion markers. Next expansion should
retain their frozen 8-CPU, 14/21-GiB, 4-hour resource classes, check live Slurm
capacity, skip the five validated completed species, and use bounded concurrency.
After all 38 pass, run the committed `v7_refresh assemble` command against
`revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json`; publication must
pass independent stoichiometric reconstruction and the fitter input contract.

This turn validates the checkpoint before expansion. No new Slurm submissions,
chemical calculations, reaction assembly, fitting, build, commit or push.
Full 20-row v7 publication and real-data ridge/grid fitting remain pending;
this is not bulk-production validation or authorization.
