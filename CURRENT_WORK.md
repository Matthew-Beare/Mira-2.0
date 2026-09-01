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
- `HOST-CONNECT-EXEC-001` is the bounded host executor proof selected for this packet.
- `ANDROID-COMMAND-BOUNDARY-001` remains partial with its live isolated Google queued-writer proof pending immediately after this packet.
- `ANDROID-CLIENT-CORE-001` remains queued immediately after that live proof.

### `ROADMAP.md`

- M2-M0.5 has already delivered the no-app Personal foundation and multiple canonical verticals.
- M2-M1 remains paused only for the remaining hard shared-writer proof before Android mutation begins.
- Provider expansion including Apple/iCloud remains later unless it becomes a hard dependency.

### Direction result

**ALIGNED.** Close the stock-ChatGPT host executor seam, then immediately resume the existing live queued-writer proof before Android. Do not add unrelated feature work.

## Active packet

### `M2-M0-029` — Stock ChatGPT native connection execution proof

- **Primary work:** `HOST-CONNECT-EXEC-001`
- **Primary features:** `PROVIDER-002`, `ONBOARD-006`
- **Related invariants/features:** `PROVIDER-001`, `SOURCE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-029-host-connect-exec`
- **Base/main SHA:** `604ec697d7566640aa9333da18d1f60dd4a66036`
- **Starting branch head:** `604ec697d7566640aa9333da18d1f60dd4a66036`
- **Current implementation head:** updated by the commits recorded below; verify exact remote head before merge
- **Dependencies:** `PROVIDER-ONBOARD-001` complete; current ChatGPT Plugin Management capability available in this host session
- **Blockers:** none for packet closure; CI/merge/readback remain

## Objective

Prove that stock ChatGPT can execute the host-controlled side of MIRA’s connection contract: ordinary-language intent for a supported service can resolve the relevant current ChatGPT app/plugin and surface the host-native install/connect action directly, without manual settings navigation or technical provider setup.

## Acceptance criteria

1. Verify current host capability through live Plugin Management discovery rather than relying only on documentation or repository assumptions.
2. Use a user-recognizable supported service, initially Google Calendar, as the bounded proof target.
3. Resolve the exact current ChatGPT plugin/app through host discovery from service intent; do not hard-code a stale catalog identifier as product truth.
4. Surface the host-native install/connect action through ChatGPT’s supported plugin UI without silently authorizing on the user's behalf.
5. Record explicit user tap/provider consent as unavoidable host/provider ceremony rather than a MIRA failure or automatic authorization.
6. Do not mutate Calendar, Gmail, Drive, MIRROR canonical state, or legacy production data during this proof.
7. Do not claim capability verification, Connected state, or service activation merely because the host surfaced or completed the app authorization flow.
8. Verify that `mira/provider_onboarding.py` host planning maps coherently to the live host action: discover/install/connect when authorization is required, then separate capability verification.
9. Capture only generic/nonpersonal host evidence in Git.
10. Encode host-execution behavior in source-backed operating instructions/protocol.
11. Direct tests/CI prevent regression into settings treasure hunts, fake authorization success, or local-checkout-dependent scheduled runtime behavior.
12. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required.
13. Mark `HOST-CONNECT-EXEC-001` only to the evidence actually demonstrated. Provider resource/capability readback and provider mutation remain separate.

## Completed evidence in this packet

- Live Plugin Management discovery from ordinary Google Calendar service intent resolved the current supported Google Calendar integration.
- The host-native install/connect control was surfaced directly in ChatGPT.
- The human user completed the native host/provider connection ceremony. MIRA did not click through consent on the user's behalf.
- No Calendar event, Gmail message, Drive file, MIRROR canonical entity, or protected legacy production state was mutated by this proof.
- `docs/host_connect_execution_evidence.md` records the generic evidence ceiling without account identifiers, tokens, scope details, or private provider state.
- `PROJECT_INSTRUCTIONS.md` now requires current host discovery, direct native connect surfacing, service isolation, honest unsupported-provider failure, and separation of authorization from verified `Connected` state.
- `tests/test_project_instructions_contract.py` adds regression coverage for the connection contract and scheduled-runtime portability rule.

## Production incident captured during packet

The enabled MIRA AM/PM brief automations fired but failed because their prompts incorrectly required a local repository/skill script (`skill/ops-brief-policy/scripts/ops_policy.py`) to exist inside the scheduled ChatGPT runtime. The scheduler itself worked; the deployment assumption was invalid.

Both enabled AM and PM automation prompts were corrected live so the exact-schedule trigger is authoritative for slot entry, the platform runtime/system clock is used when needed, local policy scripts are optional verification rather than mandatory deployment dependencies, and independent modules fail closed independently when their own canonical access/integrity/readback fails.

This durable rule is now also encoded in `PROJECT_INSTRUCTIONS.md` and regression-tested. Do not restore a mandatory local-checkout/local-skill precondition in scheduled ChatGPT automations.

## Evidence ceiling

`HOST-CONNECT-EXEC-001` has live host discovery + native connection-surface execution evidence for Google Calendar. User-driven authorization through the surfaced host flow occurred, but this packet does not claim operation-specific Calendar capability/resource verification, verified `Connected` presentation, MIRA service activation, Calendar reads/writes, or provider mutation/readback.

## Explicitly deferred

- live Calendar capability/resource/scope readback after consent;
- Calendar/Gmail/Drive reads or writes;
- Microsoft/Apple adapters;
- Android implementation;
- legacy production migration.

## Android preserved resume point

- `ANDROID-COMMAND-BOUNDARY-001`: provider-neutral sequencer plus synthetic Google Workspace queued-worker proof complete in PRs #54/#55; live isolated Google worker proof pending.
- `ANDROID-CLIENT-CORE-001`: follows that proof and owns scoped/revocable identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, exact server readback and the product-owned Connections surface.
- `ANDROID-SYNC`: then proves Android mutation and stock ChatGPT readback from the same canonical authority.

## Exact next action / resume point

1. Verify the current branch remote head and run exact-head CI for the instruction/evidence/regression changes.
2. Open/merge the bounded M2-M0-029 PR only after required CI is green.
3. Remotely read back the merge and post-merge main CI.
4. Reconcile `HOST-CONNECT-EXEC-001` in BACKLOG to the live-host evidence ceiling during closure.
5. Immediately resume `ANDROID-COMMAND-BOUNDARY-001` live isolated Google queued-writer proof.
6. Then start `ANDROID-CLIENT-CORE-001`.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M0-029` / `HOST-CONNECT-EXEC-001` on `integration/m0-029-host-connect-exec`, based on green main SHA `604ec697d7566640aa9333da18d1f60dd4a66036`. Live stock-ChatGPT Google Calendar host discovery and native connection surfacing have been proven; source instruction/evidence/test changes are committed. Resume with exact-head CI and PR closure, then return immediately to the live Android command-boundary prerequisite. Do not expand into provider mutation, Apple implementation, or Android client code until this bounded packet closes.
