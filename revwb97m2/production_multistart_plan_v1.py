"""Non-submitting 56-solve graph and reproducible noise preparation.

No optimizer, license, scheduler or artifact publication calls.
"""
import numpy as np

BUDGETS = (14, 24, 32, 40, 48, 64, 80)


def simple_seed(source_coefficients):
    source = np.asarray(source_coefficients, dtype=float)
    if source.shape != (292,) or not np.isfinite(source).all():
        raise ValueError('invalid scalar source')
    beta = np.zeros(292)
    beta[[0, 1, 96, 192, 288]] = [.85, 1., 1., 1., .15]
    beta[289:] = source[289:]
    return beta


def task_graph():
    tasks = []
    for phase in (1, 2):
        # Original COACH initializes one RNG per sweep; freeze draw order before
        # splitting independent solves across jobs. 292 draws, not original 289.
        rng = np.random.default_rng(0)
        for budget in BUDGETS:
            starts = ['simple'] if phase == 1 else ['simple', 'pass1_r0', 'pass1_r1']
            for start in starts:
                for repeat in (0, 1):
                    noise = np.zeros(292) if repeat == 0 else rng.normal(scale=.05, size=292)
                    source = 'simple' if start == 'simple' else f'p1_k{budget}_simple_r{start[-1]}'
                    tasks.append(dict(id=f'p{phase}_k{budget}_{start}_r{repeat}', phase=phase,
                        budget=budget, start_source=source, repeat=repeat,
                        noise=noise.tolist(), seconds=7200, threads=16,
                        dependencies=[] if phase == 1 else ['grid_selection'],
                        acceptance='selected_constraints_only' if phase == 2 else 'ungridded'))
    discovery = [task['id'] for task in tasks if task['phase'] == 1]
    return dict(tasks=tasks, grid_selection=dict(id='grid_selection', dependencies=discovery,
        candidate_pool=discovery, top_per_candidate=100, additional_remaining_l1=200),
        submission_authorized=False, production_executor_implemented=False)


def materialize_start(task, original):
    beta = np.asarray(original, dtype=float)
    noise = np.asarray(task['noise'], dtype=float)
    if beta.shape != (292,) or noise.shape != (292,) or not np.isfinite(beta).all() or not np.isfinite(noise).all():
        raise ValueError('invalid original start/noise')
    # Suggestions are intentionally NOT clipped/projected; fit feasibility is a
    # separate required check in the eventual production executor.
    return beta + noise
