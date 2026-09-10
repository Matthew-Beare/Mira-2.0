"""Provider-neutral publication/import transport for sanitized MIRA feature shares.

The transport deliberately owns only package movement and exact remote readback.
It does not own package construction, feature approval, installation, source
mutation, or activation.  Provider implementations are injected behind the
``FeatureShareStore`` protocol and receive symbolic namespaces rather than
credentials or provider endpoints through this public contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Protocol, runtime_checkable

from .feature_share import (
    FeatureShareError,
    ImportInspection,
    inspect_feature_share_import,
    package_from_mapping,
)


class FeatureShareTransportError(ValueError):
    """Raised for invalid authorization, provider material, or transport state."""


_NAMESPACE = re.compile(r"^[a-z0-9][a-z0-9._-]*(?:/[a-z0-9][a-z0-9._-]*){0,7}$")
_AUTH_ID = re.compile(r"^[A-Z][A-Z0-9-]{1,79}$")
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_NAMESPACE_MARKERS = (
    "http:",
    "https:",
    "@",
    "\\",
    "..",
    "token",
    "secret",
    "credential",
)


@dataclass(frozen=True)
class SharePublicationAuthorization:
    """Explicit runtime authorization bound to one package and destination."""

    authorization_id: str
    package_id: str
    destination: str
    actor_fingerprint: str
    authorized: bool


@dataclass(frozen=True)
class ShareWriteResult:
    """Provider-neutral result from one attempted remote write."""

    outcome: str  # performed | unknown
    remote_revision: str | None = None


@dataclass(frozen=True)
class SharePublicationReceipt:
    package_id: str
    destination: str
    authorization_id: str
    actor_fingerprint: str
    write_state: str  # not_attempted | performed | unknown
    remote_revision: str | None
    replay: bool
    verified: bool
    recovery_required: bool
    activation_authorized: bool = False
    source_mutation_authorized: bool = False
    install_authorized: bool = False


@dataclass(frozen=True)
class ImportedFeatureShare:
    destination: str
    package_id: str
    inspection: ImportInspection
    canonical_bytes: bytes
    activation_authorized: bool = False
    source_mutation_authorized: bool = False
    install_authorized: bool = False


@runtime_checkable
class FeatureShareStore(Protocol):
    """Injected provider adapter for an optional share namespace."""

    def read_package(self, *, destination: str, package_id: str) -> bytes | None:
        """Return exact stored package bytes, or ``None`` when absent."""

    def write_package(
        self, *, destination: str, package_id: str, payload: bytes
    ) -> ShareWriteResult:
        """Attempt one package write without granting any install/activation authority."""


def authorize_feature_share_publication(
    *,
    private_actor_id: str,
    authorization_id: str,
    package_id: str,
    destination: str,
) -> SharePublicationAuthorization:
    """Create explicit package/destination-bound authorization.

    The private actor identity is reduced to a domain-separated fingerprint so
    downstream receipts can reconcile authorization without exporting the raw
    private identity.
    """

    actor = _require_private_actor(private_actor_id)
    auth_id = _require_authorization_id(authorization_id)
    package = _require_package_id(package_id)
    namespace = _require_namespace(destination)
    actor_fingerprint = hashlib.sha256(
        b"mira-feature-share-publisher-v1\0" + actor.encode("utf-8")
    ).hexdigest()
    return SharePublicationAuthorization(
        authorization_id=auth_id,
        package_id=package,
        destination=namespace,
        actor_fingerprint=actor_fingerprint,
        authorized=True,
    )


def publish_feature_share(
    material: Mapping[str, Any],
    *,
    authorization: SharePublicationAuthorization,
    store: FeatureShareStore,
) -> SharePublicationReceipt:
    """Publish one validated package and require exact remote readback.

    Existing byte-identical material is a zero-write replay.  Any write whose
    outcome or readback cannot be proven exact returns a recovery-required
    receipt instead of fabricated success.
    """

    package = _validated_package(material)
    _validate_authorization(authorization, package.package_id)
    destination = authorization.destination
    expected = package.canonical_bytes()

    try:
        before = store.read_package(destination=destination, package_id=package.package_id)
    except Exception as exc:  # provider outcome is unavailable, not clean absence
        raise FeatureShareTransportError("preflight remote read failed") from exc

    if before is not None:
        if before == expected:
            return _publication_receipt(
                authorization=authorization,
                write_state="not_attempted",
                remote_revision=None,
                replay=True,
                verified=True,
                recovery_required=False,
            )
        raise FeatureShareTransportError(
            "destination already contains different bytes for this package_id"
        )

    try:
        write_result = store.write_package(
            destination=destination,
            package_id=package.package_id,
            payload=expected,
        )
    except Exception:
        return _publication_receipt(
            authorization=authorization,
            write_state="unknown",
            remote_revision=None,
            replay=False,
            verified=False,
            recovery_required=True,
        )

    _validate_write_result(write_result)
    if write_result.outcome == "unknown":
        return _publication_receipt(
            authorization=authorization,
            write_state="unknown",
            remote_revision=write_result.remote_revision,
            replay=False,
            verified=False,
            recovery_required=True,
        )

    try:
        after = store.read_package(destination=destination, package_id=package.package_id)
    except Exception:
        return _publication_receipt(
            authorization=authorization,
            write_state="performed",
            remote_revision=write_result.remote_revision,
            replay=False,
            verified=False,
            recovery_required=True,
        )

    if after != expected:
        return _publication_receipt(
            authorization=authorization,
            write_state="performed",
            remote_revision=write_result.remote_revision,
            replay=False,
            verified=False,
            recovery_required=True,
        )

    # Re-parse the remote bytes rather than trusting byte equality alone to keep
    # the transport boundary independently fail-closed against malformed stores.
    remote_package = _package_from_bytes(after)
    if remote_package.package_id != package.package_id:
        return _publication_receipt(
            authorization=authorization,
            write_state="performed",
            remote_revision=write_result.remote_revision,
            replay=False,
            verified=False,
            recovery_required=True,
        )

    return _publication_receipt(
        authorization=authorization,
        write_state="performed",
        remote_revision=write_result.remote_revision,
        replay=False,
        verified=True,
        recovery_required=False,
    )


def import_feature_share(
    *,
    destination: str,
    package_id: str,
    store: FeatureShareStore,
    runtime_schema: int,
    available_feature_ids: Iterable[str],
) -> ImportedFeatureShare:
    """Retrieve untrusted remote package bytes and return inert review material."""

    namespace = _require_namespace(destination)
    package = _require_package_id(package_id)
    try:
        payload = store.read_package(destination=namespace, package_id=package)
    except Exception as exc:
        raise FeatureShareTransportError("remote import read failed") from exc
    if payload is None:
        raise FeatureShareTransportError("requested feature-share package was not found")

    parsed = _package_from_bytes(payload)
    if parsed.package_id != package:
        raise FeatureShareTransportError("remote package identity does not match request")

    try:
        material = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FeatureShareTransportError("remote package is not canonical UTF-8 JSON") from exc
    try:
        inspection = inspect_feature_share_import(
            material,
            runtime_schema=runtime_schema,
            available_feature_ids=available_feature_ids,
        )
    except FeatureShareError as exc:
        raise FeatureShareTransportError(str(exc)) from exc

    canonical = parsed.canonical_bytes()
    if payload != canonical:
        raise FeatureShareTransportError("remote package bytes are not canonical")

    return ImportedFeatureShare(
        destination=namespace,
        package_id=package,
        inspection=inspection,
        canonical_bytes=canonical,
    )


def _validated_package(material: Mapping[str, Any]):
    try:
        return package_from_mapping(material)
    except FeatureShareError as exc:
        raise FeatureShareTransportError(str(exc)) from exc


def _package_from_bytes(payload: bytes):
    if not isinstance(payload, bytes) or not payload:
        raise FeatureShareTransportError("remote package payload must be non-empty bytes")
    try:
        decoded = payload.decode("utf-8")
        material = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FeatureShareTransportError("remote package is not canonical UTF-8 JSON") from exc
    if not isinstance(material, Mapping):
        raise FeatureShareTransportError("remote feature-share package must be an object")
    return _validated_package(material)


def _validate_authorization(
    authorization: SharePublicationAuthorization, package_id: str
) -> None:
    if not isinstance(authorization, SharePublicationAuthorization):
        raise FeatureShareTransportError("explicit SharePublicationAuthorization is required")
    _require_authorization_id(authorization.authorization_id)
    _require_package_id(authorization.package_id)
    _require_namespace(authorization.destination)
    _require_fingerprint(authorization.actor_fingerprint)
    if authorization.authorized is not True:
        raise FeatureShareTransportError("publication authorization is denied")
    if authorization.package_id != package_id:
        raise FeatureShareTransportError("publication authorization is for another package")


def _validate_write_result(result: ShareWriteResult) -> None:
    if not isinstance(result, ShareWriteResult):
        raise FeatureShareTransportError("share store returned malformed write result")
    if result.outcome not in {"performed", "unknown"}:
        raise FeatureShareTransportError("share store returned invalid write outcome")
    if result.remote_revision is not None:
        if not isinstance(result.remote_revision, str) or not result.remote_revision.strip():
            raise FeatureShareTransportError("remote_revision must be non-empty text when set")
        lowered = result.remote_revision.lower()
        if any(marker in lowered for marker in ("http://", "https://", "@", "token", "secret")):
            raise FeatureShareTransportError("remote_revision contains private/provider material")


def _publication_receipt(
    *,
    authorization: SharePublicationAuthorization,
    write_state: str,
    remote_revision: str | None,
    replay: bool,
    verified: bool,
    recovery_required: bool,
) -> SharePublicationReceipt:
    return SharePublicationReceipt(
        package_id=authorization.package_id,
        destination=authorization.destination,
        authorization_id=authorization.authorization_id,
        actor_fingerprint=authorization.actor_fingerprint,
        write_state=write_state,
        remote_revision=remote_revision,
        replay=replay,
        verified=verified,
        recovery_required=recovery_required,
    )


def _require_private_actor(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FeatureShareTransportError("private_actor_id must be non-empty text")
    return value.strip()


def _require_authorization_id(value: Any) -> str:
    if not isinstance(value, str) or not _AUTH_ID.fullmatch(value):
        raise FeatureShareTransportError("authorization_id must be a canonical uppercase ID")
    return value


def _require_package_id(value: Any) -> str:
    if not isinstance(value, str) or not _HEX_64.fullmatch(value):
        raise FeatureShareTransportError("package_id must be a lowercase SHA-256 digest")
    return value


def _require_fingerprint(value: Any) -> str:
    if not isinstance(value, str) or not _HEX_64.fullmatch(value):
        raise FeatureShareTransportError("actor_fingerprint must be a lowercase SHA-256 digest")
    return value


def _require_namespace(value: Any) -> str:
    if not isinstance(value, str) or not _NAMESPACE.fullmatch(value):
        raise FeatureShareTransportError("destination must be a symbolic share namespace")
    lowered = value.lower()
    if any(marker in lowered for marker in _FORBIDDEN_NAMESPACE_MARKERS):
        raise FeatureShareTransportError("destination contains provider/private material")
    return value
