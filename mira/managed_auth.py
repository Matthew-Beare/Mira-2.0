"""Restart-stable bearer authentication for managed MIRA deployments."""

from __future__ import annotations

import hashlib
import hmac
import re

from .api_core import AuthenticatedPrincipal, Grant
from .http_transport import SessionAuthenticationError, SessionValidationError


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_MIN_BEARER_LENGTH = 32
_MAX_BEARER_LENGTH = 4096


class StaticSecretAuthenticator:
    """Authenticate one injected bearer secret without retaining its raw value."""

    def __init__(self, token: str, principal: AuthenticatedPrincipal) -> None:
        normalized = _validate_bearer(token, field="token")
        self._token_hash = hashlib.sha256(normalized.encode("utf-8")).digest()
        self._principal = _copy_principal(principal)

    def authenticate(self, token: str) -> AuthenticatedPrincipal:
        normalized = _validate_bearer(token, field="bearer credential")
        candidate = hashlib.sha256(normalized.encode("utf-8")).digest()
        if not hmac.compare_digest(candidate, self._token_hash):
            raise SessionAuthenticationError("unknown bearer credential")
        return _copy_principal(self._principal)


def _validate_bearer(value: object, *, field: str) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not _MIN_BEARER_LENGTH <= len(value) <= _MAX_BEARER_LENGTH
    ):
        if field == "bearer credential":
            raise SessionAuthenticationError("invalid bearer credential")
        raise SessionValidationError(
            f"{field} must be a trimmed string from "
            f"{_MIN_BEARER_LENGTH} through {_MAX_BEARER_LENGTH} characters"
        )
    return value


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
                data_class=_validate_id(grant.data_class, "grant.data_class"),
                action=_validate_id(grant.action, "grant.action"),
                resource_id=_validate_id(grant.resource_id, "grant.resource_id", wildcard=True),
            )
        )
    if not grants:
        raise SessionValidationError("principal must contain at least one grant")
    return AuthenticatedPrincipal(
        actor_id=actor_id,
        client_id=client_id,
        grants=tuple(grants),
    )


def _validate_id(value: object, field: str, *, wildcard: bool = False) -> str:
    if wildcard and value == "*":
        return "*"
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise SessionValidationError(f"{field} must match {_ID_RE.pattern}")
    return value
