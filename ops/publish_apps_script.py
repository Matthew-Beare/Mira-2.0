#!/usr/bin/env python3
"""Publish MIRA's verified bound Apps Script runtime into a Google Sheet.

This is maintainer/release tooling, not an ordinary-user setup step. It creates a
container-bound Apps Script project for an explicitly supplied disposable Sheet,
replaces the project's HEAD content with the repository runtime, then performs an
exact provider readback before reporting success.

Credentials remain outside Git. The access token is read from an environment
variable and is never accepted as a command-line argument or written to output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


API_ROOT = "https://script.googleapis.com/v1"
DEFAULT_TOKEN_ENV = "MIRA_APPS_SCRIPT_ACCESS_TOKEN"
_RUNTIME_FILES = ("Code.gs", "CommandWorker.gs", "appsscript.json")
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,256}$")


class PublicationError(Exception):
    """Raised when bound-script publication or exact readback fails."""


@dataclass(frozen=True)
class ScriptFile:
    name: str
    type: str
    source: str

    def projection(self) -> dict[str, str]:
        return {"name": self.name, "type": self.type, "source": self.source}


@dataclass(frozen=True)
class PublishedProject:
    script_id: str
    parent_id: str


Transport = Callable[[str, str, Mapping[str, object] | None, str], Mapping[str, object]]


def load_runtime_files(repository_root: str | Path = ".") -> tuple[ScriptFile, ...]:
    root = Path(repository_root) / "workspace" / "apps_script"
    files: list[ScriptFile] = []
    for filename in _RUNTIME_FILES:
        path = root / filename
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PublicationError(f"missing Apps Script runtime file: {filename}") from exc
        if not source:
            raise PublicationError(f"Apps Script runtime file is empty: {filename}")
        if filename.endswith(".gs"):
            files.append(ScriptFile(name=filename[:-3], type="SERVER_JS", source=source))
        elif filename == "appsscript.json":
            try:
                manifest = json.loads(source)
            except json.JSONDecodeError as exc:
                raise PublicationError("appsscript.json must be valid JSON") from exc
            if not isinstance(manifest, dict):
                raise PublicationError("appsscript.json must contain a JSON object")
            canonical = json.dumps(
                manifest,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            files.append(ScriptFile(name="appsscript", type="JSON", source=canonical))
        else:  # pragma: no cover - fixed internal list
            raise PublicationError(f"unsupported runtime file: {filename}")
    return tuple(files)


def _validate_provider_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise PublicationError(f"{field} is invalid")
    return value


def _normalize_provider_files(material: Mapping[str, object]) -> tuple[ScriptFile, ...]:
    raw_files = material.get("files")
    if not isinstance(raw_files, list):
        raise PublicationError("Apps Script content readback is missing files")
    files: list[ScriptFile] = []
    seen: set[tuple[str, str]] = set()
    for raw in raw_files:
        if not isinstance(raw, Mapping):
            raise PublicationError("Apps Script content contains malformed file metadata")
        name = raw.get("name")
        file_type = raw.get("type")
        source = raw.get("source")
        if not all(isinstance(value, str) for value in (name, file_type, source)):
            raise PublicationError("Apps Script content contains malformed file fields")
        key = (name, file_type)
        if key in seen:
            raise PublicationError("Apps Script content readback contains duplicate files")
        seen.add(key)
        if file_type == "JSON" and name == "appsscript":
            try:
                parsed = json.loads(source)
            except json.JSONDecodeError as exc:
                raise PublicationError("provider appsscript manifest is invalid JSON") from exc
            source = json.dumps(parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        files.append(ScriptFile(name=name, type=file_type, source=source))
    return tuple(sorted(files, key=lambda item: (item.name, item.type)))


def _expected_files(files: Sequence[ScriptFile]) -> tuple[ScriptFile, ...]:
    return tuple(sorted(files, key=lambda item: (item.name, item.type)))


def default_transport(
    method: str,
    path: str,
    body: Mapping[str, object] | None,
    access_token: str,
) -> Mapping[str, object]:
    if not isinstance(access_token, str) or not access_token.strip():
        raise PublicationError("Apps Script access token is unavailable")
    url = API_ROOT + path
    data = None
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed HTTPS API root
            raw = response.read()
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - defensive provider error path
            detail = ""
        raise PublicationError(
            f"Apps Script API request failed with HTTP {exc.code}: {detail[:500]}"
        ) from exc
    except URLError as exc:
        raise PublicationError("Apps Script API request failed") from exc
    try:
        material = json.loads(raw.decode("utf-8")) if raw else {}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicationError("Apps Script API returned invalid JSON") from exc
    if not isinstance(material, Mapping):
        raise PublicationError("Apps Script API response must be an object")
    return material


def publish_bound_runtime(
    *,
    sheet_id: str,
    access_token: str,
    title: str = "MIRA Personal Runtime",
    repository_root: str | Path = ".",
    transport: Transport = default_transport,
) -> PublishedProject:
    """Create, replace, and exact-readback one bound Apps Script runtime."""

    parent_id = _validate_provider_id(sheet_id, "sheet_id")
    if not isinstance(title, str) or not title.strip() or len(title) > 128:
        raise PublicationError("project title is invalid")
    files = load_runtime_files(repository_root)

    created = transport(
        "POST",
        "/projects",
        {"title": title.strip(), "parentId": parent_id},
        access_token,
    )
    script_id = _validate_provider_id(str(created.get("scriptId", "")), "script_id")
    returned_parent = _validate_provider_id(str(created.get("parentId", "")), "parent_id")
    if returned_parent != parent_id:
        raise PublicationError("Apps Script project was not bound to the requested Sheet")

    encoded_script_id = quote(script_id, safe="")
    transport(
        "PUT",
        f"/projects/{encoded_script_id}/content",
        {"files": [item.projection() for item in files]},
        access_token,
    )
    observed = transport(
        "GET",
        f"/projects/{encoded_script_id}/content",
        None,
        access_token,
    )
    if _normalize_provider_files(observed) != _expected_files(files):
        raise PublicationError("Apps Script provider readback does not match repository runtime")
    return PublishedProject(script_id=script_id, parent_id=parent_id)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish and exact-verify the MIRA bound Apps Script runtime"
    )
    parser.add_argument("--sheet-id", required=True)
    parser.add_argument("--title", default="MIRA Personal Runtime")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--token-env", default=DEFAULT_TOKEN_ENV)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate repository runtime material without making provider calls",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        files = load_runtime_files(args.repository_root)
        if args.validate_only:
            print(f"Apps Script runtime valid: files={len(files)}")
            return 0
        token = os.environ.get(args.token_env, "")
        if not token:
            raise PublicationError(
                f"short-lived Apps Script access token is unavailable in environment: {args.token_env}"
            )
        publish_bound_runtime(
            sheet_id=args.sheet_id,
            access_token=token,
            title=args.title,
            repository_root=args.repository_root,
        )
        print("Apps Script runtime published and exact provider readback verified")
        return 0
    except PublicationError as exc:
        print(f"apps-script-publication error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
