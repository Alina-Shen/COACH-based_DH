# Step 11 published omegaB97M(2) source audit

The uploaded 2018 paper is now the hash-pinned source for the displayed
omegaB97M(2) coefficients and the conventions it states explicitly. It is not
treated as authority for details it delegates or omits.

## Established from the paper

- The method is xDH on fixed self-consistent omegaB97M-V orbitals.
- Exchange is repartitioned into semilocal short-range exchange, scaled
  short-range HF, and full long-range HF.
- Correlation contains semilocal same/opposite-spin terms, scaled VV10, and
  scaled canonical PT2.
- `omega=0.3`, VV10 `b=10,C=0.01`, def2-QZVPPD without counterpoise, frozen-
  core RI-MP2, and the paper's fitting/application grids are explicit.
- Table II provides 16 displayed nonzero coefficients representing 14
  independent parameters after `c_x+c_x00=1` and `c_PT2+c_VV10=1`.

## Implemented safely

`revwb97m2/published_wb97m2.py` freezes the printed coefficients and assembles
an R0 energy only from explicitly named, already evaluated published-definition
components. It cannot accept the R2 291-vector as though it were the original
functional. Tests cover coefficient signs and constraints, named assembly,
and refusal of missing/non-finite components.

## Completed gate

The uploaded omegaB97M-V paper and implementation SI resolved the exact
semilocal definitions and nonlinear values. The R0 density evaluator reproduces
a matched native Q-Chem H2O energy within `7.46e-9 Eh` and H2 dissociation within
`1.61e-6 kcal/mol`; the six-case representative fixture array also completed.
The immutable comparison schema now separates published `R0`, the original
78-feature family refitted by COACH as `R1`, and the expanded 291-feature COACH
model as `R2`. Step 11 is complete with no unresolved convention bug.
