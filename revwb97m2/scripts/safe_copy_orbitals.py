#!/usr/bin/env python3.9
"""Create and verify the immutable rev-wB97M(2) orbital input snapshot.

Only species named by the authoritative manifests are copied.  The two GSCDB
species whose primary wB97M-V archives are incomplete are copied wholesale
from the validated wb97m_os_rimp2 tree.  Data are first written to a sibling
staging directory and are published by an atomic rename only after an rsync
checksum comparison succeeds.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_ROOT = PROJECT_ROOT / "manifests" / "gscdb137"
GSCDB_MANIFEST = MANIFEST_ROOT / "species_manifest.csv"
BIGNC_MANIFEST = MANIFEST_ROOT / "bignc_species_manifest.csv"

DEFAULT_DESTINATION = Path("/clusterfs/mhg-data/yaoshen/scf_read/rev_wb97m2")
DEFAULT_GSCDB_SOURCE = Path("/global/scratch/users/jsliang/wB97M-V")
DEFAULT_BIGNC_SOURCE = Path("/global/scratch/users/jsliang/BigNC/wB97M-V")
DEFAULT_FALLBACK_SOURCE = Path(
    "/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2"
)
FALLBACK_SPECIES = ("3d4dIPSS_V_ES", "3d4dIPSS_V_GS")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def read_column(path: Path, column: str) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        values = [row[column] for row in csv.DictReader(handle)]
    if not values or len(values) != len(set(values)):
        raise RuntimeError(f"{path}: {column} must be nonempty and unique")
    for value in values:
        if not value or value in {".", ".."} or "/" in value or "\0" in value:
            raise RuntimeError(f"unsafe species name in {path}: {value!r}")
    return sorted(values)


def staging_path(destination: Path) -> Path:
    return destination.parent / f".{destination.name}.incomplete"


def selected_sources(args: argparse.Namespace) -> dict[str, tuple[Path, list[str]]]:
    gscdb = read_column(GSCDB_MANIFEST, "species")
    bignc = read_column(BIGNC_MANIFEST, "species")
    fallback = sorted(FALLBACK_SPECIES)
    missing_from_manifest = sorted(set(fallback) - set(gscdb))
    if missing_from_manifest:
        raise RuntimeError(f"fallback species absent from GSCDB manifest: {missing_from_manifest}")
    primary = sorted(set(gscdb) - set(fallback))
    return {
        "gscdb_primary": (args.gscdb_source, primary),
        "gscdb_fallback": (args.fallback_source, fallback),
        "bignc": (args.bignc_source, bignc),
    }


def validate_source(root: Path, species: list[str]) -> list[str]:
    errors: list[str] = []
    for name in species:
        species_dir = root / name
        if not species_dir.is_dir():
            errors.append(f"missing directory: {species_dir}")
        elif not (species_dir / "qarchive.h5").is_file():
            errors.append(f"missing qarchive.h5: {species_dir}")
    return errors


def preflight(args: argparse.Namespace, *, allow_staging: bool) -> dict[str, object]:
    destination = args.destination.resolve()
    staging = staging_path(destination)
    if destination.exists():
        raise RuntimeError(f"refusing to overwrite existing destination: {destination}")
    if staging.exists() and not allow_staging:
        raise RuntimeError(
            f"staging directory already exists: {staging}; inspect it and use --resume"
        )
    if not shutil.which("rsync"):
        raise RuntimeError("rsync is not available")

    selections = selected_sources(args)
    errors: list[str] = []
    for root, species in selections.values():
        if not root.is_dir():
            errors.append(f"missing source root: {root}")
        else:
            errors.extend(validate_source(root, species))
    if errors:
        preview = "\n".join(errors[:30])
        suffix = f"\n... plus {len(errors) - 30} errors" if len(errors) > 30 else ""
        raise RuntimeError(f"source validation failed:\n{preview}{suffix}")

    free_bytes = shutil.disk_usage(destination.parent).free
    return {
        "checked_at": now_iso(),
        "destination": str(destination),
        "staging": str(staging),
        "free_bytes_at_preflight": free_bytes,
        "counts": {name: len(species) for name, (_, species) in selections.items()},
        "sources": {name: str(root) for name, (root, _) in selections.items()},
        "manifests": {
            "gscdb": str(GSCDB_MANIFEST),
            "bignc": str(BIGNC_MANIFEST),
        },
    }


def write_text_atomic(path: Path, content: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def write_plan(args: argparse.Namespace, preflight_record: dict[str, object]) -> dict[str, Path]:
    staging = staging_path(args.destination.resolve())
    metadata = staging / "_copy_metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    selections = selected_sources(args)
    list_paths: dict[str, Path] = {}
    for label, (_, species) in selections.items():
        path = metadata / f"{label}.files-from.txt"
        write_text_atomic(path, "".join(f"{name}/\n" for name in species))
        list_paths[label] = path
    write_text_atomic(
        metadata / "preflight.json",
        json.dumps(preflight_record, indent=2, sort_keys=True) + "\n",
    )
    return list_paths


def run_logged(command: list[str], log_path: Path) -> None:
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n[{now_iso()}] command: {json.dumps(command)}\n")
        log.flush()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log.write(line)
        return_code = process.wait()
        log.write(f"[{now_iso()}] exit_code: {return_code}\n")
    if return_code:
        raise RuntimeError(f"command failed with exit code {return_code}: {command}")


def copy(args: argparse.Namespace, *, resume: bool) -> None:
    record = preflight(args, allow_staging=resume)
    staging = staging_path(args.destination.resolve())
    if staging.exists() and not resume:
        raise RuntimeError(f"staging directory already exists: {staging}")
    staging.mkdir(parents=False, exist_ok=resume)
    list_paths = write_plan(args, record)
    selections = selected_sources(args)
    metadata = staging / "_copy_metadata"

    for label in ("gscdb_primary", "gscdb_fallback", "bignc"):
        source, species = selections[label]
        target = staging / ("bignc" if label == "bignc" else "gscdb")
        target.mkdir(exist_ok=True)
        worker_count = min(args.jobs, len(species))
        commands: list[tuple[list[str], Path]] = []
        for part_number in range(worker_count):
            part_species = species[part_number::worker_count]
            part_list = metadata / f"{label}.part{part_number + 1:02d}.files-from.txt"
            write_text_atomic(part_list, "".join(f"{name}/\n" for name in part_species))
            command = [
                "rsync",
                "--archive",
                "--human-readable",
                "--stats",
                "--partial",
                f"--files-from={part_list}",
                f"{source}/",
                f"{target}/",
            ]
            log = metadata / f"rsync-copy-{label}-part{part_number + 1:02d}.log"
            commands.append((command, log))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(run_logged, command, log) for command, log in commands]
            for future in futures:
                future.result()


def rsync_checksum_differences(
    source: Path, target: Path, files_from: Path, log_path: Path
) -> list[str]:
    command = [
        "rsync",
        "--archive",
        "--dry-run",
        "--checksum",
        "--delete",
        "--itemize-changes",
        "--out-format=%i|%n%L",
        f"--files-from={files_from}",
        f"{source}/",
        f"{target}/",
    ]
    completed = subprocess.run(command, text=True, capture_output=True)
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n[{now_iso()}] command: {json.dumps(command)}\n")
        log.write(completed.stdout)
        log.write(completed.stderr)
        log.write(f"[{now_iso()}] exit_code: {completed.returncode}\n")
    if completed.returncode:
        raise RuntimeError(
            f"rsync verification failed ({completed.returncode}): {completed.stderr.strip()}"
        )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def clean_cached_verification(log_path: Path) -> bool:
    """Recognize a completed zero-difference log from an earlier interrupted run."""
    if not log_path.is_file():
        return False
    lines = [line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    command_lines = [index for index, line in enumerate(lines) if "] command: " in line]
    if not command_lines:
        return False
    lines = lines[command_lines[-1] :]
    return (
        len(lines) == 2
        and "] command: " in lines[0]
        and lines[1].endswith("] exit_code: 0")
    )


def verify(args: argparse.Namespace) -> dict[str, object]:
    staging = staging_path(args.destination.resolve())
    metadata = staging / "_copy_metadata"
    if not staging.is_dir() or not metadata.is_dir():
        raise RuntimeError(f"incomplete or absent staging directory: {staging}")
    selections = selected_sources(args)
    expected_gscdb = set(selections["gscdb_primary"][1]) | set(
        selections["gscdb_fallback"][1]
    )
    expected_bignc = set(selections["bignc"][1])

    errors: list[str] = []
    for label, expected in (("gscdb", expected_gscdb), ("bignc", expected_bignc)):
        root = staging / label
        actual = {path.name for path in root.iterdir() if path.is_dir()}
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        missing_archives = sorted(
            name for name in expected if not (root / name / "qarchive.h5").is_file()
        )
        if missing:
            errors.append(f"{label}: missing directories: {missing[:20]}")
        if extra:
            errors.append(f"{label}: extra directories: {extra[:20]}")
        if missing_archives:
            errors.append(f"{label}: missing qarchive.h5: {missing_archives[:20]}")

    checksum_differences: dict[str, list[str]] = {}
    for label in ("gscdb_primary", "gscdb_fallback", "bignc"):
        source, species = selections[label]
        target = staging / ("bignc" if label == "bignc" else "gscdb")
        worker_count = min(args.jobs, len(species))
        tasks: list[tuple[Path, Path]] = []
        pending_parts: list[tuple[int, list[str]]] = []
        for part_number in range(worker_count):
            part_species = species[part_number::worker_count]
            part_list = metadata / f"{label}.part{part_number + 1:02d}.files-from.txt"
            write_text_atomic(part_list, "".join(f"{name}/\n" for name in part_species))
            log = metadata / f"rsync-verify-{label}-part{part_number + 1:02d}.log"
            if args.reuse_passing_parts and clean_cached_verification(log):
                print(f"reusing clean checksum result: {log.name}")
            else:
                pending_parts.append((part_number, part_species))
        if args.reuse_passing_parts and len(pending_parts) == 1 and worker_count > 1:
            part_number, part_species = pending_parts[0]
            for sub_number in range(worker_count):
                sub_species = part_species[sub_number::worker_count]
                sub_list = metadata / (
                    f"{label}.part{part_number + 1:02d}.sub{sub_number + 1:02d}.files-from.txt"
                )
                write_text_atomic(sub_list, "".join(f"{name}/\n" for name in sub_species))
                sub_log = metadata / (
                    f"rsync-verify-{label}-part{part_number + 1:02d}-sub{sub_number + 1:02d}.log"
                )
                if clean_cached_verification(sub_log):
                    print(f"reusing clean checksum result: {sub_log.name}")
                else:
                    tasks.append((sub_list, sub_log))
        else:
            for part_number, _ in pending_parts:
                tasks.append(
                    (
                        metadata / f"{label}.part{part_number + 1:02d}.files-from.txt",
                        metadata / f"rsync-verify-{label}-part{part_number + 1:02d}.log",
                    )
                )
        differences = []
        with ThreadPoolExecutor(max_workers=min(worker_count, max(1, len(tasks)))) as executor:
            futures = [
                executor.submit(
                    rsync_checksum_differences, source, target, part_list, log
                )
                for part_list, log in tasks
            ]
            for future in futures:
                differences.extend(future.result())
        checksum_differences[label] = differences
        if differences:
            errors.append(f"{label}: checksum comparison reported {len(differences)} changes")

    result: dict[str, object] = {
        "verified_at": now_iso(),
        "status": "pass" if not errors else "fail",
        "destination": str(args.destination.resolve()),
        "staging": str(staging),
        "counts": {"gscdb": len(expected_gscdb), "bignc": len(expected_bignc)},
        "required_qarchives": len(expected_gscdb) + len(expected_bignc),
        "checksum_difference_counts": {
            label: len(lines) for label, lines in checksum_differences.items()
        },
        "errors": errors,
    }
    write_text_atomic(
        metadata / "verification.json", json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    if errors:
        raise RuntimeError("verification failed:\n" + "\n".join(errors))
    return result


def publish(args: argparse.Namespace, verification: dict[str, object]) -> None:
    destination = args.destination.resolve()
    staging = staging_path(destination)
    if destination.exists():
        raise RuntimeError(f"refusing to overwrite existing destination: {destination}")
    if verification.get("status") != "pass":
        raise RuntimeError("refusing to publish without passing verification")
    metadata = staging / "_copy_metadata"
    complete = {
        **verification,
        "published_at": now_iso(),
        "policy": (
            "Authoritative orbital input snapshot. Do not modify in place; copy required "
            "species into disposable run directories."
        ),
    }
    write_text_atomic(
        metadata / "COPY_COMPLETE.json", json.dumps(complete, indent=2, sort_keys=True) + "\n"
    )
    os.replace(staging, destination)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("preflight", "copy", "verify", "verify-publish", "all")
    )
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--gscdb-source", type=Path, default=DEFAULT_GSCDB_SOURCE)
    parser.add_argument("--bignc-source", type=Path, default=DEFAULT_BIGNC_SOURCE)
    parser.add_argument("--fallback-source", type=Path, default=DEFAULT_FALLBACK_SOURCE)
    parser.add_argument(
        "--jobs",
        type=int,
        default=4,
        choices=range(1, 17),
        metavar="N",
        help="number of disjoint rsync workers per source tree (default: 4)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume an existing incomplete staging copy (never overwrites final destination)",
    )
    parser.add_argument(
        "--reuse-passing-parts",
        action="store_true",
        help=(
            "reuse only prior per-part logs containing exactly a command and exit_code 0; "
            "use after a controlled interrupted verification"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.action == "preflight":
            print(json.dumps(preflight(args, allow_staging=args.resume), indent=2, sort_keys=True))
        elif args.action == "copy":
            copy(args, resume=args.resume)
        elif args.action == "verify":
            verification = verify(args)
            print(json.dumps(verification, indent=2, sort_keys=True))
        elif args.action == "verify-publish":
            verification = verify(args)
            publish(args, verification)
            print(json.dumps(verification, indent=2, sort_keys=True))
            print(f"published: {args.destination.resolve()}")
        else:
            copy(args, resume=args.resume)
            verification = verify(args)
            publish(args, verification)
            print(json.dumps(verification, indent=2, sort_keys=True))
            print(f"published: {args.destination.resolve()}")
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
