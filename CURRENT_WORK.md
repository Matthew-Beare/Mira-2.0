# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must stop; commands use the serialized shared command boundary. Ordinary users must not open Apps Script, paste code, manage triggers, copy provider IDs, or understand queued-writer internals merely to enable Android/shared access.

Pre-Android feature growth remains frozen except for this hard shared-writer proof. After this packet reaches its live Google evidence ceiling, start `ANDROID-CLIENT-CORE-001`.

## Session-start alignment verification — 2026-09-01 M2-M1-001 live-auth checkpoint

### `FEATURES.md`

- `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require one safe shared canonical mutation boundary rather than independent read-then-write clients.
- Default Personal setup remains no-terminal/no-developer-console when software can provide an ordinary-user control.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` remains partial: provider-neutral sequencer, Workspace worker, ordinary-user activation surface, and maintainer publication/release path are test/integration verified; live isolated Google trigger/worker proof remains pending.
- `ANDROID-CLIENT-CORE-001` is queued immediately after this live proof.
- `HOST-CONNECT-EXEC-001` was implemented/live-host-proven in M2-M0-029 / PR #90, but its stale BACKLOG row still requires closure reconciliation before this packet closes.

### `ROADMAP.md`

- M2-M1 is blocked on live shared-writer proof, not on another concurrency architecture.
- Android client implementation follows this packet; unrelated provider expansion remains deferred.

### Direction result

**ALIGNED.** Continue `M2-M1-001`. Source/release work is merged and green; a fresh isolated synthetic Sheet is prepared. The next hard boundary is one-time Google authorization for the private maintainer Apps Script release identity, then provider publication, user-style activation, and one real queued command.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `governance/m1-001-live-auth-checkpoint`
- **Base/main SHA:** `f40e4801634a4da0450e3c94a7bbaad97137e14f`
- **Dependencies:** fresh isolated synthetic Google Sheet; one private maintainer Google authorization credential; Apps Script API availability.
- **Current blocker:** live Google authorization has not yet been granted to the maintainer release identity. This ChatGPT host's Google connector does not expose its OAuth token or Apps Script project actions, and the local execution container has no outbound DNS/network. No legitimate automatic path remains inside this surface to grant Google Apps Script scopes without provider consent.

## Objective

Prove the existing queued-writer architecture against a fresh isolated Google Workspace copy using an ordinary-user activation path: privately publish the verified bound runtime, enable Android/shared access without Apps Script-editor work, enqueue a synthetic API-001 command, observe the real time-driven worker serialize and commit it, and verify exact canonical/idempotency/result readback.

## Acceptance criteria

1. Use only a fresh isolated synthetic Sheet; legacy MIRA production Sheets, briefs, Calendars, automations, and user operational data are not fixtures.
2. The verified bound Apps Script release exposes `MIRA → Enable Android / shared access`; no normal user opens Apps Script or manually runs an internal function.
3. Maintainer publication uses explicit Apps Script API operations with credentials external to Git, binds to the exact requested Sheet, and independently reads back `Project.parentId` before content mutation.
4. Publication replaces the complete approved runtime and exact-reads provider HEAD before success.
5. OAuth refresh material and ephemeral access tokens are never committed, emitted as workflow outputs, or printed by release tooling.
6. The release workflow requires explicit fresh/disposable target confirmation so an accidental rerun cannot silently be treated as an upgrade path.
7. Activation creates/validates exactly one one-minute worker trigger before persisted `mutation_mode=queued_writer` becomes authoritative.
8. Activation creates the canonical `Commands` transport tab and persists queued-writer mode.
9. Submit one synthetic same-user API-001 `entity` upsert command with stable command/idempotency IDs and expected revision 0.
10. The actual Google time-driven worker processes the pending command under `ScriptLock`.
11. Success is recorded only after exact Resource + Idempotency readback; the new entity is revision 1 and matches submitted material.
12. Re-reading the command shows a durable succeeded result rather than assuming scheduler execution.
13. No independent direct-native canonical mutation path remains active after queued mode is authoritative.
14. Record only generic/synthetic provider evidence in public Git; provider IDs and OAuth material remain private session/release evidence.
15. Exact-head CI, expected-head merge, remote readback, and post-merge CI are required for source changes.
16. Reconcile the stale M2-M0-029 `HOST-CONNECT-EXEC-001` BACKLOG row before packet closure.
17. After live proof, mark `ANDROID-COMMAND-BOUNDARY-001` only to the evidence actually demonstrated and start `ANDROID-CLIENT-CORE-001`.

## Completed evidence

### Shared writer and activation

- PR #54: provider-neutral serialized command sequencer.
- PR #55: Workspace `Commands` inbox + `ScriptLock` worker, synthetic/fake-provider verified.
- PR #91 merged at `b6b7455422608dc0308f1e8634c33c2e7291e7d0`; exact-head CI `33547638096` and post-merge CI `33547715540` green. `Code.gs` exposes `MIRA → Enable Android / shared access` through the tested worker activation wrapper.

### Apps Script publication and private release authorization

- PR #92 merged at `bbea10ce0a4d52b3ddbe330621c9e5af37d9d5a9`; post-merge CI `33548158788` green. Direct Apps Script create/binding/content exact-readback protocol is test-verified.
- PR #93 merged at `f40e4801634a4da0450e3c94a7bbaad97137e14f`; exact-head CI `33550835232` green and post-merge CI `33550883206` green.
- `ops/publish_apps_script.py` now supports private clasp 3.x refresh credentials, exchanges them for an ephemeral access token without persisting/printing that token, independently verifies exact `Project.parentId`, and exact-verifies provider HEAD after update.
- `.github/workflows/publish-personal-apps-script.yml` is a fail-closed one-shot fresh-release workflow requiring explicit fresh-target confirmation and private release inputs. Provider mutation/readback delegates to the tested Python publisher.
- A current clasp source review caught and removed an unsafe CLI-output assumption: current `create-script --parentId` may bind correctly while its JSON `parentId` is absent. Binding is therefore read back through the Apps Script Project API.

### Fresh live Google proof target

A new disposable Google Sheet was created specifically for this packet. Its provider ID is intentionally not recorded in public Git.

Independent provider readback currently proves:

- title identifies it as the M2-M1-001 fresh disposable live-worker proof;
- timezone is `Etc/UTC`;
- tabs are `Metadata`, `Resources`, `Events`, and `Idempotency`; there is no `Commands` tab before activation;
- Metadata declares `schema_version=mira-structured-state-v1`, `environment=mira_2_sandbox`, `data_policy=synthetic_only`, `adapter_contract=STORE-001`, and `writer_model=single_writer`;
- Resources contains exactly one verified/enabled synthetic Google Sheets Authority and one `entity` Authority binding;
- Authority owner is the synthetic same-user subject `m1-live-synthetic-user`;
- no legacy production data is present.

## Evidence ceiling

- Provider-neutral serialized command semantics: test-verified.
- Workspace worker implementation: test-verified.
- Ordinary-user shared-access activation surface: merged/test-verified.
- Apps Script direct publication protocol: merged/test-verified.
- Private refresh-credential release path: merged/test-verified with exact-head and post-merge CI green.
- Fresh isolated Google canonical substrate: live provider readback verified.
- Actual authorized Apps Script API publication, trigger creation/firing, and queued command execution: **not yet live-verified**.

## Exact next action / resume point

1. Establish the one-time private maintainer Google authorization for Apps Script project scopes without exposing OAuth material to Git or ordinary-user setup. Prefer ChatGPT Work Cloud Browser/provider-native browser consent if available; only use a serverless clasp redirect handoff as the last-resort maintainer ceremony.
2. Feed the private authorization and fresh Sheet provider ID into the private release path and execute one publication; require exact parent + provider HEAD readback.
3. Open the fresh Sheet and invoke the only unavoidable ordinary-user-style action if the host cannot invoke the custom menu itself: `MIRA → Enable Android / shared access`.
4. Read back Commands + Metadata, submit one synthetic entity command, and verify actual worker result/Resource/Idempotency state.
5. Reconcile BACKLOG lifecycle evidence, close `ANDROID-COMMAND-BOUNDARY-001`, then start `ANDROID-CLIENT-CORE-001`.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Active work is `M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` on `governance/m1-001-live-auth-checkpoint`, based on green main `f40e4801634a4da0450e3c94a7bbaad97137e14f`. Source and release plumbing are merged and green; a fresh synthetic Google proof target is already prepared and read back. Resume at the one-time private Google Apps Script authorization boundary, then publish, activate shared access, and prove one real queued worker command. Never export Apps Script editing, trigger setup, copied provider IDs, or release credentials to ordinary Personal users.
