# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-043` — Studio durable compute dispatch

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `STUDIO-001`, `DEV-004`, `LOCAL-001`, `PROVIDER-001`.
- **Related invariants/features:** `STORE-001`, `API-001`, `SOURCE-001`, `RECOVERY-002`, `DEV-008`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-043-studio-compute-dispatch`.
- **Base SHA:** `8be20acff6dec61d3367c9258eb84d553842625d`.
- **Packet:** `docs/work-packets/M2-M1-043.md`.

## Closed parent packet

`M2-M1-042` / PR #158 merged at exact `main` SHA `8be20acff6dec61d3367c9258eb84d553842625d`. Post-merge CI #635 / run `34717164107` completed successfully on that exact merge SHA. M2-M1-042 is therefore **integration verified** at its stated deterministic restricted-runtime admission ceiling. It does **not** claim live private host containment, private LM Studio or physical-worker execution.

## Customer outcome

Connect ordinary-language MIRA Studio work to the already-built durable compute fabric so MIRA, not the customer, owns job creation, worker routing, exact leasing, start/terminal lifecycle and restricted-runtime execution plumbing.

The customer must not supply job IDs, lease IDs, worker IDs, Git plumbing, model endpoint details or machine selection. Worker/runtime choice remains capability-, policy-, privacy-, availability- and evidence-driven.

## Why this packet is next

The merged chain already provides Studio intake, a real bounded local worker, durable compute jobs/leasing, durable worker state, routing, secure-channel trust, safety/lifecycle policy, model-profile evidence and restricted-runtime admission.

The remaining vertical gap is composition:

1. M2-M1-041 can execute one controller-owned `WorkerManifest`.
2. M2-M1-042 can authorize execution only when a matching durable job is **already leased** to the exact worker.
3. Nothing yet turns one review-ready Studio draft into a durable job, routes that job to an eligible durable worker, acquires/starts the lease and reconciles worker success/failure into durable compute state.

## Implementation-discovered hard dependency

`ComputeJobControlPlane.lease_next()` is a worker-pull scheduler that selects the globally highest-ranked eligible queued job. Studio dispatch is controller-routed around one exact Studio job. Calling `lease_next()` after routing can lease a different queued job.

M2-M1-043 therefore first adds a replay-safe `lease_job()`-style exact-job primitive to the existing compute control plane. This is an integrity prerequisite inside the existing scheduler authority, not a second scheduler.

## Existing authority reused

- `ComputeJobControlPlane`: durable job/lease/start/cancel/pause/resume/fail/complete/result provenance authority.
- `WorkerRegistryService`: durable worker identity/state authority.
- `worker_registry_view_to_advertisement()` + `project_worker_candidate()`: worker identity/freshness projection authority.
- `route_runtime()`: deterministic policy/capability runtime selection authority.
- external `ProviderCapabilitySnapshot`: provider capability/authorization evidence.
- `manifest_from_review_ready_intake()`: customer-intent → controller execution-manifest binding.
- M2-M1-042 `RestrictedRuntimePolicy` / permit gate: pre-execution restricted-runtime authority.
- `studio_local_worker`: bounded Git/model/test execution primitive.

No second scheduler, router, registry, model selector, approval system or activation executor is introduced.

## Expected owned surfaces

- `mira/command_sequencer.py`
- `ops/studio_compute_dispatch.py`
- `tests/test_compute_control_plane.py`
- `tests/test_studio_compute_dispatch.py`
- `docs/work-packets/M2-M1-043.md`
- branch-local `CURRENT_WORK.md`

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

`STUDIO-001` / `DEV-004` already own bounded Studio implementation and `LOCAL-001` / `PROVIDER-001` already own scoped local execution plus evidence-driven runtime routing. `STORE-001`, `API-001`, `SOURCE-001` and `RECOVERY-002` preserve durable-state, authority/readback and failure-isolation invariants.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` is the existing accepted work anchor. Its old global class remains `LATER`, but the product owner explicitly reprioritized the compute-fabric/Studio direction in M2-M1-021 and that durable packet chain has continued through M2-M1-042. This packet continues that already-active bounded vertical rather than manufacturing a duplicate work ID.

### `ROADMAP.md`

Local/self-hosted execution remains optional advanced infrastructure and must not become a Standard Personal prerequisite. This packet composes optional compute behind existing product contracts only; it does not make private hardware mandatory for MIRA Studio or ordinary Personal MIRA.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Reuses `STUDIO-001`, `DEV-004`, `LOCAL-001`, `PROVIDER-001`, and `LOCAL-INTEGRATIONS`.
- Exact-job leasing is an integrity prerequisite inside the existing M2-M1-024 durable compute control plane, not a new feature vertical.
- No private deployment binding or live-host behavior is silently admitted.
- No duplicate feature/work ID is added.

### Direction result

ALIGNED

## Acceptance criteria

1. Add exact-job durable leasing without changing `lease_next()` semantics.
2. Exact-job lease is replay-safe, capability-bound, attempt-bounded and collision-safe.
3. Review-ready Studio draft deterministically creates/replays one durable compute job bound to exact draft + manifest digest.
4. Worker selection reads durable worker state and external provider capability evidence through existing projection/router contracts.
5. Missing/ambiguous worker mapping or any policy/capability/freshness/health/lock failure blocks before lease/execution.
6. Exact submitted Studio job is leased and started for the exact selected worker.
7. Restricted-runtime admission remains mandatory before lower-worker entry.
8. Success completes the durable job with result digest + worker/runtime provenance.
9. Bounded failure records durable failure without fabricating success.
10. Replay does not duplicate job, lease attempts or terminal result.
11. Worker success grants no merge/push/activation/publication/install authority.
12. Full exact-head CI and exact post-merge CI/readback required before closure.
13. No live private worker/host/model/provider claim from synthetic CI.

## Evidence state

- Parent M2-M1-042: **integration verified** through exact post-merge CI #635.
- M2-M1-043 branch created from exact verified `main` `8be20acff6dec61d3367c9258eb84d553842625d`.
- Packet scope/capture audit: **durably checkpointed**.
- Implementation: **not yet verified**.

## Exact next action / resume point

1. Add and directly test exact-job leasing in `ComputeJobControlPlane` while preserving `lease_next()` behavior.
2. Implement `ops/studio_compute_dispatch.py` over existing worker registry, router, compute control plane, restricted-runtime admission and Studio local worker.
3. Add adversarial dispatch/lifecycle tests.
4. Open draft PR and require exact-head repository CI.
5. Perform semantic/adversarial review + capture audit.
6. Re-read current `main` and concurrent overlap, then merge only with expected-head protection if green.
7. Require post-merge exact-SHA CI before closure and next-work selection.
