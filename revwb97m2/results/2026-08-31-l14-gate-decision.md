# L14 high-cost gateway and D4-ATM scope decision

The frozen revwb97m2 scientific specification explicitly sets
`double_hybrid_energy.dispersion_policy.include_coach_d4_atm: false`. The model
is an omegaB97M(2)-style double hybrid whose fitted terms are semilocal
short-range exchange, same- and opposite-spin semilocal correlation,
short-range HF exchange, VV10 (`b=10,C=0.01`), and total frozen-core RI-MP2.

D4-ATM belongs to the final COACH hybrid, not published omegaB97M(2). Adding it
here would change the R0/R1/R2 model comparison rather than merely reuse the
COACH fitting workflow. Original COACH optimized its D4-ATM parameters on L14
and vL11; fitting any revwb97m2 model or dispersion parameter on those data
would therefore also remove BigNC's locked untouched final-assessment role.

`L14_GGG_monB` was selected for Step 10 only as an upper-tail counterpoise-
ghost feasibility measurement. It is not coefficient-fitting, model-selection,
or overfitting-diagnostic data. The project decision is therefore:

- allow job `25431773` to reach its declared terminal state without modifying
  it;
- record a timeout or parent nonconvergence as valid Step-12 feasibility
  evidence rather than require this species to pass;
- proceed toward R1/R2 fitting without using or waiting for this species;
- keep production routing and resource authorization subject to Step-12
  sign-off;
- if the complete post-freeze BigNC assessment is later desired, make one
  engineered 72-hour `mhg` parent retry that resumes the preserved checkpoint,
  uses a validated robust but scientifically equivalent SCF strategy, and
  separates parent, grids, VV10, and RI-MP2 into restartable stages.

At the decision check, job `25431773` remained `RUNNING` at `08:13:56` of its
12-hour limit. No retry was submitted and no live artifact was modified.
