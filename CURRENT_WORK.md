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
- **Pull request:** `#158`.

## Customer outcome

Make the executable MIRA Studio path fail closed unless it is bound to an exact durable compute lease, a verified/approved healthy unlocked worker, allowed data classification/capabilities and fresh trusted host-isolation evidence. The customer still supplies ordinary-language product intent; MIRA owns the engineering plumbing.

The resulting short-lived permit is cryptographically bound to the complete Studio worker manifest and complete restricted-runtime policy so changes to repository/base/branch, editable paths, tests, model endpoint/model, budgets, customer objective, capability/isolation requirements, freshness limits or network policy invalidate admission before execution.

## Prior packet closeout

`M2-M1-041` / PR #157 merged to `main` at `41550d60c92e692528b3de4b1deae6020d405011`. Exact post-merge CI #626 completed successfully on that exact SHA. The executable Studio worker/intake bridge is therefore integration-verified at its stated evidence ceiling. Host-level restricted runtime containment was explicitly left unverified and is the dependency addressed here.

## Existing authority reused

- `ComputeJobView` / durable compute control plane remains job, lease, cancellation and capability-requirement authority.
- `WorkerRegistryView` remains worker identity, principal/runtime binding, approval, data-classification, local-compute policy, health/availability and interactive-lock authority.
- M2-M1-025 remains the authenticated worker/channel boundary; this packet does not mint generic API authority or trust LAN presence.
- M2-M1-028/029 remain deterministic safety/lifecycle policy boundaries.
- `WorkerManifest` remains controller-owned Studio execution policy and the lower `run_manifest()` worker remains isolated Git/model/test execution machinery.

No second scheduler, worker registry, authentication service, local-compute policy or Studio intake model is introduced.

## Implemented behavior

- `ops/studio_restricted_runtime.py` adds trusted `RuntimeIsolationEvidence`, controller-owned `RestrictedRuntimePolicy`, short-lived `StudioExecutionPermit`, exact whole-manifest and whole-policy SHA-256 binding, deterministic admission validation and a revalidating `run_authorized_manifest()` entrypoint.
- Admission requires an active unexpired durable lease for the exact worker, correct operation/service, no cancellation request, optional draft-input binding, verified/approved worker identity, local compute enabled, ready/busy availability, healthy state, no interactive lock, allowed data classification and complete capabilities.
- Worker identity/health/lock evidence is freshness-bounded by an explicit heartbeat-age policy; future or stale heartbeat state fails closed.
- Trusted isolation evidence must match worker/principal/runtime identity, use an allowlisted attestation kind, be fresh/not future-dated, prove restricted identity/filesystem/process-tree/credential/resource isolation, and match explicit network-mode policy.
- Permit expiry is bounded by both controller TTL and durable lease expiry. Permit integrity is independently rechecked before execution.
- Revalidation accepts legitimate newer heartbeat/isolation observations while requiring the permit's original manifest/policy/job/lease/worker/principal/runtime/draft/isolation provenance bindings to remain valid.
- Permit material contains only logical IDs/digests/timestamps/attestation kind. It excludes repository path, model endpoint/model, tests, credentials, hostnames/IPs/MACs/hardware IDs and raw source/customer text.
- `ops/studio_execution_bridge.py` provides `run_review_ready_intake_restricted()` as the controller-facing safe path: review-ready intake → manifest → permit → revalidation → lower worker.
- Direct tests cover the admission policy and the bridge composition, including proof that failed admission never enters the lower worker.

## Owned implementation surfaces

- `ops/studio_restricted_runtime.py`
- `ops/studio_execution_bridge.py`
- `tests/test_studio_restricted_runtime.py`
- `tests/test_studio_execution_bridge.py`
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

## Semantic/adversarial review

Review found and corrected three security/integrity defects before closeout:

1. Stored worker health/lock state initially had no heartbeat freshness gate. Admission now rejects stale/future heartbeat evidence and invalid identity-verification/heartbeat ordering.
2. Permit revalidation originally reconstructed a permit using the original issue time plus current worker evidence, which could falsely reject a legitimate newer heartbeat. Revalidation now checks current context independently and validates the original permit material/integrity directly.
3. Permit binding initially carried only the runtime policy ID. It now binds the complete controller-owned restricted-runtime policy with `policy_sha256`, so a changed capability, freshness, network or draft-binding policy invalidates the permit.

Bridge composition also received a direct test proving permit issuance precedes the authorized lower-worker entrypoint.

No further blocking semantic defect was identified in the bounded packet review. The durable compute job already retains its input SHA-256; this packet binds the exact content-derived Studio draft ID plus the complete worker manifest and does not invent a second artifact-store contract.

## Verification evidence

- PR #158 is open as the packet draft PR.
- CI #632 passed end to end on exact implementation head `3c8bcb86e1e40c000f69e33cbef5ab14ab135855` after the semantic fixes and adversarial tests.
- Passing gates included compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android unit/proof/provenance gates, Python unit tests and Workspace Apps Script tests.
- This documentation closeout changes the branch head, so one final exact-head CI run remains mandatory before merge.

## Acceptance criteria

1. Whole-manifest digest binds every `WorkerManifest` field. **PASS — implementation + CI #632.**
2. Whole-policy digest and permit bind exact policy/job/lease/worker/principal/runtime/draft/manifest/isolation provenance. **PASS — implementation + CI #632.**
3. Lease mismatch/cancellation/expiry fail closed. **PASS — adversarial tests + CI #632.**
4. Worker identity/approval/local mode/health/availability/interactive lock and heartbeat freshness fail closed. **PASS — adversarial tests + CI #632.**
5. Data-classification/capability mismatch fail closed. **PASS — adversarial tests + CI #632.**
6. Isolation identity/attestation/freshness/property/network mismatches fail closed. **PASS — adversarial tests + CI #632.**
7. Manifest or runtime-policy mutation and permit expiry prevent lower-worker entry. **PASS — adversarial tests + CI #632.**
8. Controller-facing Studio bridge gates execution through permit issuance/revalidation before lower-worker entry. **PASS — direct composition test + CI #632.**
9. Permit excludes private endpoint/path/credential material. **PASS — direct privacy test + CI #632.**
10. Existing full repository CI remains green on implementation head. **PASS — CI #632.**
11. Exact documentation-head + post-merge CI/readback complete before closure. **PENDING.**
12. No live host/LM Studio/private-hardware containment claim from synthetic CI. **PRESERVED.**

## Concurrency state

At packet start, remote `main` was `41550d60c92e692528b3de4b1deae6020d405011`. Old draft PR #135 for Sheets control-surface work remains stale relative to current main and does not own this packet's `ops/studio_*` or direct test surfaces. No `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md` or monolithic ownership-manifest edit is required because existing IDs and repository ownership boundaries already cover this work.

## Pre-merge capture audit

CAPTURE AUDIT COMPLETE

- All implementation changes remain inside existing `LOCAL-001` / `LOCAL-INTEGRATIONS` and `STUDIO-001` / `DEV-004` scope.
- The heartbeat-freshness, permit-revalidation and full-policy-binding repairs are defects/integrity requirements inside this packet, not new product scope.
- Live host attestation and provider/OS-specific containment remain explicitly deferred evidence and are not claimed by CI.
- No unrelated feature work was admitted.

## Evidence ceiling

CI proves deterministic admission/binding, permit integrity, freshness/policy enforcement, bridge composition and repository compatibility. It does not prove that a private machine is actually sandboxed, that LM Studio is loaded, or that generated code executed on user hardware under a restricted OS identity. A live host/runtime adapter must later produce trustworthy isolation evidence from the actual containment boundary before MIRA may claim production-safe local execution.

## Exact next action / resume point

1. Require final exact-head CI green on this documentation-closeout commit.
2. Re-read current remote `main`, PR #158 exact head/mergeability and concurrent changed-file overlap.
3. If compatible, mark PR #158 ready and merge only with exact expected-head protection.
4. Read back the exact merged `main` SHA and require post-merge CI success before closing M2-M1-042.
5. Select the next Studio/local-compute child from current Git state rather than chat history.
