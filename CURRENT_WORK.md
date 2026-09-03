# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android extends the same canonical MIRA semantics and must never become a second provider/database/source authority or bypass the serialized shared command boundary.

`M2-M1-001` through `M2-M1-005` were already durably closed before this packet. `M2-M1-006` adds the deterministic default-Personal Workspace row protocol beneath the future native Android Google connection surface. It does not claim live Google authorization/network binding, physical-device behavior, or the full `ANDROID-SYNC` vertical.

Ordinary users still must not see Apps Script, copied spreadsheet IDs, OAuth scopes, developer consoles, terminal setup, or other developer ceremony.

## Prior-packet recovery verification — 2026-09-02

- Repository: `Matthew-Beare/Mira-2.0`.
- M2-M1-005 final authoritative `main`: `7562c247a471c6ebb27f77d8494054e7a54d52b1`.
- M2-M1-005 final closeout CI: `33701057632` — success on that exact head.
- M2-M1-001 through M2-M1-005 are durably closed and must not be rerun.

## Session-start alignment verification — 2026-09-02 M2-M1-006

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires native Android to reuse shared `API-001`, protected credentials, replay-safe synchronization and evidence-based provider capabilities without becoming canonical authority.
- `API-001` owns bounded commands, synchronization and verified canonical readback.
- `PROVIDER-002` preserves an ordinary-user Connect/Connected/Reconnect/Needs-attention/Disconnect experience and keeps provider mechanics out of setup.
- `RECOVERY-002` requires ambiguous network outcomes and duplicate transport delivery to converge safely without dropping pending work.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` remained the unfinished prerequisite before `ANDROID-SYNC`.
- M2-M1-002 through M2-M1-005 already provided client trust, protected credentials, encrypted offline state and provider-neutral reconnect orchestration.
- The dependency-correct M2-M1-006 slice was the concrete default-Personal Workspace transport protocol beneath `ReconnectCoordinator`.

### `ROADMAP.md`

- M2-M1 still requires Android to read and mutate the same canonical Personal reality without becoming a second authority.
- Live provider-bound Android canonical read, Android mutation, stock ChatGPT cross-readback and representative-device proof remained later evidence.

### `PRODUCT_INVARIANTS.md`

- The default Personal lane remains Google Workspace first and requires no server or terminal from ordinary users.
- OAuth/provider access material remains transport-local and does not enter `OfflineSyncStateStore` or become canonical identity.
- Historical proof resources and legacy MIRA production state remain protected.

### Direction result

**ALIGNED.** Implement only the Workspace row protocol, replay-safe duplicate physical delivery, verified canonical change projection and Android transport mapping. Do not absorb OAuth/Connections UI, live-provider proof, representative-device proof or the full `ANDROID-SYNC` vertical.

## Active packet

### `M2-M1-006` — Android client core, default-Personal Google Workspace transport protocol

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `PROVIDER-002`, `RECOVERY-002`, `STORE-001`, `AUTH-001`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Checkpoint branch:** `main`
- **Packet base/main SHA:** `7562c247a471c6ebb27f77d8494054e7a54d52b1`
- **Final verified PR head:** `f11e765da8e995957df7d77bb9b8163cbeebef25`
- **Final verified PR-head CI:** `33704935627` — success
- **PR:** #101 — merged with expected-head protection
- **Merge/main SHA before this closeout commit:** `30fe317ac11f2c573fcadaa484adb94c1ffc9339`
- **Verified post-merge CI:** `33705047103` — success on that exact merge SHA
- **Merged changed-file scope:** exactly 8 intended files
- **Status:** complete for this bounded source/build/test/repository-integration slice; this final closeout commit requires exact-head CI before durable closure

## Objective result

**COMPLETE AT THE BOUNDED SOURCE/BUILD/TEST/REPOSITORY-INTEGRATION EVIDENCE CEILING.**

M2-M1-006 now provides the concrete deterministic Workspace row protocol between the provider-neutral Android reconnect coordinator and the already-proven serialized Apps Script worker boundary:

1. append-only, nonauthoritative `Changes` projection derived from exact-readback-verified canonical `Resources`;
2. deterministic initial/recovery reconciliation of current canonical Resources into that projection;
3. exact duplicate physical `Commands` row convergence for at-least-once/ambiguous Sheets append outcomes;
4. fail-closed rejection of changed material under one `command_id`;
5. Android `GoogleWorkspaceTransport` implementing `ReconnectCoordinator.Transport` through a narrow injected `SheetsGateway`;
6. strict Commands/Changes schema, canonical JSON, status/result, change-hash, contiguous-sequence and opaque-cursor verification;
7. API-23-compatible production source and deterministic Android JVM verification; and
8. Android DEV-006 ownership coverage without weakening repository gates.

This does **not** complete `ANDROID-CLIENT-CORE-001`. The concrete Google authorization/network gateway, automatic Workspace discovery/binding, user-facing connection state, live Android canonical read/mutation, conflict presentation and representative-device evidence remain unfinished.

## Completed evidence

### Workspace worker / change projection

- `workspace/apps_script/CommandWorker.gs` now owns the append-only verified `Changes` projection under the same serialized worker lock as canonical command processing.
- Current canonical resources can seed/reconcile missing projection rows without making `Changes` authoritative.
- Projection replay is idempotent for exact canonical revision material and fails closed on contradictory same-version material.
- Exact duplicate physical command rows converge as one logical command when material matches; mismatched material fails closed.
- Deterministic Apps Script tests cover seed/reconcile, update projection, crash/retry recovery, exact duplicates and conflicting duplicates.

### Android Workspace transport

- Added `android-client/core/src/main/java/com/mira/client/core/sync/GoogleWorkspaceTransport.java`.
- The transport source owns no spreadsheet ID, Google account identity, OAuth token, provider URL or concrete Google client.
- Exact supported command intent maps to the existing Workspace `Commands` schema.
- Ambiguous append failure triggers exact readback before another append is permitted.
- Terminal success is returned only after exact logical identity, valid result material and `readback_verified=true`.
- Verified `Changes` rows require canonical payload material, matching SHA-256 `change_id`, contiguous sequence and verified readback before snapshots/cursor are exposed.
- Cursor tokens remain opaque to `ReconnectCoordinator`.
- API-24-only `Double.isFinite()` was removed before merge so declared minSdk 23 remains truthful.

### Deterministic Android verification

`GoogleWorkspaceTransportTest` covers:

- exact command mapping and single append;
- ambiguous append that actually landed;
- exact duplicate physical rows;
- duplicate command ID with changed material;
- pending/succeeded/failed command parsing;
- success without verified canonical readback;
- initial/incremental/no-op change paging;
- sequence gaps, unverified changes and tampered change hashes;
- malformed cursors and gateway failure; and
- unsupported command shape rejection before provider write.

### Repository / PR evidence

- Initial governance-only alignment failures were fixed without weakening the validator or changing product semantics.
- Fully corrected implementation head `d93a706064b100ee0e2bcae0934270d512b8a1f2` passed CI `33703880669` completely.
- Backlog-reconciliation head `c2b42050770fce73d841fa8be74a6fc37c750a75` passed CI `33704143863` completely.
- Final merge-candidate head `f11e765da8e995957df7d77bb9b8163cbeebef25` passed CI `33704935627` completely.
- PR #101 was open, non-draft, mergeable and exactly eight intended files at that verified head.
- PR #101 merged using expected-head protection.
- Remote `main` independently read back merge SHA `30fe317ac11f2c573fcadaa484adb94c1ffc9339`.
- Post-merge CI `33705047103` succeeded on that exact merge SHA with compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android tests, Python tests and Workspace Apps Script tests green.
- No live Google provider resource, Apps Script project, authorization flow, historical proof Sheet, Work mode session or legacy MIRA production state was accessed or modified.

## Acceptance criteria result

1. No live provider/resource/legacy-state access — **satisfied**.
2. Append-only, nonauthoritative, sequence-versioned change projection — **satisfied**.
3. Projection only from verified canonical Resources with seed/reconcile support — **satisfied**.
4. Projection replay idempotency and same-version contradiction failure — **satisfied**.
5. Opaque deterministic Android cursor handling — **satisfied**.
6. Strict malformed/unverified/noncontiguous change rejection — **satisfied**.
7. Lossless supported command-to-Workspace mapping — **satisfied**.
8. Local acknowledgement remains behind exact terminal verified readback — **satisfied**.
9. Exact duplicate physical command convergence and mismatched duplicate failure — **satisfied**.
10. Pending/terminal-failed states do not acknowledge locally — **satisfied**.
11. Ambiguous append readback convergence without second append — **satisfied**.
12. Required deterministic Apps Script coverage — **satisfied**.
13. Required deterministic Android JVM coverage — **satisfied**.
14. Android DEV-006 ownership without gate weakening — **satisfied**.
15. Existing Android/Python/Apps Script/governance CI — **satisfied**.
16. End-of-packet feature/backlog/roadmap alignment — **satisfied without marking the umbrella complete**.
17. Exact PR head/scope, merge/main readback and post-merge CI — **satisfied through merge head `30fe317ac11f2c573fcadaa484adb94c1ffc9339`; final closeout-head CI is the only remaining recovery gate**.

## Evidence ceiling

- **Implemented:** deterministic default-Personal Workspace row protocol, verified change projection, duplicate-delivery convergence and Android transport mapping.
- **Test verified:** deterministic Apps Script and Android JVM transport/recovery/protocol behavior, plus Android production compilation.
- **Integration verified:** PR exact-head and post-merge repository CI integrate this transport with existing Android/Python/Apps Script/governance gates.
- **Not provider/live/device verified:** Google Identity authorization, actual Sheets REST/SDK calls from Android, automatic Workspace resource discovery/binding, access-token lifecycle, physical-device execution, live Android command submission/readback, live canonical change synchronization, connection UI, conflict UI or stock-ChatGPT cross-readback.

## Session-end alignment verification — 2026-09-02 M2-M1-006

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partial. M2-M1-006 advances the concrete Workspace transport protocol only. `API-001` and `STORE-001` remain the canonical command/readback boundary and authority semantics; Android does not become canonical authority.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains unfinished. Its canonical status remains **partial** even though the narrative row still names M2-M1-006 as the active slice. At the next packet activation, reconcile that narrative to record M2-M1-006 complete before opening new work; do not promote the umbrella to complete.

The next dependency-correct bounded implementation slice is the Android-native Google authorization/network binding beneath `GoogleWorkspaceTransport`: acquire explicitly consented same-user Google authorization, discover/bind the intended MIRA Workspace resource automatically, and implement the narrow concrete Sheets gateway needed by the existing transport. Keep user-facing Connections polish, conflict UI, full `ANDROID-SYNC`, stock-ChatGPT cross-readback and representative-device proof separate unless they become hard acceptance dependencies.

### `ROADMAP.md`

M2-M1 ordering remains correct. The local/reconnect/Workspace protocol prerequisites now have implementation/test/repository evidence. Live provider-bound read/mutate/cross-readback/device proof remains unfinished and must not be inferred from deterministic transport tests.

### `PRODUCT_INVARIANTS.md`

The default Personal lane remains Google Workspace first, ordinary-user friendly and provider-consent driven. No server, copied IDs, Apps Script editor, developer console or terminal may become normal Android setup. Provider authorization material stays outside canonical/offline state.

### Direction result

**ALIGNED.** M2-M1-006 closes only the deterministic Workspace transport protocol. The next bounded slice should connect that protocol to Google authorization/network capability without silently expanding into the whole Android product vertical.

## Exact next action / resume point

1. Require CI on this final `main` closeout commit and verify it succeeds on the exact pushed head.
2. Independently read back remote `main` at that exact closeout head.
3. Once both are verified, treat M2-M1-006 as durably closed and never rerun its Workspace protocol/change-projection work.
4. Before opening M2-M1-007, re-read `CURRENT_WORK.md`, `BACKLOG.md`, `ROADMAP.md`, `FEATURES.md` and `PRODUCT_INVARIANTS.md`; reconcile the stale BACKLOG narrative for `ANDROID-CLIENT-CORE-001` while preserving overall partial status.
5. Open exactly one bounded continuation, likely `M2-M1-007`, for Android-native Google authorization + automatic Workspace discovery/binding + the concrete narrow Sheets gateway beneath `GoogleWorkspaceTransport`.
6. Do not absorb broad Connections UI polish, conflict-resolution UI, notifications/TTS, capture, release signing, full `ANDROID-SYNC`, stock-ChatGPT cross-readback or representative-device proof unless a hard dependency is discovered.
7. Do not touch historical M2-M1-001 proof resources or legacy MIRA production state. Any future live provider proof must use an explicitly authorized isolated/synthetic resource and a separate acceptance checkpoint.

## Recovery protocol

Read this file first. Verify remote `main` plus exact final closeout CI. If both are green on the same final head, M2-M1-006 is durably closed. Do not reconstruct or rerun M2-M1-001 through M2-M1-006 from chat history. Git remains authoritative.
