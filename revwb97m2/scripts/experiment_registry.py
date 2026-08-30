#!/usr/bin/env python3
"""Create immutable experiment configs and maintain the experiment registry."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required by experiment_registry.py") from exc


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments" / "registry.csv"
SUMMARY = ROOT / "EXPERIMENTS.md"
STATUSES = ("succeed", "fail", "not start")
FIELDS = (
    "experiment_id",
    "created_at",
    "status",
    "description",
    "model",
    "profile",
    "sparsity",
    "pass",
    "config_path",
    "config_sha256",
    "last_updated_at",
    "result_path",
)
ID_PATTERN = re.compile(
    r"^(?P<model>[a-z0-9]+)-(?P<profile>[a-z0-9]+)-"
    r"s(?P<sparsity>[0-9]+|na)-p(?P<pass>[0-9]+)-(?P<hash>[0-9a-f]{8})$"
)


def now_local() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_registry() -> list[dict[str, str]]:
    if not REGISTRY.is_file():
        return []
    with REGISTRY.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f"Unexpected registry columns: {reader.fieldnames}")
        return list(reader)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def csv_text(rows: list[dict[str, str]]) -> str:
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        handle.seek(0)
        return handle.read()


def markdown_text(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Experiment registry",
        "",
        "This table is generated from `experiments/registry.csv`. Use",
        "`scripts/experiment_registry.py create` when freezing a new experiment and",
        "`scripts/experiment_registry.py mark` after every completed run attempt.",
        "",
        "| Experiment | Created | Status | Description |",
        "|---|---|---|---|",
    ]
    for row in sorted(rows, key=lambda item: (item["created_at"], item["experiment_id"])):
        identifier = row["experiment_id"]
        config_link = row["config_path"]
        description = row["description"].replace("|", "\\|")
        lines.append(
            f"| [`{identifier}`]({config_link}) | {row['created_at']} | "
            f"**{row['status']}** | {description} |"
        )
    lines.extend(
        [
            "",
            "Status values are restricted to `succeed`, `fail`, and `not start`.",
            "The immutable config hash and result locations are retained in the CSV.",
            "",
        ]
    )
    return "\n".join(lines)


def save_registry(rows: list[dict[str, str]]) -> None:
    atomic_write(REGISTRY, csv_text(rows))
    atomic_write(SUMMARY, markdown_text(rows))


def clean_token(value: str, label: str) -> str:
    token = value.lower()
    if not re.fullmatch(r"[a-z0-9]+", token):
        raise ValueError(f"{label} must contain only lowercase letters and digits")
    return token


def make_id(model: str, profile: str, sparsity: str, pass_number: str, digest: str) -> str:
    model = clean_token(model, "model")
    profile = clean_token(profile, "profile")
    sparsity = sparsity.lower()
    if sparsity != "na":
        sparsity = str(int(sparsity))
    pass_number = str(int(pass_number))
    return f"{model}-{profile}-s{sparsity}-p{pass_number}-{digest[:8]}"


def validate_structured_config(source: Path, args: argparse.Namespace) -> None:
    with source.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    required_sections = {"experiment", "provenance", "inputs", "model", "solver", "execution"}
    missing_sections = sorted(required_sections - set(config or {}))
    if missing_sections:
        raise ValueError(f"Structured experiment config is missing sections: {missing_sections}")
    identity = config["experiment"]
    expected = {
        "model": args.model.lower(),
        "profile": args.profile.lower(),
        "sparsity": args.sparsity.lower(),
        "pass": str(int(args.pass_number)),
        "description": args.description,
    }
    observed = {
        "model": str(identity.get("model", "")).lower(),
        "profile": str(identity.get("profile", "")).lower(),
        "sparsity": str(identity.get("sparsity", "")).lower(),
        "pass": str(identity.get("pass", "")),
        "description": str(identity.get("description", "")),
    }
    if observed != expected:
        raise ValueError(f"CLI/config identity mismatch: expected {expected}, observed {observed}")
    serialized = source.read_text(encoding="utf-8")
    if "<fill-before-create>" in serialized:
        raise ValueError("Config still contains <fill-before-create> placeholders")


def create(args: argparse.Namespace) -> int:
    source = args.config.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if "\n" in args.description or "\r" in args.description:
        raise ValueError("description must be one line")
    validate_structured_config(source, args)
    digest = sha256(source)
    identifier = make_id(args.model, args.profile, args.sparsity, args.pass_number, digest)
    rows = read_registry()
    if any(row["experiment_id"] == identifier for row in rows):
        raise ValueError(f"Experiment already exists: {identifier}")
    experiment_dir = ROOT / "experiments" / identifier
    experiment_dir.mkdir(parents=True, exist_ok=False)
    destination = experiment_dir / "config.yaml"
    shutil.copyfile(source, destination)
    destination.chmod(0o444)
    created_at = args.created_at or now_local()
    rows.append(
        {
            "experiment_id": identifier,
            "created_at": created_at,
            "status": "not start",
            "description": args.description,
            "model": args.model.lower(),
            "profile": args.profile.lower(),
            "sparsity": args.sparsity.lower(),
            "pass": str(int(args.pass_number)),
            "config_path": str(destination.relative_to(ROOT)),
            "config_sha256": digest,
            "last_updated_at": created_at,
            "result_path": "",
        }
    )
    save_registry(rows)
    print(identifier)
    return 0


def mark(args: argparse.Namespace) -> int:
    rows = read_registry()
    matches = [row for row in rows if row["experiment_id"] == args.experiment_id]
    if len(matches) != 1:
        raise KeyError(f"Expected one registry row for {args.experiment_id!r}, found {len(matches)}")
    row = matches[0]
    row["status"] = args.status
    row["last_updated_at"] = args.updated_at or now_local()
    if args.result_path is not None:
        row["result_path"] = args.result_path
    save_registry(rows)
    print(f"{args.experiment_id}: {args.status}")
    return 0


def render(_: argparse.Namespace) -> int:
    rows = read_registry()
    atomic_write(SUMMARY, markdown_text(rows))
    print(SUMMARY)
    return 0


def validate(_: argparse.Namespace) -> int:
    rows = read_registry()
    failures: list[str] = []
    identifiers = [row["experiment_id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        failures.append("duplicate experiment IDs")
    for row in rows:
        identifier = row["experiment_id"]
        match = ID_PATTERN.fullmatch(identifier)
        if not match:
            failures.append(f"invalid ID: {identifier}")
            continue
        if row["status"] not in STATUSES:
            failures.append(f"invalid status for {identifier}: {row['status']}")
        if "\n" in row["description"] or "\r" in row["description"]:
            failures.append(f"multiline description: {identifier}")
        config = ROOT / row["config_path"]
        if not config.is_file():
            failures.append(f"missing config: {identifier}")
            continue
        observed_hash = sha256(config)
        if observed_hash != row["config_sha256"]:
            failures.append(f"config hash mismatch: {identifier}")
        if observed_hash[:8] != match.group("hash"):
            failures.append(f"ID hash mismatch: {identifier}")
        for field in ("model", "profile", "sparsity", "pass"):
            if row[field] != match.group(field):
                failures.append(f"ID/{field} mismatch: {identifier}")
    if not SUMMARY.is_file() or SUMMARY.read_text(encoding="utf-8") != markdown_text(rows):
        failures.append("EXPERIMENTS.md is not synchronized with registry.csv")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print(f"PASS {len(rows)} registered experiments")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="freeze a config and register a not-started experiment")
    create_parser.add_argument("--config", type=Path, required=True)
    create_parser.add_argument("--model", required=True, help="for example r2")
    create_parser.add_argument("--profile", required=True, help="for example c0, c1, or smoke")
    create_parser.add_argument("--sparsity", required=True, help="integer or na")
    create_parser.add_argument("--pass-number", required=True, help="nonnegative integer")
    create_parser.add_argument("--description", required=True)
    create_parser.add_argument("--created-at", help="ISO-8601 timestamp; defaults to local now")
    create_parser.set_defaults(func=create)

    mark_parser = subparsers.add_parser("mark", help="update status after a run attempt")
    mark_parser.add_argument("--experiment-id", required=True)
    mark_parser.add_argument("--status", required=True, choices=STATUSES)
    mark_parser.add_argument("--result-path")
    mark_parser.add_argument("--updated-at", help="ISO-8601 timestamp; defaults to local now")
    mark_parser.set_defaults(func=mark)

    render_parser = subparsers.add_parser("render", help="regenerate EXPERIMENTS.md")
    render_parser.set_defaults(func=render)
    validate_parser = subparsers.add_parser("validate", help="verify IDs, hashes, statuses, and summary synchronization")
    validate_parser.set_defaults(func=validate)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    try:
        exit_code = arguments.func(arguments)
    except (FileExistsError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        exit_code = 2
    raise SystemExit(exit_code)
