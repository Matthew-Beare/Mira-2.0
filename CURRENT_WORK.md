# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Ordinary-user provider setup must be intent-first and as close to one-click as the host/provider safely permits. Product-owned clients expose obvious connection controls; stock ChatGPT uses the closest supported native host/provider flow. Manual resource creation, copied IDs, OAuth-scope editing, Apps Script/developer-console work, pasted code, terminal setup, Linux, SQL, Cloud Run, or paid OpenAI API usage are not prerequisites for the default Personal path when software can route around them.

Android remains a later companion extension over the same canonical state and provider/service semantics. It is paused while no-app Personal MIRA becomes genuinely usable.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable product invariants.

## Session-start alignment verification — 2026-09-01

### `FEATURES.md`

- `SOURCE-001` requires independent read, write, and remote-readback capability truth.
- `PROVIDER-001` requires provider-neutral runtime routing from observed capability evidence.
- `PROVIDER-002` requires ordinary-user provider onboarding with native consent, automatic discovery/binding/verification, and no avoidable technical setup.
- `ONBOARD-006` preserves browser-only nontechnical Personal setup.
- `RECOVERY-002` preserves failure isolation and fail-closed behavior.

### `BACKLOG.md`

- `SOURCE-GATES-001` is implemented by M2-M0-026 / PR #83 and is being reconciled from stale `queued` lifecycle text to its demonstrated completion evidence on this branch.
- `RUNTIME-ROUTER-001` remains the next prerequisite after this closure because `PROVIDER-ONBOARD-001` depends on verified routing truth.
- `PROVIDER-ONBOARD-001` remains the canonical work item for the seamless Connections experience and must reuse the capability/router state rather than inventing UI-only truth.
- Android remains separately preserved under `ANDROID-COMMAND-BOUNDARY-001`, `ANDROID-CLIENT-CORE-001`, and `ANDROID-SYNC`.

### `ROADMAP.md`

- M2-M0.5 continues to prioritize ordinary-user no-app Personal usefulness before Android.
- Provider/onboarding hardening belongs in M2-M0.5 because it removes setup burden across multiple user-visible services.
- M2-M1 remains paused at the live isolated Google queued-writer proof resume point.

### Direction result

**ALIGNED.** Finish the lifecycle reconciliation for M2-M0-026, verify the closure branch, merge it cleanly, then create a bounded `RUNTIME-ROUTER-001` packet. Do not expand this closure into provider OAuth, live Calendar/Gmail/Drive mutation, Android, Microsoft/Apple adapters, or legacy production writes.

## Active packet

### `M2-M0-026` — Personal provider capability-gate foundation — final lifecycle closure

- **Primary work:** `SOURCE-GATES-001`
- **Primary features:** `SOURCE-001`, `PROVIDER-001`, `PROVIDER-002`
- **Related invariants/features:** `ONBOARD-006`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `integration/m0-026-provider-capability-gates`
- **Closure checkpoint branch:** `governance/m0-026-closure`
- **Final lifecycle branch:** `governance/m0-026-final-close`
- **Original implementation base SHA:** `6e424e70e167ce69ae7cbf0064880ad2909beb45`
- **Current lifecycle base/main SHA:** `59dd2a20241e153ff31b5678e80e19425cfae0f4`
- **Implementation PR:** #83 merged
- **Implementation final head:** `b2a28113fd049227ce95250043a9c17c230ad632`
- **Implementation exact-head CI:** `33465768620` green
- **Implementation merge SHA:** `89b6e2d1f26679af247a6cc10af4e1d6fffd958f`
- **Implementation post-merge CI:** `33465833635` green
- **Closure checkpoint PR:** #84 merged
- **Closure checkpoint merge SHA:** `59dd2a20241e153ff31b5678e80e19425cfae0f4`
- **Closure checkpoint post-merge CI:** `33466001974` green
- **Blockers:** none; only canonical backlog lifecycle reconciliation remains on this branch

### Completed objective

M2-M0-026 established provider-neutral, secret-free capability evidence that keeps authorization, read capability, write capability, exact remote readback, freshness, connection presentation, and MIRA service activation as separate truths.

### Durable evidence

- `mira/service_state.py` on remote `main` contains typed authorization, capability-gate, evidence-state, connection-state, snapshot, and evaluation semantics.
- Authorization states distinguish unknown, required, authorized, denied, expired, revoked, and unavailable.
- Read, write, and exact remote-readback gates are independent.
- Evidence distinguishes unknown, unsupported, declared, verified, failed, and permission denied.
- Deterministic presentation state distinguishes Connect, Connected, Reconnect, Needs attention, and Unavailable.
- Authorization alone cannot produce Connected unless every required operation has fresh verified evidence.
- Stale evidence fails closed; future-dated evidence is rejected.
- Capability evaluation may update readiness but cannot silently create user activation intent.
- Synthetic tests cover authorized-but-unverified, read-only, exact-readback, write/readback failure, revoked/expired, permission denied, unsupported, stale, and future evidence.
- PR #83 exact-head CI and post-merge `main` CI are green.
- PR #84 closure checkpoint is merged and post-merge CI `33466001974` is green.
- No live Personal Calendar, Drive, Gmail, or other provider resource was mutated.
- On `governance/m0-026-final-close`, `BACKLOG.md` now records the PR #83 completion evidence for `SOURCE-GATES-001` instead of stale `queued` text.

### Evidence ceiling

This packet does not claim live provider authorization/discovery, provider-specific OAuth orchestration, actual Google Calendar/Drive/Gmail connection observation, runtime routing, MIRA-owned connection UI, provider mutation/readback, Microsoft/Apple proof, or Android behavior.

## Seamless connection dependency path

1. `SOURCE-GATES-001` establishes honest capability truth. Implementation and CI evidence are complete; lifecycle text is being finalized here.
2. `RUNTIME-ROUTER-001` consumes those observations and selects or blocks provider/runtime lanes without assuming capability.
3. `PROVIDER-ONBOARD-001` consumes the same router/capability truth for Connect, Connected, Reconnect, Needs attention, Unavailable, and Disconnect behavior.
4. Product-owned clients use obvious service-level controls such as **Connect Google Calendar**, **Connect Google Drive**, and **Connect Gmail**.
5. Stock ChatGPT routes ordinary-language intent to the closest supported native host/provider authorization flow rather than exporting technical setup to the user.
6. Future Android renders the same semantics through a native Connections surface rather than creating a second activation model.

## Android preserved resume point

Android remains M2-M1 and is paused, not discarded.

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer proof is complete from PRs #54/#55; live isolated Google worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` follows that live proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback.
- `ANDROID-SYNC` then proves Android mutation and stock-ChatGPT readback against the same canonical authority.
- There is still no MIRA 2.0 Android UI implementation.

## Exact next action / resume point

1. Open a bounded PR from `governance/m0-026-final-close` containing only the `SOURCE-GATES-001` lifecycle reconciliation and this corrected checkpoint.
2. Require exact-head green CI, merge with expected-head protection, then verify remote `main` readback and push-event CI.
3. Create the next bounded packet `M2-M0-027` for `RUNTIME-ROUTER-001` from that clean main SHA.
4. Reuse the merged capability evaluation; do not create another capability model.
5. Keep actual provider onboarding/connection UI under `PROVIDER-ONBOARD-001` after router truth is verified.
6. Do not resume Android unless explicitly reprioritized; its Git-backed resume point remains the live isolated Google queued-writer proof.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. M2-M0-026 implementation is merged through PR #83 at `89b6e2d1f26679af247a6cc10af4e1d6fffd958f`; PR #84 checkpoint is merged at `59dd2a20241e153ff31b5678e80e19425cfae0f4`; all recorded implementation/checkpoint CI is green. Active work is only the final lifecycle reconciliation on `governance/m0-026-final-close`. After it merges, select `RUNTIME-ROUTER-001`; do not reconstruct Android or provider state from conversation history.