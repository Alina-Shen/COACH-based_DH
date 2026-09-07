# v7 refresh: unit/configuration tests and bounded chemical gateways

## Implementation identity and unit checks

User checkpoint: `dc6a2f83f893f8fec165658aaadedd0a9dba1377` (clean at start).
The committed full suite passed: 99 tests in 6.01 s. Configuration validation
passed for spec SHA256
`32c64b5d4cec1641c1b77e094e776a0aaa62fb20a9dd101c7736dfd92ac942fc`.
That validator proves configuration consistency, not chemical/solver readiness.

The first plan freeze exposed a parser-dispatch bug for ordinary species
`11_Reactant1_EIE22`: the recovery parser gave -204.7547746795 Ha instead of
the original ordinary parser's -204.75477468260002 Ha. The 3.100012690993026e-9
Ha difference came from nuclear-energy output precision. `v7_refresh.py` now
uses the original ordinary parser for ordinary artifacts and retains the
field-aware recovery parser for recovered artifacts. No tolerance was relaxed,
no old artifact changed, and no scientific parameter changed. A regression
test covers both branches. The full corrected suite passed: 100 tests in
4.95 s; configuration validation and `git diff --check` also passed.
These corrective edits are UNCOMMITTED; tests use their explicitly frozen
file hashes, not a claim that the original commit alone passed plan preparation.
A follow-up user commit and affected reruns remain required before expansion.

## Frozen plan and bounded launch

Successful freeze independently revalidated the existing 38 species and
20-reaction baseline. It pins specification, code, source/reuse artifacts,
orbital-tree identities and Q-Chem executable/library hashes. Plan:
`revwb97m2/manifests/reaction_features/v7_refresh_plan_v1.json`; SHA256
`bb0da88f3ddea0ef724a6fcbf03e5b7c5224c648e71d927c9acfcdd4e0d6dffd`.
New output root:
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/step14/v7_vv10_refresh_v1`.
Freezing 38 cases does NOT authorize submitting all 38.

The partition skill guided live capacity/association checks. mhg had idle
CPU nodes, adequate physical memory, and the mhg/normal association; lr8 was
also viable, whereas cm1 had no idle nodes in the snapshot. Retained mhg,
8 CPUs, 14 GiB and 4 h per case, limited to two concurrent tasks. Shell syntax
and `sbatch --test-only` checks passed. New launcher:
`revwb97m2/slurm/run_v7_refresh_gateway_v1.sh`.

Submitted array **25675585**, exactly five tasks:

| Task | Species | Coverage from authoritative input |
|---|---|---|
| 0 | 48_hcn_BH76 | ordinary neutral singlet |
| 1 | 58_hn2_BH76 | ordinary neutral doublet |
| 2 | W4-17_h | one-electron doublet, approved zero PT2 |
| 3 | Dip146_HF2+ | recovered singlet with electric field |
| 4 | Dip146_LiN2+ | recovered triplet with electric field/spin recovery |

All use saved omegaB97M-V orbitals with zero SCF and b=5.5 VV10. Only vector
column 289 is refreshed; the other 291 columns, fixed energies and grid
differences must remain unchanged. Existing total-SS/OS PT2 recovery is
revalidated/reused, not recalculated. Historical sources remain read-only.
These are cohort representatives, not the separate historical h2o/NH2rad jobs.

## Final chemical results

All five array tasks COMPLETED with exit 0:0. Elapsed times by index:
27, 27, 18, 21, 21 seconds. Batch MaxRSS respectively:
1272004, 1233916, 477872, 857528, 940516 KiB (all below 14 GiB).
Every species has REFRESH_COMPLETE. A separate post-job call to
`validate_species` passed for all five, including artifact hashes, independent
output extraction, saved-orbital evidence, archive identity and unchanged
reused components. Both ordinary and recovered fixed-energy paths passed.

| Species | Old VV10 (Ha), b=10 | New VV10 (Ha), b=5.5 |
|---|---:|---:|
| 48_hcn_BH76 | 0.0286226338 | 0.0657953960 |
| 58_hn2_BH76 | 0.0306480451 | 0.0704059443 |
| W4-17_h | 0.0021611375 | 0.0051304220 |
| Dip146_HF2+ | 0.0210601122 | 0.0489903600 |
| Dip146_LiN2+ | 0.0209062196 | 0.0487239480 |

Hydrogen PT2 remains exactly zero. Raw outputs confirm b=5.50, C=0.0100,
MAX_SCF_CYCLES=0 and two saved-orbital reads. No fitting coefficient is implied
by these raw VV10 values. The remaining 33 cohort species were not launched.

## Remaining gates

Do not interpret these gateways as full 20-reaction publication, a real-data
v7 fit, production readiness or validation of all 1,498 fitting rows. After
review/commit, validate the committed identity again, then approve the remaining
bounded cohort refresh and independent assembly. Next comes a bounded real-data
ridge/grid fit and resource review before broader feature generation. The
previous corrected synthetic integration harness still needs a fresh rerun.
No bulk fitting/generation, new SCF/PT2, Q-Chem rebuild, commit or push occurred.
