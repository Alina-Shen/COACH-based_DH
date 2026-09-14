"""Read-only discovery and routing audit, then publish the scientific gate."""
import argparse
import hashlib
import json
from pathlib import Path
from .adapter import ROOT, checked_authorization
from .policy import ROUTES


def certify(authorization, output):
    from revwb97m2 import discovery_extension_v1 as e
    auth = checked_authorization(authorization)
    auth_sha = hashlib.sha256(authorization.read_bytes()).hexdigest()
    release = ROOT/'revwb97m2/manifests/discovery_extension_v1/release_20260911.json'
    p, _, _, _ = e.check(release)
    for index in auth['indices']['discovery']:
        receipt_path = Path(auth['receipts'])/('discovery_'+str(index)+'.json')
        receipt = json.loads(receipt_path.read_text())
        actual = receipt['actual_route']
        if ROUTES.get(actual['partition']) != (actual['account'], actual['qos']):
            raise ValueError('unapproved recorded route')
        if (receipt['authorization_sha256'] != auth_sha or receipt['phase'] != 'discovery'
                or receipt['index'] != index or receipt['scientific_release_sha256'] != e.old.c.digest(release)):
            raise ValueError('dispatch receipt identity mismatch')
        task = p['additional_tasks'][index]
        execution = e.old.c.read(Path(p['output_root'])/(task['id']+'.execution.json'))
        if execution.get('dispatch_receipt') != str(receipt_path) or execution['job'] != receipt['job']:
            raise ValueError('execution/dispatch identity mismatch')
    reports = e.validate(release)
    if len(reports) != 138:
        raise ValueError('incomplete discovery')
    if output.resolve() != Path(auth['discovery_gate']).resolve():
        raise ValueError('unexpected gate output path')
    e.old.c.write(output, dict(passed=True, candidates=138, dispatch_authorization_sha256=auth_sha))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorization', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    certify(args.authorization, args.output)
