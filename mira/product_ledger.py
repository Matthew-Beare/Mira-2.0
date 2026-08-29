"""Deterministic MIRA product lifecycle projection.

FEATURES.md and BACKLOG.md remain the only editable product authorities. This
module combines their current state into one machine-readable projection so a
work session can distinguish accepted product scope from implementation work,
and completed work can stay visible without being selected again by accident.

The projection is deliberately conservative. Free-form backlog status text is
normalized only when it begins with a recognized lifecycle term. Ambiguous text
is reported as ``unknown`` rather than being promoted to completed by guesswork.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Sequence

from .feature_registry import FeatureRegistry, FeatureRegistryError, parse_registry_bytes


_LEDGER_SCHEMA_VERSION = 1
_CLASS_PRIORITY = {
    "BLOCKER": 0,
    "PREREQUISITE": 1,
    "VERTICAL": 2,
    "HARDENING": 3,
    "ENHANCEMENT": 4,
    "LATER": 5,
}
_INACTIVE_STATES = frozenset({"completed", "deferred", "paused", "split", "rejected"})


class ProductLedgerError(Exception):
    """Raised when canonical product authorities cannot form a valid ledger."""


@dataclass(frozen=True)
class WorkRecord:
    work_id: str
    work_class: str
    description: str
    dependencies: str
    status: str
    lifecycle_state: str
    source_order: int


@dataclass(frozen=True)
class ProductLedger:
    feature_registry: FeatureRegistry
    backlog_path: str
    backlog_sha256: str
    work: tuple[WorkRecord, ...]

    def projection(self) -> dict[str, object]:
        features = [
            {
                "id": feature.feature_id,
                "title": feature.title,
                "requirement": feature.requirement,
                "evidence": feature.evidence,
                "dependencies": list(feature.dependencies),
            }
            for feature in self.feature_registry.features
        ]
        work = [
            {
                "id": item.work_id,
                "class": item.work_class,
                "description": item.description,
                "dependencies": item.dependencies,
                "status": item.status,
                "lifecycle_state": item.lifecycle_state,
                "source_order": item.source_order,
            }
            for item in self.work
        ]
        counts: dict[str, int] = {}
        for item in self.work:
            counts[item.lifecycle_state] = counts.get(item.lifecycle_state, 0) + 1
        return {
            "schema_version": _LEDGER_SCHEMA_VERSION,
            "sources": {
                "features": {
                    "path": self.feature_registry.source_path,
                    "sha256": self.feature_registry.source_sha256,
                },
                "backlog": {
                    "path": self.backlog_path,
                    "sha256": self.backlog_sha256,
                },
            },
            "summary": {
                "feature_count": len(features),
                "work_count": len(work),
                "work_lifecycle_counts": dict(sorted(counts.items())),
            },
            "features": features,
            "work": work,
        }

    def json_bytes(self) -> bytes:
        return (
            json.dumps(self.projection(), sort_keys=True, indent=2, ensure_ascii=False)
            + "\n"
        ).encode("utf-8")

    def selectable_work(self) -> tuple[WorkRecord, ...]:
        """Return work that has not been explicitly completed/deferred/paused/split."""

        return tuple(
            sorted(
                (item for item in self.work if item.lifecycle_state not in _INACTIVE_STATES),
                key=lambda item: (
                    _CLASS_PRIORITY.get(item.work_class, 99),
                    item.source_order,
                    item.work_id,
                ),
            )
        )


def load_product_ledger(
    features_path: str | Path = "FEATURES.md",
    backlog_path: str | Path = "BACKLOG.md",
) -> ProductLedger:
    features_source = Path(features_path)
    backlog_source = Path(backlog_path)
    try:
        feature_bytes = features_source.read_bytes()
        backlog_bytes = backlog_source.read_bytes()
    except OSError as exc:
        raise ProductLedgerError(f"cannot read product authority: {exc}") from exc
    try:
        feature_registry = parse_registry_bytes(
            feature_bytes, source_path=features_source.as_posix()
        )
    except FeatureRegistryError as exc:
        raise ProductLedgerError(str(exc)) from exc
    try:
        backlog_text = backlog_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProductLedgerError("BACKLOG.md must be UTF-8") from exc
    return ProductLedger(
        feature_registry=feature_registry,
        backlog_path=backlog_source.as_posix(),
        backlog_sha256=hashlib.sha256(backlog_bytes).hexdigest(),
        work=parse_backlog(backlog_text),
    )


def parse_backlog(text: str) -> tuple[WorkRecord, ...]:
    """Parse every Markdown table containing a ``Work ID`` column."""

    lines = text.splitlines()
    records: list[WorkRecord] = []
    seen: dict[str, int] = {}
    source_order = 0
    index = 0
    while index < len(lines):
        line = lines[index]
        if not _is_table_row(line):
            index += 1
            continue
        header = _split_table_row(line)
        if "Work ID" not in header:
            index += 1
            continue
        if index + 1 >= len(lines) or not _is_separator_row(lines[index + 1]):
            raise ProductLedgerError(
                f"BACKLOG.md Work ID table at line {index + 1} has no separator row"
            )
        indexes = {name: position for position, name in enumerate(header)}
        required = ("Work ID", "Class", "Work", "Dependencies", "Status")
        missing = [name for name in required if name not in indexes]
        if missing:
            raise ProductLedgerError(
                "BACKLOG.md Work ID table missing columns: " + ", ".join(missing)
            )
        index += 2
        while index < len(lines) and _is_table_row(lines[index]):
            cells = _split_table_row(lines[index])
            if len(cells) != len(header):
                raise ProductLedgerError(
                    f"BACKLOG.md table row {index + 1} has {len(cells)} cells; expected {len(header)}"
                )
            work_id = _strip_code(cells[indexes["Work ID"]])
            if work_id:
                if work_id in seen:
                    raise ProductLedgerError(
                        f"duplicate backlog work ID {work_id!r} at lines {seen[work_id]} and {index + 1}"
                    )
                seen[work_id] = index + 1
                source_order += 1
                status = cells[indexes["Status"]].strip()
                records.append(
                    WorkRecord(
                        work_id=work_id,
                        work_class=cells[indexes["Class"]].strip().upper(),
                        description=cells[indexes["Work"]].strip(),
                        dependencies=cells[indexes["Dependencies"]].strip(),
                        status=status,
                        lifecycle_state=normalize_work_status(status),
                        source_order=source_order,
                    )
                )
            index += 1
    if not records:
        raise ProductLedgerError("BACKLOG.md contains no Work ID tables")
    return tuple(records)


def normalize_work_status(status: str) -> str:
    """Conservatively normalize the leading status phrase."""

    if not isinstance(status, str) or not status.strip():
        return "unknown"
    value = status.strip().lower()
    prefixes = (
        ("complete", "completed"),
        ("completed", "completed"),
        ("active", "active"),
        ("policy active", "active"),
        ("queued", "queued"),
        ("deferred", "deferred"),
        ("paused", "paused"),
        ("provisional", "provisional"),
        ("split", "split"),
        ("candidate", "candidate"),
        ("partial", "partial"),
        ("blocked", "blocked"),
        ("rejected", "rejected"),
    )
    for prefix, normalized in prefixes:
        if value.startswith(prefix):
            return normalized
    return "unknown"


def _is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def _is_separator_row(line: str) -> bool:
    if not _is_table_row(line):
        return False
    cells = _split_table_row(line)
    return bool(cells) and all(cell.replace(":", "").replace("-", "").strip() == "" for cell in cells)


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip()[1:-1].split("|")]


def _strip_code(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == "`" and stripped[-1] == "`":
        return stripped[1:-1].strip()
    return stripped


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate/query the MIRA product lifecycle ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "json", "next"):
        command = subparsers.add_parser(name)
        command.add_argument("--features", default="FEATURES.md")
        command.add_argument("--backlog", default="BACKLOG.md")
        if name == "next":
            command.add_argument("--limit", type=int, default=20)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        ledger = load_product_ledger(args.features, args.backlog)
    except ProductLedgerError as exc:
        print(f"product-ledger error: {exc}", file=sys.stderr)
        return 1
    if args.command == "check":
        projection = ledger.projection()
        summary = projection["summary"]
        print(
            "product ledger valid: "
            f"features={summary['feature_count']}; work={summary['work_count']}; "
            f"states={json.dumps(summary['work_lifecycle_counts'], sort_keys=True)}"
        )
        return 0
    if args.command == "json":
        sys.stdout.buffer.write(ledger.json_bytes())
        return 0
    if args.limit < 1:
        print("product-ledger error: --limit must be >= 1", file=sys.stderr)
        return 1
    for item in ledger.selectable_work()[: args.limit]:
        print(
            f"{item.work_id}\t{item.work_class}\t{item.lifecycle_state}\t{item.description}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
