#!/usr/bin/env python3.9
"""Prepare and verify a disposable fixed-orbital Q-Chem gateway case."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SPECIES = "h2o_SW49"
RUN_NAME = "h2o_SW49_fixed_v1"
DEFAULT_INPUT = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/qchem/gscdb137_v1/species/h2o_SW49/input0"
)
DEFAULT_ORBITALS = Path(
    "/clusterfs/mhg-data/yaoshen/scf_read/rev_wb97m2/gscdb/h2o_SW49"
)
DEFAULT_QCHEM = Path("/clusterfs/mhg/yaoshen/qchem/loco_os_yao/bin/qchem")
DEFAULT_QCPROG = Path(
    "/clusterfs/mhg/yaoshen/qchem/loco_os_yao/build/qcprog.exe"
)
DEFAULT_QCAUX = Path("/global/home/groups-sw/mhg/qchem_public/qchem_620/qcaux")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path, relative_to: Path | None = None) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(relative_to) if relative_to else path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def tree_records(root: Path) -> list[dict[str, Any]]:
    return [
        file_record(path, root)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} is not a file: {path}")


def derive_fixed_orbital_input(source: str) -> str:
    """Change only the two controls required for the fixed-orbital trial."""
    rem_match = re.search(r"(?ims)^[ \t]*\$rem[ \t]*$.*?^[ \t]*\$end[ \t]*$", source)
    if rem_match is None:
        raise ValueError("authoritative input has no complete $rem section")

    rem = rem_match.group(0)
    if not re.search(r"(?im)^[ \t]*scf_guess[ \t]*(?:=[ \t]*)?read[ \t]*$", rem):
        raise ValueError("authoritative $rem does not set SCF_GUESS READ")

    max_cycles_pattern = re.compile(
        r"(?im)^(?P<indent>[ \t]*)max_scf_cycles[ \t]*(?:=[ \t]*)?\d+[ \t]*$"
    )
    matches = list(max_cycles_pattern.finditer(rem))
    if len(matches) != 1:
        raise ValueError(
            f"expected one MAX_SCF_CYCLES control, found {len(matches)}"
        )
    rem = max_cycles_pattern.sub(
        lambda match: f"{match.group('indent')}MAX_SCF_CYCLES 0", rem
    )

    scfman_pattern = re.compile(
        r"(?im)^(?P<indent>[ \t]*)gen_scfman[ \t]*(?:=[ \t]*)?\S+[ \t]*$"
    )
    scfman_matches = list(scfman_pattern.finditer(rem))
    if len(scfman_matches) > 1:
        raise ValueError(f"found {len(scfman_matches)} GEN_SCFMAN controls")
    if scfman_matches:
        rem = scfman_pattern.sub(
            lambda match: f"{match.group('indent')}GEN_SCFMAN FALSE", rem
        )
    else:
        end_match = list(re.finditer(r"(?im)^[ \t]*\$end[ \t]*$", rem))
        if len(end_match) != 1:
            raise ValueError("could not locate unique $rem terminator")
        offset = end_match[0].start()
        rem = rem[:offset] + "GEN_SCFMAN FALSE\n" + rem[offset:]

    derived = source[: rem_match.start()] + rem + source[rem_match.end() :]
    if not re.search(r"(?im)^[ \t]*max_scf_cycles[ \t]+0[ \t]*$", rem):
        raise AssertionError("derived input does not set MAX_SCF_CYCLES 0")
    if not re.search(r"(?im)^[ \t]*gen_scfman[ \t]+false[ \t]*$", rem):
        raise AssertionError("derived input does not set GEN_SCFMAN FALSE")
    return derived


def svn_identity(path: Path) -> dict[str, str] | None:
    values = {}
    for field in ("url", "revision"):
        result = subprocess.run(
            ["svn", "info", "--show-item", field, str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        values[field] = result.stdout.strip()
    return {"url": values["url"], "working_copy_revision": values["revision"]}


def qchem_identity(
    wrapper: Path, executable: Path, qcaux: Path
) -> dict[str, Any]:
    require_file(wrapper, "Q-Chem wrapper")
    require_file(executable, "Q-Chem executable")
    if not qcaux.is_dir():
        raise NotADirectoryError(f"Q-Chem auxiliary-data root is missing: {qcaux}")
    orbital_basis = qcaux / "basis" / "def2-QZVPPD.bas"
    auxiliary_basis = qcaux / "basis" / "rimp2-def2-QZVPPD.bas"
    require_file(orbital_basis, "orbital basis asset")
    require_file(auxiliary_basis, "RI auxiliary basis asset")
    identity: dict[str, Any] = {
        "wrapper": file_record(wrapper.resolve()),
        "executable": file_record(executable.resolve()),
        "binary_build_id_sha1": None,
        "svn": None,
        "qcaux": {
            "path": str(qcaux),
            "svn": svn_identity(qcaux),
            "basis_assets": [
                file_record(orbital_basis),
                file_record(auxiliary_basis),
            ],
        },
        "version_txt": None,
    }
    readelf = subprocess.run(
        ["readelf", "-n", str(executable)],
        check=False,
        capture_output=True,
        text=True,
    )
    build_id = re.search(r"Build ID:\s*([0-9a-f]+)", readelf.stdout)
    if build_id:
        identity["binary_build_id_sha1"] = build_id.group(1)

    qc_root = wrapper.resolve().parent.parent
    version_file = qc_root / "version.txt"
    if version_file.is_file():
        identity["version_txt"] = version_file.read_text().strip()
    identity["svn"] = svn_identity(qc_root)
    return identity


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def prepare(args: argparse.Namespace) -> None:
    case_root = args.case_root.resolve()
    source_input = args.authoritative_input.resolve()
    source_orbitals = args.orbitals.resolve()
    wrapper = args.qchem_wrapper.resolve()
    executable = args.qchem_executable.resolve()
    qcaux = args.qcaux.resolve()

    require_file(source_input, "authoritative input")
    if not source_orbitals.is_dir():
        raise NotADirectoryError(f"published orbital scratch is missing: {source_orbitals}")
    if case_root.exists():
        raise FileExistsError(f"refusing to overwrite existing case: {case_root}")

    authoritative_text = source_input.read_text()
    derived_text = derive_fixed_orbital_input(authoritative_text)
    identity = qchem_identity(wrapper, executable, qcaux)

    baseline = case_root / "scratch.baseline"
    working = case_root / "qcscratch" / RUN_NAME
    case_root.mkdir(parents=True)
    shutil.copy2(source_input, case_root / "input.authoritative.in")
    (case_root / "input.fixed.in").write_text(derived_text)
    diff = difflib.unified_diff(
        authoritative_text.splitlines(keepends=True),
        derived_text.splitlines(keepends=True),
        fromfile="input.authoritative.in",
        tofile="input.fixed.in",
    )
    (case_root / "input.diff").write_text("".join(diff))
    shutil.copytree(source_orbitals, baseline, copy_function=shutil.copy2)
    shutil.copytree(baseline, working, copy_function=shutil.copy2)

    identity_path = case_root / "qchem_identity.json"
    write_json(identity_path, identity)
    source_manifest = {
        "species": SPECIES,
        "authoritative_input": file_record(source_input),
        "published_orbital_root": str(source_orbitals),
        "published_orbital_files": tree_records(source_orbitals),
    }
    source_manifest_path = case_root / "source_manifest.json"
    write_json(source_manifest_path, source_manifest)

    run_script = case_root / "run_qchem.sh"
    run_script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'case_root=$(cd -- "$(dirname -- "$0")" && pwd)\n'
        'if [[ -e "$case_root/qchem.out" ]]; then\n'
        '  echo "Refusing to overwrite existing qchem.out" >&2\n'
        "  exit 2\n"
        "fi\n"
        'export QCSCRATCH="$case_root/qcscratch"\n'
        f'export QC="{wrapper.parent.parent}"\n'
        f'export QCPROG="{executable}"\n'
        f'export QCAUX="{qcaux}"\n'
        "unset QCLOCALSCR\n"
        f'exec "{wrapper}" -save -nt {args.threads} '
        '"$case_root/input.fixed.in" "$case_root/qchem.out" '
        f'"{RUN_NAME}"\n'
    )
    run_script.chmod(run_script.stat().st_mode | stat.S_IXUSR)

    prepared = {
        "schema_version": 1,
        "state": "prepared_not_run",
        "species": SPECIES,
        "run_name": RUN_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scientific_status": "mechanics-only; production integratedDV kernel unresolved",
        "derived_controls": {
            "SCF_GUESS": "READ (unchanged)",
            "MAX_SCF_CYCLES": "0 (derived from authoritative value)",
            "GEN_SCFMAN": "FALSE (added for fixed-orbital trial)",
        },
        "files": {
            "input_authoritative": file_record(case_root / "input.authoritative.in", case_root),
            "input_fixed": file_record(case_root / "input.fixed.in", case_root),
            "input_diff": file_record(case_root / "input.diff", case_root),
            "qchem_identity": file_record(identity_path, case_root),
            "source_manifest": file_record(source_manifest_path, case_root),
            "run_script": file_record(run_script, case_root),
        },
    }
    write_json(case_root / "PREPARED.json", prepared)
    verify_case(case_root, require_unrun=True)
    print(f"Prepared and verified: {case_root}")


def compare_records(
    expected: list[dict[str, Any]], actual: list[dict[str, Any]], label: str
) -> None:
    if expected != actual:
        raise ValueError(f"{label} file manifest does not match")


def verify_case(case_root: Path, require_unrun: bool) -> None:
    marker = case_root / "PREPARED.json"
    require_file(marker, "preparation marker")
    prepared = json.loads(marker.read_text())
    source_manifest = json.loads((case_root / "source_manifest.json").read_text())
    identity = json.loads((case_root / "qchem_identity.json").read_text())

    source_input = Path(source_manifest["authoritative_input"]["path"])
    source_orbitals = Path(source_manifest["published_orbital_root"])
    require_file(source_input, "authoritative input")
    if sha256(source_input) != source_manifest["authoritative_input"]["sha256"]:
        raise ValueError("authoritative input changed after case preparation")
    compare_records(
        source_manifest["published_orbital_files"],
        tree_records(source_orbitals),
        "published orbital source",
    )

    authoritative_copy = case_root / "input.authoritative.in"
    fixed_input = case_root / "input.fixed.in"
    if sha256(authoritative_copy) != sha256(source_input):
        raise ValueError("authoritative input copy differs from source")
    expected_fixed = derive_fixed_orbital_input(authoritative_copy.read_text())
    if fixed_input.read_text() != expected_fixed:
        raise ValueError("derived input is not the exact expected transformation")

    baseline_records = tree_records(case_root / "scratch.baseline")
    compare_records(
        source_manifest["published_orbital_files"], baseline_records, "baseline scratch"
    )
    if require_unrun:
        if (case_root / "qchem.out").exists():
            raise ValueError("case has already produced qchem.out")
        compare_records(
            baseline_records,
            tree_records(case_root / "qcscratch" / prepared["run_name"]),
            "working scratch",
        )

    for component in ("wrapper", "executable"):
        record = identity[component]
        if sha256(Path(record["path"])) != record["sha256"]:
            raise ValueError(f"pinned Q-Chem {component} changed")
    for record in identity["qcaux"]["basis_assets"]:
        if sha256(Path(record["path"])) != record["sha256"]:
            raise ValueError(f"pinned Q-Chem basis asset changed: {record['path']}")

    for name, record in prepared["files"].items():
        path = case_root / record["path"]
        if sha256(path) != record["sha256"]:
            raise ValueError(f"prepared file changed: {name}")
    print(f"Verification passed: {case_root}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prep = subparsers.add_parser("prepare", help="create a non-overwriting case")
    prep.add_argument("--case-root", type=Path, required=True)
    prep.add_argument("--authoritative-input", type=Path, default=DEFAULT_INPUT)
    prep.add_argument("--orbitals", type=Path, default=DEFAULT_ORBITALS)
    prep.add_argument("--qchem-wrapper", type=Path, default=DEFAULT_QCHEM)
    prep.add_argument("--qchem-executable", type=Path, default=DEFAULT_QCPROG)
    prep.add_argument("--qcaux", type=Path, default=DEFAULT_QCAUX)
    prep.add_argument("--threads", type=int, default=1)
    prep.set_defaults(func=prepare)

    verify = subparsers.add_parser("verify", help="verify a prepared case")
    verify.add_argument("--case-root", type=Path, required=True)
    verify.add_argument(
        "--allow-run", action="store_true", help="do not require untouched working scratch"
    )
    verify.set_defaults(
        func=lambda args: verify_case(args.case_root.resolve(), not args.allow_run)
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if getattr(args, "threads", 1) < 1:
        raise ValueError("--threads must be positive")
    args.func(args)


if __name__ == "__main__":
    main()
