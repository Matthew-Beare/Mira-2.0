# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must remain disabled; commands use the verified serialized shared command boundary.

Ordinary users must never be required to open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or accept maintainer/developer setup ceremony merely to enable Android/shared access. Release-grade shared access must use an obvious MIRA connection action and a clearly identified, appropriately verified provider consent surface.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be rerun. This packet begins the Android client core without touching Google provider proof resources or legacy production data.

## Session-start alignment verification — 2026-09-02 M2-M1-002

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires an Android native client adapter over `API-001`, protected client credentials, replay-safe offline sync, and evidence-based capabilities.
- `API-001` remains the authenticated service boundary in front of `AUTH-001` / `STORE-001`; Android must never become a provider, datastore, or source authority.
- Same-user core behavior depends on `AUTH-001`, `STORE-001`, `RECOVERY-002`, and `API-001`; cross-person permission semantics remain deferred unless a request actually crosses a sharing boundary.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is complete at its bounded live Google evidence ceiling.
- `ANDROID-CLIENT-CORE-001` is the exact next unblocked prerequisite before `ANDROID-SYNC`.
- The full work item includes enrollment/session identity, revocation, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback. One packet must not attempt that entire surface.

### `ROADMAP.md`

- M2-M1 explicitly orders scoped/revocable client identity and protected durable credentials before offline queue/reconnect synchronization and before the Android shared-state vertical.
- Notifications/TTS, capture, release signing, and broader UI remain later evidence layers unless required by this core boundary.

### `PRODUCT_INVARIANTS.md`

- Provider connection/activation remains intent-first and nontechnical for ordinary users.
- Android must reuse the same provider-neutral connection/service state semantics, not invent a second activation model.
- No provider credential, Google resource identifier, or maintainer setup ceremony belongs in the Android client-core contract.

### Direction result

**ALIGNED.** The smallest dependency-correct first slice is the same-user client enrollment/session trust boundary: stable client identity, least-privilege grants, revocable session state, opaque credential material, and reconstruction of an `AuthenticatedPrincipal` only while the session is active. Offline queue/cursor sync and Android Keystore integration are intentionally deferred to later bounded slices of `ANDROID-CLIENT-CORE-001`.

## Active packet

### `M2-M1-002` — Android client core, enrollment/session trust slice

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-002-android-client-core`
- **Base SHA:** `acb690e66f42bdf02d9030dc0ead0d3d42195e57`
- **Current head SHA:** `928a730a6daa383a98129ae1ee3a85e1a9ad7dae` before this metadata-fix commit
- **Status:** active; implementation and tests are present, exact-head green CI still required

## Objective

Implement the first Android-client prerequisite below UI and transport: a provider-neutral same-user enrollment/session registry that issues one opaque client credential, stores only its verifier, binds least-privilege API grants to a stable client identity, reconstructs the existing `AuthenticatedPrincipal` only for an active matching credential, and revokes sessions fail-closed.

This slice deliberately does **not** implement Android UI, Android Keystore calls, offline queue persistence, reconnect/cursor sync, command transport, provider connection UI, notifications/TTS, hardware capture, or release packaging. It creates the server/client trust seam those later slices depend on.

## Feature alignment

### User-visible behavior enabled downstream

- A MIRA Android installation can eventually enroll as a distinct revocable client instead of embedding provider/database credentials or inheriting blanket authority.
- Revoking one client session can disable that client without changing canonical user data or provider resources.
- Least-privilege grants can be carried into the already-verified API authorization path.

### Must preserve

- `API-001` remains the only policy/data service boundary for Android reads and commands.
- The queued-writer boundary remains authoritative for concurrent canonical mutation.
- Same-user scope remains fail-closed; no cross-person authorization is introduced.
- No provider credentials, OAuth tokens, Google IDs, private account data, or legacy production data enter public Git or synthetic tests.
- Ordinary-user connection/onboarding requirements remain unchanged and are not falsely claimed complete by this developer-facing trust primitive.

### Explicitly deferred

- Android Keystore/EncryptedSharedPreferences adapter and device-backed proof.
- Replay-safe offline command queue.
- Reconnect/cursor synchronization.
- Android network transport for bounded reads and queued commands.
- Conflict/readback presentation in the client.
- Native Connections UI and verified provider-consent experience.
- `ANDROID-SYNC`, native delivery, capture, and release evidence.

## Acceptance criteria

1. A deterministic provider-neutral enrollment registry creates a stable `client_id` for one actor and a session bound to explicit `Grant` values.
2. Enrollment returns opaque credential material only at creation; stored session state retains only a cryptographic verifier, never the raw credential.
3. Authentication with the correct active credential reconstructs an `AuthenticatedPrincipal` containing the exact actor/client/grants; an incorrect credential fails closed.
4. Revocation immediately prevents subsequent authentication and is idempotent/readback-verifiable.
5. Invalid/overbroad grants continue to use existing `API-001` grant validation; no new bypass around `_validate_principal` or `ApiService._authorize` is introduced.
6. Same-user identity remains explicit: the session actor is the principal actor and does not grant cross-person access.
7. Tests prove successful enrollment/authentication, wrong-secret denial, revocation denial/idempotency, exact grant reconstruction, and absence of raw credential material from stored session snapshots.
8. Existing API, command-sequencer, Workspace, and repository integrity tests remain green.
9. `CURRENT_WORK.md` records implementation/test evidence and exact next slice; `BACKLOG.md` / `ROADMAP.md` are changed only if lifecycle or milestone wording actually requires it.
10. Branch is pushed, remote head is read back, CI succeeds on that exact pushed head, and no provider/browser proof is invoked.

## Completed evidence

- Session-start Git authority review is complete and direction is `ALIGNED`.
- Remote `main` was verified at `acb690e66f42bdf02d9030dc0ead0d3d42195e57`.
- Prior exact-main CI run `33681423055` was verified `success`.
- `mira/api_core.py` now contains the provider-neutral `ClientSessionRegistry`, one-time `ClientEnrollment`, verifier-only `ClientSessionSnapshot`, and explicit `ApiAuthenticationError`.
- `tests/test_client_sessions.py` covers credential non-retention, exact principal reconstruction, wrong-credential denial, immediate/idempotent revocation, duplicate client conflict, grant validation, and explicit same-user identity.
- PR #97 contains exactly `CURRENT_WORK.md`, `mira/api_core.py`, and `tests/test_client_sessions.py` at the first implementation head.
- CI run `33682369413` reached the work-session alignment gate and failed only because this packet record used `Primary feature` instead of the mechanically required `Primary features`; compile, feature registry, product ledger, and Personal distribution gates were already green. Code/unit tests were not reached in that run.
- No Google provider resource, Apps Script project, disposable proof Sheet, or legacy production state has been accessed or modified in this packet.

## Exact next action / resume point

1. Push this packet-record fix and require a new exact-head CI run.
2. If any code/test gate fails, fix only the bounded trust-slice defect and rerun.
3. When exact-head CI is green, record final evidence and session-end alignment without expanding scope.
4. Merge the bounded PR using the verified head, read back `main`, and verify post-merge CI.
5. The next packet/slice after closure is Android OS-protected credential storage wired to this trust contract; offline queue/cursor sync remains after that.

## Recovery protocol

Read this file first, then verify the branch/head from remote Git. Do not rerun `M2-M1-001`, Google authorization, Apps Script publication, or provider proof. Continue only the bounded enrollment/session trust slice until its acceptance criteria are satisfied or a hard dependency is discovered.
