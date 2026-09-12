"""Guarded three-stage submission; preview is read-only, submission requires release."""
import argparse
import getpass
from pathlib import Path
import re
import shlex
import subprocess
from revwb97m2 import production_multistart_v1 as run

LAUNCHER = 'revwb97m2/slurm/run_production_multistart_v1.sh'


def command(route, release, phase, dependency=None):
    run.c.require(phase in ('1', '2', 'grid'), 'phase')
    run.c.require(tuple(route[k] for k in ('partition', 'account', 'qos')) in run.c.d.full.ROUTES,
                  'unapproved route')
    cmd = ['sbatch', '--parsable', '--no-requeue']
    cmd += [f'--{k}={route[k]}' for k in ('partition', 'account', 'qos')]
    if phase != 'grid':
        cmd += ['--array=0-13' if phase == '1' else '--array=0-41']
    else:
        cmd += ['--time=00:30:00']
    if dependency is not None:
        cmd += ['--dependency=afterok:' + dependency, '--kill-on-invalid-dep=yes']
    return cmd + [LAUNCHER, str(Path(release).resolve()), phase]


def check_capacity(active, additional):
    run.c.require(active >= 0 and active + additional <= 998, '998 active-task cap')


def submit(release):
    p, r, g, root = run.check(release)
    run.c.require(getpass.getuser() == 'yaoshen', 'submission user')
    # Exclusive creation makes partial or ambiguous submissions stop for review.
    root.mkdir(parents=True, exist_ok=False)
    run.c.write(root / 'identity.json', dict(release=str(Path(release).resolve()),
        release_sha256=run.c.digest(release), plan_sha256=run.c.digest(run.PLAN), commit=r['commit']))
    previous = None
    reserved_floor = 0
    for phase, count in [('1', 14), ('grid', 1), ('2', 42)]:
        queue = subprocess.check_output(['squeue', '-u', 'yaoshen', '-h', '-r', '-o', '%i'], text=True)
        active = max(len(queue.splitlines()), reserved_floor)
        check_capacity(active, count)
        cmd = command(r['route'], release, phase, previous)
        run.c.write(root / ('submission_' + phase + '_intent.json'), dict(command=cmd))
        completed = subprocess.run(cmd, cwd=run.ROOT, capture_output=True, text=True)
        run.c.write(root / ('submission_' + phase + '_response.json'),
                    dict(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr))
        run.c.require(completed.returncode == 0, 'submission failed; inspect journal, no automatic retry')
        match = re.fullmatch(r'(\d+)(?:;[A-Za-z0-9_.-]+)?\s*', completed.stdout)
        run.c.require(match is not None, 'ambiguous submission response; inspect scheduler before retry')
        previous = match.group(1)
        reserved_floor = active + count
        print(phase, previous, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--submit', action='store_true')
    args = parser.parse_args()
    if args.submit:
        submit(args.release)
    else:
        # Preview only: a proposed route in a disabled draft cannot authorize work.
        route = run.c.read(args.release)['route']
        for phase, dep in [('1', None), ('grid', '<PASS1_JOBID>'), ('2', '<GRID_JOBID>')]:
            print(shlex.join(command(route, args.release, phase, dep)))
