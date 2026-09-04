# Production R1-78 and R2-291 feature path

The production semilocal stage now evaluates the frozen R1 and R2 candidate
spaces from the same AO values and alpha/beta MGGA density tensors in every
grid block. It performs one traversal for each frozen grid and publishes:

- `r1_semilocal_features_75_<grid>.npy`, ordered by channel and then
  `w` degree outermost / `u` degree innermost from `00` through `44`;
- `r2_semilocal_features_288_<grid>.npy`, preserving the frozen selected-row
  `(64,154,166)` ordering;
- the legacy `selected_features_<grid>.npy` R2 matrix for compatibility.

R1 uses the original omegaB97M(2) nonlinear definitions (`gamma_x=0.004`,
`gamma_ss=0.2`, `gamma_os=0.006`); R2 keeps the project-frozen integratedDV
definitions (`gamma_x=0.004`, `gamma_ss=0.01`, `gamma_os=0.006`). A single
shared SR-HF/VV10/total frozen-core RI-UMP2 triple is appended to produce the
final 78- and 291-element vectors. Publication is atomic and refuses to
overwrite an existing assembly.

Implementation:

- `revwb97m2/published_wb97m2.py`: full 75-feature R1 block evaluator while
  retaining the independent 13-term published-R0 interface.
- `revwb97m2/semilocal_features.py`: shared R1/R2 density/grid traversal,
  schema-2 dual-space artifacts, hashes, grid differences, and validation;
  schema-1 R2 artifacts remain independently validatable.
- `revwb97m2/scalar_features.py`: shared-scalar R1/R2 vector assembly and
  atomic species assembly publication.
- `revwb97m2/scripts/run_r1_r2_assembly.py`: command-line assembly entry point.

Validation evidence:

- all `revwb97m2/tests` tests pass: `24 passed`;
- real `h2o_SW49` archived-v3 checkpoint, unpruned `75,302` grid: 67,952
  points, finite R1 shape `(3,25)` and R2 shape `(3,96)`;
- R1 array hash: `ee41275a7645346c5ca113714918bbf2e944cf18f79e813512b74009f4dffebc`;
- R2 array hash: `85c5527eacaa84ed02e84f9488d12e3c2a90a809e7c4212a131187799aeedd5f`;
- the R2 hash exactly equals the pre-existing Step-8 checkpoint identity
  feature hash, demonstrating no R2 numerical regression.

The full local three-grid H2O diagnostic was stopped after crossing ten
minutes; it did not fail numerically. Production reference-grid work remains
subject to Step 12 resource routing. Job `25431773` was still running at
`09:09:15 / 12:00:00` when this record was written.
