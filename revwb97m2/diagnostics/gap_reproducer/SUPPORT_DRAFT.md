# DRAFT ONLY — not submitted; attachments require user approval

Subject: Gurobi 13.0.3 returns infinite MIPGap with finite nonzero ObjVal and bound

Hello Gurobi Support,

We observe an unexpected MIPGap attribute in a single-objective MIQP using
Python 3.11.15 and gurobipy 13.0.3 on Linux with an academic WLS license.
After a 60-second time limit, with ten incumbent solutions reported:

- `ObjVal = 3.511210956300334e-07`
- `ObjBound = ObjBoundC = 1.5613942678319019e-16`
- `MIPGap = +infinity`, using both property and `getAttr` access
- `abs(ObjVal-ObjBound)/abs(ObjVal) = 0.9999999995553118`
- `IsMIP=1`, `IsMultiObj=0`, `NumObj=1`, `ObjCon=0`

Parameters include Threads=1, Seed=0, TimeLimit=60, FeasibilityTol=1e-9,
IntFeasTol=1e-9, MIPGap=1e-4, and MIPGapAbs=1e-10. The raw discrepancy was
observed before JSON serialization; it is not a confusion with the parameter.
Two original-model repeats produced identical values and feasible incumbents.

We tested a standalone LP replay with the original MIP start restored. Both
LP replays reached a different incumbent (1.7446783028823013e-06) and returned
consistent finite gaps (0.9999991006408575). Three one-binary-variable synthetic
quadratic controls, with objective scales 1, 1e-6 and 1e-9, solved optimally
with gap zero. These controls do not reproduce the problem.

A second standalone script path constructs the model directly from JSON-exported
input numbers, whose numerical round-trip was checked exactly. This path needs
only Python and gurobipy, not our project imports or quantum-chemistry software.
It **reproduces the original infinity discrepancy in both 60-second repeats**,
with exactly the objective and bound listed above. The model has 604 variables
and 610 linear constraints. This is a verified standalone reproducer, but we
have not reduced its mathematical size. The different LP-replay outcome does
not by itself establish whether precision, model ordering or search-path effects
are responsible.

Is infinity expected in this situation due to numerical handling, or does it
warrant further investigation? Which diagnostics or model format would best
preserve the triggering conditions? Is reporting both the raw attribute and
the calculated ratio appropriate while retaining TIME_LIMIT status?

We can discuss providing a reproducer after reviewing the research-derived
input data for disclosure. No model/input attachment is included in this draft.
License credentials will not be shared.

Thank you.
