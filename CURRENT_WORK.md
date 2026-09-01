# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and ordinary-user onboarding/integration hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. The connection-surface rule under `PROVIDER-002` / `PROVIDER-ONBOARD-001` requires obvious Connect/Connected/Reconnect/Needs-attention/Unavailable/Disconnect behavior wherever the client controls UI, with the closest supported native host/provider connection flow when stock ChatGPT controls the UI. Manual provider resource creation, copied IDs, scope editing, Apps Script/developer-console work, pasted code and terminal setup are prohibited for the default Personal path whenever software can route around them.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `SOURCE-001` requires independent source read, source write and remote-readback capability gates rather than treating a provider login as proof that an operation works.
- `PROVIDER-001` requires runtime capability routing from observed evidence.
- `PROVIDER-002` requires browser-only ordinary-user provider onboarding with native Connect flow, automatic post-consent discovery/binding/verification and no avoidable technical setup.
- `ONBOARD-006` preserves the browser-only nontechnical Personal path with no terminal fallback.
- `RECOVERY-002` requires failure isolation so one broken provider capability cannot fabricate readiness or break unrelated services.

### `BACKLOG.md`

- `SOURCE-GATES-001` is the immediate unfinished prerequisite for provider capability truth.
- `RUNTIME-ROUTER-001` depends on `SOURCE-GATES-001` and converts verified capability evidence into runtime routing decisions.
- `PROVIDER-ONBOARD-001` depends on that runtime routing layer and will consume the resulting state for the seamless Connections experience rather than inventing a parallel truth model.
- `APPOINTMENT-INTAKE-NOAPP-001` remains partial only at live stock-ChatGPT source/model and live Calendar evidence layers after PR #81.
- Android remains separately preserved under `ANDROID-COMMAND-BOUNDARY-001`, `ANDROID-CLIENT-CORE-001`, and `ANDROID-SYNC`; this packet does not resume Android.

### `ROADMAP.md`

- M2-M0.5 still prioritizes a useful ordinary-user no-app Personal product before Android becomes the active development focus.
- Provider/onboarding hardening belongs in that no-app path when it removes user setup burden across multiple services.
- M2-M1 remains paused with the live isolated Google queued-writer proof as the first Android resume step.

### Direction result

**ALIGNED.** Implement the smallest provider-neutral capability evidence/gating foundation required for honest seamless Connections UX. Do not draw connection UI that can claim readiness before MIRA can independently distinguish authorization, usable capability, verification failure, revocation and unavailability. Do not expand this packet into actual provider consent UI, Calendar event mutation, Gmail ingestion, Drive mutation, Android UI, Microsoft/Apple adapters or legacy production writes.

## Active packet

### `M2-M0-026` — Personal provider capability-gate foundation

- **Primary work:** `SOURCE-GATES-001`
- **Primary features:** `SOURCE-001`, `PROVIDER-001`, `PROVIDER-002`
- **Related invariants/features:** `ONBOARD-006`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-026-provider-capability-gates`
- **Base/main SHA:** `6e424e70e167ce69ae7cbf0064880ad2909beb45`
- **Starting branch head:** `6e424e70e167ce69ae7cbf0064880ad2909beb45`
- **Dependencies:** source connector/runtime capability evidence; canonical service activation remains separate
- **Blockers:** none identified for provider-neutral/synthetic implementation

### Objective

Implement a provider-neutral capability evidence model and independent gates that later `RUNTIME-ROUTER-001` and `PROVIDER-ONBOARD-001` can consume to present honest ordinary-user connection state.

The model must make it possible to distinguish at minimum:

- provider/service discovered versus unsupported/unavailable;
- authorization required, authorized, expired/revoked or denied;
- read capability declared versus read operation verified;
- write capability declared versus write operation verified;
- exact remote-readback verified versus unverified/failed;
- resource/scope-specific evidence where capability is not provider-wide;
- stale evidence requiring re-verification;
- MIRA service activation from provider authorization/capability state.

### Acceptance criteria

1. Provider-neutral capability evidence has stable typed states rather than free-form booleans or UI strings.
2. Source read, source write and remote-readback gates are independent; one passing gate never implies the others.
3. Authorization success alone never implies read/write/readback readiness.
4. Revocation, expiry, permission denial, unsupported operation, stale evidence and verification failure fail closed and produce deterministic machine-readable reasons suitable for later user-facing **Reconnect**, **Needs attention**, or **Unavailable** presentation.
5. Evidence records enough provenance to identify provider/service/resource/scope and observation time without storing credentials, tokens, secrets or private provider payloads in public Git/test fixtures.
6. Capability evidence and MIRA service activation remain separate states. Connecting Google Calendar, for example, cannot silently activate unrelated behavior or providers.
7. Re-observing the same evidence is deterministic/idempotent; newer evidence can supersede stale observations without silently erasing audit-relevant prior state where the contract requires history.
8. Direct synthetic tests cover authorized-but-unverified, read-only, read+readback, writable-but-readback-failed, revoked/expired, permission-denied, unsupported and stale-evidence cases.
9. The public API presented to later `RUNTIME-ROUTER-001` / `PROVIDER-ONBOARD-001` is small and provider-neutral; Google-specific semantics do not become canonical product truth.
10. Production code ownership/release-contract gates are updated if new runtime modules are added.
11. No legacy Personal Google production resources are mutated. Any provider demonstration, if later required in this packet, must use isolated synthetic/read-only evidence and exact readback boundaries.
12. Exact-head CI must pass before merge; merge uses expected-head protection, followed by remote `main` readback and post-merge CI verification.

### Explicitly deferred

- MIRA-owned Connect buttons/cards or Android Connections UI;
- invoking Google/Microsoft/Apple OAuth/consent itself;
- Google Calendar event creation/update/delete;
- Gmail content ingestion or provider-side mail mutation;
- Google Drive file mutation;
- full `RUNTIME-ROUTER-001` routing policy;
- `PROVIDER-ONBOARD-001` UI/orchestration;
- Android client implementation or live queued-writer proof;
- Microsoft/Apple provider adapters;
- migration of legacy MIRA production data.

## Previous packet closure evidence

`M2-M0-025` direct no-app appointment text/image implementation merged through PR #81 at `92ba63a9a7c5404309dd2f76231aed30fec76c4f`; final exact-head CI `33460001756` and post-merge `main` CI `33464770421` are green. Closure/product-invariant PR #82 merged at `6e424e70e167ce69ae7cbf0064880ad2909beb45`; exact-head CI `33465373543` and post-merge `main` CI `33465403195` are green. Remote `main` readback confirms the seamless provider connection invariant and final appointment evidence are durable.

## Android status / preserved resume point

Android remains M2-M1 and is **paused, not discarded** while usable no-app Personal MIRA is prioritized.

Current evidence:

1. `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer implementation/test proof is complete from PRs #54/#55.
2. The immediate Android prerequisite still pending is the **live isolated Google worker proof** for that stronger shared-writer boundary.
3. `ANDROID-CLIENT-CORE-001` is queued immediately after that proof. It owns scoped/revocable enrollment/session identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling and exact server readback.
4. `ANDROID-SYNC` then proves Android mutation of the same canonical state and stock ChatGPT readback from that same authority.
5. Native notification/TTS delivery, camera/barcode/QR/NFC/BLE capture, release signing and broader UI polish follow the shared-state proof unless required by the core proof itself.

There is meaningful backend/client-boundary work already completed, but **no current MIRA 2.0 Android UI implementation yet**.

## Exact next action / resume point

1. Inventory existing source/provider capability code and tests on `integration/m0-026-provider-capability-gates` before creating any new module.
2. Reuse existing typed evidence/state machinery where it satisfies the acceptance criteria; do not create a duplicate capability model.
3. Implement the smallest missing provider-neutral capability evidence/gate layer with synthetic tests only.
4. Update component ownership/release evidence if production code changes.
5. Run the full repository CI-equivalent suite, open a bounded PR, require exact-head green CI, merge with expected-head protection, then verify remote `main` readback and post-merge CI.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M0-026` on `integration/m0-026-provider-capability-gates`, based on clean `main` SHA `6e424e70e167ce69ae7cbf0064880ad2909beb45`. Previous appointment/connection-rule closure is complete and green. Resume by inventorying existing provider/source capability code and tests; do not reconstruct provider state or Android work from conversational memory.
