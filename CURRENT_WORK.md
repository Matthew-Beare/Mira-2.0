# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must remain disabled; commands use the verified serialized shared command boundary.

Ordinary users must never be required to open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or accept maintainer/developer setup ceremony merely to enable Android/shared access. Release-grade shared access must use an obvious MIRA connection action and a clearly identified, appropriately verified provider consent surface.

`M2-M1-001` / `ANDROID-COMMAND-BOUNDARY-001` is complete and must not be rerun. `M2-M1-002` completes only the first bounded `ANDROID-CLIENT-CORE-001` trust slice; the umbrella Android client core remains incomplete.

## Session-start alignment verification — 2026-09-02 M2-M1-002

### `FEATURES.md`

- `CLIENT-ANDROID-001` requires an Android native client adapter over `API-001`, protected client credentials, replay-safe offline sync, and evidence-based capabilities.
- `API-001` remains the authenticated service boundary in front of `AUTH-001` / `STORE-001`; Android must never become a provider, datastore, or source authority.
- Same-user core behavior depends on `AUTH-001`, `STORE-001`, `RECOVERY-002`, and `API-001`; cross-person permission semantics remain deferred unless a request crosses a sharing boundary.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is complete at its bounded live Google evidence ceiling.
- `ANDROID-CLIENT-CORE-001` remains the uncompleted umbrella prerequisite before `ANDROID-SYNC`.
- Its first trust slice is bounded to enrollment/session identity and revocation; OS-protected storage, bounded Android reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact client readback remain later slices.

### `ROADMAP.md`

- M2-M1 orders scoped/revocable client identity and protected durable credentials before offline queue/reconnect synchronization and before the Android shared-state vertical.
- Notifications/TTS, capture, release signing, and broader UI remain later evidence layers.

### `PRODUCT_INVARIANTS.md`

- Provider connection/activation remains intent-first and nontechnical for ordinary users.
- Android must reuse the same provider-neutral connection/service-state semantics, not invent a second activation model.
- No provider credential, Google resource identifier, or maintainer setup ceremony belongs in the Android client-core contract.

### Direction result

**ALIGNED.** The smallest dependency-correct first slice is the same-user client enrollment/session trust boundary. Android OS-protected storage and offline synchronization remain later bounded slices.

## Active packet

### `M2-M1-002` — Android client core, enrollment/session trust slice

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `PROVIDER-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `work/m2-m1-002-android-client-core`
- **Base SHA:** `acb690e66f42bdf02d9030dc0ead0d3d42195e57`
- **Final PR head:** `6b7f8f5d9334143b3d92b0b53c31d168ec06ae57`
- **Merge:** PR #97
- **Merge/main SHA:** `0bcde9955d80222b5ae6973148c4f8349bb4a2e3`
- **Status:** complete for this bounded trust slice; closeout CI on the final documentation checkpoint remains the only incomplete action

## Objective result

**COMPLETE FOR THIS BOUNDED SLICE.** The provider-neutral client session trust seam now issues a one-time opaque credential, stores only a cryptographic verifier, binds explicit least-privilege API grants to a stable client identity, reconstructs the existing `AuthenticatedPrincipal` only for an active exact credential, and revokes the client session fail-closed and idempotently.

This does **not** complete the full `ANDROID-CLIENT-CORE-001` umbrella. Android Keystore/OS-protected credential storage, offline queue, reconnect/cursor synchronization, Android transport, bounded client reads/commands, conflict/readback presentation, and representative-device evidence remain unimplemented.

## Acceptance criteria result

1. Stable actor/client enrollment with explicit grants — **satisfied**.
2. One-time opaque credential with verifier-only stored state — **satisfied**.
3. Correct active credential reconstructs exact principal; wrong credential fails closed — **satisfied**.
4. Revocation immediately blocks authentication and is idempotent/readback-verifiable — **satisfied**.
5. Existing `API-001` grant validation remains authoritative with no bypass — **satisfied**.
6. Same-user actor identity remains explicit and no cross-person grant is implied — **satisfied**.
7. Deterministic tests cover issuance, non-retention, authentication, denial, revocation, exact grants, and duplicate identity — **satisfied**.
8. Existing repository/API/command/Workspace regressions remain green — **satisfied**.
9. No semantic `FEATURES.md`, `BACKLOG.md`, or `ROADMAP.md` status change is required because the umbrella work remains incomplete — **satisfied**.
10. Exact PR head, merge/main readback, and post-merge CI are verified — **satisfied**; final documentation-only exact-head CI remains pending.

## Completed evidence

- Starting remote `main` was verified at `acb690e66f42bdf02d9030dc0ead0d3d42195e57`; prior CI `33681423055` was `success` on that exact SHA.
- `mira/api_core.py` now contains `ClientSessionRegistry`, `ClientEnrollment`, verifier-only `ClientSessionSnapshot`, and `ApiAuthenticationError`.
- `tests/test_client_sessions.py` verifies credential non-retention, exact principal reconstruction, wrong-credential denial, immediate/idempotent revocation, duplicate client conflict, existing grant validation, and explicit same-user identity.
- Initial CI `33682369413` correctly caught malformed packet metadata at the alignment gate. The gate was not weakened.
- Exact implementation-head CI `33682452491` succeeded on `fd5bb8d8da454a51b3f7ae264315600112e217d9`.
- Final PR-head CI `33682614270` succeeded on `6b7f8f5d9334143b3d92b0b53c31d168ec06ae57`, including compile, feature registry, product lifecycle ledger, Personal distribution, work-session alignment, code ownership, Python unit tests, and Workspace Apps Script tests.
- PR #97 was verified mergeable with exactly three changed files: `CURRENT_WORK.md`, `mira/api_core.py`, and `tests/test_client_sessions.py`.
- PR #97 merged successfully. Remote `main` read back exactly `0bcde9955d80222b5ae6973148c4f8349bb4a2e3`.
- Post-merge CI `33682666624` succeeded on exact merge/main SHA `0bcde9955d80222b5ae6973148c4f8349bb4a2e3`; every repository gate passed.
- Documentation closeout commit `1d0e9d02ffb2f2e332b731339bd7f99dd236ec3f` failed only the work-session alignment gate because this file renamed the required heading `## Active packet` to `## Recovery packet`. Compile, feature registry, product ledger, and Personal distribution passed before that gate. The parser contract is preserved; this checkpoint restores the required heading.
- No Google provider resource, Apps Script project, disposable proof Sheet, provider authorization flow, or legacy MIRA production state was accessed or modified in this packet.

## Session-end alignment verification — 2026-09-02 M2-M1-002

### `FEATURES.md`

`CLIENT-ANDROID-001` remains partially implemented. This trust primitive satisfies only the scoped/revocable enrollment/session identity seam and does not claim Android storage, sync, UI, transport, provider connection, or device evidence. `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` semantics remain preserved.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` remains incomplete because its later slices are unfinished. No completed umbrella status is recorded. The next dependency-correct slice is Android OS-protected credential storage wired to the trust contract completed here; replay-safe offline synchronization follows after that.

### `ROADMAP.md`

M2-M1 ordering remains correct. This packet advances step 2 without skipping into offline synchronization or `ANDROID-SYNC`. The ordinary-user verified provider connection experience remains a later release requirement and was not conflated with this developer-facing trust primitive.

### Direction result

**ALIGNED.** The bounded implementation preserves the verified queued-writer/API architecture, makes revocation possible without provider mutation, avoids direct-Google Android authority, and leaves the remaining Android client-core work structurally possible.

## Exact next action / resume point

1. Verify this corrected documentation-only closeout commit as the new remote `main` head and require exact-head CI to succeed.
2. After that CI is green, `M2-M1-002` is durably closed. Do not reopen it or rerun any Google proof.
3. In the next development session, open exactly one new bounded Android client-core packet for Android OS-protected credential storage wired to `ClientSessionRegistry` / enrollment material, with no offline queue or UI scope unless required by its acceptance criteria.
4. Preserve the ordinary-user requirement: normal Android/provider enablement eventually uses an obvious MIRA Connect/Enable action and appropriately verified provider consent; maintainer scripts, Apps Script recovery, copied IDs, terminals, and scary developer consent are never the shipped default flow.

## Recovery protocol

Read this file first and verify remote `main` plus the exact-head CI for this closeout commit. If green, treat `M2-M1-002` as complete and start no work from chat reconstruction. Select the next bounded packet from the still-incomplete `ANDROID-CLIENT-CORE-001` umbrella only after the normal session-start Git alignment gate.
