# MIRA 2.0 — Current Work

## Customer status

Objective: Live-verify the integrated Android camera/QR/barcode capture and explicit movement path against a safe canonical asset/location pair while continuing trustworthy historical inventory/manual reconciliation.
Progress: Repaired the AM/PM brief and finance-refresh pipeline, restored the hourly development/reconciliation workers, fixed the FinOps derived-formula tail, and hardened zero-entry mileage/spend rendering; Android live proof remains human-blocked.
Last 24h: Sep 24 live audit verified May 1 governance and provider-freshness fail-closed behavior, changed the current zero-entry Fri–Thu cycle from false CLOSED/lost-time semantics to OPEN/no-time-lost-yet, repaired every missing FinOps Month/Review/allowance-derived formula across 2,127 populated rows, restored exact 586↔586 NEEDS REVIEW Event-ID parity, and persisted the invariants in Durable Operating Addenda.
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
- Exact readback of `TI-0027` from canonical `Inventory` row 116 confirms `Two-post vehicle lift`, quantity 1, `verified_existing_inventory`, but brand, model, date, seller, price, serial/part number, receipt link, and photo remain blank. Broad Drive search for `Rotary` returned the inventory row but no trustworthy purchase/serial/photo evidence establishing lift model applicability. A Rotary-family operation/maintenance manual therefore remains deliberately unattached.
- Continuing rule: classify documents by actual type. Never promote QSG/setup/product/support pages to `owner_manual`, `instruction_manual`, or `service_manual`. If no exact/model-family full manual can be verified, record unavailable/not-published rather than fabricating coverage.

## Financial Escape live-state reconciliation — 2026-09-18

Direct user correction remains authoritative: May 1, 2027 is the governing Financial Escape target; March 1 and April 1 are reference/history only and must not drive current pace, status, briefs, or actions.

Verified provider/workbook evidence:
- Linked financial accounts were read live before workbook mutation. Transaction coverage reports full-history and complete for the bounded query, but provider freshness remains UNKNOWN and is preserved as UNKNOWN.
- Bounded posted and pending transaction queries for 2026-09-17 through 2026-09-18 returned no rows. No transaction was fabricated from balance movement.
- Latest available linked balances used for the Sep 18 snapshot: household depository cash $28,146.21; positive card balances owed $1,016.94; Old Dominion 401(k) $249,716.79; household 401(k) $499,433.58 by the standing 2× rule; HELOC $41,810.05; Civic $42,200.87; Robinhood brokerage + crypto $17,109.90; primary home $577,400.
- The outgoing 2026-09-17 Daily Snapshot was frozen as historical evidence before inserting the new current row. Exactly one 2026-09-18 Daily Snapshot now exists.
- Dashboard readback after mutation: duplicate Event IDs = 0; today's snapshot rows = 1; DATA FRESHNESS = UNKNOWN • PROVIDER FRESHNESS; refresh/brief cadence label = 2:20 refresh • 2:45 brief • AM + PM ET.
- The live model recomputed rather than being hard-coded: May 1 minimum paid-mile pace = 5,171/wk; current completed cycle = 6,006 paid miles; rolling realistic exit = Apr 26, 2027; status = PONITUDE • 5d AHEAD. Mileage remains a leading signal; posted debt reduction remains actual progress.
- Historical Daily Snapshot rows and March/April reference rows were preserved rather than rewritten to match the new governing target.

## Inventory evidence boundary — 2026-09-18

- Bounded Tool Inventory readback still finds 94 Details pending rows in rows 1:130.
- High-value unresolved powered/precision identity searches were run against the canonical Purchase & Receipt Archive, connected Gmail, and Drive evidence for compressor, drill press, vacuum pump, multimeter, clamp meter, pressure washer, chainsaw, soldering/rework equipment and related terms.
- Those searches produced no trustworthy exact purchase/model evidence beyond the existing inventory/interview state. No brand, model, SKU, serial, manual, or fitment identity was invented.
- Exact-model/full-manual rule remains in force: physical label/photo/serial evidence or a trustworthy retained receipt is required before attaching model-specific manuals to these legacy assets.

## Brief / finance runtime integrity repair — 2026-09-24

Root causes and verified repairs:
- AM and PM remain the only user-facing MIRA briefs, at exact 02:45 and 14:45 America/New_York. Brief prompts now forbid signed-negative ahead/behind wording, forbid verified spend-overage language when provider freshness is UNKNOWN, and suppress routine historical review ambiguity from the executive brief.
- Financial Escape Refresh remains 02:20/14:20 America/New_York but now uses exact scheduling instead of condition-watch timing, removing early-run slot drift.
- MIRA Continuous Worker is re-enabled hourly at :05 and MIRA Finance Backfill is re-enabled hourly at :55. They are not brief jobs and are staggered away from the 02:20/14:20 refresh and 02:45/14:45 briefs.
- The stale Finance Backfill blanket rule that all check-number payments are septic was removed. Check #118/#119 remain user-confirmed septic; the recurring $24 check series is explicitly not septic; each new check is event-specific.
- Check #120 ($2,800, 2026-09-21) remains NEEDS REVIEW. Same-day official Tennessee septic Certificate of Completion is recorded as supportive evidence only, not direct proof of payment purpose.
- Canonical mileage semantics were repaired: persistent HOME from a prior work cycle does not close a new zero-entry Fri–Thu week. The current Sep 24 zero-entry week reads back OPEN WEEK • 0 COMPLETED, and Escape Readiness explicitly forbids converting the full-week pace deficit into time lost while open.
- Mileage & Pay Tracker carries the same closure invariant: early HOME closure requires current-cycle paid activity; otherwise a zero-entry cycle remains open through Thursday 23:59 ET unless authoritative PTO/nonproductive evidence explicitly classifies it.
- FinOps Ledger audit found derived-tail gaps on appended/backfilled rows. Missing formulas were restored only where blank: Month AD 129 rows; Review Status AE 116; Allowance Debit Amount AH 116; Allowance Key AI 129; Allowance Status AJ 116; Deferred Status AK 116. Post-write audit across all 2,127 populated ledger rows reports zero missing values/formulas in those six derived columns.
- Post-formula parity audit found 8 canonical NEEDS REVIEW Event IDs absent from Spending Review. The eight missing Event IDs were added to the next blank native review rows without overwriting row formulas/validation. Readback now proves exact parity: FinOps NEEDS REVIEW = 586, Spending Review NEEDS REVIEW = 586, FinOps-minus-review = 0, review-minus-FinOps = 0.
- Financial Escape Refresh and Finance Backfill now enforce zero missing AD/AE/AH/AI/AJ/AK derived cells and exact NEEDS REVIEW Event-ID parity as success gates on every run.
- Spending Review readback for Check #120 now correctly shows Month 2026-09 and Review Status NEEDS REVIEW instead of blank derived state.
- Dashboard integrity readback remains: current date 2026-09-24, exactly one current Daily Snapshot, duplicate Event IDs 0, DATA FRESHNESS = UNKNOWN • PROVIDER FRESHNESS, latest posted event date 2026-09-23.
- The brief correctness/zero-entry/spend-freshness/check-specific rules were appended and read back in MIRA Durable Operating Addenda.

Provider truth at repair time remains freshness-UNKNOWN; this repair does not claim current-to-the-second transaction completeness.
## CI/readback evidence — 2026-09-24

- Functional runtime-integrity/review-parity checkpoint `0c9f414080dac2a13f2987edf31c29d1560f1c37` is integrated on `main`.
- GitHub Actions CI run `35978572919` completed `success` on that exact checkpoint.
- Trusted Runner Gate run `35978709083` completed `success` on that exact checkpoint.
- Open PR audit still includes stale finance PR #166 and historical backfill PR #165; neither is a blind merge candidate.
- Live workbook readback at checkpoint: zero duplicate Event IDs, zero missing FinOps AD/AE/AH/AI/AJ/AK derived fields across 2,127 populated rows, exact 586↔586 FinOps/Spending Review NEEDS REVIEW Event-ID parity, current zero-entry Fri–Thu week OPEN, provider freshness UNKNOWN preserved.

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
4. For `TI-0027`, do not attach a Rotary manual until exact/model-family applicability is established by trustworthy evidence.
5. Preserve stale PR #166 as historical finance evidence only; do not merge it blindly.

## Direction result

ALIGNED
