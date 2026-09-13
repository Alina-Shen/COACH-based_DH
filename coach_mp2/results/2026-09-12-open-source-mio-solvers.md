# Open-source MIO alternatives for COACH MP2

## Contents

- [Frozen mathematical specification](../configs/scientific_spec_v1.json)
- [New orbital source locations](../manifests/orbital_source_locations_v1.json)

Research date: 2026-09-12. Primary project documentation and repositories were
checked. This is a capability assessment and proposed benchmark, not a measured
solver ranking. No installation, solver execution or backend change occurred.

## Problem to preserve

Our model is a convex mixed-integer quadratic program (MIQP): 292 continuous
coefficients and 292 binary selection slots before presolve, four mandatory.
The objective is weighted SSE plus 1e-10 ridge; constraints include coefficient
bounds, big-M linkage, sum(z)<=K, UEG equality and selected linear grid limits.
Positive weights make A'WA positive semidefinite; positive ridge makes the
coefficient block positive definite mathematically. Binary selection still
makes the full problem combinatorial. Polynomial features are precomputed;
their nonlinear density dependence is not a nonlinear optimizer variable here.

Replacing the solver must preserve weights, ridge, K counting, scalar bounds,
UEG, grid rows and independent acceptance. Convex MINLP or mixed-integer conic
solvers can express the same problem through exact reformulation. A MILP-only
solver or ordinary continuous QP solver is not a direct substitute.

## Candidate comparison

The priorities and practical limitations below are project-specific judgments,
not claims of benchmark superiority.

| Candidate / open stack | Why it can work and advantages | Limitations for our project | Priority |
|---|---|---|---|
| [SCIP](https://www.scipopt.org/) + [PySCIPOpt](https://github.com/scipopt/PySCIPOpt) + open LP backend (e.g. SoPlex) | MIQP/MINLP support, Python interface, incumbent/bound reporting; broad integer-constraint support. SCIP >=8.0.3 is Apache-2.0; PySCIPOpt is MIT. | Requires a new adapter and tolerance/start/readback mapping. Quadratic objective uses an auxiliary epigraph in PySCIPOpt. Performance on our dense, correlated features is unmeasured. Ensure installed dependency stack is open. | First pilot. |
| [Pajarito](https://github.com/jump-dev/Pajarito.jl) + HiGHS + [Hypatia](https://github.com/jump-dev/Hypatia.jl/blob/master/LICENSE.md) | Mixed-integer convex conic optimization; exact squared-norm epigraph fits our objective. Published algorithm and an officially documented all-open example. Licenses: MPL-2.0/MIT/MIT. | Julia/JuMP port and conic reformulation; performance depends on both subsolvers. Must audit returned feasibility independently. | Strong independent second formulation. |
| [MindtPy](https://pyomo.readthedocs.io/en/stable/explanation/solvers/mindtpy.html) ([Pyomo license](https://github.com/Pyomo/pyomo/blob/main/LICENSE.md)) + HiGHS or Cbc + Ipopt | Python-native decomposition toolbox with convex MINLP outer approximation; suitable for convex quadratic epigraph. Pyomo is BSD; open subsolvers avoid proprietary sessions. | Additional master/NLP orchestration. Keep quadratic terms out of the MILP master (`quadratic_strategy=0`); some single-tree/pool features depend on commercial solvers. | Python-focused alternative. |
| [Bonmin](https://coin-or.github.io/Bonmin/Intro.html) ([license](https://github.com/coin-or/Bonmin)) + Cbc + Ipopt | Established convex MINLP methods (branch-and-bound, OA, hybrid); documented exact algorithms for convex models. Bonmin is EPL-1.0. | Generic NLP subproblems may be less efficient than exploiting QP structure; build/interface and strict-tolerance behavior need testing. No measured performance claim here. | Baseline comparator. |
| [SHOT](https://github.com/coin-or/SHOT) + Cbc + Ipopt | Convex MINLP/MI(QC)QP via supporting hyperplanes; supports open Cbc/Ipopt stack; SHOT is EPL-2.0. | Requires subsolver configuration and another adapter. Results obtained with Gurobi/CPLEX backends would not measure the all-open stack. | Additional OA comparator. |
| [Juniper](https://github.com/lanl-ansi/Juniper.jl) + Ipopt (optionally HiGHS) | MIT Julia MINLP heuristic; potentially useful for candidate generation. | Its documentation disclaims guaranteed global optimality. Not the preferred replacement for audited lower-bound/gap evidence. | Heuristic supplement only. |

## Exact reformulations and numerical checks

For SCIP introduce a continuous t and minimize t subject to
`sum_k w_k*(A_k@beta-y_k)^2 + 1e-10*sum_j beta_j^2 <= t`, alongside the original
linear/binary constraints. Use the convex inequality, not equality to a quadratic.
This is the documented epigraph technique; it does not approximate squared error.
[PySCIPOpt nonlinear-objective documentation](https://pyscipopt.readthedocs.io/en/stable/tutorials/expressions.html)

For a conic stack define `r = [sqrt(W)*(A beta-y); sqrt(1e-10)*beta]` and impose
`(t,1/2,r)` in a rotated second-order cone, so `t >= ||r||^2`; minimize t.
This is our algebraic derivation of an equivalent model, not a completed port.
Retain original residual-space audits rather than judging only an expanded
quadratic value. Include the objective constant in comparisons: dropping it
preserves minimizers but changes relative gap denominators.

Each backend must map status/dual bound/incumbent correctly and satisfy the
project's scientific tolerances. Default solver tolerances are not interchangeable;
none of these tools guarantees completion of a hard MIQP within a two-hour cap.
Equivalent mathematical models need not produce identical finite-time supports.

## Tools not sufficient alone

HiGHS supports MILP and continuous convex QP, but its documented support matrix
does not include MIQP. It remains useful as the MILP master inside an OA/conic
stack. Cbc/GLPK are likewise not the recommended direct route for this quadratic
model. Ipopt, OSQP and Clarabel alone do not supply the required integer search.
Pyomo, JuMP and CVXPY are modeling layers; selecting one does not itself remove
the backend dependency. [JuMP supported-solver matrix](https://jump.dev/JuMP.jl/stable/installation/)

CP-SAT requires integer modeling; discretizing our continuous coefficients would
change the fitted model and may conflict with stringent scientific tolerances.
It is not a like-for-like replacement. [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver)

## Recommendation and review reproducibility

First implement a separate SCIP adapter as a benchmark option, preserving frozen
v1/Gurobi provenance. Compare with Gurobi on fixed-support QP controls, small
known-optimum MIO examples, and representative K14/middle/K82 full-training cases
with and without the same selected grid rows. Use identical matrices, starts,
constraints and budgets; record recomputed objective, support, bound/gap, time,
RAM, failures and full-grid diagnostics. Test independent-fit throughput under
a fixed total CPU/RAM allocation, not just per-solve time. No performance estimate
is established until these measurements exist. Pajarito is the next candidate
if an independent conic formulation is useful; MindtPy avoids a Julia port.

An all-open fitting stack avoids the user's two-session Gurobi WLS bottleneck;
Slurm/global task limits, CPU/RAM and solver scaling still constrain concurrency.
Use open dependencies throughout (including the LP/NLP linear-algebra backend),
record exact versions/build flags, and retain notices. Record the full open dependency stack in the reproduction environment.

For reviewers, release feature/target/weight matrices and row/column IDs,
constraints, coefficient files, seeds, objective/readback code and an open solver
recipe where distribution rights permit. Distinguish reproduction of published
energies from rerunning the combinatorial search. An open fitting backend makes
that stage accessible without Gurobi; Q-Chem feature generation remains a separate
software dependency. Exported models and audit code are useful even if Gurobi
remains a performance comparator.

The frozen Step 1 specification currently names Gurobi. This request authorizes
research, not a switch: a selected backend needs versioned execution/spec change
control and measured validation before production. No frozen spec/index changed.
