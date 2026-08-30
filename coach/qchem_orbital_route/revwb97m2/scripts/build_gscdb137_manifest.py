#!/usr/bin/env python3
"""Build the authoritative GSCDB137 species and dataset manifests.

Dataset membership is defined by the GSCDB reaction and standard-error files,
never by whichever directories happen to exist in an orbital scratch tree.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


EXPECTED_COMMIT = "f62f5d844d64b4ff451cbfc9320a39d830857099"
EXPECTED_COUNTS = {
    "gscdb137_datasets": 137,
    "gscdb137_reactions": 8377,
    "gscdb137_species": 13907,
    "auxiliary_reactions": 71,
    "all_metadata_species": 14006,
    "bignc_datasets": 2,
    "bignc_reactions": 25,
    "bignc_species": 75,
}

SOURCE_FILES = (
    "Info/DatasetEval.csv",
    "Info/Datasets.csv",
    "Info/Standard_errors.csv",
    "Info/DatasetEval_O24x5_weight.csv",
    "Info/DatasetEval_TMC34_weight.csv",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_stoichiometry(text: str) -> list[tuple[float, str]]:
    fields = text.split(",")
    if len(fields) % 2:
        raise ValueError(f"Odd stoichiometry field count: {text!r}")
    return [(float(fields[index]), fields[index + 1]) for index in range(0, len(fields), 2)]


def git_value(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def top_level_directories(root: Path) -> set[str]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    return {entry.name for entry in os.scandir(root) if entry.is_dir(follow_symlinks=False)}


def directories_with_file(root: Path, filename: str) -> set[str]:
    """Return top-level directory names containing a requested regular file."""
    result = subprocess.run(
        [
            "find",
            str(root),
            "-mindepth",
            "2",
            "-maxdepth",
            "2",
            "-type",
            "f",
            "-name",
            filename,
            "-printf",
            "%h\n",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return {Path(line).name for line in result.stdout.splitlines() if line}


def join_names(values: Iterable[str]) -> str:
    return ";".join(sorted(set(values)))


def require_equal(actual: int, expected_key: str) -> None:
    expected = EXPECTED_COUNTS[expected_key]
    if actual != expected:
        raise ValueError(f"{expected_key}: expected {expected}, observed {actual}")


def inventory_root(
    root: Path,
    canonical_species: set[str],
    core_species: set[str],
    qarchives: set[str],
    completion_markers: set[str] | None = None,
) -> dict[str, object]:
    directories = top_level_directories(root)
    record: dict[str, object] = {
        "root": str(root),
        "top_level_directories": len(directories),
        "gscdb137_species_present": len(core_species & directories),
        "gscdb137_species_missing": sorted(core_species - directories),
        "all_metadata_species_present": len(canonical_species & directories),
        "all_metadata_species_missing": sorted(canonical_species - directories),
        "canonical_qarchives_present": len(canonical_species & qarchives),
        "canonical_qarchives_missing": sorted(canonical_species - qarchives),
        "noncanonical_directories": sorted(directories - canonical_species),
    }
    if completion_markers is not None:
        record["canonical_completion_markers_present"] = len(canonical_species & completion_markers)
        record["canonical_completion_markers_missing"] = sorted(canonical_species - completion_markers)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gscdb-root", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests" / "gscdb137",
    )
    parser.add_argument(
        "--primary-orbital-root",
        type=Path,
        default=Path("/global/scratch/users/jsliang/wB97M-V"),
    )
    parser.add_argument(
        "--working-orbital-root",
        type=Path,
        default=Path("/clusterfs/mhg-data/yaoshen/scf_read/wb97m_os_rimp2"),
    )
    parser.add_argument(
        "--bignc-orbital-root",
        type=Path,
        default=Path("/global/scratch/users/jsliang/BigNC/wB97M-V"),
    )
    parser.add_argument("--expected-commit", default=EXPECTED_COMMIT)
    args = parser.parse_args()

    gscdb_root = args.gscdb_root.resolve()
    output_dir = args.output_dir.resolve()
    commit = git_value(gscdb_root, "rev-parse", "HEAD")
    if args.expected_commit and commit != args.expected_commit:
        raise ValueError(f"Expected GSCDB commit {args.expected_commit}, observed {commit}")

    reaction_rows = read_csv(gscdb_root / "Info" / "DatasetEval.csv")
    dataset_info_rows = [row for row in read_csv(gscdb_root / "Info" / "Datasets.csv") if row["Name"]]
    standard_error_rows = read_csv(gscdb_root / "Info" / "Standard_errors.csv")
    standard_errors = {row["Dataset"]: row for row in standard_error_rows}
    core_datasets = set(standard_errors)
    require_equal(len(core_datasets), "gscdb137_datasets")

    core_rows = [row for row in reaction_rows if row["Dataset"] in core_datasets]
    auxiliary_rows = [row for row in reaction_rows if row["Dataset"] not in core_datasets]
    auxiliary_datasets = {row["Dataset"] for row in auxiliary_rows}
    if auxiliary_datasets != {"OEEFD", "SC74"}:
        raise ValueError(f"Unexpected auxiliary DatasetEval groups: {sorted(auxiliary_datasets)}")
    require_equal(len(core_rows), "gscdb137_reactions")
    require_equal(len(auxiliary_rows), "auxiliary_reactions")

    core_memberships: dict[str, set[str]] = defaultdict(set)
    core_reaction_uses: Counter[str] = Counter()
    auxiliary_memberships: dict[str, set[str]] = defaultdict(set)
    auxiliary_reaction_uses: Counter[str] = Counter()
    dataset_species: dict[str, set[str]] = defaultdict(set)
    dataset_reactions: Counter[str] = Counter()
    for row in reaction_rows:
        is_core = row["Dataset"] in core_datasets
        row_species = {species for _, species in parse_stoichiometry(row["Stoichiometry"])}
        for species in row_species:
            if is_core:
                core_memberships[species].add(row["Dataset"])
                core_reaction_uses[species] += 1
                dataset_species[row["Dataset"]].add(species)
            else:
                auxiliary_memberships[species].add(row["Dataset"])
                auxiliary_reaction_uses[species] += 1
        if is_core:
            dataset_reactions[row["Dataset"]] += 1

    core_species = set(core_memberships)
    require_equal(len(core_species), "gscdb137_species")
    allmols_path = gscdb_root / "Allmols_info.json"
    with allmols_path.open(encoding="utf-8") as handle:
        molecule_info: dict[str, dict[str, object]] = json.load(handle)
    canonical_species = set(molecule_info)
    require_equal(len(canonical_species), "all_metadata_species")
    reaction_species = core_species | set(auxiliary_memberships)
    if canonical_species != reaction_species:
        raise ValueError(
            "Allmols_info species do not exactly equal the species named by DatasetEval.csv"
        )

    qchem_inputs = {path.stem for path in (gscdb_root / "qchem_inputs").glob("*.in")}
    if qchem_inputs != canonical_species:
        raise ValueError("qchem_inputs/*.in does not exactly match Allmols_info.json")

    dataset_info = {row["Name"]: row for row in dataset_info_rows}
    if set(dataset_info) != core_datasets:
        raise ValueError("Nonblank Datasets.csv names do not exactly match Standard_errors.csv")

    primary_dirs = top_level_directories(args.primary_orbital_root)
    working_dirs = top_level_directories(args.working_orbital_root)
    primary_qarchives = directories_with_file(args.primary_orbital_root, "qarchive.h5")
    working_qarchives = directories_with_file(args.working_orbital_root, "qarchive.h5")
    working_markers = directories_with_file(args.working_orbital_root, ".staged.ok")

    species_rows: list[dict[str, object]] = []
    for species in sorted(canonical_species):
        info = molecule_info[species]
        core_member = species in core_species
        molecule = str(info["molecule"])
        species_rows.append(
            {
                "species": species,
                "scope": "gscdb137" if core_member else "auxiliary_only",
                "gscdb137_dataset_count": len(core_memberships[species]),
                "gscdb137_datasets": join_names(core_memberships[species]),
                "gscdb137_reaction_uses": core_reaction_uses[species],
                "auxiliary_dataset_count": len(auxiliary_memberships[species]),
                "auxiliary_datasets": join_names(auxiliary_memberships[species]),
                "auxiliary_reaction_uses": auxiliary_reaction_uses[species],
                "charge": info["charge"],
                "multiplicity": info["multiplicity"],
                "atom_count": len([line for line in molecule.splitlines() if line.strip()]),
                "basis": info.get("basis", ""),
                "aux_basis_corr": info.get("AUX_BASIS_CORR", ""),
                "scf_algorithm": info.get("SCF_ALGORITHM", ""),
                "xc_grid": info.get("xc_grid", ""),
                "num_basis": info.get("num_basis", ""),
                "num_pairs": info.get("num_pairs", ""),
                "qchem_input": f"qchem_inputs/{species}.in",
                "primary_orbital_dir": species in primary_dirs,
                "primary_qarchive": species in primary_qarchives,
                "working_orbital_dir": species in working_dirs,
                "working_qarchive": species in working_qarchives,
                "working_staged_ok": species in working_markers,
            }
        )
    write_csv(
        output_dir / "species_manifest.csv",
        list(species_rows[0]),
        species_rows,
    )

    dataset_rows: list[dict[str, object]] = []
    for dataset in sorted(core_datasets):
        info = dataset_info[dataset]
        error = standard_errors[dataset]
        dataset_rows.append(
            {
                "dataset": dataset,
                "category_short": info["Datatype_Short"],
                "category": info["Datatype"],
                "reaction_count": dataset_reactions[dataset],
                "species_count": len(dataset_species[dataset]),
                "reported_datapoints": info["#datapoints"],
                "metric_standard_error": error["Metric"],
                "rmse_standard_error": error["RMSE"],
                "mae_standard_error": error["MAE"],
                "theory_level": info["Theory level"],
                "description": info["Description"],
            }
        )
    write_csv(output_dir / "dataset_manifest.csv", list(dataset_rows[0]), dataset_rows)

    auxiliary_summary: list[dict[str, object]] = []
    for dataset in sorted(auxiliary_datasets):
        rows = [row for row in auxiliary_rows if row["Dataset"] == dataset]
        species = {
            item
            for row in rows
            for _, item in parse_stoichiometry(row["Stoichiometry"])
        }
        auxiliary_summary.append(
            {
                "dataset_group": dataset,
                "reaction_count": len(rows),
                "species_count": len(species),
                "auxiliary_only_species_count": len(species - core_species),
                "reason_not_gscdb137": (
                    "present in DatasetEval.csv tail but absent from both the 137-row "
                    "Standard_errors.csv and nonblank Datasets.csv registry"
                ),
            }
        )
    write_csv(
        output_dir / "auxiliary_dataset_groups.csv",
        list(auxiliary_summary[0]),
        auxiliary_summary,
    )

    bignc_root = gscdb_root / "AdditionalSets" / "BigNC"
    bignc_reactions = read_csv(bignc_root / "DatasetEval.csv")
    with (bignc_root / "Allmols_info.json").open(encoding="utf-8") as handle:
        bignc_info: dict[str, dict[str, object]] = json.load(handle)
    bignc_memberships: dict[str, set[str]] = defaultdict(set)
    bignc_uses: Counter[str] = Counter()
    for row in bignc_reactions:
        for _, species in parse_stoichiometry(row["Stoichiometry"]):
            bignc_memberships[species].add(row["Dataset"])
            bignc_uses[species] += 1
    require_equal(len(set(row["Dataset"] for row in bignc_reactions)), "bignc_datasets")
    require_equal(len(bignc_reactions), "bignc_reactions")
    require_equal(len(bignc_info), "bignc_species")
    if set(bignc_info) != set(bignc_memberships):
        raise ValueError("BigNC molecular metadata and reaction species differ")
    bignc_dirs = top_level_directories(args.bignc_orbital_root)
    bignc_qarchives = directories_with_file(args.bignc_orbital_root, "qarchive.h5")
    bignc_rows: list[dict[str, object]] = []
    for species in sorted(bignc_info):
        info = bignc_info[species]
        bignc_rows.append(
            {
                "species": species,
                "datasets": join_names(bignc_memberships[species]),
                "reaction_uses": bignc_uses[species],
                "charge": info["charge"],
                "multiplicity": info["multiplicity"],
                "atom_count": len(str(info["molecule"]).splitlines()),
                "basis": info.get("basis", ""),
                "orbital_dir": species in bignc_dirs,
                "qarchive": species in bignc_qarchives,
            }
        )
    write_csv(output_dir / "bignc_species_manifest.csv", list(bignc_rows[0]), bignc_rows)

    inventory = {
        "schema_version": 1,
        "generated_from_gscdb_commit": commit,
        "primary_gscdb137_source": inventory_root(
            args.primary_orbital_root,
            canonical_species,
            core_species,
            primary_qarchives,
        ),
        "existing_working_copy": inventory_root(
            args.working_orbital_root,
            canonical_species,
            core_species,
            working_qarchives,
            working_markers,
        ),
        "bignc_source": {
            "root": str(args.bignc_orbital_root),
            "top_level_directories": len(bignc_dirs),
            "expected_species": len(bignc_info),
            "expected_species_present": len(set(bignc_info) & bignc_dirs),
            "expected_species_missing": sorted(set(bignc_info) - bignc_dirs),
            "expected_qarchives_present": len(set(bignc_info) & bignc_qarchives),
            "expected_qarchives_missing": sorted(set(bignc_info) - bignc_qarchives),
            "noncanonical_directories": sorted(bignc_dirs - set(bignc_info)),
        },
    }
    (output_dir / "scratch_inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    source_dir = output_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_records: list[dict[str, object]] = []
    for relative in SOURCE_FILES:
        source = gscdb_root / relative
        destination = source_dir / source.name
        shutil.copyfile(source, destination)
        source_records.append(
            {
                "gscdb_path": relative,
                "vendored_path": str(destination.relative_to(output_dir.parents[2])),
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )
    provenance = {
        "schema_version": 1,
        "repository": git_value(gscdb_root, "remote", "get-url", "origin"),
        "commit": commit,
        "commit_date": git_value(gscdb_root, "show", "-s", "--format=%cI", "HEAD"),
        "commit_subject": git_value(gscdb_root, "show", "-s", "--format=%s", "HEAD"),
        "allmols_info": {
            "gscdb_path": "Allmols_info.json",
            "bytes": allmols_path.stat().st_size,
            "sha256": sha256(allmols_path),
            "vendored": False,
            "reason": "13 MB geometry-bearing source; derived lightweight fields are in species_manifest.csv",
        },
        "source_files": source_records,
        "definition": {
            "gscdb137_datasets": "the 137 dataset names in Info/Standard_errors.csv",
            "gscdb137_reactions": "DatasetEval.csv rows whose Dataset is in that 137-name registry",
            "gscdb137_species": "unique stoichiometric species in those 8377 reactions",
            "auxiliary_rows": "the appended SC74 and OEEFD rows, explicitly excluded from GSCDB137",
        },
        "counts": EXPECTED_COUNTS,
    }
    (output_dir / "source_provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"PASS: {len(core_datasets)} GSCDB137 datasets")
    print(f"PASS: {len(core_rows)} GSCDB137 reactions")
    print(f"PASS: {len(core_species)} GSCDB137 species")
    print(f"PASS: {len(canonical_species)} total molecular records including 99 auxiliary-only species")
    print(f"PASS: {len(bignc_info)} BigNC species across 25 reactions")
    print(f"WROTE: {output_dir}")


if __name__ == "__main__":
    main()
