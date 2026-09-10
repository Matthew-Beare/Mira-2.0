"""Deterministic, privacy-failing feature-share package boundary for MIRA Studio.

This module is provider-neutral and side-effect free.  It can construct and
validate sanitized feature packages and inspect imported packages as inert
candidate material.  It cannot publish, install, mutate source, approve, or
activate a feature.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence


class FeatureShareError(ValueError):
    """Raised when share-package material is malformed, unsafe, or inconsistent."""


_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_REVISION = re.compile(r"^[A-Za-z0-9._:/@+-]{1,160}$")
_ID = re.compile(r"^[A-Z][A-Z0-9-]{1,79}$")
_PATH = re.compile(r"^[A-Za-z0-9._/-]{1,240}$")
_SCHEMA_VERSION = 1
_PACKAGE_KIND = "mira-feature-share-v1"

_SECRET_MARKERS = (
    "BEGIN PRIVATE KEY",
    "client_secret",
    "access_token",
    "refresh_token",
    "authorization: bearer",
    "mira_bearer_token",
    "password=",
    "passwd=",
)
_PRIVATE_PATTERNS = (
    re.compile(r"https://docs\.google\.com/(?:spreadsheets|document|presentation)/d/[A-Za-z0-9_-]+", re.I),
    re.compile(r"\b\d{10,}-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com\b", re.I),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.(?:\d{1,3}\.){2}\d{1,3}\b"),
    re.compile(r"\b(?:sk|ghp|github_pat)_[A-Za-z0-9_-]{12,}\b", re.I),
)
_FORBIDDEN_PATH_PARTS = {
    ".env",
    "credentials",
    "credential",
    "secrets",
    "secret",
    "private_key",
    "id_rsa",
}
_FORBIDDEN_IMPORT_AUTHORITY_KEYS = {
    "approved",
    "approval",
    "approver",
    "activation",
    "activate",
    "activation_authorized",
    "capability",
    "capabilities",
    "provider_capability",
    "remote_readback",
    "write_authority",
    "install",
    "installed",
}


@dataclass(frozen=True)
class ShareArtifact:
    path: str
    sha256: str
    content_b64: str

    def projection(self) -> dict[str, str]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "content_b64": self.content_b64,
        }


@dataclass(frozen=True)
class FeatureSharePackage:
    package_id: str
    ownership_fingerprint: str
    change_id: str
    source_revision: str
    reviewed_source_sha256: str
    feature_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...]
    min_runtime_schema: int
    max_runtime_schema: int
    artifacts: tuple[ShareArtifact, ...]

    def unsigned_projection(self) -> dict[str, object]:
        return {
            "schema_version": _SCHEMA_VERSION,
            "package_kind": _PACKAGE_KIND,
            "ownership_fingerprint": self.ownership_fingerprint,
            "change_id": self.change_id,
            "source_revision": self.source_revision,
            "reviewed_source_sha256": self.reviewed_source_sha256,
            "feature_ids": list(self.feature_ids),
            "dependency_ids": list(self.dependency_ids),
            "compatibility": {
                "min_runtime_schema": self.min_runtime_schema,
                "max_runtime_schema": self.max_runtime_schema,
            },
            "artifacts": [artifact.projection() for artifact in self.artifacts],
        }

    def projection(self) -> dict[str, object]:
        material = self.unsigned_projection()
        return {"package_id": self.package_id, **material}

    def canonical_bytes(self) -> bytes:
        return _canonical_json(self.projection()) + b"\n"


@dataclass(frozen=True)
class ImportInspection:
    package_id: str
    compatible: bool
    missing_dependencies: tuple[str, ...]
    already_present_features: tuple[str, ...]
    ready_for_review: bool
    activation_authorized: bool = False
    source_mutation_authorized: bool = False
    install_authorized: bool = False


def build_feature_share_package(
    *,
    private_owner_id: str,
    change_id: str,
    source_revision: str,
    reviewed_source_sha256: str,
    feature_ids: Sequence[str],
    dependency_ids: Sequence[str],
    min_runtime_schema: int,
    max_runtime_schema: int,
    artifacts: Mapping[str, str | bytes],
) -> FeatureSharePackage:
    """Build a deterministic sanitized package without exposing private_owner_id."""

    owner = _require_text(private_owner_id, "private_owner_id")
    _reject_private_text(owner, "private_owner_id", allow_email=False)
    change = _require_id(change_id, "change_id")
    revision = _require_revision(source_revision)
    reviewed_digest = _require_sha256(reviewed_source_sha256, "reviewed_source_sha256")
    features = _normalized_ids(feature_ids, "feature_ids", required=True)
    dependencies = _normalized_ids(dependency_ids, "dependency_ids", required=False)
    if set(features) & set(dependencies):
        raise FeatureShareError("feature_ids and dependency_ids must be disjoint")
    _validate_compatibility(min_runtime_schema, max_runtime_schema)
    artifact_rows = _build_artifacts(artifacts)

    ownership_fingerprint = hashlib.sha256(
        b"mira-feature-owner-v1\0" + owner.encode("utf-8")
    ).hexdigest()

    shell = FeatureSharePackage(
        package_id="0" * 64,
        ownership_fingerprint=ownership_fingerprint,
        change_id=change,
        source_revision=revision,
        reviewed_source_sha256=reviewed_digest,
        feature_ids=features,
        dependency_ids=dependencies,
        min_runtime_schema=min_runtime_schema,
        max_runtime_schema=max_runtime_schema,
        artifacts=artifact_rows,
    )
    package_id = hashlib.sha256(_canonical_json(shell.unsigned_projection())).hexdigest()
    return FeatureSharePackage(
        package_id=package_id,
        ownership_fingerprint=shell.ownership_fingerprint,
        change_id=shell.change_id,
        source_revision=shell.source_revision,
        reviewed_source_sha256=shell.reviewed_source_sha256,
        feature_ids=shell.feature_ids,
        dependency_ids=shell.dependency_ids,
        min_runtime_schema=shell.min_runtime_schema,
        max_runtime_schema=shell.max_runtime_schema,
        artifacts=shell.artifacts,
    )


def package_from_mapping(material: Mapping[str, Any]) -> FeatureSharePackage:
    """Parse and independently validate an untrusted imported package mapping."""

    if not isinstance(material, Mapping):
        raise FeatureShareError("feature-share package must be an object")
    _reject_authority_escalation(material)
    expected_keys = {
        "package_id",
        "schema_version",
        "package_kind",
        "ownership_fingerprint",
        "change_id",
        "source_revision",
        "reviewed_source_sha256",
        "feature_ids",
        "dependency_ids",
        "compatibility",
        "artifacts",
    }
    if set(material) != expected_keys:
        raise FeatureShareError("feature-share package fields do not match schema")
    if material["schema_version"] != _SCHEMA_VERSION:
        raise FeatureShareError("unsupported feature-share schema_version")
    if material["package_kind"] != _PACKAGE_KIND:
        raise FeatureShareError("unexpected feature-share package_kind")

    package_id = _require_sha256(material["package_id"], "package_id")
    owner_fp = _require_sha256(material["ownership_fingerprint"], "ownership_fingerprint")
    change_id = _require_id(material["change_id"], "change_id")
    source_revision = _require_revision(material["source_revision"])
    reviewed_digest = _require_sha256(
        material["reviewed_source_sha256"], "reviewed_source_sha256"
    )
    feature_ids = _normalized_ids(material["feature_ids"], "feature_ids", required=True)
    dependency_ids = _normalized_ids(
        material["dependency_ids"], "dependency_ids", required=False
    )
    if set(feature_ids) & set(dependency_ids):
        raise FeatureShareError("feature_ids and dependency_ids must be disjoint")

    compatibility = material["compatibility"]
    if not isinstance(compatibility, Mapping) or set(compatibility) != {
        "min_runtime_schema",
        "max_runtime_schema",
    }:
        raise FeatureShareError("compatibility fields do not match schema")
    min_schema = compatibility["min_runtime_schema"]
    max_schema = compatibility["max_runtime_schema"]
    _validate_compatibility(min_schema, max_schema)

    raw_artifacts = material["artifacts"]
    if not isinstance(raw_artifacts, list) or not raw_artifacts:
        raise FeatureShareError("artifacts must be a non-empty list")
    artifacts: list[ShareArtifact] = []
    seen_paths: set[str] = set()
    for row in raw_artifacts:
        if not isinstance(row, Mapping) or set(row) != {"path", "sha256", "content_b64"}:
            raise FeatureShareError("artifact fields do not match schema")
        artifact = _parse_artifact(row)
        if artifact.path in seen_paths:
            raise FeatureShareError("duplicate artifact path")
        seen_paths.add(artifact.path)
        artifacts.append(artifact)
    if tuple(a.path for a in artifacts) != tuple(sorted(a.path for a in artifacts)):
        raise FeatureShareError("artifacts must be sorted by path")

    package = FeatureSharePackage(
        package_id=package_id,
        ownership_fingerprint=owner_fp,
        change_id=change_id,
        source_revision=source_revision,
        reviewed_source_sha256=reviewed_digest,
        feature_ids=feature_ids,
        dependency_ids=dependency_ids,
        min_runtime_schema=min_schema,
        max_runtime_schema=max_schema,
        artifacts=tuple(artifacts),
    )
    expected_id = hashlib.sha256(_canonical_json(package.unsigned_projection())).hexdigest()
    if package.package_id != expected_id:
        raise FeatureShareError("package_id does not match canonical package material")
    return package


def inspect_feature_share_import(
    material: Mapping[str, Any],
    *,
    runtime_schema: int,
    available_feature_ids: Iterable[str],
) -> ImportInspection:
    """Inspect an imported package as inert candidate material only."""

    package = package_from_mapping(material)
    if not isinstance(runtime_schema, int) or isinstance(runtime_schema, bool) or runtime_schema < 1:
        raise FeatureShareError("runtime_schema must be a positive integer")
    available = set(_normalized_ids(tuple(available_feature_ids), "available_feature_ids", required=False))
    compatible = package.min_runtime_schema <= runtime_schema <= package.max_runtime_schema
    missing = tuple(dep for dep in package.dependency_ids if dep not in available)
    present = tuple(fid for fid in package.feature_ids if fid in available)
    return ImportInspection(
        package_id=package.package_id,
        compatible=compatible,
        missing_dependencies=missing,
        already_present_features=present,
        ready_for_review=compatible and not missing,
    )


def verify_feature_share_package(material: Mapping[str, Any]) -> None:
    package_from_mapping(material)


def _build_artifacts(artifacts: Mapping[str, str | bytes]) -> tuple[ShareArtifact, ...]:
    if not isinstance(artifacts, Mapping) or not artifacts:
        raise FeatureShareError("artifacts must be a non-empty mapping")
    rows: list[ShareArtifact] = []
    for path in sorted(artifacts):
        if not isinstance(path, str):
            raise FeatureShareError("artifact path must be text")
        _validate_path(path)
        payload = artifacts[path]
        if isinstance(payload, str):
            raw = payload.encode("utf-8")
            text = payload
        elif isinstance(payload, bytes):
            raw = payload
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise FeatureShareError("share artifacts must be UTF-8 text") from exc
        else:
            raise FeatureShareError("artifact content must be text or bytes")
        if b"\x00" in raw:
            raise FeatureShareError("share artifacts may not contain NUL bytes")
        _reject_private_text(text, path)
        rows.append(
            ShareArtifact(
                path=path,
                sha256=hashlib.sha256(raw).hexdigest(),
                content_b64=base64.b64encode(raw).decode("ascii"),
            )
        )
    return tuple(rows)


def _parse_artifact(row: Mapping[str, Any]) -> ShareArtifact:
    path = row["path"]
    if not isinstance(path, str):
        raise FeatureShareError("artifact path must be text")
    _validate_path(path)
    digest = _require_sha256(row["sha256"], "artifact sha256")
    content_b64 = row["content_b64"]
    if not isinstance(content_b64, str) or not content_b64:
        raise FeatureShareError("artifact content_b64 must be non-empty text")
    try:
        raw = base64.b64decode(content_b64.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError) as exc:
        raise FeatureShareError("artifact content_b64 is invalid") from exc
    if hashlib.sha256(raw).hexdigest() != digest:
        raise FeatureShareError("artifact digest mismatch")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FeatureShareError("share artifacts must be UTF-8 text") from exc
    if "\x00" in text:
        raise FeatureShareError("share artifacts may not contain NUL bytes")
    _reject_private_text(text, path)
    return ShareArtifact(path=path, sha256=digest, content_b64=content_b64)


def _validate_path(path: str) -> None:
    if not _PATH.fullmatch(path) or path.startswith(("/", "./")) or ".." in path.split("/"):
        raise FeatureShareError("artifact path is invalid or unsafe")
    lowered_parts = {part.lower() for part in path.split("/")}
    if lowered_parts & _FORBIDDEN_PATH_PARTS:
        raise FeatureShareError("artifact path names private/credential material")


def _normalized_ids(values: Sequence[str] | Iterable[str], field: str, *, required: bool) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Iterable):
        raise FeatureShareError(f"{field} must be an iterable of IDs")
    normalized = tuple(values)
    if required and not normalized:
        raise FeatureShareError(f"{field} must not be empty")
    for value in normalized:
        _require_id(value, field)
    if len(set(normalized)) != len(normalized):
        raise FeatureShareError(f"{field} contains duplicates")
    if normalized != tuple(sorted(normalized)):
        raise FeatureShareError(f"{field} must be sorted")
    return normalized


def _require_id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise FeatureShareError(f"{field} must be a canonical uppercase MIRA ID")
    return value


def _require_revision(value: Any) -> str:
    if not isinstance(value, str) or not _REVISION.fullmatch(value):
        raise FeatureShareError("source_revision is invalid")
    _reject_private_text(value, "source_revision")
    return value


def _require_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _HEX_64.fullmatch(value):
        raise FeatureShareError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FeatureShareError(f"{field} must be non-empty text")
    return value.strip()


def _validate_compatibility(min_schema: Any, max_schema: Any) -> None:
    for value, field in ((min_schema, "min_runtime_schema"), (max_schema, "max_runtime_schema")):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise FeatureShareError(f"{field} must be a positive integer")
    if min_schema > max_schema:
        raise FeatureShareError("min_runtime_schema may not exceed max_runtime_schema")


def _reject_private_text(text: str, context: str, *, allow_email: bool = False) -> None:
    lowered = text.lower()
    for marker in _SECRET_MARKERS:
        if marker.lower() in lowered:
            raise FeatureShareError(f"{context} contains secret/private material")
    for pattern in _PRIVATE_PATTERNS:
        if allow_email and pattern.pattern.startswith(r"\b[A-Za-z0-9._%+-]+@"):
            continue
        if pattern.search(text):
            raise FeatureShareError(f"{context} contains private/provider-specific material")


def _reject_authority_escalation(material: Any) -> None:
    if isinstance(material, Mapping):
        for key, value in material.items():
            key_text = str(key).lower()
            if key_text in _FORBIDDEN_IMPORT_AUTHORITY_KEYS:
                raise FeatureShareError("import package attempts to smuggle execution authority")
            _reject_authority_escalation(value)
    elif isinstance(material, list):
        for value in material:
            _reject_authority_escalation(value)


def _canonical_json(material: Mapping[str, Any] | dict[str, object]) -> bytes:
    return json.dumps(
        material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
