#!/usr/bin/env python3
"""Independently validate published final/Cycle-2 COACH weight manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
WEIGHT_ROOT = ROOT / "revwb97m2/manifests/weights"
SOURCE = WEIGHT_ROOT / "coach_si_table2_final_cycle.yaml"
ROWS = WEIGHT_ROOT / "coach_si_table2_final_cycle_training_weights.csv"
ENTRIES = WEIGHT_ROOT / "coach_si_table2_final_cycle_entries.csv"
PROVENANCE = WEIGHT_ROOT / "coach_si_table2_final_cycle_provenance.json"
DATASET_EVAL = ROOT / "revwb97m2/manifests/gscdb137/source/DatasetEval.csv"
SI_PDF = ROOT / "coach/paper/SI_COACH_2026MHG.pdf"
EXPECTED_SI_SHA256 = "751b32e29c5a0cfb660d2f912be7d447014697294e9ef317eedd07f26d61956b"
EXPECTED_DATASET_EVAL_SHA256 = "0b95de0d35308e7ea39e1f73ed68d7ab5a65f4195212ee6295383fbf22281fbe"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}
    source = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    row_manifest = read_csv(ROWS)
    entries = read_csv(ENTRIES)
    dataset_eval = read_csv(DATASET_EVAL)
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))

    checks["si_pdf_sha256"] = sha256(SI_PDF) == EXPECTED_SI_SHA256
    checks["dataset_eval_sha256"] = sha256(DATASET_EVAL) == EXPECTED_DATASET_EVAL_SHA256
    checks["source_declares_si_hash"] = source["source"]["sha256"] == EXPECTED_SI_SHA256
    checks["source_section_and_table"] = (
        source["source"]["section"] == "3.5 Training cycles, data selection, and weighting"
        and source["source"]["table"] == 2
        and source["source"]["pdf_pages"] == [18, 19, 20]
    )
    checks["49_si_rows"] = len(source["rows"]) == len(row_manifest) == 49
    checks["1498_expanded_entries"] = len(entries) == 1498

    grouped: dict[str, list[str]] = {}
    for row in dataset_eval:
        grouped.setdefault(row["Dataset"], []).append(row["Reaction"])

    expected_entries: list[tuple[str, str, str, int, int, float]] = []
    row_checks: list[bool] = []
    for row_index, (si_row, manifest_row) in enumerate(
        zip(source["rows"], row_manifest, strict=True), start=1
    ):
        dataset = str(si_row["dataset_eval_dataset"])
        available = grouped.get(dataset, [])
        if si_row["selection"] == "all":
            selected = list(available)
            expected_datapoints = "All"
        else:
            selected = [
                str(si_row["reaction_id_template"]).format(index=index)
                for index in si_row["selection"]
            ]
            expected_datapoints = ",".join(selected)
        positions = [available.index(reaction) + 1 for reaction in selected if reaction in available]
        weight_spec = str(si_row["weight"])
        expected_coach_weight = "Shrink" if weight_spec == "1/sqrt(j)" else weight_spec
        row_checks.append(
            len(selected) == int(si_row["count"])
            and len(positions) == len(selected)
            and positions == sorted(positions)
            and len(set(selected)) == len(selected)
            and manifest_row["Dataset"] == dataset
            and manifest_row["datapoints"] == expected_datapoints
            and manifest_row["weights"] == expected_coach_weight
            and manifest_row["set_or_subset"] == str(si_row["set_or_subset"])
            and manifest_row["property_class"] == str(si_row["class"])
            and int(manifest_row["published_count"]) == int(si_row["count"])
        )
        for selection_index, (reaction, dataset_order) in enumerate(
            zip(selected, positions, strict=True), start=1
        ):
            weight = (
                1.0 / math.sqrt(selection_index)
                if weight_spec == "1/sqrt(j)"
                else float(si_row["weight"])
            )
            expected_entries.append(
                (
                    str(si_row["set_or_subset"]),
                    str(si_row["class"]),
                    dataset,
                    dataset_order,
                    selection_index,
                    weight,
                )
            )

    checks["every_si_row_matches_row_manifest_and_dataset_eval"] = all(row_checks)
    entry_checks: list[bool] = []
    for global_index, (entry, expected) in enumerate(
        zip(entries, expected_entries, strict=True), start=1
    ):
        subset, property_class, dataset, dataset_order, selection_index, weight = expected
        entry_checks.append(
            int(entry["global_index"]) == global_index
            and entry["set_or_subset"] == subset
            and entry["property_class"] == property_class
            and entry["dataset_eval_dataset"] == dataset
            and entry["reaction"] == grouped[dataset][dataset_order - 1]
            and int(entry["dataset_order"]) == dataset_order
            and int(entry["selection_index"]) == selection_index
            and math.isclose(float(entry["objective_weight"]), weight, rel_tol=0.0, abs_tol=1e-15)
        )
    checks["every_entry_dataset_reaction_order_and_weight"] = all(entry_checks)

    ae18 = [entry for entry in entries if entry["set_or_subset"] == "AE18"]
    checks["ae18_18_entries"] = len(ae18) == 18
    checks["ae18_exact_one_over_sqrt_j"] = all(
        math.isclose(
            float(entry["objective_weight"]),
            1.0 / math.sqrt(index),
            rel_tol=0.0,
            abs_tol=1e-15,
        )
        for index, entry in enumerate(ae18, start=1)
    )
    checks["no_duplicate_set_reaction_pairs"] = len(
        {(entry["set_or_subset"], entry["reaction"]) for entry in entries}
    ) == len(entries)
    checks["positive_finite_weights"] = all(
        math.isfinite(float(entry["objective_weight"]))
        and float(entry["objective_weight"]) > 0.0
        for entry in entries
    )
    checks["provenance_output_hashes"] = (
        provenance["outputs"]["row_manifest_sha256"] == sha256(ROWS)
        and provenance["outputs"]["entry_manifest_sha256"] == sha256(ENTRIES)
        and provenance["authority"]["transcription_sha256"] == sha256(SOURCE)
        and provenance["dataset_eval"]["sha256"] == sha256(DATASET_EVAL)
    )

    details["row_count"] = len(row_manifest)
    details["entry_count"] = len(entries)
    details["partial_selection_rows"] = sum(
        row["selection"] != "all" for row in source["rows"]
    )
    details["dataset_eval_datasets_used"] = len(
        {row["dataset_eval_dataset"] for row in source["rows"]}
    )
    report = {"passed": all(checks.values()), "checks": checks, "details": details}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
