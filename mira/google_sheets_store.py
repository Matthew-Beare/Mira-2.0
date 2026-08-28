"""Google Sheets implementation of the provider-neutral structured-state contract.

The adapter keeps Google-specific row/tab persistence behind a small gateway. Runtime
spreadsheet IDs and access credentials are injected; this module contains no account or
provider resource identifiers. M2-M0 intentionally uses a single-writer process model:
optimistic revisions are enforced under an adapter-local lock and each mutation is sent
as one atomic Sheets batch, but this module does not claim distributed compare-and-swap
across independent service processes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from threading import RLock
from typing import Any, Callable, Mapping, Protocol, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .structured_state import (
    EventMutationResult,
    EventRecord,
    HealthStatus,
    IdempotencyConflictError,
    IdentityConflictError,
    MutationResult,
    NotFoundError,
    ResourceRecord,
    RevisionConflictError,
    SchemaInfo,
    StructuredStateError,
    ValidationError,
)


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_RESOURCE_HEADERS = (
    "resource_type",
    "resource_id",
    "revision",
    "payload_json",
    "updated_at",
    "last_idempotency_key",
    "request_hash",
)
_EVENT_HEADERS = (
    "event_type",
    "event_id",
    "stream_type",
    "stream_id",
    "stream_revision",
    "payload_json",
    "occurred_at",
    "idempotency_key",
)
_IDEMPOTENCY_HEADERS = (
    "idempotency_key",
    "operation",
    "request_hash",
    "result_json",
    "created_at",
    "resource_ref",
)
_METADATA_HEADERS = ("Key", "Value")


class SheetsGatewayError(StructuredStateError):
    """Raised when the Google Sheets persistence gateway cannot complete an operation."""


@dataclass(frozen=True)
class SheetRowMutation:
    """One append or exact row replacement inside an atomic gateway batch."""

    tab: str
    values: tuple[object, ...]
    row_number: int | None = None

    @property
    def is_append(self) -> bool:
        return self.row_number is None


class SheetsGateway(Protocol):
    """Minimal persistence surface required by GoogleSheetsStructuredStateAdapter."""

    def read_range(self, a1_range: str) -> Sequence[Sequence[object]]: ...

    def apply_mutations(self, mutations: Sequence[SheetRowMutation]) -> None: ...


class GoogleSheetsRestGateway:
    """Stdlib Google Sheets REST gateway with runtime-injected bearer credentials."""

    def __init__(
        self,
        *,
        spreadsheet_id: str,
        access_token_provider: Callable[[], str],
        timeout_seconds: float = 15.0,
        api_base: str = "https://sheets.googleapis.com/v4",
    ) -> None:
        self._spreadsheet_id = _validate_token(spreadsheet_id, "spreadsheet_id")
        if not callable(access_token_provider):
            raise ValidationError("access_token_provider must be callable")
        if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool):
            raise ValidationError("timeout_seconds must be numeric")
        if timeout_seconds <= 0:
            raise ValidationError("timeout_seconds must be greater than zero")
        self._access_token_provider = access_token_provider
        self._timeout_seconds = float(timeout_seconds)
        self._api_base = api_base.rstrip("/")
        self._sheet_ids: dict[str, int] | None = None

    def read_range(self, a1_range: str) -> tuple[tuple[object, ...], ...]:
        normalized_range = _validate_token(a1_range, "a1_range")
        encoded = quote(normalized_range, safe="")
        payload = self._request_json(
            "GET",
            f"{self._api_base}/spreadsheets/{self._spreadsheet_id}/values/{encoded}"
            "?majorDimension=ROWS&valueRenderOption=UNFORMATTED_VALUE",
        )
        values = payload.get("values", [])
        if not isinstance(values, list):
            raise SheetsGatewayError("Sheets values response is malformed")
        rows: list[tuple[object, ...]] = []
        for row in values:
            if not isinstance(row, list):
                raise SheetsGatewayError("Sheets values row is malformed")
            rows.append(tuple(row))
        return tuple(rows)

    def apply_mutations(self, mutations: Sequence[SheetRowMutation]) -> None:
        if not mutations:
            raise ValidationError("mutations must not be empty")
        sheet_ids = self._load_sheet_ids()
        requests: list[dict[str, object]] = []
        for mutation in mutations:
            if not isinstance(mutation, SheetRowMutation):
                raise ValidationError("mutation must be a SheetRowMutation")
            try:
                sheet_id = sheet_ids[mutation.tab]
            except KeyError as exc:
                raise SheetsGatewayError(f"missing required sheet tab: {mutation.tab}") from exc
            cells = [{"userEnteredValue": _google_value(value)} for value in mutation.values]
            if mutation.is_append:
                requests.append(
                    {
                        "appendCells": {
                            "sheetId": sheet_id,
                            "rows": [{"values": cells}],
                            "fields": "userEnteredValue",
                        }
                    }
                )
            else:
                row_number = mutation.row_number
                if not isinstance(row_number, int) or isinstance(row_number, bool) or row_number < 2:
                    raise ValidationError("replacement row_number must be an integer >= 2")
                requests.append(
                    {
                        "updateCells": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": row_number - 1,
                                "endRowIndex": row_number,
                                "startColumnIndex": 0,
                                "endColumnIndex": len(cells),
                            },
                            "rows": [{"values": cells}],
                            "fields": "userEnteredValue",
                        }
                    }
                )
        self._request_json(
            "POST",
            f"{self._api_base}/spreadsheets/{self._spreadsheet_id}:batchUpdate",
            {"requests": requests},
        )

    def _load_sheet_ids(self) -> dict[str, int]:
        if self._sheet_ids is not None:
            return dict(self._sheet_ids)
        payload = self._request_json(
            "GET",
            f"{self._api_base}/spreadsheets/{self._spreadsheet_id}"
            "?fields=sheets(properties(sheetId,title))",
        )
        sheets = payload.get("sheets")
        if not isinstance(sheets, list):
            raise SheetsGatewayError("Sheets metadata response is malformed")
        result: dict[str, int] = {}
        for item in sheets:
            if not isinstance(item, Mapping):
                raise SheetsGatewayError("Sheets metadata item is malformed")
            properties = item.get("properties")
            if not isinstance(properties, Mapping):
                raise SheetsGatewayError("Sheets properties are malformed")
            title = properties.get("title")
            sheet_id = properties.get("sheetId")
            if not isinstance(title, str) or not isinstance(sheet_id, int):
                raise SheetsGatewayError("Sheets title/sheetId metadata is malformed")
            if title in result:
                raise SheetsGatewayError(f"duplicate sheet title: {title}")
            result[title] = sheet_id
        self._sheet_ids = result
        return dict(result)

    def _request_json(
        self,
        method: str,
        url: str,
        body: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        token = self._access_token_provider()
        if not isinstance(token, str) or not token.strip():
            raise SheetsGatewayError("access token provider returned no credential")
        data = None
        headers = {
            "Authorization": f"Bearer {token.strip()}",
            "Accept": "application/json",
        }
        if body is not None:
            data = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(url=url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            raise SheetsGatewayError(f"Google Sheets HTTP failure: {exc.code}") from exc
        except (URLError, OSError) as exc:
            raise SheetsGatewayError("Google Sheets transport failure") from exc
        if not raw:
            return {}
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SheetsGatewayError("Google Sheets returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise SheetsGatewayError("Google Sheets JSON response is not an object")
        return payload


class GoogleSheetsStructuredStateAdapter:
    """Single-writer Google Sheets adapter preserving StructuredStateAdapter semantics."""

    def __init__(
        self,
        gateway: SheetsGateway,
        *,
        clock: Callable[[], datetime] | None = None,
        row_limit: int = 1000,
    ) -> None:
        if not hasattr(gateway, "read_range") or not hasattr(gateway, "apply_mutations"):
            raise ValidationError("gateway must implement the SheetsGateway contract")
        if not isinstance(row_limit, int) or isinstance(row_limit, bool) or row_limit < 2:
            raise ValidationError("row_limit must be an integer >= 2")
        self._gateway = gateway
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._row_limit = row_limit
        self._lock = RLock()

    def health(self) -> HealthStatus:
        try:
            schema = self.schema()
        except Exception:
            return HealthStatus(ok=False, adapter="google-sheets", schema_version="unknown")
        return HealthStatus(ok=True, adapter="google-sheets", schema_version=schema.schema_version)

    def schema(self) -> SchemaInfo:
        metadata = self._metadata()
        if metadata.get("adapter_contract") != "STORE-001":
            raise ValidationError("Google Sheets metadata does not declare STORE-001")
        if metadata.get("writer_model") != "single_writer":
            raise ValidationError("Google Sheets adapter requires writer_model=single_writer")
        schema_version = _validate_token(metadata.get("schema_version"), "schema_version")
        resource_types = _parse_type_json(metadata.get("resource_types_json"), "resource_types_json")
        event_types = _parse_type_json(metadata.get("event_types_json"), "event_types_json")
        return SchemaInfo(
            schema_version=schema_version,
            resource_types=tuple(sorted(resource_types)),
            event_types=tuple(sorted(event_types)),
        )

    def get(self, resource_type: str, resource_id: str) -> ResourceRecord:
        self._validate_resource_identity(resource_type, resource_id)
        matches = [
            record
            for _, record in self._resource_rows()
            if record.resource_type == resource_type and record.resource_id == resource_id
        ]
        if not matches:
            raise NotFoundError(f"{resource_type}:{resource_id} does not exist")
        if len(matches) != 1:
            raise IdentityConflictError(f"duplicate persisted resource identity: {resource_type}:{resource_id}")
        return matches[0]

    def query(
        self,
        resource_type: str,
        *,
        filters: Mapping[str, Any] | None = None,
        limit: int = 100,
    ) -> tuple[ResourceRecord, ...]:
        self._validate_resource_type(resource_type)
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("limit must be an integer from 1 through 1000")
        normalized_filters = _normalize_mapping(filters or {}, "filters")
        matches = [
            record
            for _, record in self._resource_rows()
            if record.resource_type == resource_type
            and all(record.payload.get(key) == value for key, value in normalized_filters.items())
        ]
        matches.sort(key=lambda record: record.resource_id)
        return tuple(matches[:limit])

    def upsert(
        self,
        resource_type: str,
        resource_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_revision: int | None = None,
    ) -> MutationResult:
        self._validate_resource_identity(resource_type, resource_id)
        normalized_payload = _normalize_mapping(payload, "payload")
        normalized_key = _validate_token(idempotency_key, "idempotency_key")
        _validate_expected_revision(expected_revision, "expected_revision")
        fingerprint = _fingerprint(
            {
                "operation": "upsert",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "payload": normalized_payload,
                "expected_revision": expected_revision,
            }
        )

        with self._lock:
            replay = self._idempotent_result(normalized_key, fingerprint, "upsert")
            if replay is not None:
                return MutationResult(record=_resource_from_result(replay), idempotent_replay=True)

            existing_rows = [
                (row_number, record)
                for row_number, record in self._resource_rows()
                if record.resource_type == resource_type and record.resource_id == resource_id
            ]
            if len(existing_rows) > 1:
                raise IdentityConflictError(
                    f"duplicate persisted resource identity: {resource_type}:{resource_id}"
                )
            current = existing_rows[0] if existing_rows else None
            current_revision = 0 if current is None else current[1].revision
            if expected_revision is not None and expected_revision != current_revision:
                raise RevisionConflictError(
                    f"expected revision {expected_revision}, current revision is {current_revision}"
                )

            record = ResourceRecord(
                resource_type=resource_type,
                resource_id=resource_id,
                payload=normalized_payload,
                revision=current_revision + 1,
            )
            now = _utc_text(self._clock())
            resource_values = (
                resource_type,
                resource_id,
                record.revision,
                _json_text(record.payload),
                now,
                normalized_key,
                fingerprint,
            )
            result_payload = {
                "kind": "upsert",
                "record": _resource_dict(record),
            }
            mutations = [
                SheetRowMutation(
                    tab="Resources",
                    values=resource_values,
                    row_number=None if current is None else current[0],
                ),
                SheetRowMutation(
                    tab="Idempotency",
                    values=(
                        normalized_key,
                        "upsert",
                        fingerprint,
                        _json_text(result_payload),
                        now,
                        f"{resource_type}/{resource_id}",
                    ),
                ),
            ]
            self._gateway.apply_mutations(mutations)
            readback = self.get(resource_type, resource_id)
            if readback != record:
                raise SheetsGatewayError("Google Sheets resource readback mismatch")
            return MutationResult(record=readback, idempotent_replay=False)

    def append_event(
        self,
        stream_type: str,
        stream_id: str,
        event_type: str,
        event_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str,
        expected_stream_revision: int | None = None,
    ) -> EventMutationResult:
        self._validate_resource_identity(stream_type, stream_id)
        if event_type not in self.schema().event_types:
            raise ValidationError(f"unknown event type: {event_type}")
        normalized_event_id = _validate_id(event_id, "event_id")
        normalized_payload = _normalize_mapping(payload, "payload")
        normalized_key = _validate_token(idempotency_key, "idempotency_key")
        _validate_expected_revision(expected_stream_revision, "expected_stream_revision")
        fingerprint = _fingerprint(
            {
                "operation": "append_event",
                "stream_type": stream_type,
                "stream_id": stream_id,
                "event_type": event_type,
                "event_id": normalized_event_id,
                "payload": normalized_payload,
                "expected_stream_revision": expected_stream_revision,
            }
        )

        with self._lock:
            replay = self._idempotent_result(normalized_key, fingerprint, "append_event")
            if replay is not None:
                return EventMutationResult(event=_event_from_result(replay), idempotent_replay=True)

            rows = self._event_rows()
            if any(event.event_id == normalized_event_id for _, event in rows):
                raise IdentityConflictError(f"event_id already exists: {normalized_event_id}")
            stream_events = [
                event
                for _, event in rows
                if event.stream_type == stream_type and event.stream_id == stream_id
            ]
            current_revision = max(
                (event.stream_revision for event in stream_events),
                default=0,
            )
            if (
                expected_stream_revision is not None
                and expected_stream_revision != current_revision
            ):
                raise RevisionConflictError(
                    "expected stream revision "
                    f"{expected_stream_revision}, current revision is {current_revision}"
                )

            event = EventRecord(
                event_id=normalized_event_id,
                stream_type=stream_type,
                stream_id=stream_id,
                event_type=event_type,
                payload=normalized_payload,
                stream_revision=current_revision + 1,
            )
            now = _utc_text(self._clock())
            result_payload = {"kind": "append_event", "event": _event_dict(event)}
            self._gateway.apply_mutations(
                [
                    SheetRowMutation(
                        tab="Events",
                        values=(
                            event_type,
                            normalized_event_id,
                            stream_type,
                            stream_id,
                            event.stream_revision,
                            _json_text(event.payload),
                            now,
                            normalized_key,
                        ),
                    ),
                    SheetRowMutation(
                        tab="Idempotency",
                        values=(
                            normalized_key,
                            "append_event",
                            fingerprint,
                            _json_text(result_payload),
                            now,
                            f"{stream_type}/{stream_id}#{normalized_event_id}",
                        ),
                    ),
                ]
            )
            readback_rows = [
                candidate
                for candidate in self.events_for(stream_type, stream_id, after_revision=event.stream_revision - 1)
                if candidate.event_id == normalized_event_id
            ]
            if readback_rows != [event]:
                raise SheetsGatewayError("Google Sheets event readback mismatch")
            return EventMutationResult(event=event, idempotent_replay=False)

    def events_for(
        self,
        stream_type: str,
        stream_id: str,
        *,
        after_revision: int = 0,
        limit: int = 100,
    ) -> tuple[EventRecord, ...]:
        self._validate_resource_identity(stream_type, stream_id)
        if not isinstance(after_revision, int) or isinstance(after_revision, bool) or after_revision < 0:
            raise ValidationError("after_revision must be a non-negative integer")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 1000:
            raise ValidationError("limit must be an integer from 1 through 1000")
        rows = [
            event
            for _, event in self._event_rows()
            if event.stream_type == stream_type
            and event.stream_id == stream_id
            and event.stream_revision > after_revision
        ]
        rows.sort(key=lambda event: event.stream_revision)
        return tuple(rows[:limit])

    def _metadata(self) -> dict[str, str]:
        rows = self._read_table("Metadata", "A", "B", _METADATA_HEADERS)
        result: dict[str, str] = {}
        for _, row in rows:
            key = _validate_token(row[0], "metadata key")
            value = _validate_token(row[1], f"metadata value for {key}")
            if key in result:
                raise ValidationError(f"duplicate Google Sheets metadata key: {key}")
            result[key] = value
        return result

    def _resource_rows(self) -> tuple[tuple[int, ResourceRecord], ...]:
        rows = self._read_table("Resources", "A", "G", _RESOURCE_HEADERS)
        parsed: list[tuple[int, ResourceRecord]] = []
        for row_number, row in rows:
            resource_type = _validate_token(row[0], "resource_type")
            resource_id = _validate_id(row[1], "resource_id")
            revision = _positive_int(row[2], "revision")
            payload = _parse_json_mapping(row[3], "payload_json")
            parsed.append(
                (
                    row_number,
                    ResourceRecord(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        payload=payload,
                        revision=revision,
                    ),
                )
            )
        return tuple(parsed)

    def _event_rows(self) -> tuple[tuple[int, EventRecord], ...]:
        rows = self._read_table("Events", "A", "H", _EVENT_HEADERS)
        parsed: list[tuple[int, EventRecord]] = []
        for row_number, row in rows:
            parsed.append(
                (
                    row_number,
                    EventRecord(
                        event_id=_validate_id(row[1], "event_id"),
                        stream_type=_validate_token(row[2], "stream_type"),
                        stream_id=_validate_id(row[3], "stream_id"),
                        event_type=_validate_token(row[0], "event_type"),
                        payload=_parse_json_mapping(row[5], "payload_json"),
                        stream_revision=_positive_int(row[4], "stream_revision"),
                    ),
                )
            )
        return tuple(parsed)

    def _idempotent_result(
        self,
        key: str,
        fingerprint: str,
        operation: str,
    ) -> Mapping[str, Any] | None:
        rows = self._read_table("Idempotency", "A", "F", _IDEMPOTENCY_HEADERS)
        matches = [row for _, row in rows if str(row[0]) == key]
        if not matches:
            return None
        if len(matches) != 1:
            raise IdempotencyConflictError(f"duplicate persisted idempotency key: {key}")
        row = matches[0]
        stored_operation = _validate_token(row[1], "idempotency operation")
        stored_hash = _validate_token(row[2], "request_hash")
        if stored_operation != operation:
            raise IdempotencyConflictError(
                "idempotency key was already used for a different operation"
            )
        if stored_hash != fingerprint:
            raise IdempotencyConflictError(
                "idempotency key was already used for different material input"
            )
        try:
            payload = json.loads(str(row[3]))
        except json.JSONDecodeError as exc:
            raise IdempotencyConflictError("persisted idempotency result is invalid") from exc
        if not isinstance(payload, Mapping) or payload.get("kind") != operation:
            raise IdempotencyConflictError("persisted idempotency result has wrong operation")
        return payload

    def _read_table(
        self,
        tab: str,
        start_column: str,
        end_column: str,
        headers: tuple[str, ...],
    ) -> tuple[tuple[int, tuple[object, ...]], ...]:
        rows = self._gateway.read_range(
            f"{tab}!{start_column}1:{end_column}{self._row_limit}"
        )
        if not rows:
            raise ValidationError(f"required Google Sheets tab is empty: {tab}")
        normalized_header = tuple(str(value) for value in rows[0])
        if normalized_header != headers:
            raise ValidationError(
                f"Google Sheets {tab} headers do not match adapter schema: {normalized_header!r}"
            )
        width = len(headers)
        result: list[tuple[int, tuple[object, ...]]] = []
        for row_number, raw in enumerate(rows[1:], start=2):
            values = tuple(raw)
            if not values or all(value in (None, "") for value in values):
                continue
            if len(values) > width:
                raise ValidationError(f"Google Sheets {tab} row {row_number} is too wide")
            padded = values + ("",) * (width - len(values))
            result.append((row_number, padded))
        return tuple(result)

    def _validate_resource_type(self, resource_type: str) -> None:
        if resource_type not in self.schema().resource_types:
            raise ValidationError(f"unknown resource type: {resource_type}")

    def _validate_resource_identity(self, resource_type: str, resource_id: str) -> None:
        self._validate_resource_type(resource_type)
        _validate_id(resource_id, "resource_id")


def _google_value(value: object) -> dict[str, object]:
    if value is None:
        return {}
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"numberValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    raise ValidationError(f"unsupported Google Sheets cell value type: {type(value).__name__}")


def _parse_type_json(value: object, field: str) -> frozenset[str]:
    try:
        decoded = json.loads(_validate_token(value, field))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{field} must be valid JSON") from exc
    if not isinstance(decoded, list) or not decoded:
        raise ValidationError(f"{field} must be a non-empty JSON list")
    normalized = tuple(_validate_token(item, field) for item in decoded)
    if len(set(normalized)) != len(normalized):
        raise ValidationError(f"{field} must not contain duplicates")
    return frozenset(normalized)


def _validate_token(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValidationError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise ValidationError(f"{field} must be at most 128 characters")
    return value


def _validate_id(value: object, field: str) -> str:
    normalized = _validate_token(value, field)
    if not _ID_RE.fullmatch(normalized):
        raise ValidationError(
            f"{field} must match {_ID_RE.pattern} for deterministic canonical identity"
        )
    return normalized


def _validate_expected_revision(value: int | None, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValidationError(f"{field} must be a non-negative integer or None")


def _positive_int(value: object, field: str) -> int:
    if isinstance(value, bool):
        raise ValidationError(f"{field} must be a positive integer")
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if not isinstance(value, int) or value < 1:
        raise ValidationError(f"{field} must be a positive integer")
    return value


def _normalize_mapping(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{field} must be a mapping")
    material = dict(value)
    try:
        encoded = json.dumps(
            material,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field} must contain JSON-compatible values") from exc
    return json.loads(encoded)


def _parse_json_mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a JSON object string")
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{field} contains invalid JSON") from exc
    return _normalize_mapping(decoded, field)


def _json_text(value: object) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValidationError("persisted value must be JSON-compatible") from exc


def _fingerprint(material: Mapping[str, Any]) -> str:
    return hashlib.sha256(_json_text(material).encode("utf-8")).hexdigest()


def _utc_text(value: datetime) -> str:
    if not isinstance(value, datetime):
        raise ValidationError("clock must return datetime")
    if value.tzinfo is None:
        raise ValidationError("clock datetime must be timezone-aware")
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resource_dict(record: ResourceRecord) -> dict[str, object]:
    return {
        "resource_type": record.resource_type,
        "resource_id": record.resource_id,
        "payload": record.payload,
        "revision": record.revision,
    }


def _resource_from_result(payload: Mapping[str, Any]) -> ResourceRecord:
    record = payload.get("record")
    if not isinstance(record, Mapping):
        raise IdempotencyConflictError("persisted upsert replay result is invalid")
    try:
        return ResourceRecord(
            resource_type=_validate_token(record["resource_type"], "resource_type"),
            resource_id=_validate_id(record["resource_id"], "resource_id"),
            payload=_normalize_mapping(record["payload"], "payload"),
            revision=_positive_int(record["revision"], "revision"),
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise IdempotencyConflictError("persisted upsert replay result is invalid") from exc


def _event_dict(event: EventRecord) -> dict[str, object]:
    return {
        "event_id": event.event_id,
        "stream_type": event.stream_type,
        "stream_id": event.stream_id,
        "event_type": event.event_type,
        "payload": event.payload,
        "stream_revision": event.stream_revision,
    }


def _event_from_result(payload: Mapping[str, Any]) -> EventRecord:
    event = payload.get("event")
    if not isinstance(event, Mapping):
        raise IdempotencyConflictError("persisted event replay result is invalid")
    try:
        return EventRecord(
            event_id=_validate_id(event["event_id"], "event_id"),
            stream_type=_validate_token(event["stream_type"], "stream_type"),
            stream_id=_validate_id(event["stream_id"], "stream_id"),
            event_type=_validate_token(event["event_type"], "event_type"),
            payload=_normalize_mapping(event["payload"], "payload"),
            stream_revision=_positive_int(event["stream_revision"], "stream_revision"),
        )
    except (KeyError, TypeError, ValidationError) as exc:
        raise IdempotencyConflictError("persisted event replay result is invalid") from exc
