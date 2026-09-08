# Completed smaller canaries: fixed-energy parser failure blocks expansion

User request: validate25680435/436; submit two large canaries only if OK.
Commit0e21ec9 verified; initial worktree clean. No scientific code changed,
no jobs submitted and no tolerance relaxed.

| Job | Species | Scheduler outcome | Elapsed | Batch MaxRSS |
|---|---|---|---|---|
|25680435|HR46_toluene|COMPLETED0:0; independent completed-source reuse audit PASS|7:16:59|17523800K (~16.71GiB)|
|25680436|3019_41UracilPentane090_dim_S66x8|FAILED1:0 at fixed HF identity check|11:42:49|44647036K (~42.58GiB)|

All six dimer native stages validate against frozen identities/input/output
hashes, working archive, MO-read/electron/spin and normal-termination checks.
All three Q4/IDV artifacts pass. PT2 component and scaled identities pass.
Failure occurs before species.json/ready publication, not from OOM or failed
Q-Chem execution. The existing D4-only recovery was attempted but safely refused
the missing species.json; no recovery directory/evidence was created.

## Exact cause

`qchem_scalar_features.py:170` `_last_float` appends matches by pattern order,
then returns the final appended value, not the last occurrence in the output.
`parse_qchem_fixed_energy_output` at line251 supplies the final abbreviated
`Nuclear Repu.` spelling first and the earlier `Nuclear Repulsion` spelling
second, so the earlier fallback overrides the final component value.

Raw fixed output:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/species/v7_canary_v1/3019_41UracilPentane090_dim_S66x8/stages/fixed/qchem.out`.

- Line224 earlier nuclear value:859.91310676Ha.
- Line265 final nuclear breakdown:859.9131067110Ha.
- Current parsed reconstruction error:5.180038442631485e-8Ha, exceeds2e-8Ha.
- Reconstructing from final breakdown gives-608.9860231872Ha, versus printed
  SCF-608.98602319Ha:2.8e-9Ha error, within unchanged tolerance.
- Nuclear difference is4.9e-8Ha. It should not be dismissed as solely ordinary
  last-digit rounding; the proven issue is selecting a different print record.

Recommendation requiring user direction: select the final energy-breakdown
nuclear record explicitly (retain fallback only when needed), add both-label
regressions and recheck prior cases, then recover dimer publication from retained
native data under a versioned contract. No Q-Chem rerun appears necessary from
current evidence, but recovery must pass all independent checks. Do not globally
change the shared helper without reviewing its other callers; do not loosen
the2e-8 threshold. A shared-source change requires new code/plan pins and a user
commit before large launches; preserve original plans and raw failure history.

## Resource review, not release

Partition skill helper was unavailable; used direct Slurm queries. lr8 is UP,
773569MiB/node and128CPU; user has lr_mhg2/mhg2_lr8_normal association. Both
227GiB and557GiB frozen requests fit physical node memory. No memory changed.
Most nodes allocated, some mixed; no start-time promise. Final scheduling/QOS
limits and duplicate-job checks must be refreshed at actual submission.

Four of five smaller cases now have accepted evidence (H, S22, N-methylacetamide,
toluene), with previous recovery evidence retained. Dimer remains unaccepted.
BSR36_c4 and MOR16_ed33 not submitted because the user's success condition is
not yet met. Existing all-seven first16/pilot release gate also remains closed.
