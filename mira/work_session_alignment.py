"""Verify active MIRA work against Git-authoritative product direction.

This gate is intentionally narrow. It cannot decide product strategy for the
customer, but it can prevent a work session from claiming alignment when the
active work or feature IDs do not exist in the canonical authorities, or when
CURRENT_WORK omits the required feature/backlog/roadmap review.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Sequence

from .feature_registry import FeatureRegistryError, load_registry


class WorkSessionAlignmentError(Exception):
    """Raised when CURRENT_WORK is not grounded in canonical project state."""


_WORK_ROW_RE = re.compile(r"^\|\s*`(?P<id>[A-Z0-9][A-Z0-9-]+)`\s*\|")
_ACTIVE_PACKET_RE = re.compile(r"^### `(?P<id>M2-[A-Z0-9-]+)`\s+—\s+.+$")
_FIELD_RE = re.compile(r"^- \*\*(?P<label>[^*]+):\*\*\s*(?P<value>.+)$")
_BACKTICK_ID_RE = re.compile(r"`([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{3}|[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)`")


@dataclass(frozen=True)
class AlignmentReport:
    packet_id: str
    primary_work_ids: tuple[str, ...]
    feature_ids: tuple[str, ...]


def _read(path: str | Path) -> str:
    source = Path(path)
    try:
        return source.read_text(encoding="utf-8")
    except OSError as exc:
        raise WorkSessionAlignmentError(f"cannot read {source}") from exc


def parse_backlog_work_ids(text: str) -> frozenset[str]:
    ids = {
        match.group("id")
        for line in text.splitlines()
        if (match := _WORK_ROW_RE.match(line)) is not None
    }
    if not ids:
        raise WorkSessionAlignmentError("BACKLOG.md contains no parseable work IDs")
    return frozenset(ids)


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading) + 1
    except ValueError as exc:
        raise WorkSessionAlignmentError(f"CURRENT_WORK.md missing {heading!r}") from exc
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def _extract_active_packet(active_section: str) -> tuple[str, dict[str, str]]:
    packet_id: str | None = None
    fields: dict[str, str] = {}
    for line in active_section.splitlines():
        if packet_id is None:
            match = _ACTIVE_PACKET_RE.match(line)
            if match is not None:
                packet_id = match.group("id")
                continue
        match = _FIELD_RE.match(line)
        if match is not None:
            fields[match.group("label").strip().lower()] = match.group("value").strip()
    if packet_id is None:
        raise WorkSessionAlignmentError("active packet section has no packet ID heading")
    return packet_id, fields


def _ids_from_field(fields: dict[str, str], label: str) -> tuple[str, ...]:
    value = fields.get(label)
    if value is None:
        raise WorkSessionAlignmentError(f"active packet missing required field: {label}")
    ids = tuple(match.group(1) for match in _BACKTICK_ID_RE.finditer(value))
    if not ids:
        raise WorkSessionAlignmentError(f"active packet field {label!r} contains no IDs")
    return ids


def check_alignment_texts(
    *,
    current_work: str,
    features: str,
    backlog: str,
    roadmap: str,
) -> AlignmentReport:
    try:
        registry = load_registry_from_text(features)
    except FeatureRegistryError as exc:
        raise WorkSessionAlignmentError(str(exc)) from exc
    feature_ids = frozenset(registry)
    work_ids = parse_backlog_work_ids(backlog)

    active = _section(current_work, "## Active packet")
    packet_id, fields = _extract_active_packet(active)
    primary_work_ids = _ids_from_field(fields, "primary work")
    primary_feature_ids = _ids_from_field(fields, "primary features")
    related_feature_ids = _ids_from_field(fields, "related invariants/features")

    unknown_work = sorted(set(primary_work_ids) - work_ids)
    if unknown_work:
        raise WorkSessionAlignmentError(
            "active primary work missing from BACKLOG.md: " + ", ".join(unknown_work)
        )

    referenced_features = set(primary_feature_ids) | set(related_feature_ids)
    unknown_features = sorted(referenced_features - feature_ids)
    if unknown_features:
        raise WorkSessionAlignmentError(
            "active features missing from FEATURES.md: " + ", ".join(unknown_features)
        )

    alignment = _section(current_work, "## Session-start alignment verification — 2026-08-29")
    for authority in ("### `FEATURES.md`", "### `BACKLOG.md`", "### `ROADMAP.md`"):
        if authority not in alignment:
            raise WorkSessionAlignmentError(
                f"session-start alignment missing authority review: {authority}"
            )
    if "### Direction result" not in alignment or "ALIGNED" not in alignment:
        raise WorkSessionAlignmentError(
            "session-start alignment must record an explicit ALIGNED direction result"
        )

    if "ordinary Google" not in roadmap and "Personal Google" not in roadmap:
        raise WorkSessionAlignmentError(
            "ROADMAP.md no longer contains the Personal Google product direction"
        )

    return AlignmentReport(
        packet_id=packet_id,
        primary_work_ids=tuple(sorted(set(primary_work_ids))),
        feature_ids=tuple(sorted(referenced_features)),
    )


def load_registry_from_text(text: str) -> tuple[str, ...]:
    # Keep FEATURES.md parsing owned by the canonical feature-registry parser.
    from .feature_registry import parse_registry_bytes

    registry = parse_registry_bytes(text.encode("utf-8"), source_path="FEATURES.md")
    return tuple(feature.feature_id for feature in registry.features)


def check_paths(
    *,
    current_work_path: str | Path = "CURRENT_WORK.md",
    features_path: str | Path = "FEATURES.md",
    backlog_path: str | Path = "BACKLOG.md",
    roadmap_path: str | Path = "ROADMAP.md",
) -> AlignmentReport:
    return check_alignment_texts(
        current_work=_read(current_work_path),
        features=_read(features_path),
        backlog=_read(backlog_path),
        roadmap=_read(roadmap_path),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify MIRA work-session direction")
    parser.add_argument("command", choices=("check",))
    parser.add_argument("--current-work", default="CURRENT_WORK.md")
    parser.add_argument("--features", default="FEATURES.md")
    parser.add_argument("--backlog", default="BACKLOG.md")
    parser.add_argument("--roadmap", default="ROADMAP.md")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = check_paths(
            current_work_path=args.current_work,
            features_path=args.features,
            backlog_path=args.backlog,
            roadmap_path=args.roadmap,
        )
    except WorkSessionAlignmentError as exc:
        print(f"work-session-alignment error: {exc}", file=sys.stderr)
        return 1
    print(
        "work-session alignment valid: "
        f"packet={report.packet_id}; "
        f"work={','.join(report.primary_work_ids)}; "
        f"features={','.join(report.feature_ids)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
