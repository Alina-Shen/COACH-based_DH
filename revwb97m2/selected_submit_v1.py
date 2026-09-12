"""Preview or release the 138-source grid barrier and 414-task selected pass."""
import argparse
from pathlib import Path
import re
import shlex
import subprocess
from revwb97m2 import selected_full_v1 as run


def command(route, release, phase, grid_id=None):
    run.old.c.require(tuple(route[k] for k in ('partition', 'account', 'qos')) in run.old.c.d.full.ROUTES, 'route')
    cmd = ['sbatch', '--parsable', '--no-requeue', '--kill-on-invalid-dep=yes']
    cmd += [f'--{k}={route[k]}' for k in ('partition', 'account', 'qos')]
    if phase == 'grid':
        cmd += ['--time=00:30:00', '--dependency=afterok:25796986:25801134']
    else:
        run.old.c.require(phase == 'run' and grid_id is not None, 'grid dependency required')
        cmd += ['--array=0-413%2', '--dependency=afterok:' + grid_id]
    return cmd + ['revwb97m2/slurm/run_selected_full_v1.sh', str(Path(release).resolve()), phase]


def submit(release):
    p, r, graph, root = run.check(release)
    # Separate exclusive journal; grid job alone creates the scientific run root.
    journal = root.with_name(root.name + '_submission')
    journal.mkdir(parents=True, exist_ok=False)
    floor = 0
    grid_id = None
    for phase, count in [('grid', 1), ('run', 414)]:
        queue = subprocess.check_output(['squeue', '-u', 'yaoshen', '-h', '-r', '-o', '%i'], text=True)
        active = max(floor, len(queue.splitlines()))
        run.old.c.require(active + count <= 998, '998 active task cap')
        cmd = command(r['route'], release, phase, grid_id)
        run.old.c.write(journal / (phase + '_intent.json'), dict(command=cmd, active_tasks=active))
        result = subprocess.run(cmd, cwd=run.old.ROOT, capture_output=True, text=True)
        run.old.c.write(journal / (phase + '_response.json'), dict(returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr))
        run.old.c.require(result.returncode == 0, 'submission failed; inspect journal, no blind retry')
        match = re.fullmatch(r'(\d+)(?:;[A-Za-z0-9_.-]+)?\s*', result.stdout)
        run.old.c.require(match is not None, 'ambiguous response; inspect scheduler before retry')
        if phase == 'grid':
            grid_id = match.group(1)
        floor = active + count
        print(phase, match.group(1), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--submit', action='store_true')
    args = parser.parse_args()
    if args.submit:
        submit(args.release)
    else:
        route = run.old.c.read(args.release)['route']
        for phase in ('grid', 'run'):
            print(shlex.join(command(route, args.release, phase, '<GRID_JOBID>')))
