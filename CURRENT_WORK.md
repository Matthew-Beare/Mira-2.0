# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-044` — Portable Studio worker task

- **Primary work:** `LOCAL-INTEGRATIONS`.
- **Primary features:** `STUDIO-001`, `DEV-004`, `LOCAL-001`, `PROVIDER-001`.
- **Related invariants/features:** `SOURCE-001`, `STORE-001`, `API-001`, `RECOVERY-002`, `DEV-008`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-044-portable-studio-worker-task`.
- **Base SHA:** `be73fd5eb987841be37fb050bc383dfd6f660606`.
- **Packet:** `docs/work-packets/M2-M1-044.md`.

## Closed parent packet

`M2-M1-043` / PR #159 merged to `main` at `be73fd5eb987841be37fb050bc383dfd6f660606`. Exact pre-merge CI #643 passed on PR head `298a2fa1dc00d5945bb2098989082a34fd17e5dc`, and exact post-merge push CI #644 / run `34724981182` passed on the merge SHA. Studio durable compute dispatch is therefore integration-verified at its deterministic evidence ceiling. No live private worker, private host containment, LM Studio or physical hardware execution is inferred from that proof.

## Customer outcome

Advance the executable Studio/local-compute vertical toward a real outbound private worker without putting private repository paths, model endpoints or machine bindings into controller-owned/public work material.

A selected worker must be able to receive one portable, secret-free Studio implementation task, resolve it against worker-local private bindings, and deterministically produce the exact existing `WorkerManifest` consumed by the restricted Studio execution path. The customer still supplies ordinary-language intent rather than Git paths, model endpoints or machine plumbing.

## Why this packet is required

The current `WorkerManifest` is intentionally executable but contains physical `repo_path`, `model_base_url` and concrete model identity. M2-M1-043 can compose that manifest in-process, but a real outbound worker cannot safely require the public/controller plane to know or persist its private filesystem/model endpoint binding.

M2-M1-025 explicitly deferred a live worker transport. M2-M1-026 explicitly deferred private-runner binding/isolation. M2-M1-042 binds restricted-runtime permits to exact executable manifests. Before an authenticated outbound worker agent can be added, MIRA needs a transport-safe task identity that preserves customer/controller semantics while allowing those physical bindings to remain worker-local.

This is an implementation prerequisite inside existing `LOCAL-INTEGRATIONS` / `LOCAL-001` / `STUDIO-001`, not a new product vertical.

## Scope

1. Define one strict portable Studio worker-task contract containing customer objective identity plus controller-owned source/model logical binding IDs, exact base SHA/branch, allowlisted paths, fixed test argv and execution budgets.
2. Exclude physical repo paths, hostnames/IPs, model endpoints, credentials, secrets and private machine identity from the portable task.
3. Define a worker-local private binding contract that maps logical source/model-profile IDs to the existing executable `repo_path`, loopback model endpoint and concrete model identity.
4. Deterministically bind one portable task plus exact private bindings into the existing validated `WorkerManifest` without changing customer intent or controller-owned code/test/budget policy.
5. Hash/serialize the portable task deterministically for durable job/artifact identity and later outbound transport.
6. Fail closed on malformed logical IDs, unsafe/noncanonical paths, invalid branch/base/task material, non-loopback model bindings, binding-ID mismatch, duplicate/missing private bindings, or any attempt to serialize private binding material as the portable task.
7. Add direct adversarial tests and explicit code ownership.
8. Do not add network listeners, real credentials, private hosts, live LM Studio calls, provider mutation, merge/push/activation authority or a second scheduler/router/registry.

## Acceptance criteria

1. Review-ready Studio intent can be projected into a deterministic portable task without physical worker binding material.
2. Portable task canonical serialization/hash is input-order independent where semantics are sets and changes when any execution-relevant field changes.
3. Worker-local bindings resolve the portable task into an exact valid existing `WorkerManifest`.
4. Physical repo/model endpoint/concrete-model fields never appear in portable serialization or digest input material.
5. Binding lookup fails closed on missing/duplicate/mismatched logical IDs.
6. Model endpoint remains loopback-only through the existing `WorkerManifest` validation boundary.
7. Existing Studio customer semantics, exact source SHA/branch, allowlisted paths, fixed tests and budgets survive the bind unchanged.
8. Existing full repository CI remains green; exact-head and post-merge readback are mandatory before closure.
9. No live private worker/host/model claim is made from synthetic CI.

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

This packet advances existing `STUDIO-001`, `DEV-004`, `LOCAL-001` and `PROVIDER-001`. `STUDIO-001` already owns bounded custom feature/workflow execution, `LOCAL-001` owns optional local-service/runtime integration without blanket LAN trust, and `PROVIDER-001` owns capability-based runtime selection. No new semantic feature ID is required.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` is the existing accepted work lane for optional local execution/integration. M2-M1-043 proved durable dispatch but its executable manifest still assumes physical worker bindings are known in-process. A portable task/local-binding seam is a hard implementation prerequisite for the already-accepted authenticated-outbound private-worker direction, so it outranks unrelated deferred local-service adapters without turning local compute into a Standard dependency.

### `ROADMAP.md`

The default Personal product remains independent of local infrastructure. This packet affects only the Advanced/optional local-compute path and preserves the roadmap invariant that provider-neutral API/Authority semantics are not replaced by private deployment details.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- The portable worker-task requirement is implementation-discovered inside existing `LOCAL-INTEGRATIONS`, `LOCAL-001`, `STUDIO-001` and `DEV-004`.
- No new user-visible vertical or semantic feature is introduced.
- Physical worker bindings remain private deployment configuration and are deliberately excluded from public/canonical transport artifacts.
- Authenticated outbound transport itself remains the next bounded integration step and is not silently absorbed here.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement the portable task + worker-local binding module with strict deterministic validation.
2. Add adversarial tests for privacy, task identity, binding mismatch and exact manifest projection.
3. Register bounded production ownership.
4. Run full exact-head CI and repair only packet-owned failures.
5. Review the completed diff for private-data leakage and semantic drift before merge.
6. Merge only after exact-head green evidence and post-merge exact-SHA CI/readback.

## Evidence ceiling

Synthetic tests can prove the portable task contract, privacy boundary and deterministic projection into the existing executable manifest. They cannot prove a private worker transport, real secret storage, real host isolation, LM Studio availability, private GPU execution or physical deployment. Those require later live evidence.