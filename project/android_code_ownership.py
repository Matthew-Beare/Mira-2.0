"""Validate Android production ownership and direct JVM-test evidence.

This governance gate complements the mature Python production ownership gate. It keeps
Android production source explicit without teaching the Python AST verifier to pretend
Java imports are Python modules.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
from typing import Sequence

from mira.feature_registry import FeatureRegistryError, load_registry
from mira.product_ledger import ProductLedgerError, parse_backlog


_SCHEMA_VERSION = 1
_COMPONENT_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_WORK_ROW_RE = re.compile(r"^\|\s*(?:[^|]+\|\s*)?`(?P<work_id>[^`]+)`\s*\|")


class AndroidCodeOwnershipError(Exception):
    """Raised when Android production ownership/evidence is incomplete."""


def _require_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AndroidCodeOwnershipError(f"{field} must be a non-empty string")
    return value.strip()


def _require_string_list(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise AndroidCodeOwnershipError(f"{field} must be a non-empty list")
    items = tuple(_require_string(item, field=field) for item in value)
    if len(items) != len(set(items)):
        raise AndroidCodeOwnershipError(f"{field} contains duplicates")
    return items


def _safe_path(value: object, *, field: str) -> str:
    text = _require_string(value, field=field)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or path.as_posix() in {".", ""}:
        raise AndroidCodeOwnershipError(f"{field} must be repository-relative: {text}")
    return path.as_posix()


def _load_work_ids(path: Path) -> set[str]:
    try:
        records = parse_backlog(path.read_text(encoding="utf-8"))
    except (OSError, ProductLedgerError) as exc:
        raise AndroidCodeOwnershipError(f"cannot parse backlog: {path}") from exc
    return {record.work_id for record in records}


def validate_repository(
    *,
    repository_root: str | Path = ".",
    manifest_path: str | Path = "project/android_code_ownership.json",
    features_path: str | Path = "FEATURES.md",
    backlog_path: str | Path = "BACKLOG.md",
) -> tuple[int, int]:
    repo = Path(repository_root).resolve()
    manifest_file = repo / manifest_path
    try:
        payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AndroidCodeOwnershipError(
            f"cannot read Android ownership manifest: {manifest_file}"
        ) from exc

    if not isinstance(payload, dict) or payload.get("schema_version") != _SCHEMA_VERSION:
        raise AndroidCodeOwnershipError("unsupported Android ownership schema_version")

    production_root = _safe_path(payload.get("production_root"), field="production_root")
    suffixes = _require_string_list(payload.get("suffixes"), field="suffixes")
    if any(not suffix.startswith(".") for suffix in suffixes):
        raise AndroidCodeOwnershipError("Android ownership suffixes must start with '.'")

    root = repo / production_root
    if not root.is_dir():
        raise AndroidCodeOwnershipError(f"Android production root does not exist: {production_root}")
    production_files = {
        path.relative_to(repo).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.suffix in suffixes
    }
    if not production_files:
        raise AndroidCodeOwnershipError("Android production root contains no governed source")

    try:
        feature_ids = set(load_registry(repo / features_path).feature_map())
    except FeatureRegistryError as exc:
        raise AndroidCodeOwnershipError(f"feature registry invalid: {exc}") from exc
    work_ids = _load_work_ids(repo / backlog_path)

    raw_components = payload.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        raise AndroidCodeOwnershipError("components must be a non-empty list")

    owner_by_path: dict[str, str] = {}
    seen_components: set[str] = set()
    for index, raw in enumerate(raw_components):
        if not isinstance(raw, dict):
            raise AndroidCodeOwnershipError(f"components[{index}] must be an object")
        component_id = _require_string(raw.get("id"), field="component id")
        if not _COMPONENT_ID_RE.fullmatch(component_id):
            raise AndroidCodeOwnershipError(f"invalid component id: {component_id}")
        if component_id in seen_components:
            raise AndroidCodeOwnershipError(f"duplicate component id: {component_id}")
        seen_components.add(component_id)

        _require_string(raw.get("responsibility"), field=f"{component_id} responsibility")
        _require_string(raw.get("why_separate"), field=f"{component_id} why_separate")
        owned_paths = tuple(
            _safe_path(value, field=f"{component_id} owned path")
            for value in _require_string_list(
                raw.get("owned_paths"), field=f"{component_id} owned_paths"
            )
        )
        component_features = _require_string_list(
            raw.get("feature_ids"), field=f"{component_id} feature_ids"
        )
        component_work = _require_string_list(
            raw.get("work_ids"), field=f"{component_id} work_ids"
        )
        verification = tuple(
            _safe_path(value, field=f"{component_id} verification path")
            for value in _require_string_list(
                raw.get("verification"), field=f"{component_id} verification"
            )
        )

        unknown_features = sorted(set(component_features) - feature_ids)
        if unknown_features:
            raise AndroidCodeOwnershipError(
                f"component {component_id} references unknown feature IDs: "
                + ", ".join(unknown_features)
            )
        unknown_work = sorted(set(component_work) - work_ids)
        if unknown_work:
            raise AndroidCodeOwnershipError(
                f"component {component_id} references unknown work IDs: "
                + ", ".join(unknown_work)
            )

        verification_sources: list[str] = []
        for test_path in verification:
            if "/src/test/java/" not in "/" + test_path or not test_path.endswith(".java"):
                raise AndroidCodeOwnershipError(
                    f"component {component_id} verification must be Java unit-test source: {test_path}"
                )
            absolute_test = repo / test_path
            if not absolute_test.is_file():
                raise AndroidCodeOwnershipError(
                    f"component {component_id} verification path does not exist: {test_path}"
                )
            verification_sources.append(absolute_test.read_text(encoding="utf-8"))
        verification_text = "\n".join(verification_sources)

        for owned_path in owned_paths:
            absolute_owned = repo / owned_path
            if not absolute_owned.is_file():
                raise AndroidCodeOwnershipError(
                    f"component {component_id} owned path does not exist: {owned_path}"
                )
            if owned_path not in production_files:
                raise AndroidCodeOwnershipError(
                    f"component {component_id} owns path outside Android production root: {owned_path}"
                )
            previous = owner_by_path.get(owned_path)
            if previous is not None:
                raise AndroidCodeOwnershipError(
                    f"Android production artifact {owned_path} has overlapping owners: "
                    f"{previous}, {component_id}"
                )
            owner_by_path[owned_path] = component_id

            class_name = Path(owned_path).stem
            if re.search(rf"\b{re.escape(class_name)}\b", verification_text) is None:
                raise AndroidCodeOwnershipError(
                    f"component {component_id} has no direct Java verification reference for {owned_path}"
                )

    unowned = sorted(production_files - set(owner_by_path))
    if unowned:
        raise AndroidCodeOwnershipError(
            "unowned Android production artifacts: " + ", ".join(unowned)
        )

    return len(seen_components), len(production_files)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Android production ownership")
    parser.add_argument("command", choices=("check",))
    parser.add_argument("--root", default=".")
    parser.add_argument("--manifest", default="project/android_code_ownership.json")
    args = parser.parse_args(argv)
    try:
        components, artifacts = validate_repository(
            repository_root=args.root,
            manifest_path=args.manifest,
        )
    except AndroidCodeOwnershipError as exc:
        print(f"android-code-ownership error: {exc}")
        return 1
    print(
        "Android code ownership valid: "
        f"{components} components; {artifacts} production artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
