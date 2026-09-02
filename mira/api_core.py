"""Transport-independent MIRA API service semantics.

This layer trusts an AuthenticatedPrincipal supplied by a transport/auth
boundary. It performs compatibility checks, same-user authorization, Authority
Registry routing, canonical state operations, exact readback, error mapping and
synthetic audit recording. It also defines the provider-neutral same-user client
session trust seam used by native clients before transport-specific auth exists.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import hmac
import re
import secrets
from typing import Any, Callable, Mapping, Protocol

from .authority import (
    AuthorityRegistry,
    AuthorityRegistryError,
    AuthorityUnavailableError,
)
from .structured_state import (
    EventRecord,
    IdempotencyConflictError,
    IdentityConflictError,
    NotFoundError,
    ResourceRecord,
    RevisionConflictError,
    ValidationError,
)


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_DATA_CLASS_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$")
_QUERY_ACTIONS = frozenset({"read", "query"})
_COMMAND_ACTIONS = frozenset({"upsert", "append_event"})
_ALL_ACTIONS = _QUERY_ACTIONS | _COMMAND_ACTIONS


class ApiServiceError(Exception):
    """Base stable API-service error with a machine-readable category."""

    code = "api_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ApiValidationError(ApiServiceError):
    code = "validation_error"


class ApiCompatibilityError(ApiServiceError):
    code = "compatibility_error"


class ApiAuthenticationError(ApiServiceError):
    code = "authentication_error"


class ApiAuthorizationError(ApiServiceError):
    code = "authorization_error"


class ApiConflictError(ApiServiceError):
    code = "conflict"


class ApiNotFoundError(ApiServiceError):
    code = "not_found"


class ApiAuthorityError(ApiServiceError):
    code = "authority_unavailable"


class ApiReadbackError(ApiServiceError):
    code = "readback_error"


@dataclass(frozen=True)
class Grant:
    data_class: str
    action: str
    resource_id: str


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    """Identity context already authenticated by the transport boundary."""

    actor_id: str
    client_id: str
    grants: tuple[Grant, ...]


@dataclass(frozen=True)
class ClientEnrollment:
    """One-time enrollment response containing the raw opaque credential."""

    actor_id: str
    client_id: str
    credential: str
    grants: tuple[Grant, ...]


@dataclass(frozen=True)
class ClientSessionSnapshot:
    """Stored session state. Raw credential material is deliberately absent."""

    actor_id: str
    client_id: str
    credential_verifier: str
    grants: tuple[Grant, ...]
    revoked: bool


class ClientSessionRegistry:
    """Provider-neutral same-user enrollment and revocation trust seam.

    The registry never stores provider/database credentials. Enrollment returns
    one opaque client credential, stores only a SHA-256 verifier, and reconstructs
    an existing AuthenticatedPrincipal only while the exact credential remains
    active. Transport persistence and Android OS-protected storage are separate
    adapters layered around this contract.
    """

    def __init__(self, credential_factory: Callable[[], str] | None = None) -> None:
        self._credential_factory = credential_factory or (
            lambda: secrets.token_urlsafe(32)
        )
        self._sessions: dict[str, ClientSessionSnapshot] = {}

    def enroll(
        self,
        *,
        actor_id: str,
        client_id: str,
        grants: tuple[Grant, ...],
    ) -> ClientEnrollment:
        principal = _validate_principal(
            AuthenticatedPrincipal(
                actor_id=actor_id,
                client_id=client_id,
                grants=grants,
            )
        )
        if principal.client_id in self._sessions:
            raise ApiConflictError("client_id is already enrolled")

        credential = self._credential_factory()
        _validate_client_credential(credential)
        verifier = _credential_verifier(credential)
        snapshot = ClientSessionSnapshot(
            actor_id=principal.actor_id,
            client_id=principal.client_id,
            credential_verifier=verifier,
            grants=principal.grants,
            revoked=False,
        )
        self._sessions[principal.client_id] = snapshot
        return ClientEnrollment(
            actor_id=principal.actor_id,
            client_id=principal.client_id,
            credential=credential,
            grants=principal.grants,
        )

    def authenticate(self, *, client_id: str, credential: str) -> AuthenticatedPrincipal:
        client_id = _validate_id(client_id, "client_id")
        _validate_client_credential(credential)
        snapshot = self._sessions.get(client_id)
        if snapshot is None:
            raise ApiAuthenticationError("client session is not enrolled")
        if snapshot.revoked:
            raise ApiAuthenticationError("client session is revoked")
        if not hmac.compare_digest(
            snapshot.credential_verifier,
            _credential_verifier(credential),
        ):
            raise ApiAuthenticationError("client credential is invalid")
        return _validate_principal(
            AuthenticatedPrincipal(
                actor_id=snapshot.actor_id,
                client_id=snapshot.client_id,
                grants=snapshot.grants,
            )
        )

    def revoke(self, client_id: str) -> ClientSessionSnapshot:
        client_id = _validate_id(client_id, "client_id")
        snapshot = self._sessions.get(client_id)
        if snapshot is None:
            raise ApiNotFoundError("client session is not enrolled")
        if snapshot.revoked:
            return deepcopy(snapshot)
        revoked = ClientSessionSnapshot(
            actor_id=snapshot.actor_id,
            client_id=snapshot.client_id,
            credential_verifier=snapshot.credential_verifier,
            grants=snapshot.grants,
            revoked=True,
        )
        self._sessions[client_id] = revoked
        return deepcopy(revoked)

    def snapshot(self, client_id: str) -> ClientSessionSnapshot:
        client_id = _validate_id(client_id, "client_id")
        snapshot = self._sessions.get(client_id)
        if snapshot is None:
            raise ApiNotFoundError("client session is not enrolled")
        return deepcopy(snapshot)


@dataclass(frozen=True)
class QueryEnvelope:
    request_id: str
    subject_id: str
    data_class: str
    action: str
    api_major: int
    schema_version: str
    resource_id: str | None = None
    filters: Mapping[str, Any] | None = None
    limit: int = 100


@dataclass(frozen=True)
class CommandEnvelope:
    command_id: str
    subject_id: str
    data_class: str
    action: str
    api_major: int
    schema_version: str
    resource_id: str
    payload: Mapping[str, Any]
    idempotency_key: str
    expected_revision: int | None = None
    event_id: str | None = None
    event_type: str | None = None


@dataclass(frozen=True)
class QueryResult:
    request_id: str
    authority_id: str
    items: tuple[ResourceRecord, ...]


@dataclass(frozen=True)
class CommandResult:
    command_id: str
    authority_id: str
    record: ResourceRecord | None
    event: EventRecord | None
    idempotent_replay: bool
    readback_verified: bool


@dataclass(frozen=True)
class AuditEvent:
    request_id: str
    actor_id: str
    client_id: str
    subject_id: str
    data_class: str
    action: str
    resource_id: str | None
    authorization: str
    outcome: str
    error_code: str | None = None
    authority_id: str | None = None


class AuditSink(Protocol):
    def record(self, event: AuditEvent) -> None: ...


class InMemoryAuditSink:
    """Synthetic nonauthoritative audit sink for service verification."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self._events.append(deepcopy(event))

    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(deepcopy(self._events))


class ApiService:
    """Versioned same-user service core over the canonical Authority Registry."""

    def __init__(
        self,
        registry: AuthorityRegistry,
        audit_sink: AuditSink,
        *,
        api_major: int,
        schema_version: str,
    ) -> None:
        if not isinstance(api_major, int) or isinstance(api_major, bool) or api_major < 1:
            raise ApiValidationError("api_major must be a positive integer")
        self._registry = registry
        self._audit = audit_sink
        self._api_major = api_major
        self._schema_version = _validate_token(schema_version, "schema_version")

    def execute_query(
        self,
        principal: AuthenticatedPrincipal,
        envelope: QueryEnvelope,
    ) -> QueryResult:
        principal = _validate_principal(principal)
        request_id = _validate_id(envelope.request_id, "request_id")
        audit_base = self._audit_base(principal, envelope, request_id)
        authorization = "not_evaluated"
        authority_id: str | None = None

        try:
            self._preflight_query(envelope)
            self._authorize(
                principal,
                subject_id=envelope.subject_id,
                data_class=envelope.data_class,
                action=envelope.action,
                resource_id=envelope.resource_id,
            )
            authorization = "allowed"
            route = self._registry.resolve(envelope.data_class)
            authority_id = route.authority.spec.authority_id

            if envelope.action == "read":
                item = route.adapter.get(envelope.data_class, envelope.resource_id)
                result = QueryResult(
                    request_id=request_id,
                    authority_id=authority_id,
                    items=(item,),
                )
            else:
                items = route.adapter.query(
                    envelope.data_class,
                    filters=envelope.filters,
                    limit=envelope.limit,
                )
                result = QueryResult(
                    request_id=request_id,
                    authority_id=authority_id,
                    items=tuple(items),
                )

        except ApiAuthorizationError as exc:
            self._record_audit(
                audit_base,
                authorization="denied",
                outcome="denied",
                error_code=exc.code,
                authority_id=authority_id,
            )
            raise
        except ApiServiceError as exc:
            self._record_audit(
                audit_base,
                authorization=authorization,
                outcome="failed",
                error_code=exc.code,
                authority_id=authority_id,
            )
            raise
        except Exception as exc:
            mapped = self._map_error(exc)
            self._record_audit(
                audit_base,
                authorization=authorization,
                outcome="failed",
                error_code=mapped.code,
                authority_id=authority_id,
            )
            raise mapped from exc

        self._record_audit(
            audit_base,
            authorization="allowed",
            outcome="success",
            authority_id=authority_id,
        )
        return result

    def execute_command(
        self,
        principal: AuthenticatedPrincipal,
        envelope: CommandEnvelope,
    ) -> CommandResult:
        principal = _validate_principal(principal)
        command_id = _validate_id(envelope.command_id, "command_id")
        audit_base = self._audit_base(principal, envelope, command_id)
        authorization = "not_evaluated"
        authority_id: str | None = None

        try:
            self._preflight_command(envelope)
            self._authorize(
                principal,
                subject_id=envelope.subject_id,
                data_class=envelope.data_class,
                action=envelope.action,
                resource_id=envelope.resource_id,
            )
            authorization = "allowed"
            route = self._registry.resolve(envelope.data_class)
            authority_id = route.authority.spec.authority_id

            if envelope.action == "upsert":
                mutation = route.adapter.upsert(
                    envelope.data_class,
                    envelope.resource_id,
                    envelope.payload,
                    idempotency_key=envelope.idempotency_key,
                    expected_revision=envelope.expected_revision,
                )
                readback = route.adapter.get(envelope.data_class, envelope.resource_id)
                if readback != mutation.record:
                    raise ApiReadbackError(
                        "canonical read-after-write does not match mutation result"
                    )
                result = CommandResult(
                    command_id=command_id,
                    authority_id=authority_id,
                    record=readback,
                    event=None,
                    idempotent_replay=mutation.idempotent_replay,
                    readback_verified=True,
                )
            else:
                mutation = route.adapter.append_event(
                    envelope.data_class,
                    envelope.resource_id,
                    envelope.event_type,
                    envelope.event_id,
                    envelope.payload,
                    idempotency_key=envelope.idempotency_key,
                    expected_stream_revision=envelope.expected_revision,
                )
                rows = route.adapter.events_for(
                    envelope.data_class,
                    envelope.resource_id,
                    after_revision=mutation.event.stream_revision - 1,
                    limit=1,
                )
                if not rows or rows[0] != mutation.event:
                    raise ApiReadbackError(
                        "canonical event readback does not match append result"
                    )
                result = CommandResult(
                    command_id=command_id,
                    authority_id=authority_id,
                    record=None,
                    event=rows[0],
                    idempotent_replay=mutation.idempotent_replay,
                    readback_verified=True,
                )

        except ApiAuthorizationError as exc:
            self._record_audit(
                audit_base,
                authorization="denied",
                outcome="denied",
                error_code=exc.code,
                authority_id=authority_id,
            )
            raise
        except ApiServiceError as exc:
            self._record_audit(
                audit_base,
                authorization=authorization,
                outcome="failed",
                error_code=exc.code,
                authority_id=authority_id,
            )
            raise
        except Exception as exc:
            mapped = self._map_error(exc)
            self._record_audit(
                audit_base,
                authorization=authorization,
                outcome="failed",
                error_code=mapped.code,
                authority_id=authority_id,
            )
            raise mapped from exc

        self._record_audit(
            audit_base,
            authorization="allowed",
            outcome="success",
            authority_id=authority_id,
        )
        return result

    def _preflight_query(self, envelope: QueryEnvelope) -> None:
        self._check_compatibility(envelope.api_major, envelope.schema_version)
        _validate_subject_and_class(envelope.subject_id, envelope.data_class)
        if envelope.action not in _QUERY_ACTIONS:
            raise ApiValidationError(f"unsupported query action: {envelope.action}")
        if envelope.action == "read":
            if envelope.resource_id is None:
                raise ApiValidationError("read requires resource_id")
            _validate_id(envelope.resource_id, "resource_id")
            if envelope.filters:
                raise ApiValidationError("read does not accept filters")
        else:
            if envelope.resource_id is not None:
                raise ApiValidationError("query must not specify resource_id")
            if not isinstance(envelope.limit, int) or isinstance(envelope.limit, bool):
                raise ApiValidationError("query limit must be an integer")
            if not 1 <= envelope.limit <= 1000:
                raise ApiValidationError("query limit must be from 1 through 1000")
            if envelope.filters is not None and not isinstance(envelope.filters, Mapping):
                raise ApiValidationError("query filters must be a mapping")

    def _preflight_command(self, envelope: CommandEnvelope) -> None:
        self._check_compatibility(envelope.api_major, envelope.schema_version)
        _validate_subject_and_class(envelope.subject_id, envelope.data_class)
        if envelope.action not in _COMMAND_ACTIONS:
            raise ApiValidationError(f"unsupported command action: {envelope.action}")
        _validate_id(envelope.resource_id, "resource_id")
        _validate_token(envelope.idempotency_key, "idempotency_key")
        if not isinstance(envelope.payload, Mapping):
            raise ApiValidationError("command payload must be a mapping")
        if envelope.expected_revision is not None:
            if (
                not isinstance(envelope.expected_revision, int)
                or isinstance(envelope.expected_revision, bool)
                or envelope.expected_revision < 0
            ):
                raise ApiValidationError(
                    "expected_revision must be a non-negative integer or None"
                )
        if envelope.action == "append_event":
            if envelope.event_id is None or envelope.event_type is None:
                raise ApiValidationError(
                    "append_event requires event_id and event_type"
                )
            _validate_id(envelope.event_id, "event_id")
            _validate_token(envelope.event_type, "event_type")
        elif envelope.event_id is not None or envelope.event_type is not None:
            raise ApiValidationError("upsert must not specify event fields")

    def _check_compatibility(self, api_major: int, schema_version: str) -> None:
        if api_major != self._api_major or schema_version != self._schema_version:
            raise ApiCompatibilityError(
                "request API/schema version is incompatible with this service"
            )

    def _authorize(
        self,
        principal: AuthenticatedPrincipal,
        *,
        subject_id: str,
        data_class: str,
        action: str,
        resource_id: str | None,
    ) -> None:
        if subject_id != principal.actor_id:
            raise ApiAuthorizationError(
                "cross-person requests are blocked in the same-user API core"
            )

        needed_resource = "*" if action == "query" else resource_id
        for grant in principal.grants:
            if (
                grant.data_class == data_class
                and grant.action == action
                and (grant.resource_id == "*" or grant.resource_id == needed_resource)
            ):
                if action == "query" and grant.resource_id != "*":
                    continue
                return
        raise ApiAuthorizationError(
            f"principal is not authorized for {data_class}:{action}:{needed_resource}"
        )

    def _map_error(self, exc: Exception) -> ApiServiceError:
        if isinstance(
            exc,
            (RevisionConflictError, IdempotencyConflictError, IdentityConflictError),
        ):
            return ApiConflictError(str(exc))
        if isinstance(exc, NotFoundError):
            return ApiNotFoundError(str(exc))
        if isinstance(exc, ValidationError):
            return ApiValidationError(str(exc))
        if isinstance(exc, (AuthorityUnavailableError, AuthorityRegistryError)):
            return ApiAuthorityError(str(exc))
        return ApiServiceError("unexpected API service failure")

    def _audit_base(
        self,
        principal: AuthenticatedPrincipal,
        envelope: QueryEnvelope | CommandEnvelope,
        request_id: str,
    ) -> dict[str, str | None]:
        return {
            "request_id": request_id,
            "actor_id": principal.actor_id,
            "client_id": principal.client_id,
            "subject_id": envelope.subject_id,
            "data_class": envelope.data_class,
            "action": envelope.action,
            "resource_id": envelope.resource_id,
        }

    def _record_audit(
        self,
        base: Mapping[str, str | None],
        *,
        authorization: str,
        outcome: str,
        error_code: str | None = None,
        authority_id: str | None = None,
    ) -> None:
        self._audit.record(
            AuditEvent(
                request_id=base["request_id"],
                actor_id=base["actor_id"],
                client_id=base["client_id"],
                subject_id=base["subject_id"],
                data_class=base["data_class"],
                action=base["action"],
                resource_id=base["resource_id"],
                authorization=authorization,
                outcome=outcome,
                error_code=error_code,
                authority_id=authority_id,
            )
        )


def _validate_principal(principal: AuthenticatedPrincipal) -> AuthenticatedPrincipal:
    if not isinstance(principal, AuthenticatedPrincipal):
        raise ApiAuthorizationError("authenticated principal context is required")
    actor_id = _validate_id(principal.actor_id, "actor_id")
    client_id = _validate_id(principal.client_id, "client_id")
    grants: list[Grant] = []
    for grant in principal.grants:
        if not isinstance(grant, Grant):
            raise ApiAuthorizationError("principal grants must be Grant values")
        data_class = _validate_data_class(grant.data_class)
        if grant.action not in _ALL_ACTIONS:
            raise ApiAuthorizationError(f"unknown grant action: {grant.action}")
        resource_id = (
            "*"
            if grant.resource_id == "*"
            else _validate_id(grant.resource_id, "grant.resource_id")
        )
        if grant.action == "query" and resource_id != "*":
            raise ApiAuthorizationError("query grants must be class-level wildcard grants")
        grants.append(
            Grant(
                data_class=data_class,
                action=grant.action,
                resource_id=resource_id,
            )
        )
    return AuthenticatedPrincipal(
        actor_id=actor_id,
        client_id=client_id,
        grants=tuple(grants),
    )


def _validate_subject_and_class(subject_id: str, data_class: str) -> None:
    _validate_id(subject_id, "subject_id")
    _validate_data_class(data_class)


def _validate_data_class(value: str) -> str:
    if not isinstance(value, str) or not _DATA_CLASS_RE.fullmatch(value):
        raise ApiValidationError(f"data_class must match {_DATA_CLASS_RE.pattern}")
    return value


def _validate_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ApiValidationError(f"{field} must match {_ID_RE.pattern}")
    return value


def _validate_token(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ApiValidationError(f"{field} must be a non-empty trimmed string")
    if len(value) > 128:
        raise ApiValidationError(f"{field} must be at most 128 characters")
    return value


def _validate_client_credential(value: str) -> str:
    if not isinstance(value, str) or len(value) < 32 or len(value) > 256:
        raise ApiAuthenticationError(
            "client credential must be opaque text from 32 through 256 characters"
        )
    if value != value.strip():
        raise ApiAuthenticationError("client credential must not contain edge whitespace")
    return value


def _credential_verifier(credential: str) -> str:
    return hashlib.sha256(credential.encode("utf-8")).hexdigest()
