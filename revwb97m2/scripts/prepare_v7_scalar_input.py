"""Prepare (never run) a versioned b=5.5 same-orbital scalar input."""
import argparse
from pathlib import Path
from revwb97m2.fit_spec import DEFAULT_SPEC, load_fit_settings
from revwb97m2.fit_inputs import digest
from revwb97m2.qchem_scalar_features import derive_scalar_input
from revwb97m2.solver_reporting import strict_dumps


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,default=DEFAULT_SPEC)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    settings=load_fit_settings(args.spec)
    derived,controls=derive_scalar_input(args.source.read_text(),settings=settings)
    args.output.mkdir(parents=True,exist_ok=False)
    target=args.output/'scalar.in';target.write_text(derived)
    (args.output/'preparation.json').write_text(strict_dumps({
        'status':'prepared_not_executed','scientific_specification_sha256':settings.specification_sha256,
        'source_path':str(args.source.resolve()),'source_sha256':digest(args.source),
        'input_sha256':digest(target),'controls':controls,
        'archive_copy_and_species_identity_preflight_required':True,
        'submission_authorized':False})+'\n')


if __name__=='__main__':
    main()
