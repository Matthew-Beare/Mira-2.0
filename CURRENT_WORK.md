# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Ordinary-user provider setup must be intent-first and as close to one-click as the host/provider safely permits. Product-owned clients expose obvious connection controls; stock ChatGPT uses the closest supported native host/provider flow. Manual resource creation, copied IDs, OAuth-scope editing, Apps Script/developer-console work, pasted code, terminal setup, Linux, SQL, Cloud Run, or paid OpenAI API usage are not prerequisites for the default Personal path when software can route around them.

Provider routing must be based on observed capability and explicit policy rather than provider branding, declared features, or a successful consent screen. Connecting a provider, proving a provider operation, routing an operation, and activating a MIRA service remain separate truths.

Android remains a later companion extension over the same canonical state and provider/service semantics. It is paused while no-app Personal MIRA becomes genuinely usable.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable product invariants.

## Session-start alignment verification — 2026-09-01

### `FEATURES.md`

- `SOURCE-001` requires independent source read, source write, and exact remote-readback capability gates.
- `PROVIDER-001` requires provider-neutral runtime capability routing from observed evidence.
- `PROVIDER-002` requires ordinary-user provider onboarding to consume honest connection/routing truth rather than inventing presentation-only state.
- `ONBOARD-006` preserves the browser-only nontechnical Personal path with no terminal fallback.
- `RECOVERY-002` requires failure isolation and fail-closed behavior when one provider lane is unavailable or broken.

### `BACKLOG.md`

- `SOURCE-GATES-001` is complete in M2-M0-026 / PR #83 with exact-head and post-merge CI green.
- `RUNTIME-ROUTER-001` is now the immediate unfinished prerequisite. It depends on `SOURCE-GATES-001` and policy/data-classification approval state.
- `PROVIDER-ONBOARD-001` depends on this router and remains the canonical seamless Connections UX work item.
- `SERVICE-COMPOSE-001`, `SOURCE-LANES-001`, `DISCOVERY-CORE-001`, and `MIRA-SKILL-001` also consume the router later; they do not expand this packet.
- Android remains separately preserved under `ANDROID-COMMAND-BOUNDARY-001`, `ANDROID-CLIENT-CORE-001`, and `ANDROID-SYNC`.

### `ROADMAP.md`

- M2-M0.5 continues to prioritize useful ordinary-user no-app Personal MIRA before Android.
- Provider/onboarding hardening belongs in M2-M0.5 because it removes setup burden and prevents fake readiness across multiple services.
- M2-M1 remains paused at the live isolated Google queued-writer proof resume point.

### Direction result

**ALIGNED.** Implement the smallest provider-neutral runtime routing layer over the already-merged capability evidence model. The router may select exactly one eligible lane or fail closed with deterministic reasons. Do not expand this packet into OAuth/consent, provider discovery, connection UI, service activation, live Calendar/Gmail/Drive mutation, Android, Microsoft/Apple adapters, or legacy production writes.

## Active packet

### `M2-M0-027` — Provider-neutral runtime capability router

- **Primary work:** `RUNTIME-ROUTER-001`
- **Primary features:** `PROVIDER-001`, `SOURCE-001`
- **Related invariants/features:** `PROVIDER-002`, `ONBOARD-006`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-027-runtime-router`
- **Base/main SHA:** `13503070182ce7eddad3ff17892ffb284b968a24`
- **Starting branch head:** `13503070182ce7eddad3ff17892ffb284b968a24`
- **Dependencies:** `SOURCE-GATES-001` complete; policy/data-classification/approval state supplied as explicit router inputs
- **Blockers:** none identified for provider-neutral synthetic implementation

### Objective

Implement a deterministic read-only router that takes a requested provider-backed operation, current verified capability evidence, and explicit policy/approval constraints and returns exactly one eligible provider/runtime lane or a fail-closed machine-readable decision.

The router must reuse M2-M0-026 capability truth. It must not duplicate authorization/read/write/readback state, perform provider I/O, mutate canonical state, change service activation, or infer permission from provider preference.

### Acceptance criteria

1. Route request, candidate, policy/approval, and decision shapes are typed and provider-neutral; UI strings and free-form booleans are not canonical routing truth.
2. The router consumes the merged M2-M0-026 capability evaluation/snapshot model rather than creating a second capability model.
3. Every requested operation explicitly declares required capability gates. Read, write, and remote-readback remain independent.
4. A candidate is eligible only when its required gates are freshly verified and its authorization/capability evaluation is usable for the requested operation.
5. Policy, approval, and data-classification constraints can reject an otherwise capable lane with deterministic machine-readable reasons.
6. Candidate ordering is deterministic and independent of input iteration order. Provider preference may rank eligible candidates, but an explicit provider requirement must never silently substitute another provider.
7. The router returns at most one selected lane. If no lane is eligible it fails closed and reports bounded reasons such as capability blocked, policy/approval blocked, explicit provider unavailable, or no candidates.
8. One broken or irrelevant candidate cannot poison an independently valid candidate; failure isolation from `RECOVERY-002` is preserved.
9. Routing never performs authorization, provider discovery, provider mutation/readback, canonical-state mutation, or MIRA service activation.
10. Synthetic tests cover at minimum: one valid lane; read-only lane rejected for write; missing/failed readback; revoked/stale capability; policy denial; data-classification/approval denial; deterministic ordering; preferred provider ranking; explicit-provider no-substitution; and unrelated broken-lane isolation.
11. No secrets, tokens, private provider payloads, or personal production identifiers appear in public fixtures.
12. Production code ownership/direct-verification evidence is updated if a new production module is added.
13. Exact-head CI must pass before merge; merge uses expected-head protection followed by remote `main` readback and post-merge CI verification.

### Explicitly deferred

- `PROVIDER-ONBOARD-001` Connect/Connected/Reconnect/Needs-attention/Unavailable/Disconnect UI/orchestration;
- actual provider OAuth or native consent invocation;
- live Google Calendar, Drive, Gmail, Microsoft, or Apple capability discovery;
- provider-specific Calendar/mail/file mutation;
- service composition or automatic service activation;
- source-lane implementation beyond router inputs;
- Android client/UI or live queued-writer proof;
- legacy production migration.

## Previous packet closure evidence

M2-M0-026 / `SOURCE-GATES-001` is fully lifecycle-reconciled. PR #83 merged implementation at `89b6e2d1f26679af247a6cc10af4e1d6fffd958f`; exact-head CI `33465768620` and post-merge CI `33465833635` are green. PR #84 merged the first closure checkpoint at `59dd2a20241e153ff31b5678e80e19425cfae0f4` with post-merge CI `33466001974` green. PR #85 finalized backlog lifecycle reconciliation at `13503070182ce7eddad3ff17892ffb284b968a24`; exact-head CI `33472771661` and post-merge CI `33472799791` are green. Remote `main` readback confirms `SOURCE-GATES-001` is complete.

## Android preserved resume point

Android remains M2-M1 and is paused, not discarded.

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer proof is complete from PRs #54/#55; live isolated Google worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` follows that live proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback.
- `ANDROID-SYNC` then proves Android mutation and stock-ChatGPT readback against the same canonical authority.
- There is still no MIRA 2.0 Android UI implementation.

## Exact next action / resume point

1. Inventory the complete M2-M0-026 capability evaluator API, current tests, package exports, and code-ownership manifest before creating router code.
2. Reuse existing capability evaluation directly; do not duplicate authorization/gate semantics.
3. Implement the smallest pure provider-neutral router with synthetic tests.
4. Update package exports and component ownership only if required by the chosen module boundary.
5. Run full repository CI through a bounded PR, require exact-head green, merge with expected-head protection, verify remote `main`, and verify post-merge CI.
6. Reconcile `RUNTIME-ROUTER-001` lifecycle evidence after merge.
7. Re-rank from Git. `PROVIDER-ONBOARD-001` is expected to be the next seamless-connection packet if no higher-priority integrity/dependency blocker appears.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M0-027` / `RUNTIME-ROUTER-001` on `integration/m0-027-runtime-router`, based on clean green `main` SHA `13503070182ce7eddad3ff17892ffb284b968a24`. Resume by inventorying the merged capability evaluator, tests, exports, and ownership manifest; do not reconstruct routing behavior or Android state from conversation memory.