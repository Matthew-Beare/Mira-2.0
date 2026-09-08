"""Scoped client-session authentication and WSGI HTTP transport for MIRA.

This module wraps the transport-independent :mod:`mira.api_core` service. It
stores only bearer-token hashes, supports expiry/revocation, enforces a bounded
HTTP surface, and intentionally contains no provider/deployment-specific code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import hmac
from http import HTTPStatus
import json
import re
import secrets
import time
from typing import Callable, Iterable, Mapping, Protocol
from uuid import uuid4

from .api_core import (
    ApiAuthorityError,
    ApiAuthorizationError,
    ApiCompatibilityError,
    ApiConflictError,
    ApiNotFoundError,
    ApiReadbackError,
    ApiService,
    ApiServiceError,
    ApiValidationError,
    AuthenticatedPrincipal,
    CommandEnvelope,
    Grant,
    QueryEnvelope,
)


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_DEFAULT_MAX_BODY_BYTES = 64 * 1024
_MAX_SESSION_TTL_SECONDS = 30 * 24 * 60 * 60


class SessionError(Exception):
    """Base session credential failure."""


class SessionValidationError(SessionError):
    """Raised when session issuance/revocation input is invalid."""


class SessionAuthenticationError(SessionError):
    """Raised when a bearer credential cannot authenticate a live session."""


class BearerAuthenticator(Protocol):
    """Authentication boundary consumed by the WSGI transport."""

    def authenticate(self, token: str) -> AuthenticatedPrincipal: ...


@dataclass(frozen=True)
class IssuedCredential:
    """One-time raw credential returned to the provisioning boundary."""

    session_id: str
    token: str
    issued_at: int
    expires_at: int


@dataclass(frozen=True)
class SessionMetadata:
    """Persisted in-memory session state. Raw bearer token is never retained."""

    session_id: str
    token_hash: str
    actor_id: str
    client_id: str
    grants: tuple[Grant, ...]
    issued_at: int
    expires_at: int
    revoked_at: int | None = None


class InMemorySessionStore:
    """Synthetic scoped session store with hashed bearer-token lookup."""

    def __init__(
        self,
        *,
        clock: Callable[[], int] | None = None,
        token_factory: Callable[[], str] | None = None,
        session_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._clock = clock or (lambda: int(time.time()))
        self._token_factory = token_factory or (lambda: secrets.token_urlsafe(32))
        self._session_id_factory = session_id_factory or (lambda: str(uuid4()))
        self._sessions: dict[str, SessionMetadata] = {}
        self._token_index: dict[str, str] = {}

    def issue(
        self,
        principal: AuthenticatedPrincipal,
        *,
        ttl_seconds: int = 3600,
    ) -> IssuedCredential:
        principal = _copy_principal(principal)
        if (
            not isinstance(ttl_seconds, int)
            or isinstance(ttl_seconds, bool)
            or not 1 <= ttl_seconds <= _MAX_SESSION_TTL_SECONDS
        ):
            raise SessionValidationError(
                f"ttl_seconds must be from 1 through {_MAX_SESSION_TTL_SECONDS}"
            )

        now = _clock_value(self._clock)
        session_id = _validate_id(self._session_id_factory(), "session_id")
        if session_id in self._sessions:
            raise SessionValidationError("session_id collision")

        token = self._token_factory()
        if not isinstance(token, str) or len(token) < 32 or token != token.strip():
            raise SessionValidationError(
                "token factory must return a trimmed high-entropy string of at least 32 characters"
            )
        token_hash = _hash_token(token)
        if token_hash in self._token_index:
            raise SessionValidationError("bearer token collision")

        metadata = SessionMetadata(
            session_id=session_id,
            token_hash=token_hash,
            actor_id=principal.actor_id,
            client_id=principal.client_id,
            grants=tuple(principal.grants),
            issued_at=now,
            expires_at=now + ttl_seconds,
        )
        self._sessions[session_id] = metadata
        self._token_index[token_hash] = session_id
        return IssuedCredential(
            session_id=session_id,
            token=token,
            issued_at=metadata.issued_at,
            expires_at=metadata.expires_at,
        )

    def authenticate(self, token: str) -> AuthenticatedPrincipal:
        if not isinstance(token, str) or not token or token != token.strip():
            raise SessionAuthenticationError("invalid bearer credential")
        token_hash = _hash_token(token)
        session_id = self._token_index.get(token_hash)
        if session_id is None:
            raise SessionAuthenticationError("unknown bearer credential")
        metadata = self._sessions.get(session_id)
        if metadata is None or not hmac.compare_digest(metadata.token_hash, token_hash):
            raise SessionAuthenticationError("unknown bearer credential")
        if metadata.revoked_at is not None:
            raise SessionAuthenticationError("session is revoked")
        if _clock_value(self._clock) >= metadata.expires_at:
            raise SessionAuthenticationError("session is expired")
        return AuthenticatedPrincipal(
            actor_id=metadata.actor_id,
            client_id=metadata.client_id,
            grants=tuple(metadata.grants),
        )

    def revoke(self, session_id: str) -> SessionMetadata:
        session_id = _validate_id(session_id, "session_id")
        metadata = self._sessions.get(session_id)
        if metadata is None:
            raise SessionValidationError(f"unknown session_id: {session_id}")
        if metadata.revoked_at is None:
            metadata = replace(metadata, revoked_at=_clock_value(self._clock))
            self._sessions[session_id] = metadata
        return metadata

    def metadata(self, session_id: str) -> SessionMetadata:
        session_id = _validate_id(session_id, "session_id")
        metadata = self._sessions.get(session_id)
        if metadata is None:
            raise SessionValidationError(f"unknown session_id: {session_id}")
        return replace(metadata, grants=tuple(metadata.grants))


@dataclass(frozen=True)
class HttpError:
    status: int
    code: str
    message: str


class WsgiApiApp:
    """Bounded WSGI adapter exposing the verified API service core."""

    def __init__(
        self,
        service: ApiService,
        authenticator: BearerAuthenticator,
        *,
        require_https: bool = True,
        max_body_bytes: int = _DEFAULT_MAX_BODY_BYTES,
    ) -> None:
        if not callable(getattr(authenticator, "authenticate", None)):
            raise ValueError("authenticator must implement authenticate(token)")
        if not isinstance(require_https, bool):
            raise ValueError("require_https must be boolean")
        if (
            not isinstance(max_body_bytes, int)
            or isinstance(max_body_bytes, bool)
            or not 1 <= max_body_bytes <= 1024 * 1024
        ):
            raise ValueError("max_body_bytes must be from 1 through 1048576")
        self._service = service
        self._authenticator = authenticator
        self._require_https = require_https
        self._max_body_bytes = max_body_bytes

    def __call__(self, environ: Mapping[str, object], start_response):
        method = str(environ.get("REQUEST_METHOD", "")).upper()
        path = str(environ.get("PATH_INFO", ""))

        if path == "/v1/health":
            if method != "GET":
                return self._respond(
                    start_response,
                    HTTPStatus.METHOD_NOT_ALLOWED,
                    {"error": {"code": "method_not_allowed", "message": "health requires GET"}},
                    extra_headers=(("Allow", "GET"),),
                )
            return self._respond(
                start_response,
                HTTPStatus.OK,
                {"service": "mira", "status": "ok"},
            )

        if path not in {"/v1/query", "/v1/commands"}:
            return self._respond(
                start_response,
                HTTPStatus.NOT_FOUND,
                {"error": {"code": "route_not_found", "message": "route not found"}},
            )
        if method != "POST":
            return self._respond(
                start_response,
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"error": {"code": "method_not_allowed", "message": "protected API routes require POST"}},
                extra_headers=(("Allow", "POST"),),
            )

        if self._require_https and str(environ.get("wsgi.url_scheme", "http")).lower() != "https":
            return self._respond_error(
                start_response,
                HttpError(400, "https_required", "protected API routes require HTTPS"),
            )

        try:
            principal = self._authenticate(environ)
            body = self._json_body(environ)
            if path == "/v1/query":
                try:
                    envelope = QueryEnvelope(**body)
                except TypeError as exc:
                    raise _TransportFailure(400, "invalid_request", "invalid query envelope") from exc
                result = self._service.execute_query(principal, envelope)
            else:
                try:
                    envelope = CommandEnvelope(**body)
                except TypeError as exc:
                    raise _TransportFailure(400, "invalid_request", "invalid command envelope") from exc
                result = self._service.execute_command(principal, envelope)
            return self._respond(start_response, HTTPStatus.OK, asdict(result))
        except SessionAuthenticationError as exc:
            return self._respond_error(
                start_response,
                HttpError(401, "authentication_error", str(exc)),
                authenticate=True,
            )
        except _TransportFailure as exc:
            return self._respond_error(
                start_response,
                HttpError(exc.status, exc.code, exc.message),
            )
        except ApiServiceError as exc:
            return self._respond_error(start_response, _map_api_error(exc))
        except Exception:
            return self._respond_error(
                start_response,
                HttpError(500, "internal_error", "unexpected server failure"),
            )

    def _authenticate(self, environ: Mapping[str, object]) -> AuthenticatedPrincipal:
        authorization = environ.get("HTTP_AUTHORIZATION")
        if not isinstance(authorization, str):
            raise SessionAuthenticationError("missing bearer credential")
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
            raise SessionAuthenticationError("malformed bearer credential")
        return self._authenticator.authenticate(parts[1])

    def _json_body(self, environ: Mapping[str, object]) -> dict[str, object]:
        raw_length = environ.get("CONTENT_LENGTH")
        if raw_length in (None, ""):
            raise _TransportFailure(411, "length_required", "Content-Length is required")
        try:
            length = int(str(raw_length))
        except ValueError as exc:
            raise _TransportFailure(400, "invalid_content_length", "invalid Content-Length") from exc
        if length < 0:
            raise _TransportFailure(400, "invalid_content_length", "invalid Content-Length")
        if length > self._max_body_bytes:
            raise _TransportFailure(413, "payload_too_large", "request body exceeds configured limit")
        stream = environ.get("wsgi.input")
        if stream is None or not hasattr(stream, "read"):
            raise _TransportFailure(400, "invalid_request", "request body stream is unavailable")
        raw = stream.read(length)
        if not isinstance(raw, (bytes, bytearray)) or len(raw) != length:
            raise _TransportFailure(400, "invalid_request", "request body length does not match Content-Length")
        try:
            decoded = raw.decode("utf-8")
            body = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise _TransportFailure(400, "invalid_json", "request body must be valid UTF-8 JSON") from exc
        if not isinstance(body, dict):
            raise _TransportFailure(400, "invalid_json", "request JSON must be an object")
        return body

    def _respond_error(
        self,
        start_response,
        error: HttpError,
        *,
        authenticate: bool = False,
    ):
        headers: tuple[tuple[str, str], ...] = ()
        if authenticate:
            headers = (("WWW-Authenticate", "Bearer"),)
        return self._respond(
            start_response,
            HTTPStatus(error.status),
            {"error": {"code": error.code, "message": error.message}},
            extra_headers=headers,
        )

    def _respond(
        self,
        start_response,
        status: HTTPStatus,
        payload: object,
        *,
        extra_headers: Iterable[tuple[str, str]] = (),
    ):
        body = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ]
        headers.extend(extra_headers)
        start_response(f"{status.value} {status.phrase}", headers)
        return [body]


class _TransportFailure(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def _map_api_error(exc: ApiServiceError) -> HttpError:
    if isinstance(exc, ApiValidationError):
        status = 400
    elif isinstance(exc, ApiAuthorizationError):
        status = 403
    elif isinstance(exc, ApiCompatibilityError):
        status = 409
    elif isinstance(exc, ApiConflictError):
        status = 409
    elif isinstance(exc, ApiNotFoundError):
        status = 404
    elif isinstance(exc, ApiAuthorityError):
        status = 503
    elif isinstance(exc, ApiReadbackError):
        status = 502
    else:
        status = 500
    message = exc.message if status != 500 else "unexpected API service failure"
    return HttpError(status=status, code=exc.code, message=message)


def _copy_principal(principal: AuthenticatedPrincipal) -> AuthenticatedPrincipal:
    if not isinstance(principal, AuthenticatedPrincipal):
        raise SessionValidationError("principal must be an AuthenticatedPrincipal")
    actor_id = _validate_id(principal.actor_id, "actor_id")
    client_id = _validate_id(principal.client_id, "client_id")
    grants: list[Grant] = []
    for grant in principal.grants:
        if not isinstance(grant, Grant):
            raise SessionValidationError("principal grants must be Grant values")
        grants.append(
            Grant(
                data_class=str(grant.data_class),
                action=str(grant.action),
                resource_id=str(grant.resource_id),
            )
        )
    return AuthenticatedPrincipal(
        actor_id=actor_id,
        client_id=client_id,
        grants=tuple(grants),
    )


def _clock_value(clock: Callable[[], int]) -> int:
    value = clock()
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SessionValidationError("clock must return a non-negative integer epoch second")
    return value


def _validate_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise SessionValidationError(f"{field} must match {_ID_RE.pattern}")
    return value


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Worker authentication is intentionally distinct from ordinary API client sessions.
# A worker credential proves a worker/principal identity over an approved secure
# channel; it does not mint an AuthenticatedPrincipal or generic MIRROR grants.
WORKER_CHANNEL_MUTUAL_TLS = "mutual_tls"
WORKER_CHANNEL_WIREGUARD = "wireguard"
WORKER_CHANNEL_AUTHENTICATED_OUTBOUND = "authenticated_outbound"
WORKER_SECURE_CHANNELS = frozenset(
    {
        WORKER_CHANNEL_MUTUAL_TLS,
        WORKER_CHANNEL_WIREGUARD,
        WORKER_CHANNEL_AUTHENTICATED_OUTBOUND,
    }
)
_DEFAULT_WORKER_CHANNEL_MAX_AGE_SECONDS = 120


class WorkerSessionValidationError(SessionValidationError):
    """Raised when worker credential/channel configuration is malformed."""


class WorkerSessionAuthenticationError(SessionAuthenticationError):
    """Raised when a worker credential cannot prove a live restricted identity."""


@dataclass(frozen=True)
class WorkerChannelEvidence:
    """Secret-free observation of the secure channel used by one worker request."""

    channel_kind: str
    peer_authenticated: bool
    confidential: bool
    observed_at: int

    def __post_init__(self) -> None:
        if self.channel_kind not in WORKER_SECURE_CHANNELS:
            raise WorkerSessionValidationError("unsupported worker channel kind")
        if not isinstance(self.peer_authenticated, bool):
            raise WorkerSessionValidationError("peer_authenticated must be boolean")
        if not isinstance(self.confidential, bool):
            raise WorkerSessionValidationError("confidential must be boolean")
        _worker_epoch(self.observed_at, "observed_at")


@dataclass(frozen=True)
class WorkerIssuedCredential:
    """One-time restricted credential returned only to the provisioning boundary."""

    session_id: str
    worker_id: str
    principal_id: str
    token: str
    issued_at: int
    expires_at: int


@dataclass(frozen=True)
class WorkerSessionMetadata:
    """Restricted worker session state; raw credential material is absent."""

    session_id: str
    token_hash: str
    worker_id: str
    principal_id: str
    allowed_channels: tuple[str, ...]
    issued_at: int
    expires_at: int
    revoked_at: int | None = None


class InMemoryWorkerSessionStore:
    """Synthetic restricted worker authentication boundary.

    The store binds one opaque credential to exactly one worker/principal pair.
    It stores only SHA-256 token verifiers, accepts only explicit secure channel
    classes, requires fresh authenticated+confidential channel evidence, and emits
    the existing secret-free WorkerRegistryIdentityEvidence on success.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], int] | None = None,
        token_factory: Callable[[], str] | None = None,
        session_id_factory: Callable[[], str] | None = None,
        max_channel_age_seconds: int = _DEFAULT_WORKER_CHANNEL_MAX_AGE_SECONDS,
    ) -> None:
        if (
            not isinstance(max_channel_age_seconds, int)
            or isinstance(max_channel_age_seconds, bool)
            or max_channel_age_seconds < 1
        ):
            raise WorkerSessionValidationError(
                "max_channel_age_seconds must be a positive integer"
            )
        self._clock = clock or (lambda: int(time.time()))
        self._token_factory = token_factory or (lambda: secrets.token_urlsafe(32))
        self._session_id_factory = session_id_factory or (lambda: str(uuid4()))
        self._max_channel_age_seconds = max_channel_age_seconds
        self._sessions: dict[str, WorkerSessionMetadata] = {}
        self._token_index: dict[str, str] = {}

    def provision(
        self,
        *,
        worker_id: str,
        principal_id: str,
        allowed_channels: Iterable[str],
        ttl_seconds: int = 3600,
    ) -> WorkerIssuedCredential:
        worker = _worker_id(worker_id, "worker_id")
        principal = _worker_id(principal_id, "principal_id")
        channels = _worker_channels(allowed_channels)
        if (
            not isinstance(ttl_seconds, int)
            or isinstance(ttl_seconds, bool)
            or not 1 <= ttl_seconds <= _MAX_SESSION_TTL_SECONDS
        ):
            raise WorkerSessionValidationError(
                f"ttl_seconds must be from 1 through {_MAX_SESSION_TTL_SECONDS}"
            )
        now = _worker_clock_value(self._clock)
        session_id = _worker_id(self._session_id_factory(), "session_id")
        if session_id in self._sessions:
            raise WorkerSessionValidationError("worker session_id collision")
        token = self._token_factory()
        if not isinstance(token, str) or len(token) < 32 or token != token.strip():
            raise WorkerSessionValidationError(
                "token factory must return a trimmed high-entropy string of at least 32 characters"
            )
        token_hash = _hash_token(token)
        if token_hash in self._token_index:
            raise WorkerSessionValidationError("worker credential collision")
        metadata = WorkerSessionMetadata(
            session_id=session_id,
            token_hash=token_hash,
            worker_id=worker,
            principal_id=principal,
            allowed_channels=channels,
            issued_at=now,
            expires_at=now + ttl_seconds,
        )
        self._sessions[session_id] = metadata
        self._token_index[token_hash] = session_id
        return WorkerIssuedCredential(
            session_id=session_id,
            worker_id=worker,
            principal_id=principal,
            token=token,
            issued_at=metadata.issued_at,
            expires_at=metadata.expires_at,
        )

    def authenticate(
        self,
        *,
        worker_id: str,
        token: str,
        channel: WorkerChannelEvidence,
    ):
        """Return secret-free verified identity evidence for the exact bound worker."""

        from .service_state import WorkerRegistryIdentityEvidence

        worker = _worker_id(worker_id, "worker_id")
        if not isinstance(token, str) or not token or token != token.strip():
            raise WorkerSessionAuthenticationError("invalid worker credential")
        if not isinstance(channel, WorkerChannelEvidence):
            raise WorkerSessionAuthenticationError("invalid worker channel evidence")
        token_hash = _hash_token(token)
        session_id = self._token_index.get(token_hash)
        metadata = self._sessions.get(session_id) if session_id is not None else None
        if metadata is None or not hmac.compare_digest(metadata.token_hash, token_hash):
            raise WorkerSessionAuthenticationError("unknown worker credential")
        if metadata.worker_id != worker:
            raise WorkerSessionAuthenticationError("worker credential binding mismatch")
        if metadata.revoked_at is not None:
            raise WorkerSessionAuthenticationError("worker session is revoked")
        now = _worker_clock_value(self._clock)
        if now >= metadata.expires_at:
            raise WorkerSessionAuthenticationError("worker session is expired")
        if channel.channel_kind not in metadata.allowed_channels:
            raise WorkerSessionAuthenticationError("worker channel is not allowed")
        if not channel.peer_authenticated or not channel.confidential:
            raise WorkerSessionAuthenticationError(
                "worker channel must be authenticated and confidential"
            )
        observed = _worker_epoch(channel.observed_at, "observed_at")
        if observed > now:
            raise WorkerSessionAuthenticationError(
                "worker channel evidence cannot be from the future"
            )
        if now - observed > self._max_channel_age_seconds:
            raise WorkerSessionAuthenticationError("worker channel evidence is stale")
        return WorkerRegistryIdentityEvidence(
            principal_id=metadata.principal_id,
            state="verified",
            verified_at=_worker_utc_text(now),
        )

    def revoke(self, session_id: str) -> WorkerSessionMetadata:
        session = _worker_id(session_id, "session_id")
        metadata = self._sessions.get(session)
        if metadata is None:
            raise WorkerSessionValidationError(f"unknown worker session_id: {session}")
        if metadata.revoked_at is None:
            metadata = replace(
                metadata,
                revoked_at=_worker_clock_value(self._clock),
            )
            self._sessions[session] = metadata
        return metadata

    def metadata(self, session_id: str) -> WorkerSessionMetadata:
        session = _worker_id(session_id, "session_id")
        metadata = self._sessions.get(session)
        if metadata is None:
            raise WorkerSessionValidationError(f"unknown worker session_id: {session}")
        return replace(metadata, allowed_channels=tuple(metadata.allowed_channels))


def _worker_id(value: object, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise WorkerSessionValidationError(f"{field} must match {_ID_RE.pattern}")
    return value


def _worker_channels(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise WorkerSessionValidationError("allowed_channels must be a collection")
    try:
        channels = tuple(sorted(set(values)))
    except TypeError as exc:
        raise WorkerSessionValidationError("allowed_channels must be iterable") from exc
    if not channels:
        raise WorkerSessionValidationError("allowed_channels must not be empty")
    if any(
        not isinstance(value, str) or value not in WORKER_SECURE_CHANNELS
        for value in channels
    ):
        raise WorkerSessionValidationError("allowed_channels contains unsupported channel")
    return channels


def _worker_epoch(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise WorkerSessionValidationError(
            f"{field} must be a non-negative integer epoch second"
        )
    return value


def _worker_clock_value(clock: Callable[[], int]) -> int:
    try:
        value = clock()
    except Exception as exc:
        raise WorkerSessionValidationError("worker clock failed") from exc
    return _worker_epoch(value, "clock")


def _worker_utc_text(epoch_second: int) -> str:
    epoch = _worker_epoch(epoch_second, "epoch_second")
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))
