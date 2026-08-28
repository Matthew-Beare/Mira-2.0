"""Validate MIRA production component ownership and direct verification evidence.

The ownership manifest is authored governance state. It maps production artifacts to
bounded components while FEATURES.md remains feature truth and BACKLOG.md remains work
truth. The validator fails closed on unowned/overlapping production code, dangling
feature/work references, or verification that does not materially import owned Python
modules.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Iterable, Sequence

from .feature_registry import FeatureRegistryError, load_registry


_MANIFEST_SCHEMA_VERSION = 1
_COMPONENT_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_WORK_ROW_RE = re.compile(
    r"^\|\s*(?:[^|]+\|\s*)?`(?P<work_id>[^`]+)`\s*\|"
)


class CodeOwnershipError(Exception):
    """Raised when production ownership/evidence is incomplete or contradictory."""


@dataclass(frozen=True)
class ProductionRoot:
    path: str
    profile: str
    suffixes: tuple[str, ...]


@dataclass(frozen=True)
class ComponentOwnership:
    component_id: str
    responsibility: str
    why_separate: str
    owned_paths: tuple[str, ...]
    feature_ids: tuple[str, ...]
    work_ids: tuple[str, ...]
    verification: tuple[str, ...]


@dataclass(frozen=True)
class OwnershipManifest:
    production_roots: tuple[ProductionRoot, ...]
    components: tuple[ComponentOwnership, ...]


@dataclass(frozen=True)
class OwnershipReport:
    component_count: int
    production_artifact_count: int


def _require_mapping(value: object, *, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise CodeOwnershipError(f"{field} must be an object")
    return value


def _require_string(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CodeOwnershipError(f"{field} must be a non-empty string")
    return value.strip()


def _require_string_list(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise CodeOwnershipError(f"{field} must be a non-empty list")
    items = tuple(_require_string(item, field=field) for item in value)
    if len(set(items)) != len(items):
        raise CodeOwnershipError(f"{field} contains duplicates")
    return items


def _normalize_relative_path(value: object, *, field: str) -> str:
    text = _require_string(value, field=field)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or path.as_posix() in {".", ""}:
        raise CodeOwnershipError(f"{field} must be a safe repository-relative path: {text}")
    return path.as_posix()


def load_manifest(path: str | Path) -> OwnershipManifest:
    manifest_path = Path(path)
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CodeOwnershipError(f"cannot read ownership manifest: {manifest_path}") from exc
    root = _require_mapping(payload, field="manifest")
    if root.get("schema_version") != _MANIFEST_SCHEMA_VERSION:
        raise CodeOwnershipError(
            f"unsupported ownership schema_version: {root.get('schema_version')!r}"
        )

    raw_roots = root.get("production_roots")
    if not isinstance(raw_roots, list) or not raw_roots:
        raise CodeOwnershipError("production_roots must be a non-empty list")
    production_roots: list[ProductionRoot] = []
    seen_root_paths: set[str] = set()
    for index, raw_root in enumerate(raw_roots):
        item = _require_mapping(raw_root, field=f"production_roots[{index}]")
        root_path = _normalize_relative_path(item.get("path"), field="production root path")
        if root_path in seen_root_paths:
            raise CodeOwnershipError(f"duplicate production root: {root_path}")
        seen_root_paths.add(root_path)
        profile = _require_string(item.get("profile"), field="production root profile")
        suffixes = _require_string_list(item.get("suffixes"), field="production root suffixes")
        if any(not suffix.startswith(".") for suffix in suffixes):
            raise CodeOwnershipError(f"production root {root_path} has invalid suffix")
        production_roots.append(
            ProductionRoot(path=root_path, profile=profile, suffixes=tuple(sorted(suffixes)))
        )

    raw_components = root.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        raise CodeOwnershipError("components must be a non-empty list")
    components: list[ComponentOwnership] = []
    seen_component_ids: set[str] = set()
    for index, raw_component in enumerate(raw_components):
        item = _require_mapping(raw_component, field=f"components[{index}]")
        component_id = _require_string(item.get("id"), field="component id")
        if not _COMPONENT_ID_RE.fullmatch(component_id):
            raise CodeOwnershipError(f"invalid component id: {component_id}")
        if component_id in seen_component_ids:
            raise CodeOwnershipError(f"duplicate component id: {component_id}")
        seen_component_ids.add(component_id)
        owned_paths = tuple(
            sorted(
                _normalize_relative_path(value, field=f"{component_id} owned path")
                for value in _require_string_list(
                    item.get("owned_paths"), field=f"{component_id} owned_paths"
                )
            )
        )
        verification = tuple(
            sorted(
                _normalize_relative_path(value, field=f"{component_id} verification path")
                for value in _require_string_list(
                    item.get("verification"), field=f"{component_id} verification"
                )
            )
        )
        components.append(
            ComponentOwnership(
                component_id=component_id,
                responsibility=_require_string(
                    item.get("responsibility"), field=f"{component_id} responsibility"
                ),
                why_separate=_require_string(
                    item.get("why_separate"), field=f"{component_id} why_separate"
                ),
                owned_paths=owned_paths,
                feature_ids=tuple(
                    sorted(
                        _require_string_list(
                            item.get("feature_ids"), field=f"{component_id} feature_ids"
                        )
                    )
                ),
                work_ids=tuple(
                    sorted(
                        _require_string_list(
                            item.get("work_ids"), field=f"{component_id} work_ids"
                        )
                    )
                ),
                verification=verification,
            )
        )
    return OwnershipManifest(
        production_roots=tuple(production_roots),
        components=tuple(sorted(components, key=lambda item: item.component_id)),
    )


def _load_work_ids(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CodeOwnershipError(f"cannot read backlog: {path}") from exc
    work_ids: set[str] = set()
    for line in lines:
        match = _WORK_ROW_RE.match(line)
        if match is not None:
            work_ids.add(match.group("work_id"))
    if not work_ids:
        raise CodeOwnershipError("BACKLOG.md contains no machine-readable work rows")
    return work_ids


def _is_within(path: str, root: str) -> bool:
    parts = PurePosixPath(path).parts
    root_parts = PurePosixPath(root).parts
    return len(parts) >= len(root_parts) and parts[: len(root_parts)] == root_parts


def _enumerate_production_files(
    repository_root: Path, roots: Sequence[ProductionRoot]
) -> tuple[set[str], dict[str, str]]:
    production_files: set[str] = set()
    profiles: dict[str, str] = {}
    for root in roots:
        absolute_root = repository_root / root.path
        if not absolute_root.is_dir():
            raise CodeOwnershipError(f"production root does not exist: {root.path}")
        for candidate in absolute_root.rglob("*"):
            if not candidate.is_file() or "__pycache__" in candidate.parts:
                continue
            if candidate.suffix not in root.suffixes:
                continue
            relative = candidate.relative_to(repository_root).as_posix()
            if relative in production_files:
                raise CodeOwnershipError(
                    f"production artifact appears in overlapping roots: {relative}"
                )
            production_files.add(relative)
            profiles[relative] = root.profile
    return production_files, profiles


def _python_module(path: str) -> str:
    pure = PurePosixPath(path)
    if pure.suffix != ".py":
        raise CodeOwnershipError(f"python profile received non-Python path: {path}")
    parts = list(pure.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    if not parts:
        raise CodeOwnershipError(f"cannot derive Python module from path: {path}")
    return ".".join(parts)


def _imported_python_modules(paths: Iterable[Path]) -> set[str]:
    imported: set[str] = set()
    for path in paths:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=path.as_posix())
        except (OSError, SyntaxError) as exc:
            raise CodeOwnershipError(f"cannot inspect Python verification: {path}") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
    return imported


def validate_repository(
    *,
    repository_root: str | Path = ".",
    manifest_path: str | Path = "project/code_ownership.json",
    features_path: str | Path = "FEATURES.md",
    backlog_path: str | Path = "BACKLOG.md",
) -> OwnershipReport:
    repo = Path(repository_root).resolve()
    manifest_file = repo / manifest_path
    manifest = load_manifest(manifest_file)
    production_files, profiles = _enumerate_production_files(repo, manifest.production_roots)

    try:
        feature_ids = set(load_registry(repo / features_path).feature_map())
    except FeatureRegistryError as exc:
        raise CodeOwnershipError(f"feature registry invalid: {exc}") from exc
    work_ids = _load_work_ids(repo / backlog_path)

    owner_by_path: dict[str, str] = {}
    for component in manifest.components:
        for feature_id in component.feature_ids:
            if feature_id not in feature_ids:
                raise CodeOwnershipError(
                    f"component {component.component_id} references unknown feature ID {feature_id}"
                )
        for work_id in component.work_ids:
            if work_id not in work_ids:
                raise CodeOwnershipError(
                    f"component {component.component_id} references unknown work ID {work_id}"
                )

        verification_paths: list[Path] = []
        for verification in component.verification:
            if not verification.startswith("tests/") or not verification.endswith(".py"):
                raise CodeOwnershipError(
                    f"component {component.component_id} verification is not a Python test path: {verification}"
                )
            absolute_verification = repo / verification
            if not absolute_verification.is_file():
                raise CodeOwnershipError(
                    f"component {component.component_id} verification path does not exist: {verification}"
                )
            verification_paths.append(absolute_verification)
        imported_modules = _imported_python_modules(verification_paths)

        for owned_path in component.owned_paths:
            absolute_owned = repo / owned_path
            if not absolute_owned.is_file():
                raise CodeOwnershipError(
                    f"component {component.component_id} owned path does not exist: {owned_path}"
                )
            if owned_path not in production_files:
                raise CodeOwnershipError(
                    f"component {component.component_id} owns path outside production roots: {owned_path}"
                )
            previous_owner = owner_by_path.get(owned_path)
            if previous_owner is not None:
                raise CodeOwnershipError(
                    f"production artifact {owned_path} has overlapping owners: "
                    f"{previous_owner}, {component.component_id}"
                )
            owner_by_path[owned_path] = component.component_id

            profile = profiles[owned_path]
            if profile == "python":
                module = _python_module(owned_path)
                if not any(
                    imported == module or imported.startswith(module + ".")
                    for imported in imported_modules
                ):
                    raise CodeOwnershipError(
                        f"component {component.component_id} has no direct Python verification import for {owned_path}"
                    )
            else:
                raise CodeOwnershipError(
                    f"unsupported production verification profile {profile!r} for {owned_path}"
                )

    unowned = sorted(production_files - set(owner_by_path))
    if unowned:
        raise CodeOwnershipError("unowned production artifacts: " + ", ".join(unowned))

    return OwnershipReport(
        component_count=len(manifest.components),
        production_artifact_count=len(production_files),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate MIRA production code ownership")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="validate production component ownership")
    check.add_argument("--root", default=".", help="repository root")
    check.add_argument("--manifest", default="project/code_ownership.json")
    check.add_argument("--features", default="FEATURES.md")
    check.add_argument("--backlog", default="BACKLOG.md")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = validate_repository(
            repository_root=args.root,
            manifest_path=args.manifest,
            features_path=args.features,
            backlog_path=args.backlog,
        )
    except CodeOwnershipError as exc:
        print(f"code-ownership error: {exc}", file=sys.stderr)
        return 1
    print(
        "code ownership valid: "
        f"{report.component_count} components; "
        f"{report.production_artifact_count} production artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
