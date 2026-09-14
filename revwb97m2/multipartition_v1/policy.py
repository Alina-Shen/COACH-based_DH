"""Pure routing, migration identity and phase dependency policy."""
ROUTES = {
    'cm1': ('lr_qchem', 'condo_qchem'),
    'lr7': ('lr_mhg2', 'condo_mhg_lr7'),
    'lr8': ('lr_mhg2', 'mhg2_lr8_normal'),
    'mhg': ('mhg', 'normal'),
}


def allocation(env):
    partition = env.get('SLURM_JOB_PARTITION')
    if partition not in ROUTES:
        raise ValueError('unauthorized partition')
    account, qos = ROUTES[partition]
    if (env.get('SLURM_JOB_ACCOUNT'), env.get('SLURM_JOB_QOS')) != (account, qos):
        raise ValueError('unauthorized account/QOS')
    if env.get('SLURM_CPUS_PER_TASK') != '16' or env.get('SLURM_MEM_PER_NODE') != '32768':
        raise ValueError('allocation must remain 16 CPUs / 32 GiB')
    if not env.get('SLURM_JOB_ID'):
        raise ValueError('compute allocation required')
    return dict(partition=partition, account=account, qos=qos)


def pending_targets(rows, array):
    """Consume expanded (one task per row) scheduler records, never running tasks."""
    expected = {'25801134': 'r2_discovery_ext', '25802824': 'r2_selected_full'}
    if array not in expected:
        raise ValueError('out-of-scope array')
    targets = []
    for row in rows:
        if row['array'] != array:
            continue
        if row['name'] != expected[array]:
            raise ValueError('job identity mismatch')
        if row['state'] == 'PENDING':
            targets.append(int(row['index']))
    if len(targets) != len(set(targets)):
        raise ValueError('duplicate scheduler task')
    return sorted(targets)


def dependency(kind, *, terminal_jobs=(), validated=None, build=None, grid=None):
    """afterany is permissible ONLY for the exhaustive scientific audit barrier."""
    if kind == 'audit':
        if not terminal_jobs:
            raise ValueError('missing discovery terminal jobs')
        return 'afterany:' + ':'.join(str(j) for j in terminal_jobs)
    required = {'build': [validated], 'grid': [validated, build],
                'selected': [validated, build, grid]}
    if kind not in required or any(j is None for j in required[kind]):
        raise ValueError('missing scientific prerequisite')
    return 'afterok:' + ':'.join(str(j) for j in required[kind])
