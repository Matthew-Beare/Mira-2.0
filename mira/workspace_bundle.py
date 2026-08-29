"""Google Workspace first-run bundle contract for MIRA.

The default Personal MIRA deployment begins with a copied Google Sheet and its
bound Apps Script.  This module treats the Apps Script files as a release
artifact: it validates the package shape and rejects provider identifiers or
secrets from the public source tree without importing Google-specific runtime
behavior into the provider-neutral API/storage core.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping


class WorkspaceBundleError(Exception):
    """Raised when the browser-first Workspace starter bundle is invalid."""


_REQUIRED_FILES = ("Code.gs", "appsscript.json", "README.md")
_PROVIDER_ID_PATTERNS = (
    re.compile(r"AKfycb[A-Za-z0-9_-]{8,}"),
    re.compile(r"\b\d{10,}-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com\b"),
    re.compile(r"\b[A-Za-z0-9_-]{20,}\.iam\.gserviceaccount\.com\b"),
)
_SECRET_MARKERS = (
    "BEGIN PRIVATE KEY",
    "client_secret\"",
    "MIRA_BEARER_TOKEN=",
)


@dataclass(frozen=True)
class WorkspaceBundle:
    """Validated copyable Apps Script starter files."""

    files: Mapping[str, str]

    def file(self, name: str) -> str:
        try:
            return self.files[name]
        except KeyError as exc:
            raise WorkspaceBundleError(f"unknown Workspace bundle file: {name}") from exc


def load_workspace_bundle(root: str | Path = "workspace/apps_script") -> WorkspaceBundle:
    """Load and validate the public Google Workspace starter artifact."""

    base = Path(root)
    files: dict[str, str] = {}
    for name in _REQUIRED_FILES:
        path = base / name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise WorkspaceBundleError(f"missing Workspace bundle file: {path}") from exc
        if not text.strip():
            raise WorkspaceBundleError(f"Workspace bundle file is empty: {path}")
        files[name] = text
    validate_workspace_bundle(files)
    return WorkspaceBundle(files=dict(files))


def validate_workspace_bundle(files: Mapping[str, str]) -> None:
    """Reject malformed, secret-bearing, or provider-bound public bundles."""

    if set(files) != set(_REQUIRED_FILES):
        missing = sorted(set(_REQUIRED_FILES) - set(files))
        extra = sorted(set(files) - set(_REQUIRED_FILES))
        raise WorkspaceBundleError(
            f"Workspace bundle files mismatch; missing={missing}, extra={extra}"
        )

    combined = "\n".join(files[name] for name in _REQUIRED_FILES)
    for pattern in _PROVIDER_ID_PATTERNS:
        if pattern.search(combined):
            raise WorkspaceBundleError("Workspace bundle contains a provider identifier")
    for marker in _SECRET_MARKERS:
        if marker in combined:
            raise WorkspaceBundleError("Workspace bundle contains secret material")

    code = files["Code.gs"]
    required_symbols = (
        "function onOpen()",
        "function miraInitializeCopy()",
        "function doGet(e)",
        "function doPost(e)",
        "function miraWorkspaceSchema_()",
        "function miraReadQuery_",
    )
    missing_symbols = [symbol for symbol in required_symbols if symbol not in code]
    if missing_symbols:
        raise WorkspaceBundleError(
            "Workspace Code.gs is missing required symbols: " + ", ".join(missing_symbols)
        )

    if "MIRA_SPREADSHEET_ID" not in code or "PropertiesService" not in code:
        raise WorkspaceBundleError(
            "Workspace starter must bind each copied Sheet through Script Properties"
        )
    if "SpreadsheetApp.openById" not in code:
        raise WorkspaceBundleError(
            "Workspace web runtime must reopen the initialized bound Sheet by runtime ID"
        )
    if "SpreadsheetApp.getActiveSpreadsheet" not in code:
        raise WorkspaceBundleError(
            "Workspace browser initializer must capture the copied Sheet identity"
        )


__all__ = [
    "WorkspaceBundle",
    "WorkspaceBundleError",
    "load_workspace_bundle",
    "validate_workspace_bundle",
]
