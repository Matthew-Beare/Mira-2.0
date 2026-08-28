"""Generate and validate machine-readable feature state from canonical FEATURES.md.

FEATURES.md remains the only editable feature authority. This module parses only
its `## Feature index` section, validates the semantic dependency graph, and
emits a deterministic JSON projection tied to the exact source-byte SHA-256.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Sequence


_REGISTRY_SCHEMA_VERSION = 1
_FEATURE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{3}$")
_FEATURE_ROW_RE = re.compile(
    r"^- `(?P<id>[^`]+)` \| (?P<title>.*?) \| (?P<requirement>.*?) \| "
    r"(?P<evidence>.*?) \| (?P<deps>.*?)$"
)


class FeatureRegistryError(Exception):
    """Raised when canonical feature source cannot form a valid registry."""


@dataclass(frozen=True)
class FeatureRecord:
    feature_id: str
    title: str
    requirement: str
    evidence: str
    dependencies: tuple[str, ...]


@dataclass(frozen=True)
class FeatureRegistry:
    source_path: str
    source_sha256: str
    features: tuple[FeatureRecord, ...]

    def feature_map(self) -> dict[str, FeatureRecord]:
        return {feature.feature_id: feature for feature in self.features}

    def projection(self) -> dict[str, object]:
        return {
            "schema_version": _REGISTRY_SCHEMA_VERSION,
            "source": {
                "path": self.source_path,
                "sha256": self.source_sha256,
            },
            "features": [
                {
                    "id": feature.feature_id,
                    "title": feature.title,
                    "requirement": feature.requirement,
                    "evidence": feature.evidence,
                    "dependencies": list(feature.dependencies),
                }
                for feature in sorted(self.features, key=lambda item: item.feature_id)
            ],
        }

    def json_bytes(self) -> bytes:
        return (
            json.dumps(
                self.projection(),
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")


def load_registry(path: str | Path) -> FeatureRegistry:
    source_path = Path(path)
    try:
        raw = source_path.read_bytes()
    except OSError as exc:
        raise FeatureRegistryError(f"cannot read feature source: {source_path}") from exc
    return parse_registry_bytes(raw, source_path=source_path.as_posix())


def parse_registry_bytes(raw: bytes, *, source_path: str = "FEATURES.md") -> FeatureRegistry:
    if not isinstance(raw, bytes):
        raise FeatureRegistryError("feature source must be bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FeatureRegistryError("feature source must be UTF-8") from exc
    records = _parse_feature_index(text)
    _validate_records(records)
    return FeatureRegistry(
        source_path=source_path,
        source_sha256=hashlib.sha256(raw).hexdigest(),
        features=tuple(sorted(records, key=lambda item: item.feature_id)),
    )


def _parse_feature_index(text: str) -> list[FeatureRecord]:
    lines = text.splitlines()
    section_indexes = [index for index, line in enumerate(lines) if line == "## Feature index"]
    if len(section_indexes) != 1:
        raise FeatureRegistryError(
            "FEATURES.md must contain exactly one canonical '## Feature index' section"
        )
    start = section_indexes[0] + 1
    records: list[FeatureRecord] = []
    for line_number, line in enumerate(lines[start:], start=start + 1):
        if line.startswith("## "):
            break
        if not line.startswith("- "):
            continue
        match = _FEATURE_ROW_RE.fullmatch(line)
        if match is None:
            raise FeatureRegistryError(
                f"malformed feature row at line {line_number}: {line}"
            )
        feature_id = match.group("id")
        title = match.group("title").strip()
        requirement = match.group("requirement").strip()
        evidence = match.group("evidence").strip()
        deps_field = match.group("deps").strip()
        if not title or not requirement or not evidence:
            raise FeatureRegistryError(
                f"feature {feature_id!r} has an empty title/requirement/evidence field"
            )
        if deps_field == "-":
            dependencies: tuple[str, ...] = ()
        else:
            raw_dependencies = [value.strip() for value in deps_field.split(",")]
            if any(not value for value in raw_dependencies):
                raise FeatureRegistryError(
                    f"feature {feature_id!r} has malformed dependency list"
                )
            if len(set(raw_dependencies)) != len(raw_dependencies):
                raise FeatureRegistryError(
                    f"feature {feature_id!r} repeats a dependency"
                )
            dependencies = tuple(sorted(raw_dependencies))
        records.append(
            FeatureRecord(
                feature_id=feature_id,
                title=title,
                requirement=requirement,
                evidence=evidence,
                dependencies=dependencies,
            )
        )
    if not records:
        raise FeatureRegistryError("canonical Feature index contains no feature records")
    return records


def _validate_records(records: Sequence[FeatureRecord]) -> None:
    by_id: dict[str, FeatureRecord] = {}
    for record in records:
        if not _FEATURE_ID_RE.fullmatch(record.feature_id):
            raise FeatureRegistryError(f"invalid stable feature ID: {record.feature_id}")
        if record.feature_id in by_id:
            raise FeatureRegistryError(f"duplicate stable feature ID: {record.feature_id}")
        by_id[record.feature_id] = record

    for record in sorted(records, key=lambda item: item.feature_id):
        for dependency in record.dependencies:
            if dependency == record.feature_id:
                raise FeatureRegistryError(
                    f"feature {record.feature_id} cannot depend on itself"
                )
            if dependency not in by_id:
                raise FeatureRegistryError(
                    f"feature {record.feature_id} depends on unknown feature ID {dependency}"
                )

    cycle = _find_cycle(by_id)
    if cycle is not None:
        raise FeatureRegistryError("feature dependency cycle: " + " -> ".join(cycle))


def _find_cycle(by_id: dict[str, FeatureRecord]) -> tuple[str, ...] | None:
    state: dict[str, int] = {}
    stack: list[str] = []
    positions: dict[str, int] = {}

    def visit(feature_id: str) -> tuple[str, ...] | None:
        state[feature_id] = 1
        positions[feature_id] = len(stack)
        stack.append(feature_id)
        for dependency in sorted(by_id[feature_id].dependencies):
            dependency_state = state.get(dependency, 0)
            if dependency_state == 0:
                cycle = visit(dependency)
                if cycle is not None:
                    return cycle
            elif dependency_state == 1:
                start = positions[dependency]
                return tuple(stack[start:] + [dependency])
        stack.pop()
        positions.pop(feature_id, None)
        state[feature_id] = 2
        return None

    for feature_id in sorted(by_id):
        if state.get(feature_id, 0) == 0:
            cycle = visit(feature_id)
            if cycle is not None:
                return cycle
    return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate/generate the MIRA machine-readable feature registry"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="validate canonical feature source")
    check.add_argument("path", nargs="?", default="FEATURES.md")
    emit = subparsers.add_parser("json", help="emit deterministic JSON projection")
    emit.add_argument("path", nargs="?", default="FEATURES.md")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        registry = load_registry(args.path)
    except FeatureRegistryError as exc:
        print(f"feature-registry error: {exc}", file=sys.stderr)
        return 1
    if args.command == "check":
        print(
            f"feature registry valid: {len(registry.features)} features; "
            f"sha256={registry.source_sha256}"
        )
        return 0
    sys.stdout.buffer.write(registry.json_bytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
