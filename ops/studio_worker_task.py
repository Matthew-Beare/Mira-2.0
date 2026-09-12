#!/usr/bin/env python3
"""Portable Studio worker-task contract and worker-local private binding.

The portable task is safe to move across MIRA's controller/worker boundary: it
contains customer/controller execution semantics and logical binding IDs, never a
private repository path, model endpoint, concrete model name, credential, host, or
machine binding.  A trusted worker resolves those logical IDs against private local
configuration and obtains the existing :class:`WorkerManifest` immediately before
restricted execution.

This module performs no network I/O, credential loading, Git mutation, model call,
test execution, scheduling, activation, merge, push, or publication.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import PurePosixPath
import re
from typing import Any

from mira.studio_intake import StudioIntakeDraft, StudioIntakeNextAction
from ops.studio_local_worker import StudioWorkerError, WorkerManifest


_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_DRAFT_RE = re.compile(r"^intake-[0-9a-f]{64}$")
_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SAFE_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")
_MAX_ALLOWED_PATHS = 64
_MAX_OBJECTIVE_CHARS = 32_000
_MAX_ARG_CHARS = 4096


class StudioWorkerTaskError(RuntimeError):
    """Fail-closed portable-task or private-binding validation error."""


@dataclass(frozen=True)
class PortableStudioExecutionPolicy:
    """Controller-owned portable execution policy.

    Logical binding identifiers are intentionally not paths, endpoints, machine
    identifiers, or credentials.  Physical resolution belongs to the selected
    worker's private runtime configuration.
    """

    source_binding_id: str
    base_sha: str
    branch_name: str
    allowed_paths: tuple[str, ...]
    test_argv: tuple[str, ...]
    model_profile_id: str
    max_rounds: int = 3
    wall_timeout_seconds: int = 900
    test_timeout_seconds: int = 180
    model_timeout_seconds: int = 180

    def validate(self) -> None:
        _token(self.source_binding_id, "source_binding_id")
        _sha(self.base_sha, "base_sha")
        _branch(self.branch_name)
        _paths(self.allowed_paths)
        _argv(self.test_argv)
        _token(self.model_profile_id, "model_profile_id")
        _bounded_int(self.max_rounds, "max_rounds", 1, 12)
        _bounded_int(self.wall_timeout_seconds, "wall_timeout_seconds", 5, 7200)
        _bounded_int(self.test_timeout_seconds, "test_timeout_seconds", 1, 1800)
        _bounded_int(self.model_timeout_seconds, "model_timeout_seconds", 1, 1800)


@dataclass(frozen=True)
class PortableStudioWorkerTask:
    """Secret-free transport material for one bounded Studio implementation."""

    draft_id: str
    objective: str
    source_binding_id: str
    base_sha: str
    branch_name: str
    allowed_paths: tuple[str, ...]
    test_argv: tuple[str, ...]
    model_profile_id: str
    max_rounds: int = 3
    wall_timeout_seconds: int = 900
    test_timeout_seconds: int = 180
    model_timeout_seconds: int = 180

    def validate(self) -> None:
        if not isinstance(self.draft_id, str) or not _DRAFT_RE.fullmatch(self.draft_id):
            raise StudioWorkerTaskError("draft_id must be an intake SHA-256 identity")
        _nonblank(self.objective, "objective", _MAX_OBJECTIVE_CHARS)
        _token(self.source_binding_id, "source_binding_id")
        _sha(self.base_sha, "base_sha")
        _branch(self.branch_name)
        _paths(self.allowed_paths)
        _argv(self.test_argv)
        _token(self.model_profile_id, "model_profile_id")
        _bounded_int(self.max_rounds, "max_rounds", 1, 12)
        _bounded_int(self.wall_timeout_seconds, "wall_timeout_seconds", 5, 7200)
        _bounded_int(self.test_timeout_seconds, "test_timeout_seconds", 1, 1800)
        _bounded_int(self.model_timeout_seconds, "model_timeout_seconds", 1, 1800)

    def canonical_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def canonical_bytes(self) -> bytes:
        return json.dumps(
            self.canonical_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, repr=False)
class StudioSourcePrivateBinding:
    """Worker-local source binding.  Never portable task material."""

    source_binding_id: str
    repo_path: str

    def validate(self) -> None:
        _token(self.source_binding_id, "source_binding_id")
        _nonblank(self.repo_path, "repo_path", 4096)


@dataclass(frozen=True, repr=False)
class StudioModelPrivateBinding:
    """Worker-local model binding.  Never portable task material."""

    model_profile_id: str
    model_base_url: str
    model: str

    def validate(self) -> None:
        _token(self.model_profile_id, "model_profile_id")
        _nonblank(self.model_base_url, "model_base_url", 2048)
        _nonblank(self.model, "model", 512)


@dataclass(frozen=True, repr=False)
class StudioWorkerPrivateBindings:
    """Selected worker's private deployment bindings.

    The class intentionally exposes no portable/canonical serialization helper.
    Callers keep this material in worker-local runtime configuration.
    """

    sources: tuple[StudioSourcePrivateBinding, ...]
    models: tuple[StudioModelPrivateBinding, ...]

    def validate(self) -> None:
        if not isinstance(self.sources, tuple) or not self.sources:
            raise StudioWorkerTaskError("sources must be a non-empty tuple")
        if not isinstance(self.models, tuple) or not self.models:
            raise StudioWorkerTaskError("models must be a non-empty tuple")
        source_ids: set[str] = set()
        for binding in self.sources:
            if not isinstance(binding, StudioSourcePrivateBinding):
                raise StudioWorkerTaskError(
                    "sources must contain StudioSourcePrivateBinding values"
                )
            binding.validate()
            if binding.source_binding_id in source_ids:
                raise StudioWorkerTaskError("duplicate source binding ID")
            source_ids.add(binding.source_binding_id)
        model_ids: set[str] = set()
        for binding in self.models:
            if not isinstance(binding, StudioModelPrivateBinding):
                raise StudioWorkerTaskError(
                    "models must contain StudioModelPrivateBinding values"
                )
            binding.validate()
            if binding.model_profile_id in model_ids:
                raise StudioWorkerTaskError("duplicate model profile binding ID")
            model_ids.add(binding.model_profile_id)



def objective_from_review_ready_intake(draft: StudioIntakeDraft) -> str:
    """Return the canonical customer/controller objective used by Studio workers."""

    if not isinstance(draft, StudioIntakeDraft):
        raise StudioWorkerTaskError("draft must be a StudioIntakeDraft")
    if (
        not draft.review_ready
        or draft.next_action is not StudioIntakeNextAction.REVIEW_DRAFT
        or draft.unresolved_questions
        or draft.blockers
    ):
        raise StudioWorkerTaskError(
            "Studio intake must be review-ready before worker task projection"
        )
    objective = json.dumps(
        {
            "customer_request": draft.raw_request,
            "desired_outcome": draft.desired_outcome,
            "explicit_customer_constraints": list(draft.explicit_constraints),
            "model_assumptions": list(draft.assumptions),
            "feature_ids": list(draft.feature_ids),
            "dependency_ids": list(draft.dependency_ids),
            "intake_projection_sha256": draft.projection_sha256,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    _nonblank(objective, "objective", _MAX_OBJECTIVE_CHARS)
    return objective



def portable_task_from_review_ready_intake(
    draft: StudioIntakeDraft,
    policy: PortableStudioExecutionPolicy,
) -> PortableStudioWorkerTask:
    """Project review-ready customer intent into transport-safe worker material."""

    if not isinstance(policy, PortableStudioExecutionPolicy):
        raise StudioWorkerTaskError(
            "policy must be a PortableStudioExecutionPolicy"
        )
    policy.validate()
    task = PortableStudioWorkerTask(
        draft_id=draft.draft_id,
        objective=objective_from_review_ready_intake(draft),
        source_binding_id=policy.source_binding_id,
        base_sha=policy.base_sha,
        branch_name=policy.branch_name,
        allowed_paths=policy.allowed_paths,
        test_argv=policy.test_argv,
        model_profile_id=policy.model_profile_id,
        max_rounds=policy.max_rounds,
        wall_timeout_seconds=policy.wall_timeout_seconds,
        test_timeout_seconds=policy.test_timeout_seconds,
        model_timeout_seconds=policy.model_timeout_seconds,
    )
    task.validate()
    return task



def bind_portable_task(
    task: PortableStudioWorkerTask,
    bindings: StudioWorkerPrivateBindings,
) -> WorkerManifest:
    """Resolve one portable task against exact worker-local private bindings."""

    if not isinstance(task, PortableStudioWorkerTask):
        raise StudioWorkerTaskError("task must be a PortableStudioWorkerTask")
    if not isinstance(bindings, StudioWorkerPrivateBindings):
        raise StudioWorkerTaskError(
            "bindings must be StudioWorkerPrivateBindings"
        )
    task.validate()
    bindings.validate()

    sources = tuple(
        item
        for item in bindings.sources
        if item.source_binding_id == task.source_binding_id
    )
    if len(sources) != 1:
        raise StudioWorkerTaskError(
            "portable task source binding is unavailable on this worker"
        )
    models = tuple(
        item
        for item in bindings.models
        if item.model_profile_id == task.model_profile_id
    )
    if len(models) != 1:
        raise StudioWorkerTaskError(
            "portable task model profile binding is unavailable on this worker"
        )

    source = sources[0]
    model = models[0]
    manifest = WorkerManifest(
        draft_id=task.draft_id,
        objective=task.objective,
        repo_path=source.repo_path,
        base_sha=task.base_sha,
        branch_name=task.branch_name,
        allowed_paths=task.allowed_paths,
        test_argv=task.test_argv,
        model_base_url=model.model_base_url,
        model=model.model,
        max_rounds=task.max_rounds,
        wall_timeout_seconds=task.wall_timeout_seconds,
        test_timeout_seconds=task.test_timeout_seconds,
        model_timeout_seconds=task.model_timeout_seconds,
    )
    try:
        manifest.validate()
    except StudioWorkerError as exc:
        raise StudioWorkerTaskError(
            f"private binding does not produce a valid worker manifest: {exc}"
        ) from exc
    return manifest


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        raise StudioWorkerTaskError(f"{field} must be a bounded logical ID")
    return value


def _sha(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        raise StudioWorkerTaskError(
            f"{field} must be a lowercase 40-character Git SHA"
        )
    return value


def _branch(value: object) -> str:
    if (
        not isinstance(value, str)
        or not _SAFE_BRANCH_RE.fullmatch(value)
        or ".." in value
        or "//" in value
        or value.endswith(("/", ".", ".lock"))
    ):
        raise StudioWorkerTaskError("branch_name is not a safe Git branch name")
    return value


def _paths(values: object) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values or len(values) > _MAX_ALLOWED_PATHS:
        raise StudioWorkerTaskError(
            f"allowed_paths must contain 1..{_MAX_ALLOWED_PATHS} paths"
        )
    normalized = tuple(sorted(set(_safe_relpath(value) for value in values)))
    if values != normalized:
        raise StudioWorkerTaskError(
            "allowed_paths must be canonical, unique, and sorted"
        )
    return values


def _argv(values: object) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values or len(values) > 64:
        raise StudioWorkerTaskError("test_argv must contain 1..64 fixed arguments")
    for index, value in enumerate(values):
        _nonblank(value, f"test_argv[{index}]", _MAX_ARG_CHARS)
    return values


def _safe_relpath(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise StudioWorkerTaskError(
            "editable paths must be non-empty POSIX relative paths"
        )
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix():
        raise StudioWorkerTaskError(
            "editable paths must be canonical POSIX relative paths"
        )
    if any(part in {"", ".", ".."} for part in path.parts):
        raise StudioWorkerTaskError(
            "editable paths may not contain traversal components"
        )
    if path.parts[0] == ".git":
        raise StudioWorkerTaskError("editable paths may not target .git")
    return value


def _nonblank(value: object, field: str, max_chars: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StudioWorkerTaskError(f"{field} must be non-blank text")
    if value != value.strip():
        raise StudioWorkerTaskError(f"{field} must not have surrounding whitespace")
    if len(value) > max_chars:
        raise StudioWorkerTaskError(f"{field} exceeds {max_chars} characters")
    return value


def _bounded_int(value: object, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StudioWorkerTaskError(f"{field} must be an integer")
    if value < minimum or value > maximum:
        raise StudioWorkerTaskError(
            f"{field} must be between {minimum} and {maximum}"
        )
    return value
