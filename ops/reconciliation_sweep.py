"""Deterministic reconciliation sweep and pre-reply claim gate for MIRA.

This module is provider-neutral. Domain handlers do the actual provider reads,
canonical mutations, projection rebuilds, and exact readbacks. The sweep owns
run identity, ordering, terminal dispositions, bounded checkpoint evidence,
replay, failure isolation, and claim gating.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date
import hashlib
import json
import re
from typing import Callable, Iterable, Mapping, Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DISPOSITIONS = {"complete", "needs_review", "blocked", "not_applicable"}
FRESHNESS = {"fresh", "stale", "unknown", "not_applicable"}
COVERAGE = {"complete", "partial", "unknown", "not_applicable"}
STRONG_CLAIMS = {"current", "updated", "reconciled", "done", "complete", "verified"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")


class ReconciliationError(Exception):
    """Base class for sweep errors."""


class ManifestError(ReconciliationError):
    """Invalid run or module manifest."""


class ModuleContractError(ReconciliationError):
    """A module result violates the reconciliation contract."""


class CheckpointConflictError(ReconciliationError):
    """A run ID already exists with different material."""


class ClaimGateError(ReconciliationError):
    """A requested user-facing state claim is not supported."""


@dataclass(frozen=True)
class ReconciliationCounts:
    discovered: int = 0
    matched: int = 0
    updated: int = 0
    duplicate: int = 0
    unresolved: int = 0

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ModuleContractError(f"count {name} must be a non-negative integer")


@dataclass(frozen=True)
class SourceStatus:
    source_id: str
    freshness: str
    coverage: str
    cursor: str | None = None

    def validate(self) -> None:
        _stable_id(self.source_id, "source_id")
        if self.freshness not in FRESHNESS:
            raise ModuleContractError("source freshness is invalid")
        if self.coverage not in COVERAGE:
            raise ModuleContractError("source coverage is invalid")
        if self.cursor is not None:
            _bounded_text(self.cursor, "source cursor", max_len=512)


@dataclass(frozen=True)
class MutationReadback:
    mutation_id: str
    required: bool = True
    readback_verified: bool = False
    readback_fingerprint: str | None = None

    def validate(self) -> None:
        _stable_id(self.mutation_id, "mutation_id")
        if not isinstance(self.required, bool) or not isinstance(self.readback_verified, bool):
            raise ModuleContractError("mutation flags must be boolean")
        if self.readback_verified:
            if not isinstance(self.readback_fingerprint, str) or not _SHA256_RE.fullmatch(
                self.readback_fingerprint
            ):
                raise ModuleContractError(
                    "verified mutation requires a SHA-256 readback fingerprint"
                )
        elif self.readback_fingerprint is not None:
            raise ModuleContractError(
                "unverified mutation cannot carry a readback fingerprint"
            )


@dataclass(frozen=True)
class ModuleSpec:
    module_id: str
    required: bool = True
    depends_on: tuple[str, ...] = ()
    rebuild_required: bool = False

    def validate(self) -> None:
        _stable_id(self.module_id, "module_id")
        if not isinstance(self.required, bool) or not isinstance(self.rebuild_required, bool):
            raise ManifestError("module flags must be boolean")
        if not isinstance(self.depends_on, tuple):
            raise ManifestError("depends_on must be a tuple")
        for dependency in self.depends_on:
            _stable_id(dependency, "dependency module_id", error=ManifestError)
        if self.module_id in self.depends_on:
            raise ManifestError("module cannot depend on itself")


@dataclass(frozen=True)
class ModuleResult:
    module_id: str
    disposition: str
    counts: ReconciliationCounts = field(default_factory=ReconciliationCounts)
    sources: tuple[SourceStatus, ...] = ()
    mutations: tuple[MutationReadback, ...] = ()
    rebuild_verified: bool = False
    review_item_ids: tuple[str, ...] = ()
    blocker_code: str | None = None
    next_cursor: str | None = None

    def validate(self, spec: ModuleSpec) -> None:
        if self.module_id != spec.module_id:
            raise ModuleContractError("module result identity mismatch")
        if self.disposition not in DISPOSITIONS:
            raise ModuleContractError("module disposition is invalid")
        if not isinstance(self.sources, tuple) or not isinstance(self.mutations, tuple):
            raise ModuleContractError("sources and mutations must be tuples")
        if not isinstance(self.review_item_ids, tuple):
            raise ModuleContractError("review_item_ids must be a tuple")
        self.counts.validate()

        source_ids: set[str] = set()
        for source in self.sources:
            source.validate()
            if source.source_id in source_ids:
                raise ModuleContractError("duplicate source_id in module result")
            source_ids.add(source.source_id)

        mutation_ids: set[str] = set()
        for mutation in self.mutations:
            mutation.validate()
            if mutation.mutation_id in mutation_ids:
                raise ModuleContractError("duplicate mutation_id in module result")
            mutation_ids.add(mutation.mutation_id)

        for review_id in self.review_item_ids:
            _stable_id(review_id, "review_item_id", error=ModuleContractError)
        if len(set(self.review_item_ids)) != len(self.review_item_ids):
            raise ModuleContractError("duplicate review_item_id in module result")

        if self.blocker_code is not None:
            _stable_id(self.blocker_code, "blocker_code", error=ModuleContractError)
        if self.next_cursor is not None:
            _bounded_text(self.next_cursor, "next_cursor", max_len=512, error=ModuleContractError)

        if self.disposition == "complete":
            if self.blocker_code is not None or self.review_item_ids:
                raise ModuleContractError("complete module cannot carry blocker/review state")
            for mutation in self.mutations:
                if mutation.required and not mutation.readback_verified:
                    raise ModuleContractError(
                        "complete module has required mutation without exact readback"
                    )
            if spec.rebuild_required and not self.rebuild_verified:
                raise ModuleContractError(
                    "complete module did not verify its required rebuild"
                )
        elif self.disposition == "needs_review":
            if not self.review_item_ids:
                raise ModuleContractError("needs_review requires review item IDs")
            if self.blocker_code is not None:
                raise ModuleContractError("needs_review cannot also be blocked")
        elif self.disposition == "blocked":
            if self.blocker_code is None:
                raise ModuleContractError("blocked module requires blocker_code")
        elif self.disposition == "not_applicable":
            if self.mutations or self.review_item_ids or self.blocker_code is not None:
                raise ModuleContractError(
                    "not_applicable cannot carry mutations, reviews, or blocker"
                )


@dataclass(frozen=True)
class RunSpec:
    run_id: str
    local_date: str
    timezone: str
    slot: str
    context: str | None
    modules: tuple[ModuleSpec, ...]

    @classmethod
    def build(
        cls,
        *,
        local_date: str,
        timezone: str,
        slot: str,
        modules: Iterable[ModuleSpec],
        context: str | None = None,
        run_key: str | None = None,
    ) -> "RunSpec":
        day = _date(local_date)
        zone = _timezone(timezone)
        normalized_slot = _slug(slot, "slot")
        if context is None:
            normalized_context = None
        else:
            normalized_context = _bounded_text(
                context, "context", max_len=128, error=ManifestError
            ).lower()
        module_tuple = tuple(modules)
        _validate_manifest(module_tuple)
        identity = {
            "local_date": day.isoformat(),
            "timezone": zone,
            "slot": normalized_slot,
            "context": normalized_context,
            "run_key": run_key,
            "modules": [_spec_payload(item) for item in module_tuple],
        }
        digest = _fingerprint(identity)
        key = _slug(run_key, "run_key") if run_key is not None else normalized_slot
        run_id = f"recon:{day.isoformat()}:{key}:{digest[:16]}"
        return cls(
            run_id=run_id,
            local_date=day.isoformat(),
            timezone=zone,
            slot=normalized_slot,
            context=normalized_context,
            modules=module_tuple,
        )

    @property
    def manifest_fingerprint(self) -> str:
        return _fingerprint(
            {
                "run_id": self.run_id,
                "local_date": self.local_date,
                "timezone": self.timezone,
                "slot": self.slot,
                "context": self.context,
                "modules": [_spec_payload(item) for item in self.modules],
            }
        )


@dataclass(frozen=True)
class ModuleContext:
    run_id: str
    local_date: str
    timezone: str
    slot: str
    context: str | None
    module_id: str
    previous_cursor: str | None


@dataclass(frozen=True)
class RunCheckpoint:
    run_id: str
    local_date: str
    timezone: str
    slot: str
    context: str | None
    manifest_fingerprint: str
    modules: tuple[ModuleResult, ...]
    required_action: bool
    checkpoint_fingerprint: str
    idempotent_replay: bool = False

    def module(self, module_id: str) -> ModuleResult:
        for result in self.modules:
            if result.module_id == module_id:
                return result
        raise ClaimGateError(f"module {module_id!r} is not in this run")

    def claim_allowed(self, module_id: str, claim: str) -> bool:
        normalized = claim.strip().lower()
        if normalized not in STRONG_CLAIMS:
            return True
        result = self.module(module_id)
        if result.disposition != "complete":
            return False
        if normalized == "current":
            relevant = [s for s in result.sources if s.coverage != "not_applicable"]
            return bool(relevant) and all(
                source.freshness == "fresh" and source.coverage == "complete"
                for source in relevant
            )
        return True

    def assert_claim(self, module_id: str, claim: str) -> None:
        if not self.claim_allowed(module_id, claim):
            result = self.module(module_id)
            raise ClaimGateError(
                f"claim {claim!r} is unsupported for module {module_id!r} "
                f"with disposition {result.disposition!r}"
            )

    def to_payload(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "local_date": self.local_date,
            "timezone": self.timezone,
            "slot": self.slot,
            "context": self.context,
            "manifest_fingerprint": self.manifest_fingerprint,
            "modules": [_result_payload(result) for result in self.modules],
            "required_action": self.required_action,
            "checkpoint_fingerprint": self.checkpoint_fingerprint,
        }


class CheckpointStore(Protocol):
    def get(self, run_id: str) -> RunCheckpoint | None: ...
    def put(self, checkpoint: RunCheckpoint) -> None: ...


class MemoryCheckpointStore:
    def __init__(self) -> None:
        self._items: dict[str, RunCheckpoint] = {}

    def get(self, run_id: str) -> RunCheckpoint | None:
        return self._items.get(run_id)

    def put(self, checkpoint: RunCheckpoint) -> None:
        existing = self._items.get(checkpoint.run_id)
        if existing is not None and existing.checkpoint_fingerprint != checkpoint.checkpoint_fingerprint:
            raise CheckpointConflictError("run checkpoint already exists with different material")
        self._items[checkpoint.run_id] = checkpoint


Handler = Callable[[ModuleContext], ModuleResult]


class ReconciliationSweep:
    def __init__(self, store: CheckpointStore) -> None:
        self._store = store

    def run(
        self,
        spec: RunSpec,
        handlers: Mapping[str, Handler],
        *,
        previous_cursors: Mapping[str, str | None] | None = None,
    ) -> RunCheckpoint:
        _validate_run_spec(spec)
        existing = self._store.get(spec.run_id)
        if existing is not None:
            if existing.manifest_fingerprint != spec.manifest_fingerprint:
                raise CheckpointConflictError(
                    "run_id already exists with a different manifest"
                )
            return RunCheckpoint(**{**asdict(existing), "modules": existing.modules, "idempotent_replay": True})

        cursors = dict(previous_cursors or {})
        unknown_cursor_modules = set(cursors) - {item.module_id for item in spec.modules}
        if unknown_cursor_modules:
            raise ManifestError("previous cursor references module outside manifest")
        for value in cursors.values():
            if value is not None:
                _bounded_text(value, "previous_cursor", max_len=512, error=ManifestError)

        results: dict[str, ModuleResult] = {}
        ordered = _topological_order(spec.modules)
        for module in ordered:
            blocked_dependency = next(
                (
                    dependency
                    for dependency in module.depends_on
                    if results[dependency].disposition not in {"complete", "not_applicable"}
                ),
                None,
            )
            if blocked_dependency is not None:
                results[module.module_id] = ModuleResult(
                    module_id=module.module_id,
                    disposition="blocked",
                    blocker_code="dependency_not_verified",
                )
                continue

            handler = handlers.get(module.module_id)
            if handler is None:
                results[module.module_id] = ModuleResult(
                    module_id=module.module_id,
                    disposition="blocked",
                    blocker_code="handler_missing",
                )
                continue

            context = ModuleContext(
                run_id=spec.run_id,
                local_date=spec.local_date,
                timezone=spec.timezone,
                slot=spec.slot,
                context=spec.context,
                module_id=module.module_id,
                previous_cursor=cursors.get(module.module_id),
            )
            try:
                result = handler(context)
                if not isinstance(result, ModuleResult):
                    raise ModuleContractError("handler must return ModuleResult")
                result.validate(module)
            except ModuleContractError:
                result = ModuleResult(
                    module_id=module.module_id,
                    disposition="blocked",
                    blocker_code="module_contract_violation",
                )
            except Exception:
                result = ModuleResult(
                    module_id=module.module_id,
                    disposition="blocked",
                    blocker_code="handler_exception",
                )
            results[module.module_id] = result

        normalized = tuple(results[item.module_id] for item in spec.modules)
        required_action = any(
            item.required and results[item.module_id].disposition in {"blocked", "needs_review"}
            for item in spec.modules
        )
        material = {
            "run_id": spec.run_id,
            "local_date": spec.local_date,
            "timezone": spec.timezone,
            "slot": spec.slot,
            "context": spec.context,
            "manifest_fingerprint": spec.manifest_fingerprint,
            "modules": [_result_payload(item) for item in normalized],
            "required_action": required_action,
        }
        checkpoint = RunCheckpoint(
            run_id=spec.run_id,
            local_date=spec.local_date,
            timezone=spec.timezone,
            slot=spec.slot,
            context=spec.context,
            manifest_fingerprint=spec.manifest_fingerprint,
            modules=normalized,
            required_action=required_action,
            checkpoint_fingerprint=_fingerprint(material),
        )
        self._store.put(checkpoint)
        return checkpoint


def _validate_run_spec(spec: RunSpec) -> None:
    if not isinstance(spec, RunSpec):
        raise ManifestError("spec must be RunSpec")
    _stable_id(spec.run_id.replace("recon:", "recon-", 1), "run_id", error=ManifestError)
    _date(spec.local_date)
    _timezone(spec.timezone)
    _slug(spec.slot, "slot")
    if spec.context is not None:
        _bounded_text(spec.context, "context", max_len=128, error=ManifestError)
    _validate_manifest(spec.modules)


def _validate_manifest(modules: tuple[ModuleSpec, ...]) -> None:
    if not modules:
        raise ManifestError("module manifest cannot be empty")
    ids: set[str] = set()
    for module in modules:
        module.validate()
        if module.module_id in ids:
            raise ManifestError("duplicate module_id in manifest")
        ids.add(module.module_id)
    for module in modules:
        missing = set(module.depends_on) - ids
        if missing:
            raise ManifestError("module dependency is outside manifest")
    _topological_order(modules)


def _topological_order(modules: tuple[ModuleSpec, ...]) -> tuple[ModuleSpec, ...]:
    by_id = {item.module_id: item for item in modules}
    ordered: list[ModuleSpec] = []
    permanent: set[str] = set()
    temporary: set[str] = set()

    def visit(module_id: str) -> None:
        if module_id in permanent:
            return
        if module_id in temporary:
            raise ManifestError("module dependency cycle detected")
        temporary.add(module_id)
        module = by_id[module_id]
        for dependency in module.depends_on:
            if dependency not in by_id:
                raise ManifestError("module dependency is outside manifest")
            visit(dependency)
        temporary.remove(module_id)
        permanent.add(module_id)
        ordered.append(module)

    for module in modules:
        visit(module.module_id)
    return tuple(ordered)


def _spec_payload(spec: ModuleSpec) -> dict[str, object]:
    return {
        "module_id": spec.module_id,
        "required": spec.required,
        "depends_on": list(spec.depends_on),
        "rebuild_required": spec.rebuild_required,
    }


def _result_payload(result: ModuleResult) -> dict[str, object]:
    return {
        "module_id": result.module_id,
        "disposition": result.disposition,
        "counts": asdict(result.counts),
        "sources": [asdict(source) for source in result.sources],
        "mutations": [asdict(mutation) for mutation in result.mutations],
        "rebuild_verified": result.rebuild_verified,
        "review_item_ids": list(result.review_item_ids),
        "blocker_code": result.blocker_code,
        "next_cursor": result.next_cursor,
    }


def _fingerprint(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_id(value: object, field: str, *, error: type[Exception] = ModuleContractError) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise error(f"{field} must be stable lowercase identifier text")
    return value


def _slug(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ManifestError(f"{field} must be text")
    normalized = value.strip().lower().replace("_", "-")
    if not normalized or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", normalized):
        raise ManifestError(f"{field} must be a bounded slug")
    return normalized


def _bounded_text(
    value: object,
    field: str,
    *,
    max_len: int,
    error: type[Exception] = ModuleContractError,
) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > max_len:
        raise error(f"{field} must be non-empty bounded text")
    return value


def _date(value: object) -> date:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ManifestError("local_date must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ManifestError("local_date must be YYYY-MM-DD") from exc


def _timezone(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ManifestError("timezone must be IANA text")
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ManifestError("timezone must be valid IANA text") from exc
    return value


__all__ = [
    "CheckpointConflictError",
    "ClaimGateError",
    "ManifestError",
    "MemoryCheckpointStore",
    "ModuleContext",
    "ModuleContractError",
    "ModuleResult",
    "ModuleSpec",
    "MutationReadback",
    "ReconciliationCounts",
    "ReconciliationError",
    "ReconciliationSweep",
    "RunCheckpoint",
    "RunSpec",
    "SourceStatus",
]
