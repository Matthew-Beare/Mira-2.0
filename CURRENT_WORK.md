# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and ordinary-user onboarding/integration hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. The connection-surface rule under `PROVIDER-002` / `PROVIDER-ONBOARD-001` requires obvious Connect/Connected/Reconnect/Needs-attention/Unavailable/Disconnect behavior wherever the client controls UI, with the closest supported native host/provider connection flow when stock ChatGPT controls the UI. Manual provider resource creation, copied IDs, scope editing, Apps Script/developer-console work, pasted code and terminal setup are prohibited for the default Personal path whenever software can route around them.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `SOURCE-001` requires independent source read, source write and remote-readback capability gates rather than treating provider authorization as proof that an operation works.
- `PROVIDER-001` requires runtime capability routing from observed evidence.
- `PROVIDER-002` requires browser-only ordinary-user provider onboarding with native Connect flow, automatic post-consent discovery/binding/verification and no avoidable technical setup.
- `ONBOARD-006` preserves the browser-only nontechnical Personal path with no terminal fallback.
- `RECOVERY-002` requires failure isolation so one broken provider capability cannot fabricate readiness or break unrelated services.

### `BACKLOG.md`

- `SOURCE-GATES-001` is the canonical work item implemented by M2-M0-026; backlog lifecycle reconciliation is the remaining closure edit.
- `RUNTIME-ROUTER-001` depends on `SOURCE-GATES-001` and is the next architectural prerequisite for converting verified evidence into provider/runtime routing decisions.
- `PROVIDER-ONBOARD-001` follows that router and will consume the same connection truth for the seamless Connections experience rather than inventing a parallel UI state model.
- `APPOINTMENT-INTAKE-NOAPP-001` remains partial only at live stock-ChatGPT source/model and live Calendar evidence layers after PR #81.
- Android remains separately preserved under `ANDROID-COMMAND-BOUNDARY-001`, `ANDROID-CLIENT-CORE-001`, and `ANDROID-SYNC`; this closure does not resume Android.

### `ROADMAP.md`

- M2-M0.5 still prioritizes a useful ordinary-user no-app Personal product before Android becomes the active development focus.
- Provider/onboarding hardening belongs in that no-app path when it removes user setup burden across multiple services.
- M2-M1 remains paused with the live isolated Google queued-writer proof as the first Android resume step.

### Direction result

**ALIGNED.** Close M2-M0-026 at the evidence actually demonstrated, reconcile `SOURCE-GATES-001`, then select `RUNTIME-ROUTER-001` before implementing provider connection UI. Do not expand this closure into provider OAuth, Calendar/Gmail/Drive writes, Android, Microsoft/Apple adapters, or legacy production mutation.

## Active packet

### `M2-M0-026` — Personal provider capability-gate foundation — closure checkpoint

- **Primary work:** `SOURCE-GATES-001`
- **Primary features:** `SOURCE-001`, `PROVIDER-001`, `PROVIDER-002`
- **Related invariants/features:** `ONBOARD-006`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `integration/m0-026-provider-capability-gates`
- **Closure branch:** `governance/m0-026-closure`
- **Base/main SHA:** `6e424e70e167ce69ae7cbf0064880ad2909beb45`
- **PR:** #83 merged
- **Final PR head:** `b2a28113fd049227ce95250043a9c17c230ad632`
- **Final exact-head CI:** `33465768620` green
- **Merge/main SHA:** `89b6e2d1f26679af247a6cc10af4e1d6fffd958f`
- **Post-merge main CI:** `33465833635` green
- **Remote main readback:** provider capability evidence/gate implementation is present in `mira/service_state.py`
- **Dependencies:** provider adapters later supply observations; canonical service activation remains separate
- **Blockers:** none for closure; backlog lifecycle reconciliation remains

### Completed objective

M2-M0-026 implements the provider-neutral capability evidence/gating foundation required for honest seamless Connections UX. It gives later runtime routing and onboarding code deterministic machine-readable truth instead of allowing a successful provider consent screen or declared connector feature to masquerade as verified readiness.

### Durable implementation evidence

- Existing `mira/service_state.py` was extended rather than creating a duplicate capability model or new unowned runtime component.
- Typed authorization states distinguish unknown, authorization-required, authorized, denied, expired, revoked and unavailable.
- Independent SOURCE-001 gates distinguish read, write and exact remote readback; passing one never implies another.
- Evidence states distinguish unknown, unsupported, merely declared, verified, failed and permission-denied behavior.
- Provider-neutral connection decisions distinguish Connect, Connected, Reconnect, Needs attention and Unavailable.
- Authorization success alone never produces Connected state unless every required operation has fresh verified evidence.
- Stale evidence fails closed; future-dated evidence is rejected.
- Revoked/expired authorization deterministically routes to Reconnect; unsupported required capability routes to Unavailable; permission/verification failures route to Needs attention.
- Capability snapshots retain provider/service/resource/scope/time provenance without credential, token, secret or private provider-payload fields.
- Capability evaluation can update service readiness but does not alter explicit user activation intent. A capable provider therefore cannot silently activate a MIRA service.
- Synthetic direct tests cover authorization-required, authorized-but-unverified, read-only/independent gates, exact readback, write-with-readback-failure, revoked/expired, permission-denied, unsupported and stale/future evidence cases.
- Final PR-head CI `33465768620` passed compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Python tests and Workspace Apps Script tests.
- Expected-head protected PR #83 merge succeeded at `89b6e2d1f26679af247a6cc10af4e1d6fffd958f`.
- Remote `main` readback independently confirmed the merged capability implementation.
- Post-merge `main` CI `33465833635` passed every gate/test.
- No live Personal Calendar, Drive, Gmail or other provider resource was mutated by this packet.

### Evidence ceiling

This packet does **not** claim:

- live stock-ChatGPT provider authorization or capability discovery;
- actual Google Calendar/Drive/Gmail connection-state observation;
- provider-specific OAuth/consent orchestration;
- `RUNTIME-ROUTER-001` routing behavior;
- MIRA-owned Connections cards/buttons;
- real Calendar/Gmail/Drive mutation/readback;
- Microsoft/Apple provider capability proof;
- Android behavior or UI.

## Seamless connection path

The intended dependency path is now explicit rather than hand-waved:

1. `SOURCE-GATES-001` / M2-M0-026 establishes honest provider capability truth. **Implementation merged and green; backlog lifecycle reconciliation remains.**
2. `RUNTIME-ROUTER-001` consumes that evidence and selects/blocks provider lanes without assuming capability.
3. `PROVIDER-ONBOARD-001` presents the ordinary-user Connections experience. Product-owned clients use obvious actions such as **Connect Google Calendar**, **Connect Google Drive**, and **Connect Gmail** with Connected/Reconnect/Needs-attention/Unavailable/Disconnect states.
4. Where stock ChatGPT controls the host UI, MIRA routes plain-language intent into the closest supported native ChatGPT/provider connection flow rather than sending the user into provider settings, Calendar creation, copied IDs, scope editing, Apps Script/developer consoles, pasted code or terminal work.
5. Future Android uses the same evidence/router/service state through a native Connections surface instead of inventing a second activation model.

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

1. Reconcile `BACKLOG.md` so `SOURCE-GATES-001` records PR #83 merge/main/readback/CI evidence rather than remaining queued.
2. Run closure-branch lifecycle/alignment CI after that canonical backlog reconciliation.
3. Open/merge the bounded closure PR with exact-head green CI and expected-head protection; verify remote `main` readback and post-merge CI.
4. Create the next bounded packet for `RUNTIME-ROUTER-001`, reusing the merged capability evaluation rather than creating another capability model.
5. Only after router truth is verified should `PROVIDER-ONBOARD-001` implement the actual seamless Connections orchestration/UI.
6. Do not resume Android merely because its status was discussed. Its exact Git-backed resume point remains the live isolated Google queued-writer proof.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. M2-M0-026 implementation is merged at `89b6e2d1f26679af247a6cc10af4e1d6fffd958f`; final PR-head CI `33465768620` and post-merge `main` CI `33465833635` are green; merged capability code is independently visible on remote `main`. Continue only with `SOURCE-GATES-001` backlog/lifecycle reconciliation on `governance/m0-026-closure`, then close the packet and select `RUNTIME-ROUTER-001`. Do not reconstruct Android or provider state from conversational memory.
