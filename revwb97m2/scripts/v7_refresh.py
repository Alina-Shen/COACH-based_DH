"""Explicit bounded refresh commands; no submission or automatic batch loop."""
import argparse
from pathlib import Path
from revwb97m2 import v7_refresh as workflow


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    prepare=commands.add_parser('freeze')
    prepare.add_argument('--plan',type=Path,required=True)
    prepare.add_argument('--root',type=Path,required=True)
    run=commands.add_parser('species')
    run.add_argument('--plan',type=Path,required=True)
    run.add_argument('--species',required=True)
    run.add_argument('--cpus',type=int,required=True)
    for command in ('validate-species','assemble'):
        sub=commands.add_parser(command);sub.add_argument('--plan',type=Path,required=True)
        if command=='validate-species':sub.add_argument('--species',required=True)
    args=parser.parse_args()
    if args.command=='freeze':workflow.freeze(args.plan,args.root)
    elif args.command=='species':workflow.refresh_species(args.plan,args.species,args.cpus)
    elif args.command=='validate-species':workflow.validate_species(args.plan,args.species)
    else:workflow.assemble(args.plan)


if __name__=='__main__':main()
