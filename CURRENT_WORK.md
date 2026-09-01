# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. A normal user should be able to express provider intent in plain language, such as “connect my calendar,” and have MIRA use the closest supported native ChatGPT app/plugin/provider flow. Manual settings treasure hunts, copied IDs, OAuth-scope editing, developer consoles, Apps Script, pasted code, terminals, Linux, SQL, Cloud Run, or paid OpenAI API usage are not default Personal setup when software can route around them.

Authorization, plugin/app installation, provider capability verification, runtime routing, connection presentation, and MIRA service activation remain separate truths. Host-native UI may require an explicit user tap for install/connect/consent; MIRA must surface that unavoidable action directly rather than disguising it as completed work.

Pre-Android feature growth is frozen except for hard proof dependencies: this host-execution proof, then the live isolated Google queued-writer proof, then Android client core. Apple remains a required provider-neutral lane but full Apple adapter implementation is not a pre-Android blocker.

## Session-start alignment verification — 2026-09-01 M2-M0-029

### `FEATURES.md`

- `PROVIDER-002` requires ordinary-user connection UX and native provider/host authorization routing without avoidable technical setup.
- `PROVIDER-001` and `SOURCE-001` remain the existing runtime-routing/capability truth; this packet does not create another provider state model.
- `ONBOARD-006` requires browser-only nontechnical Personal operation with no terminal fallback.
- `RECOVERY-002` requires provider failures to remain isolated and fail closed.

### `BACKLOG.md`

- `PROVIDER-ONBOARD-001` is complete in M2-M0-028 / PR #88 at the provider-neutral/test-verified evidence ceiling.
- `HOST-CONNECT-EXEC-001` is queued next and is the bounded host executor proof selected for this packet.
- `ANDROID-COMMAND-BOUNDARY-001` remains partial with its live isolated Google queued-writer proof pending immediately after this packet.
- `ANDROID-CLIENT-CORE-001` remains queued immediately after that live proof.

### `ROADMAP.md`

- M2-M0.5 has already delivered the no-app Personal foundation and multiple canonical verticals.
- M2-M1 remains paused only for the remaining hard shared-writer proof before Android mutation begins.
- Provider expansion including Apple/iCloud remains later unless it becomes a hard dependency.

### Direction result

**ALIGNED.** Prove the stock-ChatGPT host executor seam without provider mutation or silent authorization. If successful, close this packet and immediately resume the existing live queued-writer proof before Android. Do not add unrelated feature work.

## Active packet

### `M2-M0-029` — Stock ChatGPT native connection execution proof

- **Primary work:** `HOST-CONNECT-EXEC-001`
- **Primary features:** `PROVIDER-002`, `ONBOARD-006`
- **Related invariants/features:** `PROVIDER-001`, `SOURCE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-029-host-connect-exec`
- **Base/main SHA:** `604ec697d7566640aa9333da18d1f60dd4a66036`
- **Starting branch head:** `604ec697d7566640aa9333da18d1f60dd4a66036`
- **Dependencies:** `PROVIDER-ONBOARD-001` complete; current ChatGPT Plugin Management capability available in this host session
- **Blockers:** none identified for non-destructive discovery/surface proof; actual account connection may require explicit user consent and is not required to prove discovery/surfacing

## Objective

Prove that stock ChatGPT can execute the host-controlled side of MIRA’s connection contract: ordinary-language intent for a supported service can resolve the relevant current ChatGPT app/plugin and surface the host-native install/connect action directly, without manual settings navigation or technical provider setup.

## Acceptance criteria

1. Verify current host capability through live Plugin Management discovery rather than relying only on documentation or repository assumptions.
2. Use a user-recognizable supported service, initially Google Calendar, as the bounded proof target.
3. Resolve the exact current ChatGPT plugin/app through host discovery from service intent; do not hard-code a stale catalog identifier as product truth.
4. Surface the host-native install/connect action through ChatGPT’s supported plugin UI. The proof must not silently install, connect, or authorize an account.
5. If an explicit user tap/provider consent is required, that is recorded as unavoidable host/provider ceremony rather than a MIRA failure or completed authorization.
6. Do not mutate Calendar, Gmail, Drive, MIRROR canonical state, or legacy production data during this proof.
7. Do not claim provider authorization, capability verification, Connected state, or service activation merely because the host can surface the plugin/app action.
8. Verify that the existing `mira/provider_onboarding.py` host plan maps coherently to the live host action: discover/install/connect when authorization is required, then separate capability verification.
9. Capture current host evidence durably in Git using generic/nonpersonal information only; no account identifiers, private provider state, tokens, or user-specific plugin data.
10. Encode the host-execution behavior in MIRA’s source-backed operating instructions/protocol if the current instruction artifact does not already require it.
11. Direct tests/CI must prevent future instruction/protocol regression into settings treasure hunts or fake authorization success.
12. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required.
13. On closure, `HOST-CONNECT-EXEC-001` must be marked only to the evidence actually demonstrated. Actual provider authorization/write/readback remains separate unless explicitly and safely proven.

## Explicitly deferred

- clicking the install/connect action on the user’s behalf;
- provider OAuth consent or account authorization without explicit user action;
- Calendar/Gmail/Drive reads or writes;
- live provider capability/readback verification after consent;
- Microsoft/Apple adapters;
- Android implementation;
- legacy production migration.

## Previous packet evidence

M2-M0-028 / `PROVIDER-ONBOARD-001` is fully closed. PR #88 merged implementation at `a45dcea4247ff4df2588601277af6f65adb02be8`; final head `ce58d0591213cca616c55a32b713d402385fe3e1` passed exact-head CI `33474543309`; post-merge main CI `33474573636` is green. Closure PR #89 merged at `604ec697d7566640aa9333da18d1f60dd4a66036`; post-merge main CI `33475870224` is green. BACKLOG now records `PROVIDER-ONBOARD-001` complete at its provider-neutral evidence ceiling and `HOST-CONNECT-EXEC-001` as the next bounded proof.

## Android preserved resume point

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencer plus synthetic Google Workspace queued-worker proof complete in PRs #54/#55; live isolated Google worker proof pending.
- `ANDROID-CLIENT-CORE-001`: follows that proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, exact server readback and the product-owned Connections surface.
- `ANDROID-SYNC`: then proves Android mutation and stock ChatGPT readback from the same canonical authority.

## Exact next action / resume point

1. Inspect the current source-backed stock-ChatGPT operating instructions/protocol for connection-intent behavior.
2. Perform live non-destructive Plugin Management discovery for Google Calendar from the current host.
3. Surface the native install/connect action using the supported host plugin mechanism without clicking/authorizing it for the user.
4. Record only generic host capability/evidence in Git and add regression coverage if the instruction/protocol artifact requires changes.
5. Run exact-head CI and close this packet.
6. Immediately resume the live isolated Google queued-writer proof; then start Android client core.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M0-029` / `HOST-CONNECT-EXEC-001` on `integration/m0-029-host-connect-exec`, based on green main SHA `604ec697d7566640aa9333da18d1f60dd4a66036`. Resume with source instruction inspection and live non-destructive ChatGPT Plugin Management discovery. Do not expand into provider mutation, Apple implementation, or Android until this bounded proof closes.