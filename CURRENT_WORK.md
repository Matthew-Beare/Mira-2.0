# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Current priority is repeated useful no-app verticals before Android resumes. Completed work remains durable with evidence and is filtered from future selection rather than deleted.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-016` — Canonical inventory query projection

PR #70 merged to `main` as `95728763816b2ab26e29973dd2e204d7c4bdbe9c` from verified head `793f9f7866f5998509a6a3d3584cee39ed99323e`. Exact-head CI `33341004699` and post-merge main CI `33341027064` passed. Fresh isolated Google proof verified tracked-vs-untracked query behavior, identifier/location joins and zero query-side Resource/Event/Idempotency writes.

`INV-002` and `INVENTORY-QUERY-001` are reconciled in canonical feature/backlog state as merged/completed evidence.

## Active packet

### `M2-M0-017` — Replay-safe inventory movement / observation history

- **Primary work:** `MOVEMENT-CORE-001`
- **Primary feature:** `MOVE-001`
- **Related invariants/features:** `INV-001`, `LOC-001`, `INV-002`, `IDENT-001`, `ASSET-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-017-movement-core`
- **Base SHA:** `95728763816b2ab26e29973dd2e204d7c4bdbe9c`
- **PR:** `#71` (non-draft; opened non-draft because the connector's draft-to-ready mutation is known broken from M2-M0-016)
- **Objective:** add provider-neutral replay-safe event history for explicit physical asset observations/movements and deterministically project supported observed location while preserving intended placement, immutable asset identity and exact observation time. Scanner/capture, Android, passive reads, container propagation, par/grocery, fitment and OCR/evidence enrichment remain separate.

## Session-start alignment verification — 2026-08-30

### `FEATURES.md`

Verified before implementation:

- `MOVE-001` is accepted required-direction work for explicit movement with event/readback semantics;
- `INV-001` keeps physical identity on the canonical asset Entity UUID;
- `LOC-001` keeps intended placement separate from supported observed state;
- `INV-002` is a read-only query projection and must not become a movement authority;
- `IDENT-001` enables later recognition/capture but recognition alone must never equal movement.

### `BACKLOG.md`

Verified and reconciled before implementation:

- `INVENTORY-QUERY-001` is complete from PR #70;
- `MOVEMENT-CORE-001` is the one active work row;
- its prerequisites are satisfied by merged asset/identifier/location/inventory work;
- `ANDROID-CAPTURE-001`, par/grocery, fitment/OCR and other adjacent work remain unfinished.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 prioritizes useful stock-ChatGPT + Google Workspace verticals before Android;
- assets/inventory/location/scanning are an accepted family but packets must remain bounded;
- camera/barcode/QR/NFC/BLE capture is downstream client work, not part of provider-neutral movement semantics.

### Direction result

**ALIGNED.** Movement event semantics are the prerequisite that prevents a future scanner from turning mere identifier recognition into fabricated physical movement.

## Acceptance criteria

1. Movement references one existing tracked asset using the same immutable Entity UUID; missing/untracked assets fail closed.
2. Destination must be an existing canonical location; movement never creates a location implicitly.
3. Every observation uses an explicit offset-aware ISO-8601 physical observation timestamp.
4. Event identity/idempotency are independent of asset UUID; exact replay produces zero duplicate event and zero extra state revision.
5. Reusing event/idempotency identity with changed material fails closed.
6. Valid movement changes only observed location/time; intended placement and asset/acquisition/tracking/quantity/identifier truth are preserved.
7. Event records prior inventory revision, intended location, prior observed state and preserved note material required for deterministic recovery/readback.
8. Stale revision or contradictory prior-state expectations fail before a new event is acknowledged.
9. History is bounded/deterministic and derived only from persisted movement events, never synthesized from current state.
10. Same-location re-observation requires a new explicit event with a later timestamp.
11. Existing provider-neutral Resource/Event/Idempotency primitives are used; no second movement database exists.
12. Event-first/projection-second interruption recovery converges without duplicate history; unrelated state advancement causes fail-closed conflict rather than overwrite.
13. Passive identifier recognition/scanning is not movement.
14. Container-following propagation is not implemented.
15. No intended-location mutation, fitment, par/grocery, warranty/maintenance, OCR/evidence or Android behavior is claimed.
16. Direct tests cover success, replay, conflicting replay, stale/prior conflict, unknown/untracked asset, missing location, same-location observation, intended preservation, deterministic history, generic-event filtering and both interruption windows.
17. Complete Personal no-app instructions define append-event and movement semantics and release validation guards the honesty/recovery boundaries.
18. `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` and code-ownership evidence remain aligned before merge.
19. Required CI is green on the exact merge-candidate head.
20. Fresh isolated Google proof demonstrates persisted movement Event + observed-state projection + exact idempotency/readback/replay behavior using synthetic state only.
21. Whole-product reconciliation leaves scanning/capture, container propagation, par/grocery, fitment/OCR and Android unfinished.

## Completed evidence in this packet

### Implementation

- Added `mira/movement.py` as a dedicated provider-neutral movement component.
- STORE event type remains the generic existing `updated`; movement is typed by payload `event_kind=inventory_observation`, avoiding a Google/provider schema fork or starter migration for domain event names.
- New observation preflight requires tracked canonical inventory, an existing destination, expected inventory revision, optional exact prior observed state and a strictly newer offset-aware observation timestamp when prior observation exists.
- Event payload retains exact prior inventory revision, prior observed state, intended location and inventory note plus resulting inventory revision.
- Mutation order is **event first, projection second**. Event append and observed-state projection each use the existing atomic provider-neutral Event/Idempotency or Resource/Idempotency primitive.
- Projection idempotency is deterministic from Event ID (`movement-state-` + first 40 lowercase SHA-256 hex characters), allowing an event-first interruption to resume without a duplicate event.
- Projection preserves inventory participation, intended location and inventory note while changing only observed location/time.
- History filters only `updated` events whose payload is `event_kind=inventory_observation`; unrelated generic `updated` events in the same stream are excluded.

### Direct/test evidence

`tests/test_movement.py` covers:

- successful event + projection with intended location preserved;
- exact replay with one event and no extra inventory revision;
- conflicting event/replay material;
- stale revision and contradictory prior-state rejection before event append;
- missing/untracked asset and missing destination failures;
- explicit same-location later re-observation and equal-time rejection;
- deterministic stream ordering, `after_revision` and result limits;
- unrelated generic `updated` stream events excluded from movement history;
- crash after Event append/before projection, then exact one-time recovery;
- crash after projection write/before acknowledgement, then zero-duplicate replay;
- offset-aware timestamp enforcement and UTC `Z` canonicalization.

`project/code_ownership.json` registers `canonical-inventory-movement` owning `mira/movement.py` with direct verification in `tests/test_movement.py`.

PR #71 early core CI run `33341918685` passed. Release-wired CI run `33342170586` passed on `f8977ede3922284d070602552ef5bf2e6a6f40cb`. A final exact-head run remains required after this evidence checkpoint.

### No-app/release evidence

The complete `workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md` now includes:

- exact Events table preflight and generic append-event request/idempotency/readback rules;
- explicit statement that recognition alone is not movement;
- `inventory_state` / `updated` / `event_kind=inventory_observation` movement identity;
- fresh prior-state/revision/time requirements;
- event-first/projection-second mutation order;
- deterministic projection idempotency key;
- both replay-recovery windows and fail-closed unrelated-state advancement;
- same-location re-observation semantics;
- movement history from persisted movement events only;
- explicit non-implementation of container propagation, scanner/client surfaces and adjacent domain behavior.

`mira/workspace_bundle.py` and `tests/test_workspace_bundle.py` directly guard those clauses, including regressions where recognition is treated as movement or recovery order is weakened.

### Fresh isolated Google provider proof

A brand-new Google Sheet clearly marked `NOT A STARTER` was created solely for M2-M0-017. Provider ID/URL is intentionally excluded from public Git. No legacy MIRA production artifact was used or modified.

Synthetic state contained one receipt-linked asset UUID, canonical shop/shelf/workbench locations, and one tracked `inventory_state` revision 1 with intended Shelf A, no observed location and a preserved inventory note.

The stock-ChatGPT no-app STORE protocol was then exercised in two exact phases:

1. one atomic Event + Idempotency batch appended one `updated` Event with `event_kind=inventory_observation`, stream revision 1, explicit Workbench observation timestamp and prior-state material;
2. after exact Event readback, one atomic Resource + Idempotency batch projected the same asset's `inventory_state` from revision 1 to revision 2, preserving intended Shelf A and note while setting observed Workbench + exact observation time.

Exact provider readback verified:

- asset and location Resources stayed revision 1;
- inventory state is exactly revision 2;
- intended location remained Shelf A;
- observed location is Workbench with the exact explicit timestamp;
- exactly one movement Event exists at stream revision 1;
- exactly two movement-operation Idempotency records exist, one for Event append and one for state projection, with the expected persisted results and request hashes.

Replay was then evaluated using **read-only idempotency preflight**. Both stable keys resolved to the exact original operation/hash/result material, so the correct replay path invoked no Google write. A subsequent full `Resources`/`Events`/`Idempotency` snapshot remained unchanged: one movement Event, inventory revision 2 and exactly the same two idempotency records. This proves zero-write replay for the stock-ChatGPT provider protocol without manufacturing an unnecessary replay mutation call.

This provider proof exercises the no-app Google STORE protocol directly. It does not falsely claim the Python `MovementService` itself was executed inside Google's connector runtime.

## Session-end whole-product reconciliation — 2026-08-30

### `FEATURES.md`

- `INV-002` correctly carries merged/test/provider evidence from M2-M0-016.
- `MOVE-001` remains `candidate_unmerged` until PR #71 actually merges. Direct tests/provider proof do not substitute for merge evidence.

### `BACKLOG.md`

- `INVENTORY-QUERY-001` is complete.
- `MOVEMENT-CORE-001` remains the one active work row until PR #71 merge/readback.
- Scanner/capture, Android, container propagation, par/grocery, fitment and OCR/evidence remain unfinished.

### `ROADMAP.md`

No semantic change required. The packet remains a bounded no-app movement prerequisite and does not reactivate Android or expand into the entire inventory subsystem.

### Direction result

**ALIGNED FOR MERGE CANDIDATE.** Implementation, direct tests, no-app/release guards and fresh provider proof are complete. Only final exact-head CI, protected merge and remote `main` verification remain.

## Exact next action

1. Verify CI is green on the exact branch head after this checkpoint and the generic-event filtering regression.
2. Update PR #71 evidence/merge gate and re-read its exact head/mergeability.
3. Merge only with expected-head protection after exact-head CI succeeds.
4. Remotely verify `main` contains the merge and post-merge CI is green.
5. Create a post-merge lifecycle checkpoint marking `MOVEMENT-CORE-001` complete / `MOVE-001` merged evidence, then rerank unfinished accepted work before activating the next bounded packet.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-017-movement-core` descends from verified base `95728763816b2ab26e29973dd2e204d7c4bdbe9c` and PR #71 still targets `main`. Do not touch protected legacy MIRA production data. Do not implement barcode/QR/NFC/BLE capture, Android, passive-read movement, container-following propagation, par/grocery, fitment or OCR/evidence enrichment in this packet.