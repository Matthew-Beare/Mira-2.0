"""Durable reconciliation checkpoint persistence over MIRA structured state."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from typing import Mapping

from mira.structured_state import NotFoundError, StructuredStateAdapter, StructuredStateError
from ops.reconciliation_sweep import (
    CheckpointConflictError,
    ModuleResult,
    ModuleSpec,
    MutationReadback,
    ReconciliationCounts,
    ReconciliationError,
    RunCheckpoint,
    SourceStatus,
)


class StructuredCheckpointStore:
    """Persist and exactly read back reconciliation checkpoints."""

    SCHEMA_VERSION = 1

    def __init__(
        self,
        adapter: StructuredStateAdapter,
        *,
        resource_type: str = "reconciliation_run",
    ) -> None:
        if not isinstance(resource_type, str) or not resource_type or resource_type != resource_type.strip():
            raise ReconciliationError("checkpoint resource_type must be non-empty text")
        self._adapter = adapter
        self._resource_type = resource_type

    def get(self, run_id: str) -> RunCheckpoint | None:
        try:
            record = self._adapter.get(self._resource_type, run_id)
        except NotFoundError:
            return None
        except StructuredStateError as exc:
            raise ReconciliationError("checkpoint read failed") from exc
        return _checkpoint_from_payload(record.payload, expected_run_id=run_id)

    def put(self, checkpoint: RunCheckpoint) -> None:
        existing = self.get(checkpoint.run_id)
        if existing is not None:
            if existing.checkpoint_fingerprint != checkpoint.checkpoint_fingerprint:
                raise CheckpointConflictError(
                    "run checkpoint already exists with different material"
                )
            return

        payload = {"schema_version": self.SCHEMA_VERSION, **checkpoint.to_payload()}
        try:
            self._adapter.upsert(
                self._resource_type,
                checkpoint.run_id,
                payload,
                idempotency_key=(
                    f"recon-checkpoint:{checkpoint.run_id}:"
                    f"{checkpoint.checkpoint_fingerprint[:24]}"
                ),
                expected_revision=0,
            )
            readback = self._adapter.get(self._resource_type, checkpoint.run_id)
        except StructuredStateError as exc:
            raise ReconciliationError("checkpoint write/readback failed") from exc
        if readback.payload != payload:
            raise ReconciliationError("checkpoint exact readback mismatch")
        restored = _checkpoint_from_payload(readback.payload, expected_run_id=checkpoint.run_id)
        if restored.checkpoint_fingerprint != checkpoint.checkpoint_fingerprint:
            raise ReconciliationError("checkpoint fingerprint readback mismatch")


def _checkpoint_from_payload(
    payload: Mapping[str, object], *, expected_run_id: str
) -> RunCheckpoint:
    if payload.get("schema_version") != StructuredCheckpointStore.SCHEMA_VERSION:
        raise ReconciliationError("unsupported reconciliation checkpoint schema")
    run_id = payload.get("run_id")
    if run_id != expected_run_id or not isinstance(run_id, str):
        raise ReconciliationError("checkpoint run identity mismatch")

    local_date = _text(payload.get("local_date"), "local_date")
    timezone = _text(payload.get("timezone"), "timezone")
    slot = _text(payload.get("slot"), "slot")
    context = payload.get("context")
    if context is not None and not isinstance(context, str):
        raise ReconciliationError("checkpoint context is invalid")
    manifest_fingerprint = _digest(payload.get("manifest_fingerprint"), "manifest_fingerprint")
    checkpoint_fingerprint = _digest(payload.get("checkpoint_fingerprint"), "checkpoint_fingerprint")
    required_action = payload.get("required_action")
    if not isinstance(required_action, bool):
        raise ReconciliationError("checkpoint required_action is invalid")

    raw_modules = payload.get("modules")
    if not isinstance(raw_modules, list):
        raise ReconciliationError("checkpoint modules are invalid")
    modules = tuple(_module_from_payload(item) for item in raw_modules)
    if len({item.module_id for item in modules}) != len(modules):
        raise ReconciliationError("checkpoint contains duplicate module IDs")

    material = {
        "run_id": run_id,
        "local_date": local_date,
        "timezone": timezone,
        "slot": slot,
        "context": context,
        "manifest_fingerprint": manifest_fingerprint,
        "modules": [_module_payload(item) for item in modules],
        "required_action": required_action,
    }
    if _fingerprint(material) != checkpoint_fingerprint:
        raise ReconciliationError("checkpoint fingerprint does not match payload")
    return RunCheckpoint(
        run_id=run_id,
        local_date=local_date,
        timezone=timezone,
        slot=slot,
        context=context,
        manifest_fingerprint=manifest_fingerprint,
        modules=modules,
        required_action=required_action,
        checkpoint_fingerprint=checkpoint_fingerprint,
    )


def _module_from_payload(raw: object) -> ModuleResult:
    if not isinstance(raw, Mapping):
        raise ReconciliationError("checkpoint module entry is invalid")
    raw_counts = raw.get("counts")
    raw_sources = raw.get("sources")
    raw_mutations = raw.get("mutations")
    raw_reviews = raw.get("review_item_ids")
    rebuild_verified = raw.get("rebuild_verified")
    if not isinstance(raw_counts, Mapping):
        raise ReconciliationError("checkpoint counts are invalid")
    if not isinstance(raw_sources, list) or not all(isinstance(item, Mapping) for item in raw_sources):
        raise ReconciliationError("checkpoint sources are invalid")
    if not isinstance(raw_mutations, list) or not all(isinstance(item, Mapping) for item in raw_mutations):
        raise ReconciliationError("checkpoint mutations are invalid")
    if not isinstance(raw_reviews, list) or not all(isinstance(item, str) for item in raw_reviews):
        raise ReconciliationError("checkpoint review items are invalid")
    if not isinstance(rebuild_verified, bool):
        raise ReconciliationError("checkpoint rebuild verification is invalid")
    try:
        result = ModuleResult(
            module_id=raw.get("module_id"),
            disposition=raw.get("disposition"),
            counts=ReconciliationCounts(
                discovered=raw_counts.get("discovered"),
                matched=raw_counts.get("matched"),
                updated=raw_counts.get("updated"),
                duplicate=raw_counts.get("duplicate"),
                unresolved=raw_counts.get("unresolved"),
            ),
            sources=tuple(SourceStatus(**dict(item)) for item in raw_sources),
            mutations=tuple(MutationReadback(**dict(item)) for item in raw_mutations),
            rebuild_verified=rebuild_verified,
            review_item_ids=tuple(raw_reviews),
            blocker_code=raw.get("blocker_code"),
            next_cursor=raw.get("next_cursor"),
        )
        result.validate(ModuleSpec(result.module_id))
    except (TypeError, ValueError, ReconciliationError) as exc:
        raise ReconciliationError("checkpoint module readback is invalid") from exc
    return result


def _module_payload(result: ModuleResult) -> dict[str, object]:
    return {
        "module_id": result.module_id,
        "disposition": result.disposition,
        "counts": asdict(result.counts),
        "sources": [asdict(item) for item in result.sources],
        "mutations": [asdict(item) for item in result.mutations],
        "rebuild_verified": result.rebuild_verified,
        "review_item_ids": list(result.review_item_ids),
        "blocker_code": result.blocker_code,
        "next_cursor": result.next_cursor,
    }


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ReconciliationError(f"checkpoint {field} is invalid")
    return value


def _digest(value: object, field: str) -> str:
    text = _text(value, field)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise ReconciliationError(f"checkpoint {field} is invalid")
    return text


def _fingerprint(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = ["StructuredCheckpointStore"]
