# MIRA 2.0 — Current Work

## Active packet

### `M2-M1-011` — Android passive identifier capture and explicit movement

- **Primary work:** `ANDROID-CAPTURE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `IDENT-001`, `INV-001`, `MOVE-001`
- **Related invariants/features:** `API-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`, `INV-002`, `LOC-001`, `EVID-001`, `RECOVERY-002`

## Customer status

Objective: Add Android camera/QR/barcode capture to the existing canonical asset/inventory system without creating a second inventory authority.
Progress: Passive QR/barcode capture through Google Code Scanner is implemented and fully green in PR #167 CI run #697: Android tests, signed debug APK/provenance, Python tests and Apps Script tests all passed. Passive scans resolve verified canonical identifiers and have no mutation dependency. The remaining packet work is explicit replay-safe MOVE-001 execution/readback over the existing encrypted Android queue and serialized Workspace writer.
Deliverable: Bounded Android capture that treats raw camera/QR/barcode input as nonauthoritative, resolves existing canonical identifiers/assets, performs zero writes for passive scans, and requires an explicit replay-safe movement command plus exact readback before observed location changes.
Expected delivery: UNKNOWN.
Blocker: none. The next implementation seam is known: API-001/store already support append_event, while the Android Workspace row bridge and Apps Script queued worker currently support only upsert execution.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15. Exact full-history identity proof at closure: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0; duplicate canonical transaction IDs = 0; duplicate Event IDs = 0. Review-surface parity was 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs. Sanitized proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md`. Provider freshness remained UNKNOWN and closure did not claim current-to-the-second freshness.

## Active objective — ANDROID-CAPTURE-001

Implement the queued Android capture work item against the existing Android/shared-state and canonical asset graph. Do not create a parallel inventory model, local-only asset authority, or scan-driven implicit movement.

Current branch: `feature/android-capture-001`
Current PR: #167
Recorded packet base: `942ace58cb780524198670ae561605a4f399f496`
Green scanner checkpoint head: `940873b4cfee81038a7601a1fedc385fd96f40c7`
Green scanner CI: run #697, all gates passed.

Implemented and test-verified in the current PR:
- `VerifiedChangeQuery`: bounded provider-neutral read-only fold over verified canonical Changes; it never reconciles or submits commands.
- `IdentifierCaptureResolver`: strict decoded QR/UPC-A/EAN-8/EAN-13 identifier parsing and lookup against canonical `IDENT-001` snapshots.
- Honest unresolved, ambiguous, malformed, transport, protocol and integrity states; unknown scans never create assets.
- Serial-level duplicate resolution fails closed.
- Google Code Scanner 16.1.0 app-edge integration for QR/EAN-8/UPC-A/EAN-13 with auto-zoom; scanner/camera behavior remains outside provider-neutral core.
- Proof app requests no CAMERA permission; Google Play services owns scanner UI/camera interaction and returns decoded values only.
- Scan UI reports read-only resolution state without rendering provider secrets or canonical asset IDs.
- Direct JVM tests for verified query, passive resolution and scanner-format mapping plus Android ownership registration.
- CI Android SDK bootstrap no longer requests the removed legacy `tools` package.

Not yet accepted/integrated:
- PR #167 remains unmerged while MOVE-001 execution is incomplete.
- Explicit movement command/replay/readback is not implemented yet.
- Representative-device live proof is not complete.

## Movement bridge discovery

- Canonical `API-001` and `GoogleSheetsStructuredStateAdapter` already support `append_event` with idempotency, event identity, stream revision and exact event readback.
- `MOVE-001` already defines the correct event-first / projection-second semantics; do not replace it with scan-driven inventory upserts.
- `OfflineSyncStateStore.CommandIntent` already models `append_event`, including `event_id` and `event_type`.
- Current `GoogleWorkspaceTransport` rejects append-event commands and the 16-column Commands row protocol has no separate event-id/type columns.
- Current Apps Script queued worker rejects any action except `upsert`.
- Do not migrate/expand the live Commands sheet solely for event metadata. Preserve the existing 16-column production transport and encode append-event metadata in a strictly validated transport-only payload envelope while retaining the canonical event payload separately after decoding. Existing upsert row encoding remains unchanged.
- Event append success may acknowledge with verified event readback and zero Resource snapshots; the following explicit inventory-state projection remains a separate queued upsert using existing `MOVE-001` recovery semantics.

## Acceptance gates — ANDROID-CAPTURE-001

1. Android capture accepts camera/QR/barcode observations through a bounded capture interface; raw capture does not itself become canonical truth. **PASS in CI #697.**
2. Supported identifier payloads normalize through existing `IDENT-001` namespace/collision rules and resolve an existing canonical asset exactly. **PASS in CI #697.**
3. Unknown identifiers fail honestly into an unresolved result; no fabricated asset is silently created. **PASS in CI #697.**
4. A passive scan performs zero movement writes. **PASS in CI #697.**
5. Any move requires an explicit user/action command using existing `MOVE-001` event semantics and the shared queued mutation boundary. **OPEN.**
6. Replay/idempotency prevents duplicate movement effects. **OPEN.**
7. Exact readback proves canonical asset/location after an explicit move and zero-write behavior for passive scans/replay. Passive half PASS; movement half OPEN.
8. Offline/reconnect preserves the existing encrypted/replay-safe Android queue; no second queue is introduced. **PASS for passive; movement integration OPEN.**
9. Tests cover lookup, unknown identifier, malformed/unsupported payload, passive zero-write, explicit move, replay and conflict/error paths. Passive coverage PASS; movement coverage OPEN.
10. Packet-to-feature alignment and idea-capture audit pass before merge; no uncaptured parallel inventory semantics are introduced. **PASS at current checkpoint; re-run before merge.**

## Next bounded step

1. Add append-event support to the existing Android Workspace command transport without changing the 16-column Commands sheet schema; strictly encode/decode event metadata in transport-only JSON for action=`append_event`.
2. Extend the serialized Apps Script queued worker to execute canonical append_event with exact idempotency/event readback against existing Events + Idempotency tabs.
3. Add an Android MOVE-001 facade that explicitly stages event-first then inventory-state projection through the same encrypted queue, never from a passive scan callback.
4. Prove event replay, interrupted event/projection recovery, stale revision conflict and exact observed-location readback.
5. Re-run full CI, checkpoint acceptance evidence, then merge only if all packet gates pass.

## Preserved work state

- Stale PR #166 remains open from earlier finance work; do not merge it blindly or use its historical narrative as recovery authority.
- Existing Android client, Authority/store, identifier, inventory/location and movement modules remain canonical dependencies; this packet extends them rather than replacing them.
- NFC/BLE and broader native notification/release work remain outside this bounded packet unless a hard shared abstraction dependency is proven.
- Legacy/production state must never be used as test fixtures.

## Session-start alignment verification — 2026-09-15

### `FEATURES.md`

Reviewed. Active scope maps to existing Android client, identifier, inventory, movement, API, asset, location, evidence and recovery features. No new semantic feature is required for the current packet.

### `BACKLOG.md`

Reviewed. `ANDROID-CAPTURE-001` is the selected canonical work item. Camera/barcode/QR and explicit movement are the current bounded slice; NFC/BLE remain deferred within the same backlog item.

### `ROADMAP.md`

Reviewed. The work preserves the Personal Google/shared-state direction and reuses the existing Android/API/Authority boundaries rather than adding a server or second state authority.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

No materially new product capability was introduced. Google Code Scanner is an implementation choice for the already-captured camera/barcode/QR surface. Append-event transport support is required plumbing for already-canonical `MOVE-001`, not a new user-visible feature. Explicit movement must remain separate from passive capture.

### Direction result

ALIGNED
