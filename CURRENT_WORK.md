# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must remain disabled; commands use the verified serialized shared command boundary.

Ordinary users must never be required to open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or accept maintainer/developer setup ceremony merely to enable Android/shared access. Release-grade shared access must use an obvious MIRA connection action and a clearly identified, appropriately verified provider consent surface.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be rerun. This packet advances only the first bounded Android client-core trust slice.

## Session-start alignment verification — 2026-09-02 M2-M1-002

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires an Android native client adapter over `API-001`, protected client credentials, replay-safe offline sync, and evidence-based capabilities.
- `API-001` remains the authenticated service boundary in front of `AUTH-001` / `STORE-001`; Android must never become a provider, datastore, or source authority.
- Same-user core behavior depends on `AUTH-001`, `STORE-001`, `RECOVERY-002`, and `API-001`; cross-person permission semantics remain deferred unless a request actually crosses a sharing boundary.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is complete at its bounded live Google evidence ceiling.
- `ANDROID-CLIENT-CORE-001` is the exact next unblocked prerequisite before `ANDROID-SYNC`.
- The umbrella work includes enrollment/session identity, revocation, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback. This packet implements only the first trust-boundary slice.

### `ROADMAP.md`

- M2-M1 orders scoped/revocable client identity and protected durable credentials before offline queue/reconnect synchronization and before the Android shared-state vertical.
- Notifications/TTS, capture, release signing, and broader UI remain later evidence layers.

### `PRODUCT_INVARIANTS.md`

- Provider connection/activation remains intent-first and nontechnical for ordinary users.
- Android must reuse the same provider-neutral connection/service state semantics, not invent a second activation model.
- No provider credential, Google resource identifier, or maintainer setup ceremony belongs in the Android client-core contract.

### Direction result

**ALIGNED.** The smallest dependency-correct first slice is the same-user client enrollment/session trust boundary: stable client identity, least-privilege grants, revocable session state, opaque credential material, and reconstruction of an `AuthenticatedPrincipal` only while the session is active. Android OS-protected storage and offline synchronization remain later bounded slices.

## Active packet

### `M2-M1-002` — Android client core, enrollment/session trust slice

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `work/m2-m1-002-android-client-core`
- **Base SHA:** `acb690e66f42bdf02d9030dc0ead0d3d42195e57`
- **Verified implementation head:** `fd5bb8d8da454a51b3f7ae264315600112e217d9`
- **Status:** bounded implementation/test slice complete; final documentation checkpoint, merge, main readback, and post-merge CI remain

## Objective result

**IMPLEMENTED AND TEST-VERIFIED FOR THIS BOUNDED SLICE.** The provider-neutral client session trust seam now issues a one-time opaque credential, stores only a verifier, binds explicit least-privilege API grants to a stable client identity, reconstructs the existing `AuthenticatedPrincipal` only for an active exact credential, and revokes the client session fail-closed and idempotently.

This does **not** complete the full `ANDROID-CLIENT-CORE-001` umbrella. Android Keystore integration, offline queue, reconnect/cursor synchronization, transport, bounded client reads/commands, conflict/readback presentation, and device evidence remain unimplemented.

## Feature alignment

### User-visible behavior enabled downstream

- A MIRA Android installation can be represented as a distinct revocable same-user client rather than embedding provider/database credentials or receiving blanket authority.
- Revoking one client session can disable that client without mutating canonical user data or provider resources.
- Least-privilege grants flow into the existing API authorization semantics instead of creating Android-specific policy.

### Preserved invariants

- `API-001` remains the policy/data service boundary for Android reads and commands.
- The verified queued-writer boundary remains authoritative for concurrent canonical mutation.
- Same-user scope remains fail-closed; no cross-person authorization was introduced.
- No provider credentials, OAuth tokens, Google IDs, private account data, or legacy production data entered public Git or tests.
- Ordinary-user connection/onboarding requirements remain unchanged and are not falsely claimed complete by this developer trust primitive.

### Explicitly deferred

- Android Keystore/OS-protected credential adapter and representative-device proof.
- Replay-safe offline command queue.
- Reconnect/cursor synchronization.
- Android network transport for bounded reads and queued commands.
- Conflict/readback presentation in the client.
- Native Connections UI and verified provider-consent experience.
- `ANDROID-SYNC`, native delivery, capture, and release evidence.

## Acceptance criteria result

1. Stable actor/client enrollment with explicit grants — **satisfied**.
2. One-time opaque credential with verifier-only stored state — **satisfied**.
3. Correct active credential reconstructs exact principal; wrong credential fails closed — **satisfied**.
4. Revocation immediately blocks authentication and is idempotent/readback-verifiable — **satisfied**.
5. Existing `API-001` grant validation remains authoritative with no bypass — **satisfied**.
6. Same-user actor identity remains explicit and no cross-person grant is implied — **satisfied**.
7. Deterministic tests cover issuance, non-retention, authentication, denial, revocation, exact grants, and duplicate identity — **satisfied**.
8. Existing repository/API/command/Workspace regressions remain green — **satisfied at verified implementation head**.
9. Lifecycle documentation remains honest; no semantic `FEATURES.md`, `BACKLOG.md`, or `ROADMAP.md` change is required because the umbrella work remains incomplete — **satisfied**.
10. Branch push/exact-head CI succeeded; merge/main readback/post-merge CI remain — **partially satisfied pending closeout**.

## Completed evidence

- Remote starting `main` was verified at `acb690e66f42bdf02d9030dc0ead0d3d42195e57`; prior CI `33681423055` was `success` on that exact SHA.
- `mira/api_core.py` contains `ClientSessionRegistry`, `ClientEnrollment`, verifier-only `ClientSessionSnapshot`, and `ApiAuthenticationError`.
- `tests/test_client_sessions.py` covers credential non-retention, exact principal reconstruction, wrong-credential denial, immediate/idempotent revocation, duplicate client conflict, existing grant validation, and explicit same-user identity.
- PR #97 contains only `CURRENT_WORK.md`, `mira/api_core.py`, and `tests/test_client_sessions.py` through the verified implementation head.
- Initial CI `33682369413` correctly failed the mechanical work-session gate because the packet record used `Primary feature` instead of required `Primary features`; the gate was fixed by correcting metadata, not weakened.
- Exact implementation-head CI `33682452491` completed successfully on `fd5bb8d8da454a51b3f7ae264315600112e217d9`. Compile, feature registry, product lifecycle ledger, Personal distribution, work-session alignment, code ownership, Python unit tests, and Workspace Apps Script tests all passed.
- No Google provider resource, Apps Script project, disposable proof Sheet, or legacy production state was accessed or modified in this packet.

## Session-end alignment verification — 2026-09-02 M2-M1-002

### `FEATURES.md`

`CLIENT-ANDROID-001` remains only partially implemented. This trust primitive strengthens its scoped/revocable credential boundary without claiming Android storage, sync, UI, transport, or device evidence. `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` semantics remain preserved.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains the active umbrella work item because later slices are still unfinished. No completed-work status change is warranted. The next dependency-correct slice is OS-protected Android credential storage wired to the trust contract implemented here; replay-safe offline synchronization remains after that.

### `ROADMAP.md`

M2-M1 ordering remains correct. This slice advances step 2 without skipping into step 3 or the `ANDROID-SYNC` vertical. Provider onboarding hardening remains a release requirement, not part of this trust primitive.

### Direction result

**ALIGNED.** The implementation preserves the canonical shared-writer/API boundary, does not expand scope into the Android app, and leaves downstream Android work structurally possible.

## Exact next action / resume point

1. Commit this final packet evidence checkpoint on PR #97 and require exact-head CI.
2. Verify PR #97 still changes only `CURRENT_WORK.md`, `mira/api_core.py`, and `tests/test_client_sessions.py` and is mergeable at the exact green head.
3. Merge PR #97 using the exact verified head SHA.
4. Read back remote `main` and verify post-merge CI on that exact main head.
5. Persist final merge/main/CI evidence in Git before calling `M2-M1-002` fully closed.
6. Do not begin the next Android slice until this closeout is durable.

## Recovery protocol

Read this file first, then verify PR #97 / branch / remote `main`. Do not rerun `M2-M1-001`, Google authorization, Apps Script publication, or provider proof. If the final evidence checkpoint is not yet merged, continue from the exact next action above.
