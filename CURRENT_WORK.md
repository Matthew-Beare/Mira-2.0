# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Prior packet recovery verification — 2026-09-02

- Repository: `Matthew-Beare/Mira-2.0`.
- Authoritative base `main`: `7562c247a471c6ebb27f77d8494054e7a54d52b1`.
- M2-M1-005 final closeout CI: `33701057632` — success on that exact head.
- `M2-M1-001` through `M2-M1-005` are durably closed and must not be rerun.
- No Google provider resource or legacy MIRA production state was accessed while recovering or implementing this packet.

## Session-start alignment verification — 2026-09-02 M2-M1-006

- `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, `PRODUCT_INVARIANTS.md`, and the established Workspace command-boundary architecture were read before implementation.
- The dependency-correct next slice was the concrete default-Personal Workspace transport beneath the already-complete client trust, protected credential, offline-state, and provider-neutral reconnect layers.
- The packet was bounded away from OAuth/Connections UI, live Google/provider proof, representative-device proof, and the full `ANDROID-SYNC` vertical.
- Direction result at activation: **ALIGNED**.

## Active packet

### `M2-M1-006` — Android client core, default-Personal Google Workspace transport protocol

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `PROVIDER-002`, `RECOVERY-002`, `STORE-001`, `AUTH-001`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-006-google-workspace-transport`
- **Base SHA:** `7562c247a471c6ebb27f77d8494054e7a54d52b1`
- **Pre-closeout evidence head:** `c2b42050770fce73d841fa8be74a6fc37c750a75`
- **Status:** merge candidate; umbrella `ANDROID-CLIENT-CORE-001` remains incomplete

## Objective

Implement the deterministic default-Personal Google Workspace transport seam beneath the future Android Google authorization surface, without live provider access:

1. append-only, nonauthoritative verified `Changes` projection derived from canonical `Resources` under the serialized Apps Script worker lock;
2. initial/recovery reconciliation of existing canonical Resources into that projection;
3. exact duplicate physical `Commands` row convergence for ambiguous Sheets append outcomes while mismatched duplicates fail closed;
4. Android `ReconnectCoordinator.Transport` mapping through a narrow injected `SheetsGateway` with no provider IDs or OAuth material;
5. strict Commands/Changes header, row, status, result, hash and opaque-cursor validation;
6. deterministic Apps Script and Android JVM verification only.

## User-visible behavior enabled

This packet is infrastructure for the later simple Android **Connect Google** experience. It makes the transport protocol safe for reconnect after an ambiguous append or connectivity loss without duplicating a logical canonical mutation or silently skipping verified canonical changes. It does not ship end-user connection UI.

## Preserved invariants

- Canonical state remains `single sequencer → API-001 → Authority Registry → STORE-001 → exact readback`.
- `Commands` and `Changes` are transport/read evidence, never canonical authority.
- Same-user Personal semantics remain; cross-person/family scope is still blocked.
- Android source contains no spreadsheet/provider resource identifier and `OfflineSyncStateStore` contains no OAuth/provider secret.
- Historical M2-M1-001 disposable proof resources and all legacy MIRA production data remain untouched.
- Advanced Cloud Run transport remains an optional advanced profile, not the default Personal Android path.
- Ordinary users are not exposed to Apps Script, copied IDs, developer consoles, OAuth scopes, or terminal setup by this packet.

## Explicitly deferred

- Google Identity Services consent/account-picker implementation.
- Drive/Sheets discovery and automatic resource binding.
- Real Sheets REST/SDK network gateway and access-token lifecycle.
- Android Connections UI and reconnect/disconnect presentation.
- Broad canonical read/domain UI and conflict-resolution UI.
- Physical Android device/provider proof.
- Stock ChatGPT cross-readback vertical proof (`ANDROID-SYNC`).
- Notifications/TTS, capture, release signing and broader Android polish.
- Any legacy-production migration.

## Acceptance result

1. **PASS** — no live provider/resource/legacy-state access was used.
2. **PASS** — `Changes` is append-only, nonauthoritative and strictly sequence-versioned.
3. **PASS** — projection material originates from exact-readback-verified canonical Resources and current canonical state can seed/reconcile missing projection rows under the worker lock.
4. **PASS** — same canonical revision projection is idempotent; contradictory same-version material fails closed.
5. **PASS** — Android cursor tokens are opaque outside the Workspace transport; null/empty paging is deterministic.
6. **PASS** — malformed/unverified/noncontiguous change material fails closed.
7. **PASS** — supported exact command intent maps losslessly to the Workspace Commands schema.
8. **PASS** — local acknowledgement remains owned by existing `ReconnectCoordinator` verified-success semantics.
9. **PASS** — exact duplicate physical command rows converge; changed material under one command ID fails closed.
10. **PASS** — pending and terminal-failed states do not cause local acknowledgement.
11. **PASS** — ambiguous append tests prove readback convergence without a second append.
12. **PASS** — Apps Script tests cover seed/reconcile, update projection, crash/retry recovery and duplicate delivery behavior.
13. **PASS** — Android JVM tests cover row mapping, pending/success/failure parsing, change paging/cursors, malformed provider data and ambiguous transport outcomes.
14. **PASS** — Android DEV-006 ownership covers the new transport without weakening gates.
15. **PASS** — compile, feature registry, lifecycle, distribution, alignment, ownership, Android, Python and Apps Script gates are green on exact pre-closeout evidence head.
16. **PASS** — end-of-packet canonical alignment is recorded below; the umbrella remains incomplete.
17. **PENDING CLOSEOUT ONLY** — exact merge/main readback and post-merge CI must still be verified before durable closure.

## Completed evidence

- Workspace worker source/test checkpoint: `c0c44c7...7013f`.
- Android transport source checkpoint: `843c48e...f9a02`.
- PR #101 opened for the bounded packet.
- Initial PR CI `33703372121` correctly stopped at the work-session alignment gate because `CURRENT_WORK.md` used the wrong canonical field label. The gate was not weakened.
- Corrected head `e9df3093cea2d4dbac2d471046f9b82dda6aeea7` passed CI `33703713828` completely.
- API-23 compatibility correction replaced the API-24-only finite-number convenience call.
- Fully corrected implementation head `d93a706064b100ee0e2bcae0934270d512b8a1f2` passed CI `33703880669` completely.
- Canonical backlog drift was corrected without marking `ANDROID-CLIENT-CORE-001` complete.
- Pre-closeout evidence head `c2b42050770fce73d841fa8be74a6fc37c750a75` passed CI `33704143863` completely.
- CI `33704143863` green steps include compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android client core unit tests, Python tests and Workspace Apps Script tests.
- PR #101 at pre-closeout evidence head is open, non-draft and based on `main` `7562c247a471c6ebb27f77d8494054e7a54d52b1`.
- Exact bounded PR file set before this evidence checkpoint:
  - `BACKLOG.md`
  - `CURRENT_WORK.md`
  - `android-client/core/build.gradle.kts`
  - `android-client/core/src/main/java/com/mira/client/core/sync/GoogleWorkspaceTransport.java`
  - `android-client/core/src/test/java/com/mira/client/core/sync/GoogleWorkspaceTransportTest.java`
  - `project/android_code_ownership.json`
  - `tests/apps_script/workspace_worker.test.js`
  - `workspace/apps_script/CommandWorker.gs`
- Evidence-only checkpoint `b290c334dcda36b456dfa9979562c58bdd13499c` reached CI `33704631432`; compile/registry/lifecycle/distribution were green, then alignment correctly rejected the missing required `## Session-start alignment verification` heading. This commit restores that required heading without altering product code.

## End-of-packet alignment verification — 2026-09-02

### `FEATURES.md`

- `CLIENT-ANDROID-001` remains required and partial. This packet advances its concrete default-Personal transport prerequisite but does not prove a live Android/provider vertical.
- `API-001`, `STORE-001` and `RECOVERY-002` remain the authority/readback/recovery semantics; the Workspace adapter does not redefine them.
- `PROVIDER-002` still requires an ordinary-user native connection flow and automated post-consent verification. Those user-facing/provider authorization requirements are deliberately not claimed here.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` is correctly recorded as partial through M2-M1-005 with M2-M1-006 as the active concrete Workspace transport slice; the stale claim that no Android implementation existed was removed.
- The umbrella remains unfinished after this packet because real provider authorization/network binding, a bounded live canonical read/mutation vertical, conflict presentation and representative-device proof remain.
- `ANDROID-SYNC` remains the dependency-following vertical rather than being silently folded into this packet.

### `ROADMAP.md`

- The milestone intent remains unchanged: Android must read and mutate the same canonical Personal reality without becoming a second authority.
- M2-M1 steps 2 and 3 now have substantially more implementation/test evidence than the older roadmap narrative states: client identity/protected credential work, durable offline state, reconnect orchestration and the concrete Workspace row protocol are implemented/test-verified.
- The remaining milestone proof is still live provider-bound Android canonical read, Android mutation through the shared boundary, stock ChatGPT cross-readback and representative-device evidence. No completion claim is made for those steps.

### Result

**ALIGNED FOR MERGE.** The packet advances only the dependency-correct transport layer and preserves the accepted product direction. No unrelated feature work, provider ceremony, live Google proof, or legacy-state mutation was absorbed.

## Exact next action / resume point

1. Read back this branch head and verify CI on the exact evidence-checkpoint commit containing this file.
2. Re-read PR #101 exact head, mergeability and changed-file scope.
3. Merge PR #101 only if the exact head is green and scope remains bounded.
4. Independently read back remote `main` at the merge SHA.
5. Verify post-merge `main` CI on that exact SHA.
6. Write the final Git-backed M2-M1-006 closure checkpoint on `main`, keeping `ANDROID-CLIENT-CORE-001` incomplete and identifying the next bounded dependency-correct slice.

## Recovery protocol

Read this file first and verify branch/main heads before continuing. Do not rerun M2-M1-001 through M2-M1-005. Do not access Google provider state or Work mode merely to close deterministic transport code.
