"""Restricted-runtime admission gate for MIRA Studio local execution.

This module composes existing durable compute-job and worker-registry truth with
trusted host-isolation evidence. It issues a short-lived, secret-free permit
bound to one exact Studio worker manifest. It does not create an OS sandbox,
authenticate a network peer, execute a compute job, or make worker-supplied
isolation claims trustworthy by itself.

A live adapter must construct RuntimeIsolationEvidence from the actual trusted
runtime/host boundary. Production Studio execution should enter through
run_authorized_manifest(), not call the lower-level local worker directly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re

from mira.command_sequencer import ComputeJobView
from mira.service_state import WorkerRegistryView
from ops.studio_local_worker import WorkerManifest, WorkerResult, run_manifest


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_NETWORK_MODES = frozenset({"none", "loopback_only"})


class RestrictedRuntimeError(RuntimeError):
    """Fail-closed Studio restricted-runtime admission error."""


@dataclass(frozen=True)
class RuntimeIsolationEvidence:
    """Trusted observation of one runtime's host-enforced isolation properties."""

    worker_id: str
    principal_id: str
    runtime_id: str
    observed_at: str
    attestation_kind: str
    restricted_identity: bool
    filesystem_isolation: bool
    process_tree_containment: bool
    credential_isolation: bool
    resource_limits_enforced: bool
    network_mode: str
    provenance_sha256: str

    def __post_init__(self) -> None:
        _token(self.worker_id, "worker_id")
        _token(self.principal_id, "principal_id")
        _token(self.runtime_id, "runtime_id")
        _utc(self.observed_at, "observed_at")
        _token(self.attestation_kind, "attestation_kind")
        for field_name in (
            "restricted_identity",
            "filesystem_isolation",
            "process_tree_containment",
            "credential_isolation",
            "resource_limits_enforced",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise RestrictedRuntimeError(f"{field_name} must be boolean")
        if self.network_mode not in _NETWORK_MODES:
            raise RestrictedRuntimeError("network_mode is unsupported")
        _sha256(self.provenance_sha256, "provenance_sha256")


@dataclass(frozen=True)
class RestrictedRuntimePolicy:
    """Controller-owned requirements for one class of Studio execution."""

    policy_id: str
    required_operation_id: str
    required_service_id: str
    required_worker_capabilities: tuple[str, ...]
    allowed_attestation_kinds: tuple[str, ...]
    max_evidence_age_seconds: int
    max_worker_heartbeat_age_seconds: int
    permit_ttl_seconds: int
    required_network_mode: str = "loopback_only"
    bind_job_input_to_draft: bool = True

    def __post_init__(self) -> None:
        _token(self.policy_id, "policy_id")
        _token(self.required_operation_id, "required_operation_id")
        _token(self.required_service_id, "required_service_id")
        _sorted_tokens(
            self.required_worker_capabilities,
            "required_worker_capabilities",
            allow_empty=False,
        )
        _sorted_tokens(
            self.allowed_attestation_kinds,
            "allowed_attestation_kinds",
            allow_empty=False,
        )
        _positive_int(
            self.max_evidence_age_seconds,
            "max_evidence_age_seconds",
            upper=86_400,
        )
        _positive_int(
            self.max_worker_heartbeat_age_seconds,
            "max_worker_heartbeat_age_seconds",
            upper=86_400,
        )
        _positive_int(self.permit_ttl_seconds, "permit_ttl_seconds", upper=3_600)
        if self.required_network_mode not in _NETWORK_MODES:
            raise RestrictedRuntimeError("required_network_mode is unsupported")
        if not isinstance(self.bind_job_input_to_draft, bool):
            raise RestrictedRuntimeError("bind_job_input_to_draft must be boolean")


@dataclass(frozen=True)
class StudioExecutionPermit:
    """Short-lived secret-free admission receipt bound to exact controller policy."""

    permit_id: str
    policy_id: str
    policy_sha256: str
    job_id: str
    lease_id: str
    worker_id: str
    principal_id: str
    runtime_id: str
    draft_id: str
    manifest_sha256: str
    isolation_provenance_sha256: str
    attestation_kind: str
    issued_at: str
    expires_at: str

    def __post_init__(self) -> None:
        _sha256(self.permit_id, "permit_id")
        _sha256(self.policy_sha256, "policy_sha256")
        for field_name in (
            "policy_id",
            "job_id",
            "lease_id",
            "worker_id",
            "principal_id",
            "runtime_id",
            "draft_id",
            "attestation_kind",
        ):
            _token(getattr(self, field_name), field_name)
        _sha256(self.manifest_sha256, "manifest_sha256")
        _sha256(self.isolation_provenance_sha256, "isolation_provenance_sha256")
        issued = _utc(self.issued_at, "issued_at")
        expires = _utc(self.expires_at, "expires_at")
        if expires <= issued:
            raise RestrictedRuntimeError("permit expiry must be after issuance")


def manifest_sha256(manifest: WorkerManifest) -> str:
    """Hash every controller-owned execution field in canonical form."""

    if not isinstance(manifest, WorkerManifest):
        raise RestrictedRuntimeError("manifest must be a WorkerManifest")
    manifest.validate()
    return _object_sha256(asdict(manifest))


def runtime_policy_sha256(policy: RestrictedRuntimePolicy) -> str:
    """Hash the complete controller-owned restricted-runtime policy."""

    if not isinstance(policy, RestrictedRuntimePolicy):
        raise RestrictedRuntimeError("policy must be RestrictedRuntimePolicy")
    return _object_sha256(asdict(policy))


def issue_execution_permit(
    *,
    manifest: WorkerManifest,
    job: ComputeJobView,
    worker: WorkerRegistryView,
    isolation: RuntimeIsolationEvidence,
    policy: RestrictedRuntimePolicy,
    now: str,
) -> StudioExecutionPermit:
    """Fail closed unless durable lease/worker state and host isolation all agree."""

    context = _validate_context(
        manifest=manifest,
        job=job,
        worker=worker,
        isolation=isolation,
        policy=policy,
        now=now,
    )
    issued = context["now"]
    lease_expires = context["lease_expires"]
    expires = min(
        issued + timedelta(seconds=policy.permit_ttl_seconds),
        lease_expires,
    )
    if expires <= issued:
        raise RestrictedRuntimeError("compute lease expires before permit can be issued")

    material = {
        "policy_id": policy.policy_id,
        "policy_sha256": context["policy_sha256"],
        "job_id": job.job_id,
        "lease_id": job.lease_id,
        "worker_id": worker.worker_id,
        "principal_id": worker.principal_id,
        "runtime_id": worker.runtime_id,
        "draft_id": manifest.draft_id,
        "manifest_sha256": context["manifest_sha256"],
        "isolation_provenance_sha256": isolation.provenance_sha256,
        "attestation_kind": isolation.attestation_kind,
        "issued_at": _utc_text(issued),
        "expires_at": _utc_text(expires),
    }
    permit_id = _object_sha256(material)
    return StudioExecutionPermit(permit_id=permit_id, **material)


def validate_execution_permit(
    *,
    permit: StudioExecutionPermit,
    manifest: WorkerManifest,
    job: ComputeJobView,
    worker: WorkerRegistryView,
    isolation: RuntimeIsolationEvidence,
    policy: RestrictedRuntimePolicy,
    now: str,
) -> None:
    """Revalidate current state immediately before local execution."""

    if not isinstance(permit, StudioExecutionPermit):
        raise RestrictedRuntimeError("permit must be a StudioExecutionPermit")
    context = _validate_context(
        manifest=manifest,
        job=job,
        worker=worker,
        isolation=isolation,
        policy=policy,
        now=now,
    )
    current = context["now"]
    issued = _utc(permit.issued_at, "permit.issued_at")
    expires = _utc(permit.expires_at, "permit.expires_at")
    if current < issued:
        raise RestrictedRuntimeError("current time predates permit issuance")
    if current > expires:
        raise RestrictedRuntimeError("Studio execution permit has expired")

    expected_fields = {
        "policy_id": policy.policy_id,
        "policy_sha256": context["policy_sha256"],
        "job_id": job.job_id,
        "lease_id": job.lease_id,
        "worker_id": worker.worker_id,
        "principal_id": worker.principal_id,
        "runtime_id": worker.runtime_id,
        "draft_id": manifest.draft_id,
        "manifest_sha256": context["manifest_sha256"],
        "isolation_provenance_sha256": isolation.provenance_sha256,
        "attestation_kind": isolation.attestation_kind,
    }
    for field_name, expected in expected_fields.items():
        if getattr(permit, field_name) != expected:
            raise RestrictedRuntimeError(
                f"Studio execution permit field mismatch: {field_name}"
            )

    if expires > context["lease_expires"]:
        raise RestrictedRuntimeError("Studio execution permit exceeds current lease expiry")
    if expires > issued + timedelta(seconds=policy.permit_ttl_seconds):
        raise RestrictedRuntimeError("Studio execution permit exceeds current policy TTL")

    material = {
        "policy_id": permit.policy_id,
        "policy_sha256": permit.policy_sha256,
        "job_id": permit.job_id,
        "lease_id": permit.lease_id,
        "worker_id": permit.worker_id,
        "principal_id": permit.principal_id,
        "runtime_id": permit.runtime_id,
        "draft_id": permit.draft_id,
        "manifest_sha256": permit.manifest_sha256,
        "isolation_provenance_sha256": permit.isolation_provenance_sha256,
        "attestation_kind": permit.attestation_kind,
        "issued_at": permit.issued_at,
        "expires_at": permit.expires_at,
    }
    if permit.permit_id != _object_sha256(material):
        raise RestrictedRuntimeError("Studio execution permit integrity check failed")


def run_authorized_manifest(
    *,
    permit: StudioExecutionPermit,
    manifest: WorkerManifest,
    job: ComputeJobView,
    worker: WorkerRegistryView,
    isolation: RuntimeIsolationEvidence,
    policy: RestrictedRuntimePolicy,
    now: str,
) -> WorkerResult:
    """Revalidate a permit and only then enter the bounded Studio local worker."""

    validate_execution_permit(
        permit=permit,
        manifest=manifest,
        job=job,
        worker=worker,
        isolation=isolation,
        policy=policy,
        now=now,
    )
    return run_manifest(manifest)


def _validate_context(
    *,
    manifest: WorkerManifest,
    job: ComputeJobView,
    worker: WorkerRegistryView,
    isolation: RuntimeIsolationEvidence,
    policy: RestrictedRuntimePolicy,
    now: str,
) -> dict[str, object]:
    if not isinstance(job, ComputeJobView):
        raise RestrictedRuntimeError("job must be a ComputeJobView")
    if not isinstance(worker, WorkerRegistryView):
        raise RestrictedRuntimeError("worker must be a WorkerRegistryView")
    if not isinstance(isolation, RuntimeIsolationEvidence):
        raise RestrictedRuntimeError("isolation must be RuntimeIsolationEvidence")
    if not isinstance(policy, RestrictedRuntimePolicy):
        raise RestrictedRuntimeError("policy must be RestrictedRuntimePolicy")
    fingerprint = manifest_sha256(manifest)
    policy_digest = runtime_policy_sha256(policy)
    now_dt = _utc(now, "now")

    if job.operation_id != policy.required_operation_id:
        raise RestrictedRuntimeError("compute job operation is not authorized for Studio")
    if job.service_id != policy.required_service_id:
        raise RestrictedRuntimeError("compute job service is not authorized for Studio")
    if job.state not in {"leased", "running"}:
        raise RestrictedRuntimeError("compute job must hold an active lease")
    if job.cancel_requested:
        raise RestrictedRuntimeError("cancel-requested compute job cannot execute")
    if not job.lease_id or not job.lease_worker_id or not job.lease_expires_at:
        raise RestrictedRuntimeError("compute job lease evidence is incomplete")
    if job.lease_worker_id != worker.worker_id:
        raise RestrictedRuntimeError("compute job is leased to a different worker")
    lease_expires = _utc(job.lease_expires_at, "job.lease_expires_at")
    if lease_expires <= now_dt:
        raise RestrictedRuntimeError("compute job lease is expired")
    if policy.bind_job_input_to_draft and job.input_artifact_id != manifest.draft_id:
        raise RestrictedRuntimeError("compute job input is not bound to the Studio draft")

    if worker.identity_state != "verified":
        raise RestrictedRuntimeError("compute worker identity is not verified")
    if worker.approval_state != "approved":
        raise RestrictedRuntimeError("compute worker is not explicitly approved")
    if worker.local_compute_mode == "off":
        raise RestrictedRuntimeError("local compute policy is off")
    if worker.availability not in {"ready", "busy"}:
        raise RestrictedRuntimeError("compute worker is not execution-available")
    if worker.health != "healthy":
        raise RestrictedRuntimeError("compute worker is not healthy")
    if worker.interactive_lock:
        raise RestrictedRuntimeError("interactive lock blocks Studio execution")

    identity_verified = _utc(
        worker.identity_verified_at,
        "worker.identity_verified_at",
    )
    heartbeat = _utc(worker.heartbeat_at, "worker.heartbeat_at")
    if identity_verified > heartbeat:
        raise RestrictedRuntimeError("worker heartbeat predates identity verification")
    if identity_verified > now_dt:
        raise RestrictedRuntimeError("worker identity verification cannot be from the future")
    if heartbeat > now_dt:
        raise RestrictedRuntimeError("worker heartbeat cannot be from the future")
    if (
        now_dt - heartbeat
    ).total_seconds() > policy.max_worker_heartbeat_age_seconds:
        raise RestrictedRuntimeError("worker heartbeat is stale")

    if job.data_classification not in set(worker.allowed_data_classifications):
        raise RestrictedRuntimeError("worker is not approved for the job data classification")

    worker_caps = set(worker.runtime_capabilities)
    missing_job_caps = set(job.required_capabilities) - worker_caps
    if missing_job_caps:
        raise RestrictedRuntimeError(
            "worker lacks job capabilities: " + ", ".join(sorted(missing_job_caps))
        )
    missing_policy_caps = set(policy.required_worker_capabilities) - worker_caps
    if missing_policy_caps:
        raise RestrictedRuntimeError(
            "worker lacks restricted-runtime capabilities: "
            + ", ".join(sorted(missing_policy_caps))
        )

    if isolation.worker_id != worker.worker_id:
        raise RestrictedRuntimeError("isolation evidence worker identity mismatch")
    if isolation.principal_id != worker.principal_id:
        raise RestrictedRuntimeError("isolation evidence principal identity mismatch")
    if isolation.runtime_id != worker.runtime_id:
        raise RestrictedRuntimeError("isolation evidence runtime identity mismatch")
    if isolation.attestation_kind not in set(policy.allowed_attestation_kinds):
        raise RestrictedRuntimeError("isolation attestation kind is not allowed")
    observed = _utc(isolation.observed_at, "isolation.observed_at")
    if observed > now_dt:
        raise RestrictedRuntimeError("isolation evidence cannot be from the future")
    if (now_dt - observed).total_seconds() > policy.max_evidence_age_seconds:
        raise RestrictedRuntimeError("isolation evidence is stale")
    for field_name in (
        "restricted_identity",
        "filesystem_isolation",
        "process_tree_containment",
        "credential_isolation",
        "resource_limits_enforced",
    ):
        if not getattr(isolation, field_name):
            raise RestrictedRuntimeError(
                f"required isolation property is absent: {field_name}"
            )
    if isolation.network_mode != policy.required_network_mode:
        raise RestrictedRuntimeError("runtime network isolation does not match policy")

    return {
        "now": now_dt,
        "lease_expires": lease_expires,
        "manifest_sha256": fingerprint,
        "policy_sha256": policy_digest,
    }


def _object_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _token(value: object, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise RestrictedRuntimeError(f"{field} must be a bounded token")
    return value


def _sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise RestrictedRuntimeError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _sorted_tokens(values: object, field: str, *, allow_empty: bool) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise RestrictedRuntimeError(f"{field} must be a tuple")
    normalized = tuple(sorted({_token(value, field) for value in values}))
    if normalized != values or (not allow_empty and not normalized):
        raise RestrictedRuntimeError(f"{field} must be sorted, unique, and non-empty")
    return normalized


def _positive_int(value: object, field: str, *, upper: int) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 1
        or value > upper
    ):
        raise RestrictedRuntimeError(f"{field} must be an integer from 1 through {upper}")
    return value


def _utc(value: object, field: str) -> datetime:
    if not isinstance(value, str) or value != value.strip() or not value:
        raise RestrictedRuntimeError(f"{field} must be a UTC ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RestrictedRuntimeError(
            f"{field} must be a UTC ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise RestrictedRuntimeError(f"{field} must use UTC")
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
