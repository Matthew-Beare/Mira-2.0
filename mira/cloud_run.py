"""Cloud Run deployment composition for the bounded M2-M0 Google proof.

All provider identifiers and bearer material arrive through runtime injection.
This module contains only logical synthetic MIRA identifiers and deployment
invariants required by the single-writer Google Sheets authority path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from io import TextIOBase
import json
import os
import sys
from threading import RLock
import time
from typing import Callable, Mapping, MutableMapping, Protocol

from .api_core import AuditEvent, AuthenticatedPrincipal, Grant
from .authority import AuthoritySpec
from .google_runtime_auth import GoogleMetadataAccessTokenProvider
from .google_sheets_store import (
    GoogleSheetsRestGateway,
    GoogleSheetsStructuredStateAdapter,
)
from .managed_auth import StaticSecretAuthenticator
from .runtime import ManagedRuntime, RuntimeConfig, assemble_managed_runtime


_AUTHORITY_ID = "google-sheets-m0"
_ADAPTER_KEY = "google-sheets"
_RESOURCE_REF = "runtime:google-structured-state"
_NAMESPACE = "mira-2-sandbox"
_FAILURE_DOMAIN = "google-sheets-sandbox"
_OWNER_ID = "m0-synthetic-user"
_CLIENT_ID = "stock-chatgpt-proof"
_STATE_SCHEMA_VERSION = "mira-structured-state-v1"
_API_SCHEMA_VERSION = "mira-api-1"
_PROTECTED_PATHS = frozenset({"/v1/query", "/v1/commands"})


class CloudRunConfigurationError(Exception):
    """Raised when deployment-time runtime configuration is invalid."""


class WsgiApp(Protocol):
    def __call__(self, environ: Mapping[str, object], start_response): ...


@dataclass(frozen=True)
class CloudRunDeploymentConfig:
    """Private runtime configuration loaded from environment/secret injection."""

    spreadsheet_id: str
    rate_limit_per_minute: int = 120


@dataclass(frozen=True)
class CloudRunApplication:
    """Assembled Cloud Run WSGI application plus non-secret runtime graph."""

    app: WsgiApp
    runtime: ManagedRuntime
    config: CloudRunDeploymentConfig


class JsonLineAuditSink:
    """Write structured non-secret API audit events to process stdout/stderr."""

    def __init__(self, stream: TextIOBase | None = None) -> None:
        self._stream = stream or sys.stdout
        self._lock = RLock()

    def record(self, event: AuditEvent) -> None:
        if not isinstance(event, AuditEvent):
            raise TypeError("event must be an AuditEvent")
        line = json.dumps(
            {"mira_audit": asdict(event)},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        with self._lock:
            self._stream.write(line + "\n")
            self._stream.flush()


class CloudRunHttpsProxyApp:
    """Translate Cloud Run's trusted external HTTPS signal for the WSGI core.

    This adapter is only valid behind Cloud Run's Google frontend/proxy path.
    If the proxy does not assert HTTPS, the original WSGI scheme is preserved
    and protected routes remain rejected by WsgiApiApp's HTTPS gate.
    """

    def __init__(self, app: WsgiApp) -> None:
        self._app = app

    def __call__(self, environ: Mapping[str, object], start_response):
        forwarded = environ.get("HTTP_X_FORWARDED_PROTO")
        if isinstance(forwarded, str) and forwarded.lower() == "https":
            adapted: MutableMapping[str, object] = dict(environ)
            adapted["wsgi.url_scheme"] = "https"
            return self._app(adapted, start_response)
        return self._app(environ, start_response)


class FixedWindowRateLimitApp:
    """Single-instance request limiter for protected M2-M0 API routes."""

    def __init__(
        self,
        app: WsgiApp,
        *,
        requests_per_minute: int,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if (
            not isinstance(requests_per_minute, int)
            or isinstance(requests_per_minute, bool)
            or not 1 <= requests_per_minute <= 600
        ):
            raise CloudRunConfigurationError(
                "requests_per_minute must be an integer from 1 through 600"
            )
        self._app = app
        self._limit = requests_per_minute
        self._clock = clock or time.time
        self._lock = RLock()
        self._window_start = -1
        self._count = 0

    def __call__(self, environ: Mapping[str, object], start_response):
        path = str(environ.get("PATH_INFO", ""))
        if path in _PROTECTED_PATHS and not self._allow():
            payload = json.dumps(
                {
                    "error": {
                        "code": "rate_limited",
                        "message": "request rate exceeds configured limit",
                    }
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            headers = [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(payload))),
                ("Cache-Control", "no-store"),
                ("Retry-After", "60"),
            ]
            start_response("429 Too Many Requests", headers)
            return [payload]
        return self._app(environ, start_response)

    def _allow(self) -> bool:
        now = self._clock()
        if not isinstance(now, (int, float)) or isinstance(now, bool) or now < 0:
            raise CloudRunConfigurationError("rate-limit clock must be non-negative")
        window_start = int(float(now) // 60) * 60
        with self._lock:
            if window_start != self._window_start:
                self._window_start = window_start
                self._count = 0
            if self._count >= self._limit:
                return False
            self._count += 1
            return True


def build_cloud_run_application(
    environ: Mapping[str, str] | None = None,
    *,
    access_token_provider: Callable[[], str] | None = None,
    audit_sink: object | None = None,
    gateway_factory=GoogleSheetsRestGateway,
    state_factory=GoogleSheetsStructuredStateAdapter,
) -> CloudRunApplication:
    """Construct the live Cloud Run app from injected runtime configuration."""

    source = os.environ if environ is None else environ
    config = _load_config(source)
    raw_bearer = _required_secret(source, "MIRA_BEARER_TOKEN")
    principal = AuthenticatedPrincipal(
        actor_id=_OWNER_ID,
        client_id=_CLIENT_ID,
        grants=(
            Grant("entity", "read", "*"),
            Grant("entity", "query", "*"),
            Grant("entity", "upsert", "*"),
            Grant("entity", "append_event", "*"),
        ),
    )
    authenticator = StaticSecretAuthenticator(raw_bearer, principal)
    del raw_bearer

    token_provider = access_token_provider or GoogleMetadataAccessTokenProvider()
    gateway = gateway_factory(
        spreadsheet_id=config.spreadsheet_id,
        access_token_provider=token_provider,
    )
    state = state_factory(gateway)
    sink = audit_sink or JsonLineAuditSink()

    authority = AuthoritySpec(
        authority_id=_AUTHORITY_ID,
        adapter_key=_ADAPTER_KEY,
        resource_ref=_RESOURCE_REF,
        namespace=_NAMESPACE,
        failure_domain=_FAILURE_DOMAIN,
        owner_id=_OWNER_ID,
        schema_version=_STATE_SCHEMA_VERSION,
        verified=True,
        enabled=True,
    )
    runtime = assemble_managed_runtime(
        RuntimeConfig(
            authority=authority,
            api_major=1,
            api_schema_version=_API_SCHEMA_VERSION,
            data_class="entity",
            require_https=True,
        ),
        structured_state=state,
        authenticator=authenticator,
        audit_sink=sink,
    )
    app: WsgiApp = FixedWindowRateLimitApp(
        runtime.app,
        requests_per_minute=config.rate_limit_per_minute,
    )
    app = CloudRunHttpsProxyApp(app)
    return CloudRunApplication(app=app, runtime=runtime, config=config)


def build_cloud_run_wsgi_app(environ: Mapping[str, str] | None = None) -> WsgiApp:
    """Gunicorn-facing factory result."""

    return build_cloud_run_application(environ).app


def _load_config(environ: Mapping[str, str]) -> CloudRunDeploymentConfig:
    spreadsheet_id = _required_setting(environ, "MIRA_GOOGLE_SPREADSHEET_ID")
    raw_limit = environ.get("MIRA_RATE_LIMIT_PER_MINUTE", "120")
    try:
        rate_limit = int(raw_limit)
    except (TypeError, ValueError) as exc:
        raise CloudRunConfigurationError(
            "MIRA_RATE_LIMIT_PER_MINUTE must be an integer"
        ) from exc
    if not 1 <= rate_limit <= 600:
        raise CloudRunConfigurationError(
            "MIRA_RATE_LIMIT_PER_MINUTE must be from 1 through 600"
        )
    return CloudRunDeploymentConfig(
        spreadsheet_id=spreadsheet_id,
        rate_limit_per_minute=rate_limit,
    )


def _required_setting(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name)
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value
        or len(value) > 256
    ):
        raise CloudRunConfigurationError(f"{name} is missing or invalid")
    return value


def _required_secret(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name)
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not 32 <= len(value) <= 4096
    ):
        raise CloudRunConfigurationError(f"{name} is missing or invalid")
    return value
