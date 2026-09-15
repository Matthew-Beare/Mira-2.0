# MIRA 2.0 — Current Work

## Active packet

### `M2-M1-011` — Android passive identifier capture and explicit movement

- **Primary work:** `ANDROID-CAPTURE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `IDENT-001`, `INV-001`, `MOVE-001`
- **Related invariants/features:** `API-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`, `INV-002`, `LOC-001`, `EVID-001`, `RECOVERY-002`

## Customer status

Objective: Add Android camera/QR/barcode capture to the existing canonical asset/inventory system without creating a second inventory authority.
Progress: Passive scanner/identifier resolution is green; append-event Workspace transport and serialized worker plumbing now exist, and direct Android transport tests cover 16-column envelope compatibility, replay no-duplicate behavior, verified event readback, revision mismatch failure, and conflicting duplicate command material.
Last 24h: Historical finance reconciliation reached exact provider/canonical equality, then the Android capture vertical advanced through passive Google Code Scanner integration and append-event movement transport plumbing.
Deliverable: Bounded Android capture with zero-write passive scans plus explicit replay-safe movement and exact canonical location readback.
Expected delivery: UNKNOWN.
Blocker: none.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15. Exact full-history identity proof at closure: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0; duplicate canonical transaction IDs = 0; duplicate Event IDs = 0. Review-surface parity was 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs. Sanitized proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md`. Provider freshness remained UNKNOWN and closure did not claim current-to-the-second freshness.

## Active objective — ANDROID-CAPTURE-001

Implement the queued Android capture work item against the existing Android/shared-state and canonical asset graph. Do not create a parallel inventory model, local-only asset authority, or scan-driven implicit movement.

Current branch: `feature/android-capture-001`
Current PR: #167
Recorded packet base: `942ace58cb780524198670ae561605a4f399f496`
Latest transport-test checkpoint: `45910097936cd59570023af80285978bac5cff68`
Latest fully green head before this checkpoint: `d8b5834439739da11ac2b7e05826fba60573ff5f`
Latest fully green CI: GitHub Actions `python` check completed successfully at `d8b5834439739da11ac2b7e05826fba60573ff5f`; CI for the transport-test checkpoint was not yet registered at checkpoint time.

Implemented and test-verified before the latest test-only checkpoint:
- `VerifiedChangeQuery`: bounded provider-neutral read-only fold over verified canonical Changes; it never reconciles or submits commands.
- `IdentifierCaptureResolver`: strict decoded QR/UPC-A/EAN-8/EAN-13 identifier parsing and lookup against canonical `IDENT-001` snapshots.
- Honest unresolved, ambiguous, malformed, transport, protocol and integrity states; unknown scans never create assets.
- Serial-level duplicate resolution fails closed.
- Google Code Scanner 16.1.0 app-edge integration for QR/EAN-8/UPC-A/EAN-13 with auto-zoom; scanner/camera behavior remains outside provider-neutral core.
- Proof app requests no CAMERA permission; Google Play services owns scanner UI/camera interaction and returns decoded values only.
- Scan UI reports read-only resolution state without rendering provider secrets or canonical asset IDs.
- Append-event support preserves the existing 16-column Commands schema through a strict transport-only event envelope.
- Serialized Apps Script worker append-event path and tests exist on the packet branch.
- Direct Android append-event transport tests now exercise envelope compatibility, pending replay/no duplicate append, exact verified event readback with zero fabricated Resource snapshots, stale/mismatched stream revision failure, and duplicate command-id/material conflict failure.

Not yet accepted/integrated:
- PR #167 remains unmerged.
- Latest transport-test checkpoint still requires CI readback before its evidence is earned.
- Explicit Android MOVE-001 facade that stages event-first then inventory projection is not complete.
- Interrupted event/projection recovery and exact final observed-location readback remain open.
- Representative-device live proof is not complete.

## Acceptance gates — ANDROID-CAPTURE-001

1. Android capture accepts camera/QR/barcode observations through a bounded capture interface; raw capture does not itself become canonical truth. **PASS on prior green head.**
2. Supported identifier payloads normalize through existing `IDENT-001` namespace/collision rules and resolve an existing canonical asset exactly. **PASS on prior green head.**
3. Unknown identifiers fail honestly into an unresolved result; no fabricated asset is silently created. **PASS on prior green head.**
4. A passive scan performs zero movement writes. **PASS on prior green head.**
5. Any move requires an explicit user/action command using existing `MOVE-001` event semantics and the shared queued mutation boundary. **OPEN; transport plumbing exists, facade incomplete.**
6. Replay/idempotency prevents duplicate movement effects. **PARTIAL; transport replay test added, full event+projection replay remains open.**
7. Exact readback proves canonical asset/location after an explicit move and zero-write behavior for passive scans/replay. **Passive PASS; event readback test added; final location readback OPEN.**
8. Offline/reconnect preserves the existing encrypted/replay-safe Android queue; no second queue is introduced. **PASS for passive; movement integration OPEN.**
9. Tests cover lookup, unknown identifier, malformed/unsupported payload, passive zero-write, explicit move, replay and conflict/error paths. **PARTIAL; direct transport coverage added, end-to-end movement coverage OPEN.**
10. Packet-to-feature alignment and idea-capture audit pass before merge; no uncaptured parallel inventory semantics are introduced. **PASS at current checkpoint; re-run before merge.**

## Next bounded step

1. Read back CI for the latest transport-test checkpoint; fix any compile/test failure before adding scope.
2. Add the Android MOVE-001 facade that explicitly stages append-event first and inventory-state projection second through the existing encrypted queue, never from passive scan callbacks.
3. Prove event replay, interrupted event/projection recovery, stale revision conflict and exact observed-location readback.
4. Re-run full CI, checkpoint acceptance evidence, then merge only if all packet gates pass.

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
