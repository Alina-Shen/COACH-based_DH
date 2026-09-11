"""Read-only full-data optimizer preflight: no solver or license initialization."""
import argparse
import subprocess
from pathlib import Path
import numpy as np
from revwb97m2.scripts import assemble_full1498_v1 as a
from revwb97m2.fit_inputs import load_inputs
from revwb97m2.grid_selection import select_rows


def inspect(matrix):
    matrix = Path(matrix)
    validation = a.validate(matrix)
    settings = a.g.native.load_fit_settings()
    arrays, manifest = load_inputs(matrix/'inputs.json', settings)
    weighted = np.sqrt(arrays['objective_weight'])[:, None]*arrays['feature_matrix']
    singular = np.linalg.svd(weighted, compute_uv=False)
    tolerance = singular[0]*max(weighted.shape)*np.finfo(float).eps
    # Only the fixed global component is known before discovery candidates exist.
    rows = select_rows(arrays['grid_difference_99590'], np.empty((0, 292)),
                       settings.candidate_rows, settings.global_rows)
    return dict(passed=True, commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        matrix=str(matrix), validation_sha256=a.digest(matrix/'validation.json'),
        input_manifest_sha256=a.digest(matrix/'inputs.json'),
        specification_sha256=settings.specification_sha256, pilot_rows_exact=validation['pilot_rows_exact'],
        entries=1498, species=2799, features=292,
        arrays={k:dict(shape=list(v.shape),bytes=v.nbytes,min=float(v.min()),max=float(v.max())) for k,v in arrays.items()},
        weighted_feature_rank_diagnostic=dict(numerical_rank=int(np.sum(singular>tolerance)),
            tolerance=float(tolerance),largest_singular_value=float(singular[0]),
            smallest_singular_value=float(singular[-1]),
            note='Unscaled weighted A only; not MIQP conditioning, infeasibility, or a reason to remove columns.'),
        global_grid_row_indices=rows.tolist(), global_grid_row_count=len(rows),
        candidate_grid_rows_pending=True,
        model_dimensions_before_presolve=dict(beta=292,binary=292,residual=1498,total_variables=2082,
            nongrid_linear_constraints=2088,extra_constraints_per_selected_grid_row=2),
        resolved_settings=settings.record(),
        scope='Hash/readback/dimension/SVD diagnostics only; no Gurobi environment, license access or optimization.',
        code_sha256=a.digest(__file__))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    a.require(not args.report.exists(),'preserve existing report')
    result=inspect(args.matrix)
    a.write(args.report,result)
    print({k:result[k] for k in ('passed','commit','entries','features','global_grid_row_count','weighted_feature_rank_diagnostic')})
