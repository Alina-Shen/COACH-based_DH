"""Resolve the supported v7 fitting contract; no solver or job side effects."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import yaml

ROOT = Path(__file__).resolve().parent
DEFAULT_SPEC = ROOT / 'configs/scientific_spec.yaml'
V6_SHA256 = '5c7a03994f75ea0076188f20a679647b9cfc2e0ec1c72874b0cc463326a3212e'


@dataclass(frozen=True)
class FitSettings:
    specification_sha256: str
    ridge: float
    grid_limit: float
    grid_public_limit: float
    conversion: float
    seconds: int
    threads: int
    seed: int
    solver_parameters: tuple
    budgets: tuple
    candidate_rows: int
    global_rows: int
    vv10_b: float
    vv10_c: float

    def record(self):
        from dataclasses import asdict
        return asdict(self)


def load_fit_settings(path=DEFAULT_SPEC):
    path = Path(path)
    raw = path.read_bytes()
    spec = yaml.safe_load(raw)
    baseline_raw = (ROOT / 'configs/archive/scientific_spec.v6.yaml').read_bytes()
    if hashlib.sha256(baseline_raw).hexdigest() != V6_SHA256:
        raise ValueError('archived v6 identity mismatch')
    baseline = yaml.safe_load(baseline_raw)

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(spec['schema_version'] == 7 and spec['scientific_specification']['version'] == 7,
            'v7 specification required')
    require(spec['status'] in ('implemented_pending_pretest_commit', 'frozen'), 'unsupported spec state')
    require(spec['scientific_specification']['amendment']['previous_specification_sha256'] == V6_SHA256,
            'amendment baseline mismatch')
    # Reject scientifically unsupported changes rather than silently applying the
    # hardcoded R2/C0/native-kernel implementation to another functional.
    for key in ('orbital_source', 'coach_feature_grids', 'constraint_profiles',
                'feature_models', 'data_policy'):
        require(spec[key] == baseline[key], f'unsupported change to {key}')
    for channel in ('exchange', 'same_spin_correlation', 'opposite_spin_correlation', 'expansion_terms'):
        require(spec['semilocal_model'][channel] == baseline['semilocal_model'][channel],
                f'unsupported semilocal {channel}')
    expected_energy = baseline['double_hybrid_energy']
    expected_energy['vv10']['b'] = 5.5
    expected_energy['fitted_energy_terms'][4] = 'vv10_correlation_b5p5_c001'
    require(spec['double_hybrid_energy'] == expected_energy, 'unsupported energy definition')
    require(spec['project']['runtime_environment']['conda_environment_name'] == 'dh', 'dh required')
    opt = spec['optimization']
    allowed = set(baseline['optimization']) | {'objective_representation', 'objective_normalization',
              'ridge', 'solver_parameters', 'final_selection', 'execution_approval'}
    require(set(opt) == allowed, 'unknown or missing optimization setting')
    require(opt['objective'] == 'weighted_least_squares' and
            opt['objective_representation'] == 'explicit_weighted_residuals' and
            opt['objective_normalization'] == 'full_sse', 'unsupported objective')
    require(opt['ridge']['enabled'] is True and opt['ridge']['coefficient'] == 1e-10 and
            opt['ridge']['scope'] == 'all_fitted_coefficients', 'approved COACH ridge required')
    require(opt['final_selection']['primary'] == 'lowest_overall_mean_NER_among_eligible_candidates' and
            opt['final_selection']['user_review_required'] is True and
            opt['final_selection']['deferred_todos_block_initial_fitting'] is False,
            'selection protocol mismatch')
    params = opt['solver_parameters']
    require(params == {'FeasibilityTol': 1e-9, 'IntFeasTol': 1e-9,
                       'MIPGap': 1e-4, 'MIPGapAbs': 1e-10}, 'unsupported solver controls')
    grid = spec['grid_sensitivity']
    expected_grid = baseline['grid_sensitivity']
    expected_grid.update(internal_safety_factor=0.999, public_audit_slack_hartree=0.0)
    require(grid == expected_grid, 'unsupported grid contract')
    require(spec['execution_protocol'] == baseline['execution_protocol'], 'unsupported cycle protocol')
    require(spec['validation']['equality_constraint_tolerance'] == 1e-10, 'unsupported UEG audit')
    require(opt['selection_must_not_use'] == baseline['optimization']['selection_must_not_use'],
            'protected final assessment policy changed')
    conversion = spec['project']['units']['hartree_to_kcal_per_mol']
    require(conversion == 627.50947406, 'unit conversion mismatch')
    for key in ('threads', 'time_limit_seconds'):
        require(type(opt[key]) is int and opt[key] > 0, f'invalid {key}')
    require(type(opt['random_seed']) is int and 0 <= opt['random_seed'] <= 2000000000, 'invalid seed')
    budgets = opt['sparsity_scan']['R2_coachform_292']
    require(bool(budgets) and all(type(k) is int and 4 <= k <= 292 for k in budgets)
            and len(set(budgets)) == len(budgets), 'invalid budget scan')
    return FitSettings(hashlib.sha256(raw).hexdigest(), opt['ridge']['coefficient'],
                       grid['threshold_kcal_per_mol'] * grid['internal_safety_factor'] / conversion,
                       grid['threshold_kcal_per_mol'] / conversion, conversion,
                       opt['time_limit_seconds'], opt['threads'], opt['random_seed'],
                       tuple(params.items()), tuple(budgets),
                       grid['selection']['largest_model_error_rows_per_candidate'],
                       grid['selection']['largest_global_row_l1_norms'], 5.5, 0.01)
