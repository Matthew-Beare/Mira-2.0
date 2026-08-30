"""Deterministic release tooling for the no-app Personal Google starter.

Git remains the editable release authority. ``distribution/personal_google_starter.json``
describes the clean spreadsheet substrate, while the Workspace Apps Script files are
validated public artifacts. This module binds both to one canonical source SHA and can
verify an independently observed spreadsheet snapshot without embedding provider IDs,
credentials, or user state in source.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence

from .workspace_bundle import WorkspaceBundleError, load_workspace_bundle


class PersonalDistributionError(Exception):
    """Raised when the Personal starter/release material is unsafe or inconsistent."""


_SOURCE_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_PROVIDER_PATTERNS = (
    re.compile(r"AKfycb[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b\d{10,}-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com\b"),
    re.compile(r"\b[A-Za-z0-9_-]{20,}\.iam\.gserviceaccount\.com\b"),
    re.compile(r"https://docs\.google\.com/(?:spreadsheets|document|presentation)/d/[A-Za-z0-9_-]+"),
)
_SECRET_MARKERS = (
    "BEGIN PRIVATE KEY",
    "client_secret",
    "access_token",
    "refresh_token",
    "MIRA_BEARER_TOKEN",
    "Authorization: Bearer",
)
_REQUIRED_PRIVACY_INVARIANTS = frozenset(
    {
        "no_provider_identifiers",
        "no_credentials_or_secrets",
        "no_personal_state",
        "no_legacy_production_references",
        "empty_mutable_state_before_bootstrap",
    }
)
_REQUIRED_TAB_HEADERS = {
    "Metadata": ("Key", "Value"),
    "Resources": (
        "resource_type",
        "resource_id",
        "revision",
        "payload_json",
        "updated_at",
        "last_idempotency_key",
        "request_hash",
    ),
    "Events": (
        "event_type",
        "event_id",
        "stream_type",
        "stream_id",
        "stream_revision",
        "payload_json",
        "occurred_at",
        "idempotency_key",
    ),
    "Idempotency": (
        "idempotency_key",
        "operation",
        "request_hash",
        "result_json",
        "created_at",
        "resource_ref",
    ),
}
_REQUIRED_METADATA = {
    "schema_version": "mira-structured-state-v1",
    "store_role": "personal_google_starter",
    "environment": "mira_2_personal_clean",
    "data_policy": "clean_starter_only",
    "adapter_contract": "STORE-001",
    "resource_types_json": '["authority","authority_binding","entity","onboarding_ledger","ops_brief_run","receipt","service_state","task"]',
    "event_types_json": '["created","updated"]',
    "writer_model": "single_writer",
}
_MUTABLE_EMPTY_TABS = frozenset({"Resources", "Events", "Idempotency"})


@dataclass(frozen=True)
class StarterTab:
    title: str
    headers: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    must_be_empty_after_seed_rows: bool


@dataclass(frozen=True)
class StarterBlueprint:
    schema_version: int
    distribution_id: str
    spreadsheet_title: str
    spreadsheet_time_zone: str
    tabs: tuple[StarterTab, ...]
    workspace_artifacts: tuple[str, ...]
    privacy_invariants: tuple[str, ...]
    source_path: str
    source_sha256: str

    def canonical_material(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "distribution_id": self.distribution_id,
            "spreadsheet": {
                "title": self.spreadsheet_title,
                "time_zone": self.spreadsheet_time_zone,
            },
            "tabs": [
                {
                    "title": tab.title,
                    "headers": list(tab.headers),
                    "rows": [list(row) for row in tab.rows],
                    "must_be_empty_after_seed_rows": tab.must_be_empty_after_seed_rows,
                }
                for tab in self.tabs
            ],
            "workspace_artifacts": list(self.workspace_artifacts),
            "privacy_invariants": list(self.privacy_invariants),
        }


@dataclass(frozen=True)
class StarterSnapshot:
    title: str
    time_zone: str
    tabs: Mapping[str, tuple[tuple[Any, ...], ...]]


@dataclass(frozen=True)
class ReleaseManifest:
    schema_version: int
    distribution_id: str
    source_sha: str
    blueprint_path: str
    blueprint_sha256: str
    artifacts: tuple[tuple[str, str], ...]

    def projection(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "distribution_id": self.distribution_id,
            "source_sha": self.source_sha,
            "blueprint": {
                "path": self.blueprint_path,
                "sha256": self.blueprint_sha256,
            },
            "artifacts": [
                {"path": path, "sha256": digest} for path, digest in self.artifacts
            ],
        }

    def json_bytes(self) -> bytes:
        return _canonical_json(self.projection(), indent=2) + b"\n"


def load_blueprint(
    path: str | Path = "distribution/personal_google_starter.json",
    *,
    repository_root: str | Path = ".",
) -> StarterBlueprint:
    source = Path(path)
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise PersonalDistributionError(f"cannot read starter blueprint: {source}") from exc
    try:
        material = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PersonalDistributionError("starter blueprint must be valid UTF-8 JSON") from exc
    if not isinstance(material, dict):
        raise PersonalDistributionError("starter blueprint root must be an object")
    blueprint = _parse_blueprint(
        material,
        source_path=source.as_posix(),
        source_sha256=hashlib.sha256(raw).hexdigest(),
    )
    validate_blueprint(blueprint, repository_root=repository_root)
    return blueprint


def validate_blueprint(
    blueprint: StarterBlueprint,
    *,
    repository_root: str | Path = ".",
) -> None:
    if blueprint.schema_version != 1:
        raise PersonalDistributionError("unsupported starter blueprint schema_version")
    if blueprint.distribution_id != "mira-personal-google-workspace-v1":
        raise PersonalDistributionError("unexpected Personal starter distribution_id")
    if blueprint.spreadsheet_title != "MIRA Personal Starter":
        raise PersonalDistributionError("starter title must be MIRA Personal Starter")
    if blueprint.spreadsheet_time_zone != "Etc/UTC":
        raise PersonalDistributionError("clean starter spreadsheet time_zone must be Etc/UTC")

    tab_map = {tab.title: tab for tab in blueprint.tabs}
    if len(tab_map) != len(blueprint.tabs):
        raise PersonalDistributionError("starter blueprint contains duplicate tab titles")
    if set(tab_map) != set(_REQUIRED_TAB_HEADERS):
        raise PersonalDistributionError(
            "starter blueprint tabs must be exactly Metadata, Resources, Events, Idempotency"
        )
    for title, required_headers in _REQUIRED_TAB_HEADERS.items():
        tab = tab_map[title]
        if tab.headers != required_headers:
            raise PersonalDistributionError(f"{title} headers do not match STORE-001")
        for row in tab.rows:
            if len(row) != len(tab.headers):
                raise PersonalDistributionError(
                    f"{title} seed row width does not match its headers"
                )

    metadata = _metadata_from_blueprint(tab_map["Metadata"])
    if metadata != _REQUIRED_METADATA:
        raise PersonalDistributionError("starter Metadata does not match required clean schema")
    if tab_map["Metadata"].must_be_empty_after_seed_rows:
        raise PersonalDistributionError("Metadata cannot be declared empty after seed rows")
    for title in _MUTABLE_EMPTY_TABS:
        tab = tab_map[title]
        if tab.rows:
            raise PersonalDistributionError(f"clean starter {title} must contain no seed data")
        if not tab.must_be_empty_after_seed_rows:
            raise PersonalDistributionError(
                f"clean starter {title} must enforce empty mutable state"
            )

    invariants = frozenset(blueprint.privacy_invariants)
    if invariants != _REQUIRED_PRIVACY_INVARIANTS:
        raise PersonalDistributionError("starter privacy invariants are incomplete or unexpected")

    expected_artifacts = {
        "workspace/apps_script/Code.gs",
        "workspace/apps_script/CommandWorker.gs",
        "workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md",
        "workspace/apps_script/README.md",
        "workspace/apps_script/appsscript.json",
    }
    if set(blueprint.workspace_artifacts) != expected_artifacts:
        raise PersonalDistributionError("starter Workspace artifact set is incomplete or unexpected")
    if len(set(blueprint.workspace_artifacts)) != len(blueprint.workspace_artifacts):
        raise PersonalDistributionError("starter Workspace artifact list contains duplicates")

    combined = _canonical_json(blueprint.canonical_material()).decode("utf-8")
    _reject_private_material(combined, "starter blueprint")
    if any(marker in combined.lower() for marker in ("legacy production", "personal-production")):
        raise PersonalDistributionError("starter blueprint references legacy production state")

    root = Path(repository_root)
    try:
        load_workspace_bundle(root / "workspace/apps_script")
    except WorkspaceBundleError as exc:
        raise PersonalDistributionError(str(exc)) from exc
    for artifact in blueprint.workspace_artifacts:
        path = root / artifact
        try:
            payload = path.read_bytes()
        except OSError as exc:
            raise PersonalDistributionError(f"missing Workspace artifact: {artifact}") from exc
        if not payload:
            raise PersonalDistributionError(f"Workspace artifact is empty: {artifact}")
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PersonalDistributionError(
                f"Workspace artifact must be UTF-8 text: {artifact}"
            ) from exc
        _reject_private_material(text, artifact)


def build_release_manifest(
    source_sha: str,
    *,
    blueprint_path: str | Path = "distribution/personal_google_starter.json",
    repository_root: str | Path = ".",
) -> ReleaseManifest:
    if not isinstance(source_sha, str) or not _SOURCE_SHA_RE.fullmatch(source_sha):
        raise PersonalDistributionError("source_sha must be a lowercase 40-character Git SHA")
    root = Path(repository_root)
    blueprint = load_blueprint(blueprint_path, repository_root=root)
    artifacts: list[tuple[str, str]] = []
    for relative in sorted(blueprint.workspace_artifacts):
        try:
            payload = (root / relative).read_bytes()
        except OSError as exc:
            raise PersonalDistributionError(f"cannot read release artifact: {relative}") from exc
        artifacts.append((relative, hashlib.sha256(payload).hexdigest()))
    return ReleaseManifest(
        schema_version=1,
        distribution_id=blueprint.distribution_id,
        source_sha=source_sha,
        blueprint_path=blueprint.source_path,
        blueprint_sha256=blueprint.source_sha256,
        artifacts=tuple(artifacts),
    )


def verify_release_manifest(
    manifest: Mapping[str, Any],
    *,
    blueprint_path: str | Path = "distribution/personal_google_starter.json",
    repository_root: str | Path = ".",
) -> None:
    if not isinstance(manifest, Mapping):
        raise PersonalDistributionError("release manifest must be an object")
    source_sha = manifest.get("source_sha")
    expected = build_release_manifest(
        source_sha,
        blueprint_path=blueprint_path,
        repository_root=repository_root,
    ).projection()
    normalized = json.loads(_canonical_json(dict(manifest)).decode("utf-8"))
    if normalized != expected:
        raise PersonalDistributionError("release manifest does not match current source artifacts")


def verify_snapshot(
    snapshot: StarterSnapshot,
    *,
    blueprint_path: str | Path = "distribution/personal_google_starter.json",
    repository_root: str | Path = ".",
) -> None:
    blueprint = load_blueprint(blueprint_path, repository_root=repository_root)
    if snapshot.title != blueprint.spreadsheet_title:
        raise PersonalDistributionError("spreadsheet title does not match starter blueprint")
    if snapshot.time_zone != blueprint.spreadsheet_time_zone:
        raise PersonalDistributionError("spreadsheet time zone does not match starter blueprint")
    if set(snapshot.tabs) != {tab.title for tab in blueprint.tabs}:
        raise PersonalDistributionError("spreadsheet tab set does not match starter blueprint")

    expected = {tab.title: tab for tab in blueprint.tabs}
    for title, rows in snapshot.tabs.items():
        if not isinstance(rows, tuple) or not rows:
            raise PersonalDistributionError(f"snapshot tab {title} must include a header row")
        tab = expected[title]
        header = tuple(str(value) for value in rows[0])
        if header != tab.headers:
            raise PersonalDistributionError(f"snapshot {title} headers do not match blueprint")
        actual_data = tuple(tuple(row) for row in rows[1:] if any(value not in (None, "") for value in row))
        if title == "Metadata":
            metadata_rows = tuple(tuple(row) for row in tab.rows)
            if actual_data != metadata_rows:
                raise PersonalDistributionError("snapshot Metadata does not match blueprint seed rows")
        elif tab.must_be_empty_after_seed_rows and actual_data:
            raise PersonalDistributionError(
                f"snapshot {title} contains inherited mutable state"
            )


def snapshot_from_mapping(material: Mapping[str, Any]) -> StarterSnapshot:
    if not isinstance(material, Mapping):
        raise PersonalDistributionError("snapshot JSON must be an object")
    title = material.get("title")
    time_zone = material.get("time_zone")
    raw_tabs = material.get("tabs")
    if not isinstance(title, str) or not title:
        raise PersonalDistributionError("snapshot title must be non-empty text")
    if not isinstance(time_zone, str) or not time_zone:
        raise PersonalDistributionError("snapshot time_zone must be non-empty text")
    if not isinstance(raw_tabs, Mapping):
        raise PersonalDistributionError("snapshot tabs must be an object")
    tabs: dict[str, tuple[tuple[Any, ...], ...]] = {}
    for tab_name, rows in raw_tabs.items():
        if not isinstance(tab_name, str) or not tab_name:
            raise PersonalDistributionError("snapshot tab names must be non-empty text")
        if not isinstance(rows, list):
            raise PersonalDistributionError(f"snapshot tab {tab_name} must be a row list")
        converted: list[tuple[Any, ...]] = []
        for row in rows:
            if not isinstance(row, list):
                raise PersonalDistributionError(
                    f"snapshot tab {tab_name} contains a non-list row"
                )
            converted.append(tuple(row))
        tabs[tab_name] = tuple(converted)
    return StarterSnapshot(title=title, time_zone=time_zone, tabs=tabs)


def _parse_blueprint(
    material: Mapping[str, Any],
    *,
    source_path: str,
    source_sha256: str,
) -> StarterBlueprint:
    try:
        schema_version = material["schema_version"]
        distribution_id = material["distribution_id"]
        spreadsheet = material["spreadsheet"]
        raw_tabs = material["tabs"]
        artifacts = material["workspace_artifacts"]
        invariants = material["privacy_invariants"]
    except KeyError as exc:
        raise PersonalDistributionError(f"starter blueprint missing field: {exc.args[0]}") from exc
    if not isinstance(schema_version, int) or isinstance(schema_version, bool):
        raise PersonalDistributionError("starter schema_version must be integer")
    if not isinstance(distribution_id, str) or not distribution_id:
        raise PersonalDistributionError("starter distribution_id must be non-empty text")
    if not isinstance(spreadsheet, Mapping):
        raise PersonalDistributionError("starter spreadsheet must be an object")
    title = spreadsheet.get("title")
    time_zone = spreadsheet.get("time_zone")
    if not isinstance(title, str) or not isinstance(time_zone, str):
        raise PersonalDistributionError("starter spreadsheet title/time_zone must be text")
    if not isinstance(raw_tabs, list) or not raw_tabs:
        raise PersonalDistributionError("starter tabs must be a non-empty list")
    tabs: list[StarterTab] = []
    for raw_tab in raw_tabs:
        if not isinstance(raw_tab, Mapping):
            raise PersonalDistributionError("starter tab must be an object")
        tab_title = raw_tab.get("title")
        headers = raw_tab.get("headers")
        rows = raw_tab.get("rows")
        clean = raw_tab.get("must_be_empty_after_seed_rows")
        if not isinstance(tab_title, str) or not tab_title:
            raise PersonalDistributionError("starter tab title must be non-empty text")
        if not isinstance(headers, list) or not all(isinstance(item, str) for item in headers):
            raise PersonalDistributionError(f"starter {tab_title} headers must be text list")
        if not isinstance(rows, list):
            raise PersonalDistributionError(f"starter {tab_title} rows must be a list")
        converted_rows: list[tuple[Any, ...]] = []
        for row in rows:
            if not isinstance(row, list):
                raise PersonalDistributionError(f"starter {tab_title} row must be a list")
            converted_rows.append(tuple(row))
        if not isinstance(clean, bool):
            raise PersonalDistributionError(
                f"starter {tab_title} must_be_empty_after_seed_rows must be boolean"
            )
        tabs.append(
            StarterTab(
                title=tab_title,
                headers=tuple(headers),
                rows=tuple(converted_rows),
                must_be_empty_after_seed_rows=clean,
            )
        )
    if not isinstance(artifacts, list) or not all(isinstance(item, str) for item in artifacts):
        raise PersonalDistributionError("workspace_artifacts must be a text list")
    if not isinstance(invariants, list) or not all(isinstance(item, str) for item in invariants):
        raise PersonalDistributionError("privacy_invariants must be a text list")
    return StarterBlueprint(
        schema_version=schema_version,
        distribution_id=distribution_id,
        spreadsheet_title=title,
        spreadsheet_time_zone=time_zone,
        tabs=tuple(tabs),
        workspace_artifacts=tuple(artifacts),
        privacy_invariants=tuple(invariants),
        source_path=source_path,
        source_sha256=source_sha256,
    )


def _metadata_from_blueprint(tab: StarterTab) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in tab.rows:
        if len(row) != 2 or not all(isinstance(value, str) for value in row):
            raise PersonalDistributionError("Metadata seed rows must be two strings")
        key, value = row
        if key in result:
            raise PersonalDistributionError(f"duplicate Metadata key in blueprint: {key}")
        result[key] = value
    return result


def _reject_private_material(text: str, label: str) -> None:
    for pattern in _PROVIDER_PATTERNS:
        if pattern.search(text):
            raise PersonalDistributionError(f"{label} contains a provider identifier")
    lowered = text.lower()
    for marker in _SECRET_MARKERS:
        if marker.lower() in lowered:
            raise PersonalDistributionError(f"{label} contains secret-like material")


def _canonical_json(value: object, *, indent: int | None = None) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":") if indent is None else None,
        indent=indent,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _read_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PersonalDistributionError(f"cannot read JSON: {source}") from exc
    if not isinstance(value, dict):
        raise PersonalDistributionError(f"JSON root must be an object: {source}")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build/verify MIRA Personal starter distribution")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check")
    check.add_argument("--blueprint", default="distribution/personal_google_starter.json")

    manifest = subparsers.add_parser("manifest")
    manifest.add_argument("source_sha")
    manifest.add_argument("--blueprint", default="distribution/personal_google_starter.json")

    verify_manifest = subparsers.add_parser("verify-manifest")
    verify_manifest.add_argument("manifest_path")
    verify_manifest.add_argument("--blueprint", default="distribution/personal_google_starter.json")

    snapshot = subparsers.add_parser("verify-snapshot")
    snapshot.add_argument("snapshot_path")
    snapshot.add_argument("--blueprint", default="distribution/personal_google_starter.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "check":
            blueprint = load_blueprint(args.blueprint)
            print(
                "Personal starter valid: "
                f"distribution={blueprint.distribution_id}; tabs={len(blueprint.tabs)}; "
                f"artifacts={len(blueprint.workspace_artifacts)}; blueprint_sha256={blueprint.source_sha256}"
            )
            return 0
        if args.command == "manifest":
            sys.stdout.buffer.write(build_release_manifest(args.source_sha, blueprint_path=args.blueprint).json_bytes())
            return 0
        if args.command == "verify-manifest":
            verify_release_manifest(_read_json(args.manifest_path), blueprint_path=args.blueprint)
            print("Personal release manifest valid")
            return 0
        snapshot = snapshot_from_mapping(_read_json(args.snapshot_path))
        verify_snapshot(snapshot, blueprint_path=args.blueprint)
        print("Personal starter snapshot valid")
        return 0
    except PersonalDistributionError as exc:
        print(f"personal-distribution error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
