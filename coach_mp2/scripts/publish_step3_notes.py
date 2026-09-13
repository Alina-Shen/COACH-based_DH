from pathlib import Path
import argparse
NOTES=Path('/clusterfs/mhg-data/yaoshen/codex_notes/projects/coach-based_dh')
NAME='11-step3-data-roles-and-metrics-frozen.md'
CHAPTER='''# 2026-09-12 — Step 3 data roles and metrics frozen

## Contents

- [Complete work list and explanations](../../../../coach-based_dh/coach_mp2/results/step3_complete.md)
- [79-check role validation](../../../../coach-based_dh/coach_mp2/results/step3_roles_validation.json)
- [Published-metric cross-check](../../../../coach-based_dh/coach_mp2/results/step3_metrics_validation.json)
- [26-artifact hash freeze](../../../../coach-based_dh/coach_mp2/manifests/step3_freeze_v1.json)
- [Live plan](../COACH-based_mp2.md)

Tags: COACH-based_mp2, step3, completed, data-roles, weights, metrics, solver-neutral

Step 3 complete; next stable step 4. User requested pausing if solver choice is
needed. Step 3 is solver-neutral: no backend installed or selected, license used,
solver run or Slurm job submitted. Pause before backend-dependent work (expected
Step 14), or earlier if necessary. The historical frozen Gurobi field is not a
new backend decision; user choice remains deferred.

Verified current GSCDB core/BigNC/GDB reaction tables against the pinned reference.
Expanded all 49 final-cycle SI selection/weight rows into exactly 1498 ordered
fitting entries, including partial selections and AE18 1/sqrt(j). Rebuilt exact
reaction/species/dataset role tables and preserved reference orders/stoichiometry.
Validated current Allmols_info membership: 17658 metadata species, 17452 in the
energy union, 206 OPT excluded. Input chemistry remains a Step 4 gate.

| Role | Rows | Unique species |
| --- | ---: | ---: |
| Coefficient fitting | 1498 | 2799 |
| Model selection | 8377 | 13907 |
| Overfitting diagnostic | 219 | 249 |
| Final assessment | 3462 | 3573 |

All fitting rows overlap model selection; 43 MB16-43 fitting rows overlap the
diagnostic. Final-assessment reactions are disjoint, but six species overlap
fitting/final and 28 overlap selection/final. Protect reaction-level final scores;
do not mislabel development or inherited BigNC exposure as independent holdout.

Implemented dataset-specific MAE, relative error, regularized dipole metric and
weighted sums (including TMC offsets); normalize with Standard_errors.Metric.
Overall NER averages all 137 dataset NERs equally, not category means. This is
the frozen benchmark policy, distinct from the generic COACH helper's all-RMSE
analysis. Independently reproduced all 137 published COACH development NERs:
maximum disagreement 1.7676971e-12, overall mean 0.9367424523440216. No final-set
scores used. Property transformations from molecular energies remain Step 13.

All 79 semantic checks, 18 corruption/metric tests and 26 frozen-artifact hashes
pass. Step 1 recheck passes. Updated README, mutable progress, completion report,
live plan table and this dated chapter. All writes under coach_mp2 and project
notes; reference trees read-only. No quantum chemistry or production operations.
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args()
 chapter=NOTES/'2026-09-12.chapters'/NAME;assert not chapter.exists()
 planpath=NOTES/'COACH-based_mp2.md';plan=planpath.read_text();lines=plan.splitlines()
 indices=[i for i,l in enumerate(lines) if l.startswith('| 3 |')];assert len(indices)==1
 lines[indices[0]]='| 3 | Immutable data roles and metrics | Complete — 79 checks, 18 tests, hash freeze PASS | Exact fitting/selection/final roles, ordered weights and metric policy frozen; all 137 paper NERs reproduced. Solver-neutral; next Step 4. |'
 plan='\n'.join(lines)+'\n';plan=plan.replace('Steps 1 and 2 complete. Next stable step: 3, immutable data roles and metrics.','Steps 1–3 complete. Next stable step: 4, molecular input and basis authority.')
 plan=plan.replace('## Contents\n','## Contents\n\n- [Step 3 data roles and metrics frozen](./2026-09-12.chapters/'+NAME+')\n',1)
 addition='''## Step 3 completed — 2026-09-12

[Work list and evidence](../../../coach-based_dh/coach_mp2/results/step3_complete.md).
Frozen 1498 fitting rows, 8377 model-selection rows, 219 diagnostic rows and
3462 final-assessment rows, with exact weights, role overlap, stoichiometry and
reference order. All 79 semantic checks, 18 tests and 26 artifact hashes pass.
The solver-neutral metric evaluator reproduces all 137 COACH development NERs
within 1.8e-12. No final-set scoring or backend choice was performed.

Standing user instruction: pause before work requires choosing Gurobi versus an
alternative backend (expected Step 14), or earlier if a dependency emerges.
Step 3 does not require that choice. Input chemistry/orbital readiness and
property transformations retain their separate later gates.

'''
 plan=plan.replace('## Objective and decision precedence',addition+'## Objective and decision precedence',1)
 idx=NOTES/'2026-09-12.md';index=idx.read_text().replace('\nTags:', '\n- [Step 3 data roles and metrics frozen](./2026-09-12.chapters/'+NAME+')\n\nTags:',1)
 for path,text in {planpath:plan,idx:index,chapter:CHAPTER}.items():
  assert path.resolve()==path
  if args.publish:
   with path.open('x' if path==chapter else 'w') as f:f.write(text)
   assert path.read_text()==text
  print(('PUBLISHED ' if args.publish else 'PREVIEW ')+str(path))
if __name__=='__main__':main()
