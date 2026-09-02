# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace with no external infrastructure prerequisite. When Android or another software writer is enabled, direct independent Google Sheets mutation must stop; commands use the serialized shared command boundary.

Ordinary users must not open Apps Script, paste code, manage triggers, copy provider IDs, run a terminal, or understand queued-writer internals merely to enable Android/shared access. The private updater, bound-project recovery, and alarming unverified/developer Google consent shown during this proof are maintainer/development ceremony only. They are not an acceptable shipped onboarding path. Release-grade shared access must use an obvious MIRA connection action and a clearly identified, appropriately verified provider consent surface.

Pre-Android feature growth remains frozen. The shared-writer proof is now complete at its live Google evidence ceiling; `ANDROID-CLIENT-CORE-001` is the exact next work item, but it is not implemented or activated by this checkpoint.

## Session-start alignment verification — 2026-09-02 M2-M1-001 closure

### `FEATURES.md`

- `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, and `RECOVERY-002` require one safe shared canonical mutation boundary rather than independent read-then-write clients.
- The live proof closes the command-boundary prerequisite only. It does not claim Android enrollment, credentials, sync, UI, release packaging, or representative-device evidence.
- `ONBOARD-006` still forbids technical setup as the ordinary Personal product path; the development-only Google ceremony observed here does not satisfy that release requirement.

### `BACKLOG.md`

- `ANDROID-COMMAND-BOUNDARY-001` is complete at implemented, test, integration, and live isolated Google-provider evidence levels.
- `ANDROID-CLIENT-CORE-001` is now unblocked and is the exact next packet, with no Android implementation claimed yet.
- The stale `HOST-CONNECT-EXEC-001` row is reconciled to its completed M2-M0-029 / PR #90 evidence ceiling.

### `ROADMAP.md`

- M2-M1 is no longer blocked on a concurrency architecture or live Workspace worker proof.
- Android client core is next; broader Android sync, native delivery, capture, and release work remain later evidence layers.

### Direction result

**ALIGNED.** Close only M2-M1-001, preserve the provider evidence ceiling, and stop. The next session must start one bounded Android client-core packet without rerunning this provider proof.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary, live Google proof

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`
- **Primary features:** `CLIENT-ANDROID-001`, `API-001`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Checkpoint branch:** `main`
- **Checkpoint base/main SHA:** `0ea43698e0c6617897b0c8a73bb1968fee3a1d6b`
- **Status:** complete at the bounded live-provider evidence ceiling; checkpoint push/remote verification follows this file update
- **Private evidence rule:** provider Sheet/project IDs and OAuth material stay outside public Git

## Objective result

**COMPLETE.** The corrected runtime was updated only in the already-bound Apps Script project attached to the one existing disposable synthetic Sheet. Shared mode was activated, a real Google time-driven worker serialized a synthetic API-001 command under the shipped `ScriptLock` path, and exact provider readback verified the command result plus canonical Resource and Idempotency state.

## Completed evidence

### Existing-resource safety and publication integration

- Before publication mutation, the exact disposable Sheet was independently read back by ID, exact title, Google Sheets MIME type, and active/not-trashed state.
- The privately supplied existing Apps Script project was recovered directly. Its returned project identity matched and its provider `parentId` exactly matched the disposable Sheet.
- Only after those checks did the existing-project updater publish. Exact provider-head readback matched the repository runtime.
- No replacement Sheet or Apps Script project was created. No legacy MIRA production resource or data was used.

### Activation and trigger evidence

- Ordinary-user-shaped menu activation created the canonical `Commands` tab and exact readback showed `mutation_mode=queued_writer`.
- Shipped activation calls `miraEnsureCommandTrigger_()` before it writes queued mode: duplicate worker triggers fail closed, zero creates one, and one is reused. Queued mode therefore could not become authoritative through this path unless exactly one matching worker trigger existed at activation.
- Subsequent autonomous processing on two separate scheduler passes proves the real time-driven trigger was firing; no manual worker function was invoked.
- Exact queued-mode readback plus the existing direct-native mutation guard means independent direct canonical writes now fail closed in the supported client path.

### Live worker/provider readback

- A first synthetic command used the store schema token instead of the API schema token. The real worker terminally rejected it with `compatibility_error`; exact readback showed no Resource or Idempotency mutation. This is retained as honest fail-closed evidence, not counted as the successful proof.
- A corrected synthetic same-user API-001 `entity` upsert was submitted with stable command/resource/idempotency IDs, `api_major=1`, `schema_version=mira-api-1`, and expected revision 0.
- It was submitted at `2026-09-02T20:39:56.942Z`; the canonical provider write occurred at `2026-09-02T20:40:40.764Z`; the command reached `succeeded` at `2026-09-02T20:40:45.349Z`.
- Exact `Commands` readback showed `succeeded`, no error, `idempotent_replay=false`, and `readback_verified=true` with the expected authority, command, Resource identity, payload, and revision 1.
- Exact `Resources` readback showed one synthetic `entity` at revision 1 with payload `{"kind":"m2_m1_live_worker_proof","label":"Synthetic queued-writer proof","synthetic":true}`.
- Exact `Idempotency` readback showed one matching `upsert`, matching resource reference/result, and request hash `07e1dbc3a0ae2a53151d6f91068ada45b154a0dba311e3ef537053ffa5c74259`.
- An independent local SHA-256 calculation over the canonical upsert material produced the same request hash.

## Evidence classification

- **Implemented:** provider-neutral sequencer, Workspace Commands inbox, one-minute trigger setup, `ScriptLock` worker, revision/idempotency enforcement, crash recovery, exact readback, and direct-native mutation guard.
- **Test:** deterministic Python/Apps Script suites and publication/scope guards were already green on the merged implementation and scope-fix checkpoints.
- **Integration:** exact existing-project recovery, exact parent binding verification, existing-project-only update, and exact provider-head comparison succeeded.
- **Live provider:** menu activation, queued-mode/tab readback, autonomous time-driven executions, terminal fail-closed validation, successful canonical mutation, and exact Commands/Resources/Idempotency readback succeeded against the isolated disposable Sheet.
- **Not claimed:** release-grade nontechnical shared-access onboarding, a friendly/verified end-user Google consent surface, Android client behavior, cross-person authorization, synchronous sub-minute guarantees, or production-data migration.

## Repository updates required by this completion

- `BACKLOG.md`: close `ANDROID-COMMAND-BOUNDARY-001`, unblock `ANDROID-CLIENT-CORE-001`, reconcile `HOST-CONNECT-EXEC-001`, and retain the ordinary-user onboarding gap honestly.
- `ROADMAP.md`: mark the live queued-writer prerequisite complete and Android client core next.
- `docs/M1_CONCURRENT_COMMAND_BOUNDARY.md`: replace the stale live-proof-pending status with the bounded provider evidence and next slice.
- `FEATURES.md`: no semantic feature-status change is warranted because the Android client itself is not implemented.

## Exact next action / resume point

1. Do not rerun publication, activation, authorization, or live worker proof; do not further mutate the disposable proof Sheet.
2. After this checkpoint is pushed and remote head/required CI are green, stop M2-M1-001.
3. In the next session, read remote Git first and open exactly one new bounded packet for `ANDROID-CLIENT-CORE-001` from that green main.
4. Start with scoped/revocable same-user enrollment/session identity, OS-protected credentials, bounded reads/commands, replay-safe offline queue, reconnect/cursor sync, conflict handling, and exact server readback.
5. Treat a scary unverified Apps Script consent screen as a development artifact and release blocker, never as acceptable ordinary-user onboarding.

## Recovery protocol

Read this file first, then verify `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` from remote Git. M2-M1-001 / `ANDROID-COMMAND-BOUNDARY-001` is complete at its live isolated Google evidence ceiling. Do not reconstruct or rerun the private provider workflow, and do not expose provider IDs or OAuth material. The next work is one new `ANDROID-CLIENT-CORE-001` packet after the pushed checkpoint and CI are remotely verified.
