# Step 4: locked data roles and non-orbital input metadata

## Decision

Data-role policy v2 was frozen before fitting. It follows the COACH protocol
rather than inventing a random validation split:

- **Coefficient fitting:** the exact 1,498 final/Cycle-2 entries and objective
  weights already validated from updated SI Table 2.
- **Model selection:** dataset-specific errors and normalized error ratios over
  all 137 GSCDB137 datasets (8,377 reactions). This is deliberately
  COACH-faithful and overlaps the fitting data, so it is not described as an
  independent validation set.
- **Overfitting diagnostic:** mean NER over `AE11`, `MB08-165`, and
  `MB16-43` (219 reactions). `MB16-43` also contributes 43 fitting reactions;
  this source-protocol overlap is explicit and the diagnostic is not claimed
  to be fully independent.
- **Final energy assessment:** the appended `SC74` and `OEEFD` groups (71
  reactions), BigNC (`L14`/`vL11`, 25 reactions), and GDB9-W1-F12 (3,366
  reactions). GDB9-W1-F12 is the genuinely untouched COACH robustness test.
  COACH tuned D4-ATM on BigNC, so BigNC is untouched here only if no
  `revwb97m2` parameter is selected from it. OPT is a separate geometry track.

GSCDB137 results reported after freezing remain a development-domain
assessment, not an untouched test result. A full-GSCDB refit is forbidden
without a new scientific-specification version because it would replace the
adopted Cycle-2 fitting objective.

## Exact species requirements

| Role | Reactions | Unique species |
|---|---:|---:|
| Coefficient fitting | 1,498 | 2,799 |
| GSCDB137 model selection | 8,377 | 13,907 |
| Overfitting diagnostic | 219 | 249 |
| Appended `SC74`/`OEEFD` final assessment | 71 | 127 |
| BigNC final assessment | 25 | 75 |
| GDB9-W1-F12 final assessment | 3,366 | 3,371 |
| Combined final energy assessment | 3,462 | 3,573 |

Because the locked model-selection role covers all GSCDB137 datasets, future
production generation genuinely requires all 13,907 core species. This is a
consequence of the recorded scientific policy, not an accidental generate-all
default.

## Geometry and basis authority

The verified immutable Q-Chem snapshot at
`/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/authoritative_inputs/qchem/gscdb137_v1`
is the authority for geometry, charge, multiplicity, orbital-basis definition,
auxiliary-basis definition, and ECP definition for GSCDB137, `SC74`, and
`OEEFD`. The builder verified the published manifest SHA-256
`75db32bdd10efbcefa8281a05a1d56ff3205b72f2aabee277622e0c27b3e64cf`
and rehashed every one of the 14,006 byte-identical `input0` files.

The derived metadata records exact input, `$molecule`, geometry-payload,
`$basis`, `$aux_basis`, and `$ecp` hashes. Independent validation reparsed all
14,006 inputs and found 593 embedded basis sections, one embedded auxiliary
basis section, and 97 ECP sections. It also matched every charge,
multiplicity, and atom count to the pinned species manifest.

No Q-Chem orbital file, `qarchive.h5`, or scratch orbital directory was read or
used. A pinned snapshot of official GSCDB AdditionalSets commit
`8f2c7e5f683824c79c7035714de215ec22d0f04a` now supplies 75 BigNC, 3,371
GDB9-W1-F12, and 206 OPT Q-Chem inputs. All 3,652 specify `UNRESTRICTED True`.
The BigNC parser also preserves 2,771 counterpoise ghost centers across 50
monomer inputs.

## Artifacts and validation

- Policy: `revwb97m2/manifests/data_roles/revwb97m2_data_roles_v2.yaml`
- Dataset/reaction/species roles: `revwb97m2/manifests/data_roles/{dataset_roles,reaction_roles,species_roles}.csv`
- Parsed input metadata: `revwb97m2/manifests/data_roles/qchem_input_metadata.csv`
- Provenance and independent validation: `revwb97m2/manifests/data_roles/provenance.json` and `validation.json`
- Deterministic builder and validator: `revwb97m2/scripts/build_data_role_manifests.py` and `validate_data_role_manifests.py`

`validate_data_role_manifests.py` passed every role, identity, source-hash,
input-reparse, and output-hash check. The full scientific-specification
validator also passes with the locked role artifacts and geometry-authority
policy integrated into specification v3.
