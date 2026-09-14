"""Audited scheduler-only override; no solver/release or running-job changes."""
import argparse
import json
from pathlib import Path
import subprocess

ARRAYS = {'25801134': 'r2_discovery_ext', '25802824': 'r2_selected_full'}
PROBE = '25883613'


def command(*args):
    return subprocess.check_output(args, text=True, timeout=30)


def field(record, name):
    values = [x.split('=', 1)[1] for x in record.split() if x.startswith(name+'=')]
    if len(values) != 1:
        raise ValueError('missing/ambiguous scheduler field '+name)
    return values[0]


def inspect():
    result = {}
    for job, name in ARRAYS.items():
        blocks = command('scontrol', 'show', 'job', job).strip().split('\n\n')
        pending = [b for b in blocks if 'JobState=PENDING' in b]
        if len(pending) != 1:
            raise ValueError('expected one pending array placeholder')
        record = pending[0]
        expected = dict(JobName=name, Partition='cm1', Account='lr_qchem', QOS='condo_qchem',
            NumCPUs='16', MinMemoryNode='32G', TimeLimit='02:30:00')
        for key, value in expected.items():
            if field(record, key) != value:
                raise ValueError('unexpected '+key)
        if '/coach-based_dh/revwb97m2/slurm/' not in field(record, 'Command'):
            raise ValueError('out-of-scope command')
        result[job] = {key: field(record, key) for key in
            (*expected, 'Dependency', 'Command', 'ArrayTaskId', 'ArrayTaskThrottle')}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    before = inspect()
    print(json.dumps({'before': before}, indent=2), flush=True)
    if args.apply:
        log = Path('/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/logs/wls20_probe_'+PROBE+'.out').read_text()
        if 'PASS: three simultaneous WLS sessions; post-disposal token cooldown complete' not in log:
            raise SystemExit('probe/cooldown gate not complete')
        rows = command('sacct', '-j', PROBE, '-n', '-P', '--format=JobID,State,ExitCode').splitlines()
        if PROBE+'|COMPLETED|0:0' not in rows:
            raise SystemExit('probe accounting gate not complete')
        for job in ARRAYS:
            # Raising the pending dispatch ceiling does not alter running fits.
            command('scontrol', 'update', 'JobId='+job, 'ArrayTaskThrottle=10')
        after = inspect()
        for job in ARRAYS:
            if after[job]['ArrayTaskThrottle'] != '10':
                raise SystemExit('throttle verification failed')
            for key in before[job]:
                if key not in ('ArrayTaskId', 'ArrayTaskThrottle') and before[job][key] != after[job][key]:
                    raise SystemExit('unexpected scheduler change: '+key)
        print(json.dumps({'after': after, 'passed': True}, indent=2), flush=True)
