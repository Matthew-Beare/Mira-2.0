# MIRA 2.0 — Current Work

## Customer status

Objective: Live-verify the integrated Android camera/QR/barcode capture and explicit movement path against a safe canonical asset/location pair while continuing trustworthy historical inventory/manual reconciliation.
Progress: Verified current main and Actions CI green after the recovery repair; re-read the legacy Tool Inventory and bounded 94 currently `Details pending` rows, preserving fail-closed identity/manual handling rather than attaching guessed manuals.
Last 24h: Historical finance coverage closed with exact full-history identity parity, Android passive capture + explicit replay-safe movement integrated to main, and legacy manual evidence was audited without promoting setup guides to manuals.
Deliverable: A representative-device proof showing one read-only identifier resolution, one explicit MOVE-001 effect, and exact canonical location readback without duplicate movement; exact-model inventory/manual reconciliation continues where trustworthy identity evidence exists.
Expected delivery: UNKNOWN until representative-device/provider consent is available.
Blocker: Install/update the retained com.mira.deviceproof APK on a representative Android device, authorize the intended MIRA Personal Google Workspace copy, and run the safe scan + explicit-move proof.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Active packet

### `M2-M1-046` — Android capture live-proof and inventory evidence reconciliation

- **Primary work:** `ANDROID-CAPTURE-001`
- **Primary features:** `IDENT-001`, `ASSET-001`
- **Related invariants/features:** `CLIENT-ANDROID-001`, `EVID-001`, `MOVE-001`, `INV-001`
- **State:** integrated/test-verified; live representative-device proof pending; historical inventory/manual evidence reconciliation continues where exact identity is trustworthy
- **Owned surfaces:** `CURRENT_WORK.md` recovery/status checkpoint; no Android implementation changes are claimed in this checkpoint
- **Shared/high-contention surfaces:** `CURRENT_WORK.md`
- **Blocker:** representative Android device + provider consent are required only for the live proof; evidence reconciliation remains dependency-safe

## Session-start alignment verification — 2026-09-16

### `FEATURES.md`

Reviewed against the active Android capture/inventory objective. `IDENT-001`, `ASSET-001`, `CLIENT-ANDROID-001`, `EVID-001`, `MOVE-001`, and `INV-001` remain the existing canonical feature semantics; no parallel inventory system is introduced.

### `BACKLOG.md`

Reviewed against remote main. `ANDROID-CAPTURE-001` remains the canonical work item for nonauthoritative camera/barcode/QR capture; passive reads do not silently move assets. Historical evidence reconciliation is treated as integrity work under the existing asset/evidence semantics rather than invented as a competing product model.

### `ROADMAP.md`

Reviewed against the current Personal Google + Android shared-state direction. The live proof remains a representative-device/provider evidence gate, not something CI can fabricate.

### Idea/backlog capture audit

No materially new product idea was introduced by repairing the recovery checkpoint or enforcing the full-manual evidence rule. Existing inventory, identity, movement, evidence, and Android capture semantics are reused. `CAPTURE AUDIT COMPLETE`.

### Direction result

ALIGNED

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15. Exact full-history identity proof at closure: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0; duplicate canonical transaction IDs = 0; duplicate Event IDs = 0. Review-surface parity was 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs. Sanitized proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md`. Provider freshness remained UNKNOWN and closure did not claim current-to-the-second freshness.

## Integrated packet — ANDROID-CAPTURE-001

Merged to `main` on 2026-09-15. PR #167 is no longer open. Stale finance PR #166 remains open as historical evidence and must not be merged blindly.

Verified deterministic/integration evidence:
- Passive scan is read-only and unknown identifiers never create assets.
- QR/UPC-A/EAN-8/EAN-13 identifiers normalize through existing IDENT-001 semantics.
- Movement requires a distinct explicit MOVE-001 action through the existing encrypted/replay-safe queue.
- Serialized provider worker preserves event uniqueness, revision/idempotency, crash recovery and exact readback.
- Deterministic tests cover replay, FIFO blocking, conflict recovery, malformed/unknown identifiers and verified projection refusal.
- Exact canonical location readback is PASS in deterministic/CI evidence; live representative-device/provider proof remains pending.

## Inventory/manual evidence audit — 2026-09-16

No protected production rows were deleted or rewritten.

- The legacy `Tool Inventory` is an inventory evidence source, not the MIRA 2.0 development authority.
- Fresh bounded provider readback found 94 rows currently matching `Details pending` in rows 1:130. This supersedes the older checkpoint count of 101 for that bounded surface; no rows were mutated merely to force parity.
- The bounded Knowledge Index manual scan found the WRX factory service manual, FL5 service-reference manual, and Eastwood 31158 manufacturer-manual-search record; no setup/QSG artifact was silently classified as a full manual.
- The retained WRX factory service manual is `service_manual` evidence.
- The retained FL5 service-reference manual is `service_manual` evidence with an explicit warning to verify 2025 applicability per procedure/specification.
- Eastwood 31158 remains an exact-SKU manufacturer-instructions search whose advertised official file was unavailable to the connected runtime; no substitute was fabricated.
- LAUNCH CRP129E V2.0 Elite remains source-unavailable because the manufacturer manual found was for a different V3 family.
- Logitech C920s manufacturer evidence resolves to a quick-start/setup guide only. It may be secondary setup evidence but does **not** satisfy a full owner/instruction/service-manual requirement.
- High-value powered/precision examples still lacking stable manufacturer/model identity include the two-post lift, compressor, drill press, meters, vacuum pump, rework/soldering stations, pressure washer, chainsaw and powered woodworking tools.
- The current two-post lift row is `TI-0027`, with ownership confirmed but brand/model still blank in the canonical legacy sheet. A genuine Rotary SPOA10/2000-Series manufacturer-family operation/maintenance manual path exists, but it must not be attached until receipt/serial/photo evidence establishes applicability.
- Continuing rule: classify documents by actual type. Never promote QSG/setup/product/support pages to `owner_manual`, `instruction_manual`, or `service_manual`. If no exact/model-family full manual can be verified, record unavailable/not-published rather than fabricating coverage.

## CI/readback evidence — 2026-09-16

- Remote `main` head at session verification: `9122b74be01c80f3c08a94ffdfcbbfb728b661f6` (`Repair work-session alignment checkpoint`).
- GitHub Actions `Trusted Runner Gate` run 181 for that exact head completed `success`.
- Commit Status API reports no legacy status contexts (`total_count=0`), so the aggregate `pending` value there is not evidence of a failing workflow; Actions is the relevant CI evidence.
- Open PR audit still shows stale finance PR #166; it is preserved as historical evidence and is not a merge candidate.

### Idea/backlog capture audit

This evidence-quality correction introduces no new feature. It tightens evidence classification under existing asset/evidence/knowledge semantics. `CAPTURE AUDIT COMPLETE`.

## Human-only live proof wall

`REQUIRES-HUMAN-ACTION`

Minimum safe proof:
1. Install/update the retained `com.mira.deviceproof` APK on a representative Android device.
2. Authorize/select the intended MIRA Personal Google Workspace copy through provider UI.
3. Scan one supported identifier tied to an existing approved safe canonical asset and confirm one read-only resolution without movement.
4. Select an approved safe existing canonical destination and press `Move scanned asset explicitly`.
5. Allow the serialized Workspace worker to reconcile; retry the exact movement action only if still pending.
6. Verify UI reaches `applied with verified canonical location readback`.
7. Read back canonical Event + inventory-state projection and confirm exactly one movement effect and expected location.

Do not use protected/legacy production state as a disposable proof fixture.

## Next bounded step

1. Await representative-device/provider proof for live Android capture; do not fabricate it.
2. Continue historical inventory/receipt/manual reconciliation without treating quick-start/setup material as a full manual.
3. Resolve manufacturer/model identity from trustworthy receipts, serial/part numbers, or retained photos before attaching manuals to `Details pending` rows; prioritize powered/precision equipment.
4. For `TI-0027`, seek exact Rotary model identity from purchase/serial/photo evidence before attaching the SPOA10/2000-Series manual family.
5. Preserve stale PR #166 as historical finance evidence only; do not merge it blindly.

## Direction result

ALIGNED
