"""Provider-neutral managed runtime assembly for the MIRA API boundary.

This module composes already-verified state, authority, API, authentication, and
HTTP components. It intentionally performs no provider credential discovery and
contains no deployment-platform identifiers or secrets.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from .api_core import ApiService, AuditSink
from .authority import AuthorityRegistry, AuthoritySpec
from .http_transport import BearerAuthenticator, WsgiApiApp
from .runtime_bootstrap import RuntimeBootstrapResult, bootstrap_runtime_authority
from .structured_state import StructuredStateAdapter


_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class RuntimeAssemblyError(Exception):
    """Raised when the managed runtime cannot be assembled safely."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Non-secret runtime composition settings for the bounded M2-M0 entity proof."""

    authority: AuthoritySpec
    api_major: int = 1
    api_schema_version: str = "mira-api-1"
    data_class: str = "entity"
    require_https: bool = True
    max_body_bytes: int = 64 * 1024


@dataclass(frozen=True)
class ManagedRuntime:
    """Fully assembled service graph after startup verification succeeds."""

    config: RuntimeConfig
    registry: AuthorityRegistry
    service: ApiService
    app: WsgiApiApp
    bootstrap: RuntimeBootstrapResult


def assemble_managed_runtime(
    config: RuntimeConfig,
    *,
    structured_state: StructuredStateAdapter,
    authenticator: BearerAuthenticator,
    audit_sink: AuditSink,
) -> ManagedRuntime:
    """Build and verify the managed API runtime or fail before serving requests."""

    config = _validate_config(config)
    _validate_dependency(
        structured_state,
        "structured_state",
        ("health", "schema", "get", "query", "upsert"),
    )
    _validate_dependency(authenticator, "authenticator", ("authenticate",))
    _validate_dependency(audit_sink, "audit_sink", ("record",))

    try:
        health = structured_state.health()
        schema = structured_state.schema()
    except Exception as exc:
        raise RuntimeAssemblyError("structured-state startup inspection failed") from exc

    if not health.ok:
        raise RuntimeAssemblyError("structured-state adapter is unhealthy")
    if health.schema_version != schema.schema_version:
        raise RuntimeAssemblyError("structured-state health/schema version mismatch")
    if schema.schema_version != config.authority.schema_version:
        raise RuntimeAssemblyError("structured-state schema does not match Authority metadata")

    required_types = {"authority", "authority_binding", config.data_class}
    missing = required_types.difference(schema.resource_types)
    if missing:
        raise RuntimeAssemblyError(
            "structured-state schema is missing required resource types: "
            + ", ".join(sorted(missing))
        )

    try:
        registry = AuthorityRegistry(structured_state)
        bootstrap = bootstrap_runtime_authority(
            registry,
            spec=config.authority,
            data_class=config.data_class,
            adapter=structured_state,
        )
        # Readiness is based on persisted routing plus the mounted adapter, not
        # merely the success of a bootstrap mutation.
        registry.resolve(config.data_class)
        service = ApiService(
            registry,
            audit_sink,
            api_major=config.api_major,
            schema_version=config.api_schema_version,
        )
        app = WsgiApiApp(
            service,
            authenticator,
            require_https=config.require_https,
            max_body_bytes=config.max_body_bytes,
        )
    except Exception as exc:
        raise RuntimeAssemblyError("managed runtime startup verification failed") from exc

    return ManagedRuntime(
        config=config,
        registry=registry,
        service=service,
        app=app,
        bootstrap=bootstrap,
    )


def _validate_config(config: RuntimeConfig) -> RuntimeConfig:
    if not isinstance(config, RuntimeConfig):
        raise RuntimeAssemblyError("config must be a RuntimeConfig")
    if not isinstance(config.authority, AuthoritySpec):
        raise RuntimeAssemblyError("config.authority must be an AuthoritySpec")
    if (
        not isinstance(config.api_major, int)
        or isinstance(config.api_major, bool)
        or config.api_major < 1
    ):
        raise RuntimeAssemblyError("api_major must be a positive integer")
    _validate_token(config.api_schema_version, "api_schema_version")
    if config.data_class != "entity":
        raise RuntimeAssemblyError(
            "M2-M0 managed runtime currently supports only data_class=entity"
        )
    if not isinstance(config.require_https, bool):
        raise RuntimeAssemblyError("require_https must be boolean")
    if (
        not isinstance(config.max_body_bytes, int)
        or isinstance(config.max_body_bytes, bool)
        or not 1 <= config.max_body_bytes <= 1024 * 1024
    ):
        raise RuntimeAssemblyError("max_body_bytes must be from 1 through 1048576")
    return config


def _validate_token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise RuntimeAssemblyError(f"{field} must match {_TOKEN_RE.pattern}")
    return value


def _validate_dependency(dependency: object, name: str, methods: tuple[str, ...]) -> None:
    if any(not callable(getattr(dependency, method, None)) for method in methods):
        raise RuntimeAssemblyError(
            f"{name} does not implement required runtime methods: {', '.join(methods)}"
        )
