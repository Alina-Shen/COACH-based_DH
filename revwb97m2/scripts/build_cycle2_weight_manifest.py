#!/usr/bin/env python3
"""Build deterministic COACH final/Cycle-2 fitting-weight manifests."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "revwb97m2/manifests/weights/coach_si_table2_final_cycle.yaml"
DEFAULT_DATASET_EVAL = ROOT / "revwb97m2/manifests/gscdb137/source/DatasetEval.csv"
DEFAULT_OUTPUT_DIR = ROOT / "revwb97m2/manifests/weights"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_dataset_eval(path: Path) -> tuple[list[dict[str, str]], dict[str, list[str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or list(rows[0]) != ["Reaction", "Dataset", "Reference", "Stoichiometry"]:
        raise ValueError(f"Unexpected DatasetEval.csv columns in {path}")
    grouped: dict[str, list[str]] = {}
    for row in rows:
        grouped.setdefault(row["Dataset"], []).append(row["Reaction"])
    return rows, grouped


def expand_source(
    source: dict, grouped_reactions: dict[str, list[str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    row_records: list[dict[str, object]] = []
    entry_records: list[dict[str, object]] = []
    seen_subsets: set[str] = set()

    for row_number, row in enumerate(source["rows"], start=1):
        subset = str(row["set_or_subset"])
        dataset = str(row["dataset_eval_dataset"])
        if subset in seen_subsets:
            raise ValueError(f"Duplicate SI set/subset label: {subset}")
        seen_subsets.add(subset)
        if dataset not in grouped_reactions:
            raise KeyError(f"SI row {subset}: DatasetEval dataset {dataset!r} is absent")

        dataset_reactions = grouped_reactions[dataset]
        selection = row["selection"]
        if selection == "all":
            reactions = list(dataset_reactions)
            selection_mode = "All"
        else:
            template = str(row["reaction_id_template"])
            reactions = [template.format(index=index) for index in selection]
            selection_mode = "explicit"
            missing = [reaction for reaction in reactions if reaction not in dataset_reactions]
            if missing:
                raise KeyError(f"SI row {subset}: reactions absent from {dataset}: {missing}")
            positions = [dataset_reactions.index(reaction) for reaction in reactions]
            if positions != sorted(positions) or len(set(positions)) != len(positions):
                raise ValueError(f"SI row {subset}: selection is not unique DatasetEval order")

        expected_count = int(row["count"])
        if len(reactions) != expected_count:
            raise ValueError(
                f"SI row {subset}: selected {len(reactions)} reactions, expected {expected_count}"
            )

        weight_spec = str(row["weight"])
        coach_weight_spec = "Shrink" if weight_spec == "1/sqrt(j)" else weight_spec
        datapoints = "All" if selection_mode == "All" else ",".join(reactions)
        row_records.append(
            {
                "Dataset": dataset,
                "datapoints": datapoints,
                "weights": coach_weight_spec,
                "set_or_subset": subset,
                "property_class": row["class"],
                "published_count": expected_count,
                "selection_mode": selection_mode,
            }
        )

        position_by_reaction = {
            reaction: index for index, reaction in enumerate(dataset_reactions, start=1)
        }
        for selection_index, reaction in enumerate(reactions, start=1):
            weight = (
                1.0 / math.sqrt(selection_index)
                if weight_spec == "1/sqrt(j)"
                else float(row["weight"])
            )
            entry_records.append(
                {
                    "global_index": len(entry_records) + 1,
                    "si_row_index": row_number,
                    "set_or_subset": subset,
                    "property_class": row["class"],
                    "dataset_eval_dataset": dataset,
                    "reaction": reaction,
                    "dataset_order": position_by_reaction[reaction],
                    "selection_index": selection_index,
                    "weight_spec": weight_spec,
                    "objective_weight": format(weight, ".17g"),
                }
            )

    if len(row_records) != int(source["expected"]["row_count"]):
        raise ValueError("SI row count does not match the source expectation")
    if len(entry_records) != int(source["expected"]["entry_count"]):
        raise ValueError("Expanded entry count does not match the source expectation")
    return row_records, entry_records


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dataset-eval", type=Path, default=DEFAULT_DATASET_EVAL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    source = yaml.safe_load(args.source.read_text(encoding="utf-8"))
    si_path = ROOT / source["source"]["path"]
    if sha256(si_path) != source["source"]["sha256"]:
        raise ValueError(f"COACH SI hash mismatch: {si_path}")
    _, grouped = read_dataset_eval(args.dataset_eval)
    row_records, entry_records = expand_source(source, grouped)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows_path = args.output_dir / "coach_si_table2_final_cycle_training_weights.csv"
    entries_path = args.output_dir / "coach_si_table2_final_cycle_entries.csv"
    provenance_path = args.output_dir / "coach_si_table2_final_cycle_provenance.json"
    write_csv(rows_path, row_records)
    write_csv(entries_path, entry_records)

    provenance = {
        "schema_version": 1,
        "status": "generated_pending_independent_validation",
        "authority": {
            "si_pdf": str(si_path.relative_to(ROOT)),
            "si_pdf_sha256": sha256(si_path),
            "si_section": source["source"]["section"],
            "si_table": source["source"]["table"],
            "si_pdf_pages": source["source"]["pdf_pages"],
            "transcription": str(args.source.relative_to(ROOT)),
            "transcription_sha256": sha256(args.source),
        },
        "dataset_eval": {
            "path": str(args.dataset_eval.relative_to(ROOT)),
            "sha256": sha256(args.dataset_eval),
        },
        "outputs": {
            "row_manifest": str(rows_path.relative_to(ROOT)),
            "row_manifest_sha256": sha256(rows_path),
            "entry_manifest": str(entries_path.relative_to(ROOT)),
            "entry_manifest_sha256": sha256(entries_path),
            "row_count": len(row_records),
            "entry_count": len(entry_records),
        },
        "weight_definition": {
            "non_ae18": "constant SI Table 2 wk multiplying each squared residual",
            "ae18": "objective_weight(j) = 1/sqrt(j), j is the 1-based listed-atom order",
        },
    }
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
