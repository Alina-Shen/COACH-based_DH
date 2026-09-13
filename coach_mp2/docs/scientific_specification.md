# COACH MP2 scientific specification v1

## Contents

- [Machine-readable scientific specification](../configs/scientific_spec_v1.json)
- [Frozen step index](../configs/step_index_v1.json)
- [Source identities](../manifests/step1_sources_v1.json)
- [Storage policy](storage_layout.md)
- [Semantic validator](../scripts/validate_scientific_spec.py)

The scientific contract fixes the initial M2-total model on imported COACH UKS
orbitals at target omega=0.27 bohr^-1. It includes total frozen-core canonical
RI-UMP2, without orbital optimization in this workflow. This specification is
complete for Step 1; archive coverage, native chemistry, assembly, fitting and
execution release are later gates. No reference project's passed chemistry or
job authorization transfers. A missing source path is an explicitly deferred
runtime binding, not an unresolved scientific choice.

## Model and feature order

For each species, use one verified COACH solution for all orbital-dependent terms:

`E = E_fixed + F_SL beta_SL + c_SRHF E_SRHF + c_VV10 E_VV10 + c_PT2 (E_OS+E_SS) + c_ATM E_ATM`.

`E_fixed = E_nuclear + E_one-electron + E_Coulomb + E_full_LRHF(omega=0.27)`.

The 292 columns are exchange [0,96), same-spin correlation [96,192), opposite-spin
correlation [192,288), SR-HF 288, VV10 289, total PT2 290 and pure D4-ATM 291.
Each semilocal channel has eight u orders and twelve companion orders, flattened
as `8*companion_degree + u_degree`. This follows the reference kernel's actual
ordering; transposing coefficient grids silently would change the functional.
Selected integratedDV rows are 64/154/166 after transposing printed 96x180 to
180x96. The specification includes the actual base densities, variables,
polynomial families, gamma constants and corrections inherited from v7.

Use omega=0.27 consistently in exchange attenuation and the SR/LR-HF decomposition.
The Q-Chem input convention is OMEGA/OMEGA2=270; reference 300 constants cannot
remain in the port. Parent-energy reconstruction uses the verified actual parent
functional and is a separate gate from target double-hybrid reconstruction.
The parent's documented SR-HF fraction 0.22878980716640696 is not the fitted
model's SR-HF coefficient or the paired algorithmic initial coefficient 0.15.

VV10 uses b=5.5, C=0.01, on fixed SG-1. Pure D4-ATM uses
s6=s8=0, s9=1, a1=0.215, a2=5.8 and alp=16, with a separate linear scale.
RI-UMP2 stores both spin contributions and fits their sum. Native validation
must establish archive MO/density/orbital-energy identity, frozen-core and
auxiliary-basis conventions; zero requested SCF cycles alone is insufficient.

## C0 constraints and objective

Use binary selection z with sum(z)<=K and -25 z_j<=beta_j<=25 z_j.
All four scalar slots are mandatory and counted; the SR-HF coefficient may
still be zero. SR-HF is bounded [0,1]; VV10/PT2/ATM are independently bounded
[1e-8,0.99999999]. No scalar unit-sum constraint is imposed. The exchange UEG
condition is `gx(0,0)+c_SRHF=1`, which in this polynomial ordering is
`sum_j beta_exchange[8*j]*P_j(0) + beta[288] = 1`.
One-electron and sampled enhancement constraints are deferred; dense factor
and boundary-saturation diagnostics remain required.

The objective is full weighted SSE plus `1e-10*sum(beta^2)` over all 292
coefficients. Weights multiply squared residuals; they are not squared a second
time. Use the current expanded quadratic representation with big-M selection,
and independently recompute acceptance in original residual space to expose
cancellation/roundoff. The ridge is equivalent to COACH's half-SSE convention
with 5e-11 ridge. Preserve the pinned numerical audit and solver tolerances.

## Data, numerical grids and selection

The named GSCDB root is read-only. Its DatasetEval/Datasets/Standard_errors
tables are byte-identical to the pinned reference versions (8448/142/137 rows).
This table check does not establish the full 17452-species role union or any
COACH orbital coverage. Step 3 binds and verifies full role/weight manifests;
Step 4 validates exact input/basis/ECP identities. No missing species may be
silently excluded or regenerated using another parent.

Retain 1498 fitting entries/2799 species and the existing overlapping GSCDB137
model-selection roles. Retain final-only SC74/OEEFD/L14/vL11/GDB_W1-F12;
OPT remains outside initial fixed-geometry energies. Preserve the original
COACH D4 damping development exposure to L14/vL11 in reporting.

Unpruned grids: 250974 reference, 99590 practical, 75302 diagnostic. Pass 1 has
no grid inequalities. Audit all 138 discoveries, union their top 100 absolute
99590-difference rows, then add up to 200 highest-L1 rows from the remainder.
Freeze one common row set. Pass 2 enforces only those rows at 0.015 kcal/mol
with internal factor 0.999. Report full-grid violations for user review; do not
silently substitute an all-row rejection rule. Fixed SG-1 VV10 has zero grid
difference with explicit provenance, as do grid-independent HF/PT2/ATM.

Use all integer K14–82, two discovery fits and six selected fits per K (552
solves). Preserve reference start/noise mapping and budgets, with original/noisy
starts from each original source, not preceding-repeat restarts. The common
seed is an initialization only, must be audited on COACH matrices, and does
not import a reference result as a COACH candidate. Keep full-precision readback,
exact source hashes and honest finite-time incumbent/gap reporting.

Select eligible candidates using the inherited dataset-specific NER protocol,
category/overall means and scientific diagnostics, with final user review.
Existing near-tie/category tradeoff details remain deferred and do not block
initial fitting. Freeze model/K before using final assessment results.

## Optional future omega scan

Initial omega=0.27 is fixed, not an initial guess. A discrete outer scan with
inner refits is deferred until functional-design choices are settled. The
future grid, budget and detailed schedule remain unset. Each point needs
consistent exchange/Nofit/reaction/grid features. A scan does not imply new
parent-orbital updates. The 552-solve budget is for one fixed-omega setting.

## Frozen tracking and execution boundaries

The 18 IDs are permanent: never renumber or reuse them. Before freezing, Step 5
was renamed for archive import, Step 9 clarified implementation, and Step 16
renamed for final selection/model freeze. Step 7 is optional and nonblocking.
IDs are tracking identifiers, not a strict execution order: Step 13/14 pilots
can validate assembly/fitting before Step 12 bulk completion. Later full-domain
assembly and campaign completion still require production outputs.

The hash freeze covers the scientific specification, index, reviewed sources,
validator, tests and these scientific/storage documents. Mutable progress and
README files are outside that immutable payload. Scientific amendments require
a new version and affected validation; runtime manifests bind concrete archives
and builds separately. If a runtime discovery contradicts v1, stop and amend it.
Hash freezing does not mean a Git commit has been made.

Recheck Step 1 with:

```bash
python3.9 -B coach_mp2/scripts/validate_scientific_spec.py
python3.9 -B -m unittest discover -s coach_mp2/tests -p 'test_*.py' -v
```

Only the one-time builder uses PyYAML in the existing dh environment. The
validator/tests use the standard library. Use -B so reference Python package
directories receive no bytecode writes. No Gurobi/license or Q-Chem process is
needed for Step 1. Future execution must fit the globally shared two WLS
sessions and undergo the inherited resource/submission gates.
