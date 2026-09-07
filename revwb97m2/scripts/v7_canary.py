"""Explicit freeze/run/validate CLI for seven v7 fresh-feature canaries."""
import argparse
from pathlib import Path
from revwb97m2 import v7_canary as workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    freeze = subs.add_parser('freeze')
    freeze.add_argument('--plan', type=Path, required=True)
    freeze.add_argument('--root', type=Path, required=True)
    for command in ('run', 'validate'):
        sub = subs.add_parser(command)
        sub.add_argument('--plan', type=Path, required=True)
        sub.add_argument('--species', required=True, choices=workflow.NAMES)
        if command == 'run':
            sub.add_argument('--cpus', type=int, required=True)
            sub.add_argument('--memory-gib', type=int, required=True)
            sub.add_argument('--large-reviewed', action='store_true')
    args = parser.parse_args()
    if args.command == 'freeze':
        workflow.freeze(args.plan, args.root)
    elif args.command == 'validate':
        workflow.validate_species(args.plan, args.species)
    else:
        workflow.run(args.plan, args.species, args.cpus, args.memory_gib,
                     large_reviewed=args.large_reviewed)


if __name__ == '__main__':
    main()
