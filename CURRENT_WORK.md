# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and ordinary-user onboarding/integration hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. The connection-surface refinement under `PROVIDER-002` / `PROVIDER-ONBOARD-001` now requires obvious Connect/Connected/Reconnect/Needs-attention/Disconnect behavior wherever the client controls UI, with the closest supported native host/provider connection flow when stock ChatGPT controls the UI. Manual provider resource creation, copied IDs, scope editing, Apps Script/developer-console work, pasted code and terminal setup are prohibited for the default Personal path whenever software can route around them.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-008` remains the primary feature for the closing direct no-app appointment slice.
- `CAL-005`, `CAL-006`, `CAL-007`, `SERVICE-001`, `RECOVERY-002`, `ONBOARD-006`, `PROVIDER-002`, and `MAIL-002` remain preserved related product boundaries.
- `PROVIDER-002` now explicitly carries the ordinary-user connection-surface refinement instead of creating a duplicate integration feature ID.

### `BACKLOG.md`

- `APPOINTMENT-INTAKE-NOAPP-001` remains the canonical work ID for M2-M0-025 and remains partial only at the live stock-ChatGPT source/model and live Calendar evidence layers.
- `PROVIDER-ONBOARD-001` already exists as the canonical queued provider-onboarding work item; the new connection UX requirement refines that work rather than expanding this appointment implementation packet.
- Android work remains separately preserved under `ANDROID-COMMAND-BOUNDARY-001`, `ANDROID-CLIENT-CORE-001`, and `ANDROID-SYNC`.

### `ROADMAP.md`

- M2-M0.5 still prioritizes useful no-app Personal MIRA before Android becomes the development focus.
- M2-M1 remains paused with the live isolated Google queued-writer proof as the first Android resume step.
- The seamless-connection refinement strengthens ordinary-user onboarding but does not change the provider-neutral migration or shared-state architecture.

### Direction result

**ALIGNED.** Close M2-M0-025 at the evidence actually demonstrated, durably preserve the seamless provider-connection requirement under the existing provider-onboarding feature/work IDs, and do not silently expand this closure packet into Android, Gmail, live Calendar mutation, or a new provider runtime.

## Active packet

### `M2-M0-025` — Direct no-app appointment text/image flow — closure checkpoint

- **Primary work:** `APPOINTMENT-INTAKE-NOAPP-001`
- **Primary features:** `CAL-008`
- **Related invariants/features:** `CAL-005`, `CAL-006`, `CAL-007`, `SERVICE-001`, `RECOVERY-002`, `ONBOARD-006`, `PROVIDER-002`, `MAIL-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `integration/m0-025-appointment-noapp`
- **Closure branch:** `governance/m0-025-closure`
- **Implementation base SHA:** `e400593af676ecbdf3c08d2eda2b8ab2eab0b87a`
- **PR:** #81 merged
- **Final PR head:** `249947fcde31435c24adeef5d6d39aa9da893d74`
- **Final exact-head CI:** `33460001756` green
- **Merge/main SHA:** `92ba63a9a7c5404309dd2f76231aed30fec76c4f`
- **Post-merge main CI:** `33464770421` green
- **Remote main readback:** `mira/appointment_noapp.py` present on `main`
- **Closure PR:** #82 open

### Completed objective

M2-M0-025 provides the deterministic stock-ChatGPT Personal planning seam for direct appointment text/image evidence over the merged appointment identity/intake core and native Google Workspace persistence contract. It preserves provenance, fails closed on material ambiguity, asks only materially blocking clarification, reuses canonical reconciliation instead of inventing another identity engine, performs zero-write replay where appropriate, and keeps Calendar projection behind independently verified service/capability state.

### Durable implementation evidence

- `mira/appointment_noapp.py` is merged to `main` and independently read back.
- Direct `text` and `image` evidence contracts are deterministic and provenance-bound.
- Text uses exact UTF-8 SHA-256 material identity without copying whole raw chat messages into canonical payloads.
- Image evidence never fabricates a raw-file hash; when raw bytes are unavailable, deterministic normalized extraction material is explicitly identified as derived evidence.
- Provider and appointment reconciliation reuse `AppointmentIdentityService` and `AppointmentIntakeService`.
- Google Workspace appointment-provider/appointment authority bindings and exact Resource+Idempotency persistence/readback were verified in a fresh isolated synthetic Google namespace.
- Protected Primary/Family Calendar and legacy Personal production state were not used as fixtures.
- Final exact-head CI `33460001756` passed.
- Expected-head protected PR #81 merge succeeded at `92ba63a9a7c5404309dd2f76231aed30fec76c4f`.
- Post-merge `main` CI `33464770421` passed.

### Evidence ceiling

`APPOINTMENT-INTAKE-NOAPP-001` remains partial at the live source/model evidence layer. This packet does **not** claim:

- independently verified live stock-ChatGPT text interpretation or image/vision extraction quality;
- a live connector-runtime invocation of the Python planner;
- Gmail appointment-source integration;
- real Google/Microsoft/Apple Calendar event mutation/readback;
- reminder delivery;
- outbound provider contact;
- medical interpretation;
- Android behavior.

The umbrella `APPOINTMENT-INTAKE-001` therefore remains split/partial.

## Product refinement captured during closure

The customer reiterated a cross-product ordinary-user requirement: connecting apps must be as close to one-click as the host/provider permits. This does **not** expand the appointment implementation packet. It refines existing `PROVIDER-002` / `PROVIDER-ONBOARD-001` scope for later implementation.

Durable rule now recorded in `PRODUCT_INVARIANTS.md` and `FEATURES.md`:

- product-owned clients expose an obvious Connections/Integrations surface with actions such as **Connect Google Calendar**, **Connect Google Drive**, and **Connect Gmail**;
- user-facing states include Connect, Connected, Reconnect, Needs attention, Unavailable and Disconnect;
- selecting Connect launches the host/provider-native authorization flow directly;
- MIRA performs post-consent capability discovery, binding and exact verification automatically;
- provider authorization does not silently activate unrelated services or grant unrelated scope;
- if stock ChatGPT cannot render MIRA-owned buttons, plain-language intent routes to the closest supported native ChatGPT/provider connection flow rather than exporting technical setup to the user;
- future Android uses the same provider/service semantics through a native Connections surface rather than creating a second activation model.

## Android status / preserved resume point

Android remains M2-M1 and is **paused, not discarded** while usable no-app Personal MIRA is prioritized.

Current evidence:

1. `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencing plus synthetic Google Workspace queued-writer implementation/test proof is complete from PRs #54/#55.
2. The immediate Android prerequisite still pending is the **live isolated Google worker proof** for that stronger shared-writer boundary.
3. `ANDROID-CLIENT-CORE-001` is queued immediately after that proof. It will own scoped/revocable enrollment/session identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling and exact server readback.
4. `ANDROID-SYNC` then proves Android mutation of the same canonical state and stock ChatGPT readback from that same authority.
5. Native notification/TTS delivery, camera/barcode/QR/NFC/BLE capture, release signing and broader UI polish follow the shared-state proof unless required by the core proof itself.

There is therefore meaningful backend/client-boundary work already done, but **no current MIRA 2.0 Android UI implementation yet**.

## Exact next action / resume point

1. Reconcile `BACKLOG.md` with PR #81 merge/main/post-merge evidence and the refined `PROVIDER-ONBOARD-001` ordinary-user connection requirement without creating a duplicate feature ID.
2. Keep `APPOINTMENT-INTAKE-NOAPP-001` partial at the live source/model evidence layer and the umbrella intake work split/partial.
3. Re-run closure-branch lifecycle/CI gates after governance reconciliation.
4. Merge closure PR #82 only with final exact-head green CI and expected-head protection, then verify remote `main` readback and push-event CI.
5. Re-rank unfinished accepted M2-M0.5 work from canonical Git after closure. Seamless provider onboarding may rank highly because it unlocks multiple user-visible provider lanes, but it does not silently preempt dependency/integrity blockers.
6. Do not resume Android merely because its status was discussed; if it becomes next work, first create the next bounded packet from the preserved live-worker proof resume point.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. M2-M0-025 implementation is merged at `92ba63a9a7c5404309dd2f76231aed30fec76c4f`; final PR-head CI `33460001756` and post-merge `main` CI `33464770421` are green; `mira/appointment_noapp.py` is present on remote `main`. Continue only with closure/backlog reconciliation on `governance/m0-025-closure`; do not reconstruct Android or provider-onboarding work from conversational memory.
