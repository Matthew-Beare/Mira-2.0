# MIRA 2.0 — Current Work

## Active packet

### `M2-M1-011` — Android passive identifier capture and explicit movement

- **Primary work:** `ANDROID-CAPTURE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `IDENT-001`, `INV-001`, `MOVE-001`
- **Related invariants/features:** `API-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`, `INV-002`, `LOC-001`, `EVID-001`, `RECOVERY-002`

## Customer status

Objective: Add Android camera/QR/barcode capture to the existing canonical asset/inventory system without creating a second inventory authority.
Progress: The bounded camera/QR/barcode + explicit-movement code slice is implemented and fully green. Passive scan remains read-only; explicit movement uses the existing encrypted FIFO queue, canonical append-event semantics, event-first/projection-second MOVE-001 recovery, and exact verified inventory-state readback. CI run #711 passed every repository gate at head `90806c9b03fe66fa139b69b45004b85689c8108c`.
Deliverable: Bounded Android capture with zero-write passive scans plus explicit replay-safe movement and exact canonical location readback.
Expected delivery: code integration is ready after this final checkpoint CI; physical-device live verification remains a human-only proof step.
Blocker: no code blocker. Live verification requires a representative Android device and provider consent.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15. Exact full-history identity proof at closure: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0; duplicate canonical transaction IDs = 0; duplicate Event IDs = 0. Review-surface parity was 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs. Sanitized proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md`. Provider freshness remained UNKNOWN and closure did not claim current-to-the-second freshness.

## Active objective — ANDROID-CAPTURE-001

Implement the queued Android capture work item against the existing Android/shared-state and canonical asset graph. Do not create a parallel inventory model, local-only asset authority, or scan-driven implicit movement.

Current branch: `feature/android-capture-001`
Current PR: #167
Recorded packet base: `942ace58cb780524198670ae561605a4f399f496`
Latest fully green implementation head: `90806c9b03fe66fa139b69b45004b85689c8108c`
Latest fully green CI: run #711, completed successfully on 2026-09-15; Android unit tests, proof APK build/provenance, Python tests, Apps Script tests, work-session alignment and Android ownership all passed.

Implemented and test-verified:
- `VerifiedChangeQuery`: bounded provider-neutral read-only fold over verified canonical Changes; it never reconciles or submits commands.
- `IdentifierCaptureResolver`: strict decoded QR/UPC-A/EAN-8/EAN-13 identifier parsing and lookup against canonical `IDENT-001` snapshots.
- Honest unresolved, ambiguous, malformed, transport, protocol and integrity states; unknown scans never create assets.
- Serial-level duplicate resolution fails closed.
- Google Code Scanner 16.1.0 app-edge integration for QR/EAN-8/UPC-A/EAN-13 with auto-zoom; scanner/camera behavior remains outside provider-neutral core.
- Proof app requests no CAMERA permission; Google Play services owns scanner UI/camera interaction and returns decoded values only.
- Scan UI reports read-only resolution state without rendering provider secrets or canonical asset IDs.
- Append-event support preserves the existing 16-column Commands schema through a strict transport-only event envelope.
- Serialized Apps Script worker executes append-event with canonical Event-ID uniqueness, stream revision, idempotency, exact event readback and event-before-idempotency crash recovery.
- `GoogleWorkspaceEventTransport` delegates all existing upsert/change behavior unchanged and adds only the append-event envelope/readback path.
- `MovementCommandFacade` stages one explicit MOVE-001 event followed by its inventory-state projection through the existing encrypted FIFO queue; there is no second queue or scan-triggered implicit mutation.
- Movement tests cover event-first ordering, multi-pass worker convergence, exact replay without provider I/O, event-success/projection-conflict recovery, FIFO blocking, and refusal to accept mismatched verified projection readback.
- Device proof shell uses the event-capable transport, keeps passive scan separate from movement, requires a distinct `Move scanned asset explicitly` action, verifies the destination location and fresh current inventory state, and reports success only after canonical location readback.
- Proof-shell retry handling preserves the exact in-memory MOVE request while asynchronous worker reconciliation is incomplete and will not stage a second observation merely because earlier queued work finished during a retry.

## Acceptance gates — ANDROID-CAPTURE-001

1. Android capture accepts camera/QR/barcode observations through a bounded capture interface; raw capture does not itself become canonical truth. **PASS.**
2. Supported identifier payloads normalize through existing `IDENT-001` namespace/collision rules and resolve an existing canonical asset exactly. **PASS.**
3. Unknown identifiers fail honestly into an unresolved result; no fabricated asset is silently created. **PASS.**
4. A passive scan performs zero movement writes. **PASS.**
5. Any move requires an explicit user/action command using existing `MOVE-001` event semantics and the shared queued mutation boundary. **PASS.**
6. Replay/idempotency prevents duplicate movement effects. **PASS.**
7. Exact readback proves canonical asset/location after an explicit move and zero-write behavior for passive scans/replay. **PASS in deterministic/CI evidence.**
8. Offline/reconnect preserves the existing encrypted/replay-safe Android queue; no second queue is introduced. **PASS.**
9. Tests cover lookup, unknown identifier, malformed/unsupported payload, passive zero-write, explicit move, replay and conflict/error paths. **PASS.**
10. Packet-to-feature alignment and idea-capture audit pass before merge; no uncaptured parallel inventory semantics are introduced. **PASS; capture audit repeated below.**

## Verification state

- **Desired:** complete for bounded QR/barcode capture + explicit movement.
- **Specified:** complete in existing feature/backlog semantics; no new product feature introduced.
- **Implemented:** complete on PR #167.
- **Tested:** complete for deterministic/unit/Apps Script/CI evidence at run #711.
- **Integrated:** pending PR #167 merge.
- **Live verified:** **NOT YET**. Requires representative-device proof.

### Human-only live proof wall

`REQUIRES-HUMAN-ACTION`

Minimum action after the final retained APK is available:
1. Install/update the CI-retained `com.mira.deviceproof` APK on a representative Android device.
2. Open it and authorize/select the intended MIRA Personal Google Workspace copy through provider UI.
3. Scan one supported identifier tied to an existing test/safe canonical asset and confirm the app reports one read-only resolution without a movement write.
4. Enter/select a safe existing canonical test destination and press `Move scanned asset explicitly`.
5. Allow the serialized Workspace worker to reconcile, retry the exact movement action if it is still pending, and verify the UI reaches `applied with verified canonical location readback`.
6. Read back the canonical Event + inventory-state projection and confirm one movement effect, no duplicate event/economic/state effect, and the expected observed location.

Do not use protected/legacy production state as a disposable proof fixture. Use an approved test/safe asset/location pair.

## Next bounded step

1. Run CI on this acceptance checkpoint commit and repair only actual regressions.
2. Refresh PR #167 title/body so it describes the complete bounded slice rather than the original passive-only draft.
3. If final checkpoint CI is green and PR head/base have not moved, merge PR #167 and verify remote `main` contains the merge.
4. Record implementation/test/integration truth after merge; retain live verification as `REQUIRES-HUMAN-ACTION` until a representative device supplies evidence.
5. Select the next bounded backlog packet from canonical Git state; NFC/BLE remains outside this completed QR/barcode packet unless selected next.

## Preserved work state

- Stale PR #166 remains open from earlier finance work; do not merge it blindly or use its historical narrative as recovery authority.
- Existing Android client, Authority/store, identifier, inventory/location and movement modules remain canonical dependencies; this packet extends them rather than replacing them.
- NFC/BLE and broader native notification/release work remain outside this bounded packet unless a hard shared abstraction dependency is proven or selected as the next packet.
- Legacy/production state must never be used as test fixtures.

## Session-start alignment verification — 2026-09-15

### `FEATURES.md`

Reviewed. Active scope maps to existing Android client, identifier, inventory, movement, API, asset, location, evidence and recovery features. No new semantic feature is required for the current packet.

### `BACKLOG.md`

Reviewed. `ANDROID-CAPTURE-001` is the selected canonical work item. Camera/barcode/QR and explicit movement are this bounded slice; NFC/BLE remain deferred/outside the packet.

### `ROADMAP.md`

Reviewed. The implementation preserves the Personal Google/shared-state direction and reuses the existing Android/API/Authority boundaries rather than adding a server, second state authority, or second offline queue.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

No materially new product capability was introduced. Google Code Scanner is an implementation choice for the already-captured camera/barcode/QR surface. Append-event transport support is required plumbing for already-canonical `MOVE-001`. `MovementCommandFacade` composes existing MOVE-001 + inventory semantics through the existing encrypted queue. The explicit proof-app movement button is evidence/UI for the same feature, not a new inventory model. NFC/BLE remains deferred and was not silently absorbed.

### Direction result

ALIGNED
