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
- **PR:** `#159`.
- **Packet:** `docs/work-packets/M2-M1-043.md`.

## Closed parent packet

`M2-M1-042` / PR #158 merged at exact `main` SHA `8be20acff6dec61d3367c9258eb84d553842625d`. Post-merge CI #635 / run `34717164107` completed successfully on that exact merge SHA. M2-M1-042 is integration verified only at its deterministic restricted-runtime-admission ceiling. It does not prove private host containment, LM Studio or physical-worker execution.

## Customer outcome

Connect ordinary-language MIRA Studio work to the existing durable compute fabric so MIRA owns job identity, capability requirements, worker routing, exact leasing, lifecycle reconciliation and restricted-runtime plumbing instead of making the customer provide job IDs, lease IDs, worker IDs, Git plumbing, model endpoints or machine selection.

Local execution remains optional, capability- and policy-gated infrastructure. Nothing in this packet makes private hardware a Standard Personal dependency.

## Implemented vertical

- `ComputeJobControlPlane.lease_job()` now leases one explicit queued job to one explicit worker without changing worker-pull `lease_next()` semantics.
- Exact-job leasing preserves capability checks, cancellation/terminal/attempt gates, active lease-ID collision protection, attempt accounting and transition idempotency.
- `ops/studio_compute_dispatch.py` deterministically derives the existing `WorkerManifest`, binds one durable compute job to the exact draft and manifest digest, reads durable workers, projects external provider capability evidence through the existing router, resolves the selected lane/runtime back to one durable worker and leases the exact submitted Studio job.
- Dispatch transitions the exact job through queued → leased → running before entering the M2-M1-042 restricted-runtime path.
- Selected worker isolation evidence must bind to the exact worker/principal/runtime. Local-compute OFF, stale worker evidence and ordinary router policy/capability blockers remain fail-closed before worker execution.
- Successful worker evidence completes the exact durable job with a result digest plus worker/runtime provenance. Bounded worker or restricted-runtime failure records deterministic durable failure instead of fabricating success.
- Successful replay returns the existing durable terminal result without rerunning the worker or incrementing attempts.
- Current Studio local execution intentionally uses `max_attempts=1`; one failed local run consumes its controller-owned Git branch and automatic retry is deferred until stronger branch/retry semantics exist.
- No merge, push, activation, publication, install or feature-share authority is granted by dispatch success.

## Semantic / adversarial review

Review after the first full dispatch implementation found one false-positive test rather than a persistence leak: the raw-error test rejected the generic substring `private`, which is legitimately present in the durable `data_classification='private_source'`. The implementation persists only the stable `studio_execution_error` code for that path. The test now asserts that the actual synthetic exception text and path are absent from the durable job representation.

The exact worker mapping was also checked against the existing router contract. `route_runtime()` requires unique `lane_id` values before selection, so dispatch deliberately fails closed on duplicate durable lanes rather than attempting to reinterpret the router's identity semantics.

No new scheduler/router/registry/model selector/approval system was introduced. The packet composes existing authorities only.

## Verification evidence

- Earlier exact-job lease and dispatch CI runs exercised the new durable paths and exposed the raw-error assertion defect.
- CI #638 on `28a42a17d3d8680fcfd594aa66fe85d12bc56aa8` failed only the over-broad raw-error-persistence assertion; all repository gates before the Python assertion and the remaining dispatch/exact-lease tests passed.
- Commit `4a9cc3c8b20700803bd6e2bca4b6cbc4c76e26f8` repaired that assertion to check the actual raw synthetic exception material.
- CI #639 / run `34724545588` completed successfully on exact head `4a9cc3c8b20700803bd6e2bca4b6cbc4c76e26f8`, including compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests and Workspace Apps Script tests.
- CI #641 correctly rejected a noncanonical session-alignment heading, and CI #642 then proved the heading prefix but exposed the missing required authority-review subsections. Those documentation-only failures are now repaired in this checkpoint.
- This checkpoint changes the branch head, therefore one final exact-head CI run is still mandatory before merge.

## Acceptance state

1. Exact-job lease preserves existing lease/idempotency/capability/attempt/collision semantics and leaves `lease_next()` intact. **PASS.**
2. Studio dispatch creates/replays one durable job bound to the review-ready draft and complete manifest digest. **PASS.**
3. Worker selection uses durable worker registry plus external provider capability evidence through the existing projection/router contracts. **PASS.**
4. Missing/ambiguous durable worker mapping fails closed. **PASS.**
5. Existing router policy/capability/freshness/health/lock gates remain in the path before local worker entry. **PASS at deterministic composition ceiling.**
6. The exact submitted Studio job is leased instead of an unrelated higher-ranked queued job. **PASS, directly tested.**
7. Durable job reaches leased/running before restricted Studio execution. **PASS.**
8. M2-M1-042 restricted-runtime admission remains mandatory before lower-worker execution. **PASS.**
9. Success records durable result digest and worker/runtime provenance. **PASS.**
10. Bounded worker/restricted-runtime failure records durable failure and sanitized error code. **PASS.**
11. Dispatch grants no merge/push/activation/publication/install authority. **PASS by implementation boundary.**
12. Successful replay does not duplicate jobs, attempts or execution. **PASS.**
13. Competing queued-job test proves exact-job lease does not consume the wrong job. **PASS.**
14. Public Git material remains synthetic and secret-free. **PASS.**
15. Full exact-head and post-merge CI/readback are required. **FINAL HEAD PENDING after this checkpoint; post-merge pending.**
16. No live private worker/host/model/provider/hardware claim is made from synthetic CI. **PASS.**

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

This packet advances the already-defined `STUDIO-001`, `DEV-004`, `LOCAL-001` and `PROVIDER-001` capabilities. It composes Studio execution with optional local compute under existing provider/runtime boundaries and does not invent a new feature family or make private compute mandatory.

### `BACKLOG.md`

`LOCAL-INTEGRATIONS` is the existing primary work lane for wiring optional local compute into product capabilities. M2-M1-043 fills the durable Studio-dispatch seam inside that lane by reusing the existing compute control plane, worker registry and runtime router rather than creating duplicate scheduling authority.

### `ROADMAP.md`

Product direction remains unchanged: make MIRA usable through ordinary-language flows while keeping Personal Google support and optional advanced/local infrastructure on verified capability boundaries. This packet advances the executable Studio path without weakening Standard-mode independence from local hardware.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Reuses existing `STUDIO-001`, `DEV-004`, `LOCAL-001`, `PROVIDER-001` and `LOCAL-INTEGRATIONS`.
- Exact-job leasing is an integrity prerequisite inside the existing M2-M1-024 compute-control-plane authority, not a new feature vertical.
- The raw-error assertion repair and session-alignment metadata repairs are packet-owned verification work, not scope growth.
- No private deployment binding or live-host behavior is silently admitted.
- No duplicate feature/work ID is added.

### Direction result

ALIGNED

## Exact next action / resume point

1. Require full CI green on the exact checkpoint head created by this documentation update.
2. Update PR #159 to reflect the completed dispatch vertical and verification evidence.
3. Re-read remote `main`, PR #159 exact head and mergeability immediately before merge.
4. Mark PR #159 ready and merge only with expected-head protection if exact-head CI is green and `main` remains compatible.
5. Read back exact post-merge `main` and require the push CI on that exact merge SHA to pass before closing M2-M1-043.
6. After closure, rank the next existing Studio/local-compute work from Git rather than inventing a parallel work ID.

## Evidence ceiling

Synthetic CI proves deterministic dispatch composition, exact durable job leasing, router/worker-registry integration, restricted-runtime handoff and durable terminal reconciliation. It does not prove a private worker authenticated over a real transport, that a host containment mechanism is physically enforced, that LM Studio is running, that a private GPU exists, or that generated code executed on private hardware. Those remain separate live-verification gates.