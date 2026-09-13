# Step 9 — C0 physical and numerical constraints complete

## Work performed

1. Read the frozen scientific specification and the current revwb97m2 `mio.py`, `selective_grid_v1.py`, and `fit_spec.py`. Recorded source hashes. Implemented a project-owned solver-neutral interface; no Gurobi import, license session, optimization, or backend decision was required.
2. Implemented sparse linear constraints in variable order `[292 coefficients, 292 binary support indicators]`. These encode ±25 big-M linkage, coefficient bounds, mandatory selection of all four scalar slots, and `sum(z) <= K`. Zero SR-HF remains allowed while its selected slot counts toward K. VV10, total PT2 and ATM each retain independent bounds [1e-8, 0.99999999]; no extra scalar equalities were added.
3. Implemented the correct UEG equation: `sum_w P_w(0) * beta_X[8*w] + c_SRHF = 1`. This includes nonconstant even Legendre terms; it is not just the constant exchange coefficient plus SR-HF. Verified exact agreement with revwb97m2's R2 vector and tested a nonconstant contribution.
4. Implemented discovery without grid constraints and selected-pass constraints using only explicitly supplied row identities. The optimization-side limit is `0.999 * 0.015 / 627.50947406` hartree; the independent public audit uses `0.015 / 627.50947406` with zero added grid slack. Full-grid violations remain review diagnostics rather than automatic rejection.
5. Implemented the mirrored row-selection rule: union of each candidate's top 100 absolute predicted errors, followed by 200 largest L1 rows among those remaining. Preserve duplicate candidates, deduplicate rows, and match reversed NumPy argsort tie ordering. Tested against the actual reference function with 138 synthetic candidate records and tied rows. Actual production row identities cannot be frozen until the real validated discoveries exist in Step15.
6. Added independent full-precision coefficient audits for finite values, binary support, K, mandatory slots, bounds, unselected zeros, UEG and selected-grid acceptance. Kept reference readback tolerances (UEG 1e-10, semilocal bound 1e-8, scalar/unselected-zero 1e-9) distinct from the exact mathematical matrix bounds.
7. Added 101x101 dense polynomial enhancement-factor sampling over u=[0,1], companion=[-1,1], using the correct monomial/Legendre families. Reports extrema and coordinates; imposes neither sampled enhancement bounds nor the disabled one-electron bound. These are sampled polynomial diagnostics, not a proof of global bounds or full density-dependent factor limits.
8. Reverified the Step8 frozen evidence and published feature hashes. Exercised the constraints on the frozen simple algorithmic starting vector and both native molecular grid differences. Exported pilot sparse matrices, bounds, integrality flags and UEG row; no fitted coefficients were generated.
9. Ran eight targeted tests covering UEG/reference parity, matrix feasibility and linkage rejection, zero-SRHF slot counting, independent scalar bounds, grid safety margin and zero public slack, selected-only acceptance, exact row-selection parity, malformed input rejection, and independent polynomial checks. All pass.
10. Published the constraint contract, validation report and frozen hashes. Updated progress, README, the project plan table, STATUS and a dated project-note chapter. Frozen step numbering is unchanged; next Step10.

## Numerical pilot evidence

The frozen simple seed has zero UEG residual and passes C0. Its maximum absolute molecular grid differences are 1.94238e-7 hartree (99590) and 1.04444e-7 hartree (75302), both below the internal limit. These two molecular rows are a gateway exercise, not the later full reaction-row selection. The simple seed's sampled exchange polynomial ranges from 0.85 to 1.85; both correlation polynomials equal 1.

Discovery has 585 inequality rows plus one equality over 584 variables; the two-row selected pilot has 589 inequalities plus one equality. Variable bounds and integrality are exported separately. Backend binding and actual solves remain Step14 work, at which point solver choice is required.

## Artifacts and remaining scope

- [Implementation](../scripts/step9_constraints.py)
- [Constraint contract](../configs/step9_constraint_contract_v1.json)
- [Validation](step9_validation.json) and [tests](step9_tests.log)
- [Frozen hashes](../manifests/step9_freeze_v1.json)
- [Dense factor pilot](step9_constraint_pilot_v1/simple_seed_dense_factors.json)

All new scripts/settings/results are under `/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2`; only authorized project notes were written outside that root. No Q-Chem jobs or new orbital calculations were necessary. Source archives and reference projects remain read-only. Carbon F01, missing GDB9 F02, omega=0.27 and deferred optional Step7 remain unchanged.
