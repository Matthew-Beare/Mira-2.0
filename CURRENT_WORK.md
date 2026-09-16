# MIRA 2.0 — Current Work

## Customer status

Objective: Live-verify the integrated Android camera/QR/barcode capture and explicit movement path against a safe canonical asset/location pair.
Progress: Android capture is merged to main and post-merge Trusted Runner Gate passed. The stale pre-merge checkpoint was reconciled to remote Git; deterministic acceptance remains green and only representative-device/provider proof remains.
Last 24h: Historical finance coverage closed with exact full-history identity parity, then Android passive capture + explicit replay-safe movement was integrated to main with green CI.
Deliverable: A representative-device proof showing one read-only identifier resolution, one explicit MOVE-001 effect, and exact canonical location readback without duplicate movement.
Expected delivery: UNKNOWN until representative-device/provider consent is available.
Blocker: Install/update the retained com.mira.deviceproof APK on a representative Android device, authorize the intended MIRA Personal Google Workspace copy, and run the safe scan + explicit-move proof below.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15. Exact full-history identity proof at closure: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0; duplicate canonical transaction IDs = 0; duplicate Event IDs = 0. Review-surface parity was 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs. Sanitized proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md`. Provider freshness remained UNKNOWN and closure did not claim current-to-the-second freshness.

## Integrated packet — ANDROID-CAPTURE-001

Merged to `main` on 2026-09-15. Remote main merge commit at reconciliation: `dc9611b195b8e6907bc6974cdedf8aa0202f12aa`.

Verified integration evidence:
- Merge commit message: `Merge ANDROID-CAPTURE-001 passive capture and explicit movement`.
- Post-merge `Trusted Runner Gate` completed successfully on remote main.
- Pre-merge deterministic acceptance/CI was fully green for the bounded QR/barcode + explicit movement slice.
- PR #167 is no longer open. Stale finance PR #166 remains open and must not be merged blindly.

Implemented and test-verified:
- `VerifiedChangeQuery`: bounded provider-neutral read-only fold over verified canonical Changes; it never reconciles or submits commands.
- `IdentifierCaptureResolver`: strict decoded QR/UPC-A/EAN-8/EAN-13 identifier parsing and lookup against canonical `IDENT-001` snapshots.
- Honest unresolved, ambiguous, malformed, transport, protocol and integrity states; unknown scans never create assets.
- Serial-level duplicate resolution fails closed.
- Google Code Scanner app-edge integration for QR/EAN-8/UPC-A/EAN-13; proof app requests no CAMERA permission and scanner UI/camera interaction remains provider-owned.
- Passive scan remains read-only and does not imply movement.
- Append-event support preserves the existing Commands schema through a strict transport-only event envelope.
- Serialized Apps Script worker executes append-event with canonical Event-ID uniqueness, stream revision, idempotency, exact event readback and event-before-idempotency crash recovery.
- `MovementCommandFacade` stages one explicit MOVE-001 event followed by inventory-state projection through the existing encrypted FIFO queue; no second queue exists.
- Movement tests cover event-first ordering, multi-pass convergence, exact replay without provider I/O, event-success/projection-conflict recovery, FIFO blocking, and mismatched verified projection refusal.
- Proof shell requires a distinct `Move scanned asset explicitly` action and reports success only after canonical location readback.

## Acceptance state

1. Camera/QR/barcode observation is bounded and does not itself become canonical truth: **PASS**.
2. Supported identifiers normalize through existing IDENT-001 semantics and resolve existing assets exactly: **PASS**.
3. Unknown identifiers fail honestly without fabricated assets: **PASS**.
4. Passive scan performs zero movement writes: **PASS**.
5. Movement requires an explicit MOVE-001 action through the shared queued mutation boundary: **PASS**.
6. Replay/idempotency prevents duplicate movement effects: **PASS**.
7. Exact canonical asset/location readback after explicit movement: **PASS in deterministic/CI evidence; live proof pending**.
8. Existing encrypted/replay-safe Android queue is preserved; no second queue: **PASS**.
9. Error/conflict/replay/unknown/malformed paths are test-covered: **PASS**.
10. Packet-to-feature alignment and capture audit: **PASS**.

## Human-only live proof wall

`REQUIRES-HUMAN-ACTION`

Minimum safe proof:
1. Install/update the CI-retained `com.mira.deviceproof` APK on a representative Android device.
2. Authorize/select the intended MIRA Personal Google Workspace copy through provider UI.
3. Scan one supported identifier tied to an existing approved test/safe canonical asset and confirm one read-only resolution without movement.
4. Enter/select an approved safe existing canonical test destination and press `Move scanned asset explicitly`.
5. Allow the serialized Workspace worker to reconcile; retry the exact movement action only if still pending.
6. Verify UI reaches `applied with verified canonical location readback`.
7. Read back canonical Event + inventory-state projection and confirm exactly one movement effect and expected observed location.

Do not use protected/legacy production state as a disposable proof fixture.

## Next bounded step

1. Await representative-device/provider proof for the integrated Android capture vertical; do not fabricate live verification.
2. Continue dependency-safe work that does not require physical-device/provider consent from canonical BACKLOG/ROADMAP on the next execution boundary.
3. Keep NFC/BLE outside this bounded QR/barcode packet unless independently selected from canonical backlog.
4. Preserve stale PR #166 as historical finance evidence only; do not use it as recovery authority or merge it blindly.

## Direction result

ALIGNED
