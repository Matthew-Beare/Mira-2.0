# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-042` — Restricted Studio runtime admission

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `LOCAL-001`, `STUDIO-001`, `DEV-004`, `RECOVERY-002`.
- **Related invariants/features:** `API-001`, `PROVIDER-001`, `SOURCE-001`, `DEV-008`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-042-restricted-studio-runtime`.
- **Base SHA:** `41550d60c92e692528b3de4b1deae6020d405011`.
- **Packet:** `docs/work-packets/M2-M1-042.md`.

## Customer outcome

Make the executable MIRA Studio path fail closed unless it is bound to an exact durable compute lease, a verified/approved healthy unlocked worker, allowed data classification/capabilities and fresh trusted host-isolation evidence. The customer still supplies ordinary-language product intent; MIRA owns the engineering plumbing.

The resulting short-lived permit is cryptographically bound to the complete Studio worker manifest so changes to repository/base/branch, editable paths, tests, model endpoint/model, budgets or customer objective invalidate admission before execution.

## Prior packet closeout

`M2-M1-041` / PR #157 merged to `main` at `41550d60c92e692528b3de4b1deae6020d405011`. Exact post-merge CI #626 completed successfully on that exact SHA. The executable Studio worker/intake bridge is therefore integration-verified at its stated evidence ceiling. Host-level restricted runtime containment was explicitly left unverified and is the dependency addressed here.

## Existing authority reused

- `ComputeJobView` / durable compute control plane remains job, lease, cancellation and capability-requirement authority.
- `WorkerRegistryView` remains worker identity, principal/runtime binding, approval, data-classification, local-compute policy, health/availability and interactive-lock authority.
- M2-M1-025 remains the authenticated worker/channel boundary; this packet does not mint generic API authority or trust LAN presence.
- M2-M1-028/029 remain deterministic safety/lifecycle policy boundaries.
- `WorkerManifest` remains controller-owned Studio execution policy and the lower `run_manifest()` worker remains isolated Git/model/test execution machinery.

No second scheduler, worker registry, authentication service, local-compute policy or Studio intake model is introduced.

## Implemented so far

- `ops/studio_restricted_runtime.py` adds trusted `RuntimeIsolationEvidence`, controller-owned `RestrictedRuntimePolicy`, short-lived `StudioExecutionPermit`, exact whole-manifest SHA-256 binding, deterministic admission validation and a revalidating `run_authorized_manifest()` entrypoint.
- Admission requires an active unexpired durable lease for the exact worker, correct operation/service, no cancellation request, optional draft-input binding, verified/approved worker identity, local compute enabled, ready/busy availability, healthy state, no interactive lock, allowed data classification and complete capabilities.
- Trusted isolation evidence must match worker/principal/runtime identity, use an allowlisted attestation kind, be fresh/not future-dated, prove restricted identity/filesystem/process-tree/credential/resource isolation, and match explicit network-mode policy.
- Permit expiry is bounded by both controller TTL and durable lease expiry.
- Permit material contains only logical IDs/digests/timestamps/attestation kind. It excludes repository path, model endpoint/model, tests, credentials, hostnames/IPs/MACs/hardware IDs and raw source/customer text.
- `ops/studio_execution_bridge.py` now provides `run_review_ready_intake_restricted()` as the controller-facing safe path: review-ready intake → manifest → permit → revalidation → lower worker.
- `tests/test_studio_restricted_runtime.py` covers successful binding, manifest mutation, permit expiry, lease/worker/principal/runtime mismatch, cancellation, health/approval/local-mode/interactive lock, data classification, capabilities, stale/disallowed/incomplete isolation evidence, draft binding, permit privacy and lower-worker non-entry on failed validation.

## Owned implementation surfaces

- `ops/studio_restricted_runtime.py`
- `ops/studio_execution_bridge.py`
- `tests/test_studio_restricted_runtime.py`
- `docs/work-packets/M2-M1-042.md`
- branch-local `CURRENT_WORK.md`

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

`LOCAL-001` already requires scoped local-service permissions/capability verification and rejects blanket LAN trust. `STUDIO-001` / `DEV-004` already own bounded Studio implementation. No new feature vertical is required.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` is the existing accepted work family for local compute/runtime integration. Earlier M2-M1-021 through M2-M1-030 already implemented the compute fabric/control/identity/safety/lifecycle/model-profile foundations. M2-M1-041 explicitly identified restricted worker identity/runtime isolation as the remaining hard gate before production-safe autonomous local Studio execution.

### `ROADMAP.md`

Direction is unchanged: finish the smallest safe infrastructure needed for a usable Studio/local-compute vertical, then prove real provider/runtime execution separately. This packet closes the admission-policy gap without pretending synthetic CI is live host containment.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Reused existing `LOCAL-001` / `LOCAL-INTEGRATIONS` rather than manufacturing a duplicate restricted-runtime feature/work ID.
- Reused `STUDIO-001` / `DEV-004` for the executable Studio path.
- No unrelated product idea entered this packet.
- Provider/OS-specific live isolation attestation remains separate deployment evidence and is not silently absorbed.

### Direction result

ALIGNED

## Acceptance criteria

1. Whole-manifest digest binds every `WorkerManifest` field. **IMPLEMENTED; CI pending.**
2. Permit binds exact policy/job/lease/worker/principal/runtime/draft/manifest/isolation provenance. **IMPLEMENTED; CI pending.**
3. Lease mismatch/cancellation/expiry fail closed. **IMPLEMENTED; CI pending.**
4. Worker identity/approval/local mode/health/availability/interactive lock fail closed. **IMPLEMENTED; CI pending.**
5. Data-classification/capability mismatch fail closed. **IMPLEMENTED; CI pending.**
6. Isolation identity/attestation/freshness/property/network mismatches fail closed. **IMPLEMENTED; CI pending.**
7. Manifest mutation or permit expiry prevents lower-worker entry. **IMPLEMENTED; CI pending.**
8. Controller-facing Studio bridge gates execution through restricted-runtime admission. **IMPLEMENTED; CI pending.**
9. Permit excludes private endpoint/path/credential material. **IMPLEMENTED; CI pending.**
10. Existing full repository CI remains green. **PENDING.**
11. Exact-head + post-merge CI/readback complete before closure. **PENDING.**
12. No live host/LM Studio/private-hardware containment claim from synthetic CI. **PRESERVED.**

## Concurrency state

At packet start, remote `main` was `41550d60c92e692528b3de4b1deae6020d405011`. Old draft PR #135 for Sheets control-surface work remains open and stale relative to current main. It does not own this packet's `ops/studio_*` or direct test surfaces. Shared/high-contention governance is limited to this branch-local `CURRENT_WORK.md`; no `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md` or monolithic ownership-manifest edit is needed because existing IDs/production-root boundaries already cover the work.

## Evidence ceiling

Current branch contains implementation and direct tests but has not yet run PR CI. The local container cannot resolve GitHub, so no fake local-pass claim is made. Verification will use repository CI after the draft PR is opened.

Even after CI passes, evidence proves deterministic admission/binding behavior only. A private host must later produce trustworthy isolation evidence from a real restricted OS/container/service boundary before MIRA may claim live production-safe local execution.

## Exact next action / resume point

1. Open draft PR from `work/m2-m1-042-restricted-studio-runtime` to current `main` to trigger full CI.
2. Inspect exact CI failures and repair only this packet's bounded surfaces.
3. Perform semantic/adversarial review after the first green implementation head.
4. Record final exact-head CI evidence in this file and packet doc.
5. Re-read current `main`, concurrent PRs and overlap before merge.
6. Mark ready and merge only with expected-head protection when exact-head CI is green.
7. Read back exact merged `main` and require post-merge CI before closing M2-M1-042.
