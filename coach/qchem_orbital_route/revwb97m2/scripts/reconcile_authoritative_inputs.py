#!/usr/bin/env python3
"""Build or verify the immutable Q-Chem input snapshot for revwb97m2."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "manifests" / "gscdb137" / "species_manifest.csv"
DEFAULT_SOURCE = Path("/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2")
DEFAULT_ORBITALS = Path("/clusterfs/mhg-data/yaoshen/scf_read/rev_wb97m2/gscdb")
DEFAULT_DESTINATION = Path(
    "/clusterfs/mhg-data/yaoshen/coach-based_dh_data/revwb97m2/"
    "authoritative_inputs/qchem/gscdb137_v1"
)
FIELDS = [
    "species",
    "scope",
    "source_input",
    "snapshot_input",
    "sha256",
    "bytes",
    "charge",
    "multiplicity",
    "method",
    "basis",
    "aux_basis_corr",
    "scf_guess",
    "max_scf_cycles",
    "scf_algorithm",
    "unrestricted",
    "orbital_snapshot_dir",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "promote", "verify"))
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--orbitals", type=Path, default=DEFAULT_ORBITALS)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def block(text: str, name: str) -> str:
    match = re.search(
        rf"(?ims)^\s*\${re.escape(name)}\s*$\n(.*?)^\s*\$end\s*$", text
    )
    if not match:
        raise ValueError(f"missing ${name} block")
    return match.group(1)


def rem_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in block(text, "rem").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("!", "#")):
            continue
        fields = line.replace("=", " ").split()
        if len(fields) >= 2:
            values[fields[0].upper()] = fields[1]
    return values


def charge_multiplicity(text: str) -> tuple[str, str]:
    for raw_line in block(text, "molecule").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("!", "#")):
            continue
        fields = line.split()
        if len(fields) >= 2 and re.fullmatch(r"[+-]?\d+", fields[0]) and re.fullmatch(
            r"\d+", fields[1]
        ):
            return fields[0], fields[1]
        break
    raise ValueError("missing charge/multiplicity line in $molecule block")


def norm(value: str) -> str:
    return value.strip().upper()


def load_species(manifest: Path) -> list[dict[str, str]]:
    with manifest.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    names = [row["species"] for row in rows]
    if len(names) != 14006:
        raise ValueError(f"expected 14006 manifest rows, found {len(names)}")
    if len(set(names)) != len(names):
        raise ValueError("duplicate species names in manifest")
    if any(not name or name in {".", ".."} or "/" in name for name in names):
        raise ValueError("unsafe species name in manifest")
    return rows


def inspect_input(
    row: dict[str, str], data: bytes, orbital_root: Path
) -> tuple[dict[str, str], list[str]]:
    species = row["species"]
    errors: list[str] = []
    try:
        text = data.decode("utf-8")
        rem = rem_values(text)
        charge, multiplicity = charge_multiplicity(text)
    except (UnicodeDecodeError, ValueError) as exc:
        return {}, [f"{species}: {exc}"]

    basis = rem.get("BASIS", "")
    auxiliary = rem.get("AUX_BASIS_CORR", "")
    if charge != row["charge"] or multiplicity != row["multiplicity"]:
        errors.append(
            f"{species}: charge/multiplicity manifest={row['charge']} {row['multiplicity']} "
            f"input={charge} {multiplicity}"
        )
    generated_basis = norm(basis) in {"GEN", "GENERAL"}
    if not (generated_basis and re.search(r"(?im)^\s*\$basis\s*$", text)):
        if norm(basis) != norm(row["basis"]):
            errors.append(f"{species}: BASIS manifest={row['basis']} input={basis}")
    manifest_aux = row["aux_basis_corr"]
    if manifest_aux and norm(auxiliary) != norm(manifest_aux):
        errors.append(
            f"{species}: AUX_BASIS_CORR manifest={manifest_aux} input={auxiliary}"
        )
    if generated_basis and not re.search(r"(?im)^\s*\$basis\s*$", text):
        errors.append(f"{species}: generated BASIS lacks $basis block")
    if norm(auxiliary) == "GEN" and not re.search(r"(?im)^\s*\$aux_basis\s*$", text):
        errors.append(f"{species}: generated AUX_BASIS_CORR lacks $aux_basis block")

    orbital_dir = orbital_root / species
    if not orbital_dir.is_dir() or not (orbital_dir / "qarchive.h5").is_file():
        errors.append(f"{species}: published orbital scratch or qarchive.h5 missing")

    record = {
        "species": species,
        "scope": row["scope"],
        "charge": charge,
        "multiplicity": multiplicity,
        "method": rem.get("METHOD", ""),
        "basis": basis,
        "aux_basis_corr": auxiliary,
        "scf_guess": rem.get("SCF_GUESS", ""),
        "max_scf_cycles": rem.get("MAX_SCF_CYCLES", ""),
        "scf_algorithm": rem.get("SCF_ALGORITHM", ""),
        "unrestricted": rem.get("UNRESTRICTED", ""),
        "orbital_snapshot_dir": str(orbital_dir),
    }
    return record, errors


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(args: argparse.Namespace) -> int:
    destination = args.destination.resolve()
    staging = destination.with_name(f".{destination.name}.incomplete")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing snapshot: {destination}")
    if staging.exists():
        raise FileExistsError(f"remove or inspect stale staging directory first: {staging}")

    rows = load_species(args.manifest)
    staging.mkdir(parents=True)
    species_root = staging / "species"
    species_root.mkdir()
    records: list[dict[str, str]] = []
    errors: list[str] = []
    distributions: dict[str, Counter[str]] = {
        "scf_guess": Counter(),
        "max_scf_cycles": Counter(),
        "method": Counter(),
    }

    for row in rows:
        species = row["species"]
        source = args.source / species / "input0"
        if not source.is_file():
            errors.append(f"{species}: source input0 missing")
            continue
        data = source.read_bytes()
        record, input_errors = inspect_input(row, data, args.orbitals)
        errors.extend(input_errors)
        target_dir = species_root / species
        target_dir.mkdir()
        target = target_dir / "input0"
        shutil.copy2(source, target)
        copied = target.read_bytes()
        if copied != data:
            errors.append(f"{species}: copied bytes differ from source")
        digest = sha256_bytes(data)
        record.update(
            {
                "source_input": str(source),
                "snapshot_input": str(Path("species") / species / "input0"),
                "sha256": digest,
                "bytes": str(len(data)),
            }
        )
        records.append(record)
        for key in distributions:
            distributions[key][record.get(key, "")] += 1

    checks = {
        "manifest_has_14006_unique_species": len(rows) == 14006,
        "all_manifest_inputs_copied": len(records) == len(rows),
        "all_copies_byte_identical": not any("copied bytes differ" in e for e in errors),
        "all_inputs_parse_and_match_manifest_semantics": not any(
            "source input0 missing" not in e
            and "published orbital" not in e
            and "copied bytes differ" not in e
            for e in errors
        ),
        "all_published_orbital_pairs_present": not any("published orbital" in e for e in errors),
        "scf_guess_values_preserved_from_source": not any(
            "copied bytes differ" in error for error in errors
        ),
        "max_scf_cycles_values_preserved_from_source": not any(
            "copied bytes differ" in error for error in errors
        ),
    }
    report = {
        "status": "pass" if all(checks.values()) and not errors else "fail",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "counts": {
            "manifest_species": len(rows),
            "snapshot_inputs": len(records),
            "total_input_bytes": sum(int(record["bytes"]) for record in records),
            "distributions": {key: dict(value) for key, value in distributions.items()},
        },
        "errors": errors[:200],
        "provenance": {
            "species_manifest": str(args.manifest.resolve()),
            "species_manifest_sha256": sha256_file(args.manifest),
            "source_input_root": str(args.source.resolve()),
            "published_orbital_root": str(args.orbitals.resolve()),
            "snapshot_root": str(destination),
            "copy_policy": "byte-for-byte shutil.copy2; no Q-Chem input edits",
        },
    }

    with (staging / "input_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    write_json(staging / "validation.json", report)
    if report["status"] != "pass":
        print(json.dumps(report, indent=2, sort_keys=True))
        print(f"FAILED; staging retained for inspection: {staging}")
        return 1

    marker = {
        "status": "complete",
        "created_utc": report["created_utc"],
        "species_count": len(records),
        "input_manifest_sha256": sha256_file(staging / "input_manifest.csv"),
        "validation_sha256": sha256_file(staging / "validation.json"),
        "note": "Every input0 is byte-identical to its recorded source.",
    }
    write_json(staging / "INPUTS_COMPLETE.json", marker)
    staging.rename(destination)
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Published immutable input snapshot: {destination}")
    return 0


def promote(args: argparse.Namespace) -> int:
    """Revalidate and atomically publish a complete retained staging tree."""
    destination = args.destination.resolve()
    staging = destination.with_name(f".{destination.name}.incomplete")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing snapshot: {destination}")
    manifest_path = staging / "input_manifest.csv"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"staging manifest missing: {manifest_path}")
    rows = load_species(args.manifest)
    rows_by_species = {row["species"]: row for row in rows}
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    errors: list[str] = []
    distributions: dict[str, Counter[str]] = {
        "scf_guess": Counter(),
        "max_scf_cycles": Counter(),
        "method": Counter(),
    }
    for record in records:
        species = record["species"]
        source = args.source / species / "input0"
        snapshot = staging / record["snapshot_input"]
        if species not in rows_by_species or not source.is_file() or not snapshot.is_file():
            errors.append(f"{species}: manifest, source, or staged input missing")
            continue
        source_data = source.read_bytes()
        snapshot_data = snapshot.read_bytes()
        digest = sha256_bytes(source_data)
        if snapshot_data != source_data or record["sha256"] != digest:
            errors.append(f"{species}: staged bytes or recorded SHA-256 differ from source")
            continue
        observed, input_errors = inspect_input(rows_by_species[species], source_data, args.orbitals)
        errors.extend(input_errors)
        for key in (
            "charge",
            "multiplicity",
            "method",
            "basis",
            "aux_basis_corr",
            "scf_guess",
            "max_scf_cycles",
            "scf_algorithm",
            "unrestricted",
        ):
            if record[key] != observed.get(key, ""):
                errors.append(f"{species}: recorded {key} differs from source")
        for key in distributions:
            distributions[key][observed.get(key, "")] += 1

    checks = {
        "manifest_has_14006_unique_species": len(rows) == 14006,
        "staging_has_one_record_per_manifest_species": len(records) == len(rows)
        and {record["species"] for record in records} == set(rows_by_species),
        "all_staged_inputs_byte_identical_to_source": not any(
            "staged bytes" in error for error in errors
        ),
        "all_inputs_parse_and_match_manifest_semantics": not errors,
        "scf_guess_values_preserved_from_source": not errors,
        "max_scf_cycles_values_preserved_from_source": not errors,
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "counts": {
            "manifest_species": len(rows),
            "snapshot_inputs": len(records),
            "total_input_bytes": sum(int(record["bytes"]) for record in records),
            "distributions": {key: dict(value) for key, value in distributions.items()},
        },
        "errors": errors[:200],
        "provenance": {
            "species_manifest": str(args.manifest.resolve()),
            "species_manifest_sha256": sha256_file(args.manifest),
            "source_input_root": str(args.source.resolve()),
            "published_orbital_root": str(args.orbitals.resolve()),
            "snapshot_root": str(destination),
            "copy_policy": "byte-for-byte shutil.copy2; no Q-Chem input edits",
        },
    }
    write_json(staging / "validation.json", report)
    if report["status"] != "pass":
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    marker = {
        "status": "complete",
        "created_utc": report["created_utc"],
        "species_count": len(records),
        "input_manifest_sha256": sha256_file(manifest_path),
        "validation_sha256": sha256_file(staging / "validation.json"),
        "note": "Every input0 is byte-identical to its recorded source.",
    }
    write_json(staging / "INPUTS_COMPLETE.json", marker)
    staging.rename(destination)
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Published immutable input snapshot: {destination}")
    return 0


def verify(args: argparse.Namespace) -> int:
    destination = args.destination.resolve()
    marker_path = destination / "INPUTS_COMPLETE.json"
    manifest_path = destination / "input_manifest.csv"
    if not marker_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("snapshot completion marker or input manifest missing")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    errors: list[str] = []
    distributions = {"scf_guess": Counter(), "max_scf_cycles": Counter()}
    for record in records:
        snapshot = destination / record["snapshot_input"]
        source = Path(record["source_input"])
        if not snapshot.is_file():
            errors.append(f"{record['species']}: snapshot input missing")
            continue
        digest = sha256_file(snapshot)
        if digest != record["sha256"]:
            errors.append(f"{record['species']}: snapshot SHA-256 mismatch")
        if not source.is_file() or sha256_file(source) != record["sha256"]:
            errors.append(f"{record['species']}: source missing or changed")
        distributions["scf_guess"][record["scf_guess"]] += 1
        distributions["max_scf_cycles"][record["max_scf_cycles"]] += 1
    checks = {
        "completion_marker_complete": marker.get("status") == "complete",
        "input_manifest_hash_matches_marker": sha256_file(manifest_path)
        == marker.get("input_manifest_sha256"),
        "record_count_is_14006": len(records) == 14006,
        "all_snapshot_and_source_hashes_match": not errors,
        "scf_guess_values_match_recorded_sources": sum(distributions["scf_guess"].values())
        == 14006,
        "max_scf_cycles_values_match_recorded_sources": sum(
            distributions["max_scf_cycles"].values()
        )
        == 14006,
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "counts": {
            "records": len(records),
            "scf_guess": dict(distributions["scf_guess"]),
            "max_scf_cycles": dict(distributions["max_scf_cycles"]),
        },
        "errors": errors[:200],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


def main() -> int:
    args = parse_args()
    if args.action == "build":
        return build(args)
    if args.action == "promote":
        return promote(args)
    return verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
