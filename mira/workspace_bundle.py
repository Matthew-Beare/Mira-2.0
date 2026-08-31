"""Google Workspace first-run bundle contract for MIRA.

The default Personal MIRA deployment begins with a copied Google Sheet and its
bound Apps Script. This module treats the default Apps Script files and complete
no-app operating instructions as one release artifact: it validates package
shape and rejects provider identifiers, secrets, or optional-provider permission
creep from the public default starter.
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
    "Never ask the user to rename MIRA.",
    "Chat history, model memory, Git, documents, and prior prose are evidence or source material.",
    "schema_version=mira-structured-state-v1",
    "adapter_contract=STORE-001",
    "writer_model=single_writer",
    "event_types_json` contains both `created` and `updated`",
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
    "authority_binding/binding-identifier",
    "authority_binding/binding-location",
    "authority_binding/binding-inventory-state",
    "authority_binding/binding-shopping-intent",
    "resource id: `minimum-useful-setup`",
    "`timezone`",
    "`life_pattern`",
    "`goals`",
    "`appointment_help`",
    "continue setup now, or start using MIRA",
    "progressive-discovery",
    "`fitness_wellness`",
    "`meals_groceries`",
    "`receipts_assets_inventory`",
    "`connected_integrations`",
    "Silence is never an answer.",
    "at most one new unanswered discovery topic",
    "After seven distinct topic-days",
    "## Intent-first provider activation",
    "Yes, use my calendar",
    "provider's own unavoidable authorization",
    "Do not ask a normal user to create a Calendar",
    "single_writer_preflight_non_atomic",
    "MIRA-PROJECTION-ID:",
    "## Canonical tasks",
    "`state`: `open`, `completed`, or `cancelled`",
    "## Canonical receipts and purchase history",
    "canonical resource type is `receipt`",
    "integer minor units",
    "Exact source-fingerprint replay",
    "Receipt capture does **not** automatically create or mutate an asset",
    "## Canonical shopping intent and receipt reconciliation",
    "canonical resource type is `shopping_intent`",
    "A canonical receipt merely existing never fulfills shopping intent.",
    "Shopping fulfillment requires a canonical receipt whose state is `captured`",
    "A `needs_review` receipt cannot fulfill shopping intent.",
    "Receipt reconciliation never mutates the canonical receipt",
    "## Canonical physical assets and receipt-linked acquisition",
    "canonical resource type is `asset`",
    "immutable RFC 4122 Entity UUID",
    "Receipt capture never automatically creates assets.",
    "`tracking_mode=individual` requires asset quantity exactly `1`",
    "Asset acquisition alone therefore never claims an item is installed on a vehicle",
    "## Canonical asset identifiers and lookup",
    "canonical resource type is `identifier`",
    "`authority_binding/binding-identifier`",
    "Leading zeroes are preserved.",
    "`serial_number`, `imei`, and `mac` are serial-level collision-protected identifiers.",
    "identifiers cannot manufacture physical assets.",
    "Identifier attachment alone never infers fitment",
    "## Canonical inventory participation and location state",
    "canonical inventory participation resource type is `inventory_state`",
    "Resource ID and payload `entity_uuid` must both be exactly the existing canonical asset Entity UUID",
    "`intended_location_id` answers “where does this belong?”",
    "`observed_location_id` answers “where was this item last supported as being?”",
    "requires an explicit offset-aware ISO-8601 `observed_at` timestamp",
    "This base location state is not movement-event history.",
    "## Canonical inventory query projection",
    "Inventory query is read-only composition",
    "Untracked assets are not silently presented as inventory.",
    "Multiple supplied filters are ANDed.",
    "Descendant matching never means",
    "render a deterministic root-to-leaf canonical path",
    "A query performs zero Resource, Event, or Idempotency writes",
    "no matching tracked inventory item was found",
    "## Canonical grocery list vs known-stock reconciliation",
    "creates no `grocery` Resource",
    "explicitly select one or more canonical shopping-intent IDs",
    "supply one existing canonical `stock_location_id`",
    "Substring, fuzzy, semantic, LLM-selected, and “close enough” matches are not allowed.",
    "`known_in_stock`",
    "`needs_to_buy`",
    "`unresolved`",
    "`stock_quantity=null` and `stock_quantity_known=false`",
    "Never use immutable asset acquisition `quantity`",
    "Grocery reconciliation performs zero Resource, Event, or Idempotency writes.",
    "`PAR-001` current-quantity/target/threshold behavior remains optional and separate.",
    "## Canonical append-event rule",
    "append_event",
    "expected_stream_revision",
    "## Canonical inventory movement / observation history",
    "Recognition alone is not movement",
    "event_kind=inventory_observation",
    "event-first/projection-second",
    "movement-state-",
    "same-location re-observation",
    "Container-following propagation is **not** implemented.",
    "## First no-app Ops Brief vertical",
    "ops-brief:<YYYY-MM-DD>:am",
    "immutable `ops_brief_run` resource",
    "**Composition is not delivery.**",
    "`calendar_capability_verified`: false",
    "`calendar_projection_active`: false",
    "`appointment_service_activated`: false",
    "service_state/appointments_calendar",
    "`activation_state` to `requested`",
    "Do **not** mark the service active.",
    "## Canonical current-Resource backup and isolated restore",
    "A MIRA backup artifact is a **nonauthoritative snapshot**",
    "complete_current_resources_under_query_bound",
    "not_exported_interface_not_enumerable",
    "Creating the backup is read-only.",
    "Restore only into a genuinely fresh, isolated, schema-compatible target authority.",
    "A restore-key replay on the supposedly fresh target is evidence that the target is not fresh; fail closed.",
    "Restore-generated provider timestamps, request hashes",
    "Verified restore requires exact schema, Resource identity, payload, revision",
    "does **not** prove Event-history recovery",
    "Backup and authority migration remain separate.",
    "**snapshot created**",
    "**restore verified**",
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
    """Load and validate the public default Google Workspace starter artifact."""

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
            "Workspace bundle files mismatch; missing={missing}, extra={extra}".format(
                missing=missing, extra=extra
            )
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
    if ".addItem('Enable Calendar', 'miraEnableGoogleCalendar')" in code:
        raise WorkspaceBundleError(
            "default Personal starter must not require a hidden Sheet menu for Calendar activation"
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
        raise WorkspaceBundleError(
            "Workspace queued worker requires bounded trigger-management scope"
        )
    forbidden_default_scopes = (
        "https://www.googleapis.com/auth/script.external_request",
        "https://www.googleapis.com/auth/calendar.app.created",
        "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.calendars",
    )
    leaked_scopes = [scope for scope in forbidden_default_scopes if scope in manifest]
    if leaked_scopes:
        raise WorkspaceBundleError(
            "default Personal starter must not pre-authorize optional Calendar/provider scopes: "
            + ", ".join(leaked_scopes)
        )

    readme = files["README.md"]
    readme_markers = (
        "Calendar is not authorized during unrelated MIRA Sheet setup.",
        "ordinary-language intent",
        "provider's own authorization",
        "MIRA-PROJECTION-ID:",
        "single_writer_preflight_non_atomic",
        "The stronger Apps Script Calendar adapter is not part of the default Personal starter.",
    )
    missing_readme = [marker for marker in readme_markers if marker not in readme]
    if missing_readme:
        raise WorkspaceBundleError(
            "Workspace README is missing intent-first provider activation markers: "
            + ", ".join(missing_readme)
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
