"""Google Workspace first-run bundle contract for MIRA.

The default Personal MIRA deployment begins with a copied Google Sheet and its
bound Apps Script. This module treats the Apps Script files and complete no-app
operating instructions as one release artifact: it validates package shape and
rejects provider identifiers or secrets from the public source tree without
importing Google-specific runtime behavior into provider-neutral core modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping


class WorkspaceBundleError(Exception):
    """Raised when the browser-first Workspace starter bundle is invalid."""


_REQUIRED_FILES = (
    "Code.gs",
    "CommandWorker.gs",
    "appsscript.json",
    "README.md",
    "MIRA_NO_APP_INSTRUCTIONS.md",
)
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
_PROTOCOL_MARKERS = (
    "Replace the existing Personal MIRA operating-instruction block with this entire document.",
    "You are **MIRA — Modular Intelligence & Reasoning Assistant**.",
    "Chat history, model memory, Git, documents, and prior prose are evidence or source material.",
    "schema_version=mira-structured-state-v1",
    "adapter_contract=STORE-001",
    "writer_model=single_writer",
    "mutation_mode=queued_writer",
    "Every mutable data class used by MIRA must resolve through exactly one persisted `authority_binding`",
    "resource id: `google-sheets-personal`",
    "authority_binding/binding-entity",
    "authority_binding/binding-onboarding-ledger",
    "authority_binding/binding-service-state",
    "authority_binding/binding-task",
    "authority_binding/binding-ops-brief-run",
    "authority_binding/binding-receipt",
    "authority_binding/binding-asset",
    "resource type: `onboarding_ledger`",
    "resource id: `minimum-useful-setup`",
    "`timezone`",
    "`life_pattern`",
    "`goals`",
    "`appointment_help`",
    "continue setup now, or start using MIRA",
    "resource id: `progressive-discovery`",
    "`fitness_wellness`",
    "`meals_groceries`",
    "`receipts_assets_inventory`",
    "`connected_integrations`",
    "Silence is never an answer.",
    "at most one new unanswered discovery topic",
    "After seven distinct topic-days",
    "## Canonical tasks",
    "resource type: `task`",
    "`state`: `open`, `completed`, or `cancelled`",
    "## Canonical receipts and purchase history",
    "resource type is `receipt`",
    "integer minor units",
    "Exact source-fingerprint replay",
    "Receipt capture does **not** automatically create or mutate an asset",
    "## Canonical physical assets and receipt-linked acquisition",
    "canonical resource type is `asset`",
    "immutable RFC 4122 Entity UUID",
    "Receipt capture never automatically creates assets.",
    "`tracking_mode=individual` requires asset quantity exactly `1`",
    "Asset acquisition alone therefore never claims an item is installed on a vehicle",
    "## First no-app Ops Brief vertical",
    "ops-brief:<YYYY-MM-DD>:am",
    "immutable `ops_brief_run` resource",
    "**Composition is not delivery.**",
    "`calendar_capability_verified`: false",
    "`calendar_projection_active`: false",
    "`appointment_service_activated`: false",
    "resource type: `service_state`",
    "resource id: `appointments_calendar`",
    "`activation_state` to `requested`",
    "Do **not** mark the service active.",
    "SHA-256",
    "expected_revision",
    "Idempotency",
    "exact provider readback",
)


@dataclass(frozen=True)
class WorkspaceBundle:
    """Validated copyable Workspace starter files and operating protocol."""

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
    """Reject malformed, secret-bearing, provider-bound, or incomplete bundles."""

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

    worker = files["CommandWorker.gs"]
    worker_symbols = (
        "function miraEnableQueuedWriter()",
        "function miraProcessCommandQueue()",
        "LockService.getScriptLock()",
        "everyMinutes(1)",
        "MIRA_COMMAND_HEADERS_",
    )
    missing_worker = [symbol for symbol in worker_symbols if symbol not in worker]
    if missing_worker:
        raise WorkspaceBundleError(
            "Workspace CommandWorker.gs is missing required symbols: "
            + ", ".join(missing_worker)
        )

    manifest = files["appsscript.json"]
    if "https://www.googleapis.com/auth/spreadsheets.currentonly" not in manifest:
        raise WorkspaceBundleError("Workspace manifest must remain current-Sheet scoped")
    if "https://www.googleapis.com/auth/script.scriptapp" not in manifest:
        raise WorkspaceBundleError("Workspace queued worker requires bounded trigger-management scope")

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

    protocol = files["MIRA_NO_APP_INSTRUCTIONS.md"]
    missing_protocol = [marker for marker in _PROTOCOL_MARKERS if marker not in protocol]
    if missing_protocol:
        raise WorkspaceBundleError(
            "Workspace no-app instructions are missing required contract clauses: "
            + ", ".join(missing_protocol)
        )

    if "Cloud Run" not in protocol or "must not require Cloud Run" not in protocol:
        raise WorkspaceBundleError(
            "Workspace no-app instructions must preserve the zero-external-infrastructure baseline"
        )
    if "Apple/iCloud" not in protocol or "Microsoft/Outlook/M365" not in protocol:
        raise WorkspaceBundleError(
            "Workspace no-app instructions must preserve accepted Calendar provider choices"
        )
    if "Never ask the user to rename MIRA." not in protocol:
        raise WorkspaceBundleError("Workspace no-app instructions must keep MIRA's name fixed")


__all__ = [
    "WorkspaceBundle",
    "WorkspaceBundleError",
    "load_workspace_bundle",
    "validate_workspace_bundle",
]
