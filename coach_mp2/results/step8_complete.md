# Step 8 — native named-feature gateway

Status: COMPLETE for the frozen Step8 pilot scope. Validation job 25833319 passed; build 25832707 and native job 25832918 completed successfully. Next required step: 9.

## Work performed

1. Inspected the revwb97m2 feature implementation and the separate original COACH Q-Chem build. Ported only feature export/diagnostic code into project-owned source files, preserving COACH functional availability and the Step5 NoSCF orientation bypass. Built an isolated executable and `libks.so`; shared Q-Chem files remain read-only.
2. Set feature omega to 0.27, retaining gammaX=0.004, gammaSS=0.01, gammaOS=0.006 and native row indices 64/154/166. Recorded source/compiler/link hashes, build commands and runtime library selection.
3. Prepared twelve isolated fixed-orbital pilot calculations: water and open-shell carbon, each on grids 250974/99590/75302 plus SR-HF+VV10, full-HF and LR-HF component calculations. Verified scratch staging against immutable Step5 import receipts. No SCF optimization or source archive modification was performed.
4. Implemented strict native matrix and diagnostic-density parsers plus independent full-matrix and selected-row Python references adapted from revwb97m2 at omega=0.27. Native full matrices have 96x180 entries; stored matrices are transposed, with selected rows flattened into 288 named semilocal columns.
5. Implemented checks for normal native termination, fixed-MO markers, exact saved MO bytes, density reconstruction, all six native/reference grid matrices, HF range separation and parent/fixed-energy identities. The actual native COACH SR-HF coefficient 0.22878981 is used only for parent reconstruction, not imposed on the future fit.
6. Reused hash-frozen Step6 canonical frozen-core RI-UMP2 OS/SS doubles, excluding singles. Kept the approved carbon auxiliary basis and explicit F01 accuracy deferral. Evaluated geometry-only D4-ATM and compared its nonzero ISOL24 value with existing native evidence.
7. Prepared atomic publication of six 292-column pilot vectors and four coarse-minus-reference grid-difference vectors. Scalar columns are SRHF, VV10, total PT2 doubles and D4-ATM; fixed energy contains nuclear, one-electron, Coulomb and full LR-HF. Scalar grid differences are zero because HF/PT2/ATM are grid independent and VV10 uses fixed SG-1.
8. Added rejection tests for truncated/nonfinite matrices, damaged density dumps, row mapping and accidental omega=0.30. Three tests pass. Validation job 25833049 exposed an incorrect Python function import, corrected before rerunning; native calculations were unaffected.

## Scope and follow-up

This is a two-species native feature gateway, not full-domain production. Step7 remains optional/deferred. Step9 implements physical/numerical constraints and is next after this gate passes. Solver selection remains open and will be required before backend-dependent work, expected Step14. Carbon F01 and GDB9 final-assessment orbital F02 remain unchanged.

Code/settings/results are under `/clusterfs/mhg-data/yaoshen/coach-based_dh/coach_mp2`. Build, native outputs, diagnostic dumps and published vectors are under `/clusterfs/mhg-data/yaoshen/coach-based_dh_data/coach_mp2` (`build/step8_features_v1` and `step8_v1`). Working scratch is `/clusterfs/mhg-data/yaoshen/scf_read/coach_mp2/step8_v1`. Original imported orbitals remain in `step5_import_v1/species`; `/global/scratch/users/jsliang/COACH3` and BigNC sources remain read-only.

## Validation results

All twelve native cases pass fixed-MO and reconstructed-density checks. All six full-matrix and selected-row comparisons pass (largest full-matrix absolute difference 8.882e-16). Parent reconstruction maximum residual is 4.4293e-9 hartree, below 1e-8. The full-HF = SR-HF + LR-HF split residual is at most 2.0e-10 hartree. Nonzero ISOL24 D4-ATM native/reference difference is 2.1641817474931692e-11 hartree. Three rejection/kernel tests pass. Six feature vectors and four grid-difference vectors were atomically published.

Evidence: [numerical audit](step8_validation.json), [tests](step8_tests.log), [runtime authority](../configs/step8_runtime_authority_v1.json), [frozen hashes](../manifests/step8_freeze_v1.json). This does not remove the explicit carbon RI accuracy deferral.
