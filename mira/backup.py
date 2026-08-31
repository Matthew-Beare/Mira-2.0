"""Provider-neutral current-resource backup and isolated restore for MIRA.

This first backup slice intentionally covers canonical current Resource state only.
The public StructuredStateAdapter can enumerate Resources by declared type, but it
cannot enumerate every Event stream or persisted idempotency row. The artifact
therefore records those omissions explicitly instead of pretending to be a full
provider/disaster-recovery image.

A backup artifact is nonauthoritative. Restore is allowed only into a caller-proven
fresh compatible authority whose Resource space is empty. Source replay identities,
provider row metadata, Event history, scheduling, encryption, retention and offsite
durability are outside this module.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Sequence

from .structured_state import ResourceRecord, StructuredStateAdapter, StructuredStateError


BACKUP_ARTIFACT_VERSION = 1
RESOURCE_COVERAGE = "complete_current_resources_under_query_bound"
EVENT_COVERAGE = "not_exported_interface_not_enumerable"
IDEMPOTENCY_COVERAGE = "not_exported_interface_not_enumerable"
_QUERY_LIMIT = 1000


class BackupError(Exception):
    """Base class for backup/restore failures."""


class BackupValidationError(BackupError):
    """Raised when an artifact or requested operation is malformed/incompatible."""


class BackupIntegrityError(BackupError):
    """Raised when export or restored readback cannot be proven complete/equal."""


@dataclass(frozen=True)
class BackupResource:
    resource_type: str
    resource_id: str
    revision: int
    payload: dict[str, Any]

    def material(self) -> dict[str, Any]:
        return {
            "payload": deepcopy(self.payload),
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "revision": self.revision,
        }


@dataclass(frozen=True)
class BackupArtifact:
    artifact_version: int
    schema_version: str
    resource_types: tuple[str, ...]
    event_types: tuple[str, ...]
    resource_coverage: str
    event_coverage: str
    idempotency_coverage: str
    resources: tuple[BackupResource, ...]
    material_sha256: str

    @property
    def resource_count(self) -> int:
        return len(self.resources)

    def unsigned_material(self) -> dict[str, Any]:
        return {
            "artifact_version": self.artifact_version,
            "coverage": {
                "events": self.event_coverage,
                "idempotency": self.idempotency_coverage,
                "resources": self.resource_coverage,
            },
            "resources": [row.material() for row in self.resources],
            "schema": {
                "event_types": list(self.event_types),
                "resource_types": list(self.resource_types),
                "schema_version": self.schema_version,
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.unsigned_material(),
            "material_sha256": self.material_sha256,
        }

    def to_json(self) -> str:
        return _canonical_json(self.to_dict())

    @classmethod
    def from_json(cls, encoded: str) -> "BackupArtifact":
        if not isinstance(encoded, str) or not encoded.strip():
            raise BackupValidationError("backup artifact JSON must be non-empty text")
        try:
            value = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise BackupValidationError("backup artifact contains invalid JSON") from exc
        return _artifact_from_mapping(value)


@dataclass(frozen=True)
class RestoreResult:
    restored_resource_count: int
    verified_material_sha256: str


class BackupService:
    """Export current Resource truth and restore it into a fresh compatible authority."""

    def create(self, source: StructuredStateAdapter) -> BackupArtifact:
        schema = _schema(source)
        rows: list[BackupResource] = []
        seen: set[tuple[str, str]] = set()

        for resource_type in schema.resource_types:
            try:
                records = tuple(source.query(resource_type, limit=_QUERY_LIMIT))
            except StructuredStateError as exc:
                raise BackupIntegrityError(str(exc)) from exc
            if len(records) >= _QUERY_LIMIT:
                raise BackupIntegrityError(
                    f"cannot prove complete export for {resource_type!r}: "
                    f"the public query bound is {_QUERY_LIMIT} rows with no pagination"
                )
            for record in records:
                row = _backup_resource(record, expected_type=resource_type)
                identity = (row.resource_type, row.resource_id)
                if identity in seen:
                    raise BackupIntegrityError(
                        f"duplicate Resource identity during backup: {identity!r}"
                    )
                seen.add(identity)
                rows.append(row)

        rows.sort(key=lambda row: (row.resource_type, row.resource_id))
        unsigned = {
            "artifact_version": BACKUP_ARTIFACT_VERSION,
            "coverage": {
                "events": EVENT_COVERAGE,
                "idempotency": IDEMPOTENCY_COVERAGE,
                "resources": RESOURCE_COVERAGE,
            },
            "resources": [row.material() for row in rows],
            "schema": {
                "event_types": list(schema.event_types),
                "resource_types": list(schema.resource_types),
                "schema_version": schema.schema_version,
            },
        }
        digest = _sha256(unsigned)
        return BackupArtifact(
            artifact_version=BACKUP_ARTIFACT_VERSION,
            schema_version=schema.schema_version,
            resource_types=schema.resource_types,
            event_types=schema.event_types,
            resource_coverage=RESOURCE_COVERAGE,
            event_coverage=EVENT_COVERAGE,
            idempotency_coverage=IDEMPOTENCY_COVERAGE,
            resources=tuple(rows),
            material_sha256=digest,
        )

    def restore(
        self,
        artifact: BackupArtifact | str,
        target: StructuredStateAdapter,
    ) -> RestoreResult:
        backup = artifact if isinstance(artifact, BackupArtifact) else BackupArtifact.from_json(artifact)
        _validate_artifact(backup)
        target_schema = _schema(target)
        if (
            target_schema.schema_version != backup.schema_version
            or target_schema.resource_types != backup.resource_types
            or target_schema.event_types != backup.event_types
        ):
            raise BackupValidationError(
                "restore target schema does not exactly match backup schema"
            )

        # The public contract cannot enumerate target Events/idempotency. This
        # first slice therefore requires the caller/provider proof to establish a
        # genuinely fresh authority and additionally proves Resource emptiness here.
        for resource_type in target_schema.resource_types:
            try:
                if tuple(target.query(resource_type, limit=1)):
                    raise BackupValidationError(
                        "restore target Resource space must be empty"
                    )
            except BackupValidationError:
                raise
            except StructuredStateError as exc:
                raise BackupIntegrityError(str(exc)) from exc

        for row in backup.resources:
            # STORE-001 has no arbitrary revision import operation. Repeating the
            # final canonical payload with deterministic restore-only keys preserves
            # the current revision number without claiming historical payload replay.
            for wanted_revision in range(1, row.revision + 1):
                key = _restore_key(backup.material_sha256, row, wanted_revision)
                try:
                    result = target.upsert(
                        row.resource_type,
                        row.resource_id,
                        row.payload,
                        idempotency_key=key,
                        expected_revision=wanted_revision - 1,
                    )
                except StructuredStateError as exc:
                    raise BackupIntegrityError(
                        f"restore failed for {row.resource_type}:{row.resource_id} "
                        f"at revision {wanted_revision}: {exc}"
                    ) from exc
                if result.record.revision != wanted_revision:
                    raise BackupIntegrityError(
                        "restore write returned unexpected Resource revision"
                    )

        verified = self.create(target)
        if verified.material_sha256 != backup.material_sha256:
            raise BackupIntegrityError("restored Resource snapshot parity verification failed")
        if verified.unsigned_material() != backup.unsigned_material():
            raise BackupIntegrityError("restored Resource material does not equal backup")
        return RestoreResult(
            restored_resource_count=verified.resource_count,
            verified_material_sha256=verified.material_sha256,
        )

    def verify(self, artifact: BackupArtifact | str) -> BackupArtifact:
        backup = artifact if isinstance(artifact, BackupArtifact) else BackupArtifact.from_json(artifact)
        _validate_artifact(backup)
        return backup


def _artifact_from_mapping(value: object) -> BackupArtifact:
    if not isinstance(value, Mapping):
        raise BackupValidationError("backup artifact must be a JSON object")
    root = dict(value)
    if set(root) != {"artifact_version", "coverage", "material_sha256", "resources", "schema"}:
        raise BackupValidationError("backup artifact fields are incomplete or unexpected")
    schema = root["schema"]
    coverage = root["coverage"]
    if not isinstance(schema, Mapping) or set(schema) != {"schema_version", "resource_types", "event_types"}:
        raise BackupValidationError("backup schema fields are incomplete or unexpected")
    if not isinstance(coverage, Mapping) or set(coverage) != {"resources", "events", "idempotency"}:
        raise BackupValidationError("backup coverage fields are incomplete or unexpected")

    resource_types = _string_tuple(schema["resource_types"], "resource_types")
    event_types = _string_tuple(schema["event_types"], "event_types")
    if resource_types != tuple(sorted(resource_types)) or event_types != tuple(sorted(event_types)):
        raise BackupValidationError("backup schema type lists must be deterministically sorted")

    raw_resources = root["resources"]
    if not isinstance(raw_resources, list):
        raise BackupValidationError("backup resources must be a list")
    rows: list[BackupResource] = []
    for raw in raw_resources:
        if not isinstance(raw, Mapping) or set(raw) != {"resource_type", "resource_id", "revision", "payload"}:
            raise BackupValidationError("backup Resource fields are incomplete or unexpected")
        revision = raw["revision"]
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise BackupValidationError("backup Resource revision must be a positive integer")
        if not isinstance(raw["payload"], Mapping):
            raise BackupValidationError("backup Resource payload must be an object")
        row = BackupResource(
            resource_type=_text(raw["resource_type"], "resource_type"),
            resource_id=_text(raw["resource_id"], "resource_id"),
            revision=revision,
            payload=_json_mapping(raw["payload"], "payload"),
        )
        rows.append(row)
    if rows != sorted(rows, key=lambda row: (row.resource_type, row.resource_id)):
        raise BackupValidationError("backup Resources must be deterministically sorted")
    if len({(row.resource_type, row.resource_id) for row in rows}) != len(rows):
        raise BackupValidationError("backup contains duplicate Resource identity")

    artifact = BackupArtifact(
        artifact_version=root["artifact_version"],
        schema_version=_text(schema["schema_version"], "schema_version"),
        resource_types=resource_types,
        event_types=event_types,
        resource_coverage=_text(coverage["resources"], "resource coverage"),
        event_coverage=_text(coverage["events"], "event coverage"),
        idempotency_coverage=_text(coverage["idempotency"], "idempotency coverage"),
        resources=tuple(rows),
        material_sha256=_digest(root["material_sha256"]),
    )
    _validate_artifact(artifact)
    return artifact


def _validate_artifact(artifact: BackupArtifact) -> None:
    if artifact.artifact_version != BACKUP_ARTIFACT_VERSION:
        raise BackupValidationError("unsupported backup artifact version")
    if artifact.resource_coverage != RESOURCE_COVERAGE:
        raise BackupValidationError("unsupported Resource coverage declaration")
    if artifact.event_coverage != EVENT_COVERAGE:
        raise BackupValidationError("backup must declare Event history as not covered in v1")
    if artifact.idempotency_coverage != IDEMPOTENCY_COVERAGE:
        raise BackupValidationError("backup must declare original idempotency history as not covered in v1")
    if artifact.resource_types != tuple(sorted(set(artifact.resource_types))):
        raise BackupValidationError("backup resource_types must be unique and sorted")
    if artifact.event_types != tuple(sorted(set(artifact.event_types))):
        raise BackupValidationError("backup event_types must be unique and sorted")
    for row in artifact.resources:
        if row.resource_type not in artifact.resource_types:
            raise BackupValidationError(
                f"backup Resource uses undeclared type: {row.resource_type}"
            )
    expected = _sha256(artifact.unsigned_material())
    if artifact.material_sha256 != expected:
        raise BackupIntegrityError("backup artifact SHA-256 digest mismatch")


def _backup_resource(record: ResourceRecord, *, expected_type: str) -> BackupResource:
    if not isinstance(record, ResourceRecord):
        raise BackupIntegrityError("source query returned a non-ResourceRecord")
    if record.resource_type != expected_type:
        raise BackupIntegrityError("source query returned a Resource with the wrong type")
    if not isinstance(record.revision, int) or isinstance(record.revision, bool) or record.revision < 1:
        raise BackupIntegrityError("source Resource revision is invalid")
    return BackupResource(
        resource_type=_text(record.resource_type, "resource_type"),
        resource_id=_text(record.resource_id, "resource_id"),
        revision=record.revision,
        payload=_json_mapping(record.payload, "payload"),
    )


def _schema(adapter: StructuredStateAdapter):
    try:
        schema = adapter.schema()
    except StructuredStateError as exc:
        raise BackupIntegrityError(str(exc)) from exc
    if tuple(schema.resource_types) != tuple(sorted(set(schema.resource_types))):
        raise BackupIntegrityError("adapter resource_types must be unique and sorted")
    if tuple(schema.event_types) != tuple(sorted(set(schema.event_types))):
        raise BackupIntegrityError("adapter event_types must be unique and sorted")
    return schema


def _restore_key(digest: str, row: BackupResource, revision: int) -> str:
    material = f"{digest}:{row.resource_type}:{row.resource_id}:{revision}"
    suffix = hashlib.sha256(material.encode("utf-8")).hexdigest()[:40]
    return f"backup-restore-{suffix}"


def _string_tuple(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise BackupValidationError(f"{field} must be a non-empty list")
    rows = tuple(_text(item, field) for item in value)
    if len(set(rows)) != len(rows):
        raise BackupValidationError(f"{field} must not contain duplicates")
    return rows


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise BackupValidationError(f"{field} must be non-empty trimmed text")
    if len(value) > 128:
        raise BackupValidationError(f"{field} must be at most 128 characters")
    return value


def _digest(value: object) -> str:
    text = _text(value, "material_sha256")
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise BackupValidationError("material_sha256 must be 64 lowercase hexadecimal characters")
    return text


def _json_mapping(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise BackupValidationError(f"{field} must be an object")
    try:
        encoded = _canonical_json(dict(value))
        decoded = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise BackupValidationError(f"{field} must contain JSON-compatible values") from exc
    if not isinstance(decoded, dict):
        raise BackupValidationError(f"{field} must be an object")
    return decoded


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise BackupValidationError("backup material must be JSON-compatible") from exc


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


__all__ = [
    "BACKUP_ARTIFACT_VERSION",
    "BackupArtifact",
    "BackupError",
    "BackupIntegrityError",
    "BackupResource",
    "BackupService",
    "BackupValidationError",
    "EVENT_COVERAGE",
    "IDEMPOTENCY_COVERAGE",
    "RESOURCE_COVERAGE",
    "RestoreResult",
]
