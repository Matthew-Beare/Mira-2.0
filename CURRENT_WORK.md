# MIRA 2.0 — Current Work

## Customer status

Objective: Make MIRA behave like one usable Personal product instead of a collection of verified modules.
Progress: M2-M0-031 is merged on main at `3ecf6c058aa02032090020c9e8dc2790bb7ad4f9`. M2-M0-032 now advances `GOOGLE-BOOTSTRAP-001` with deterministic selected-service planning and fail-closed capability verification for Personal Google Workspace.
Last 24h: PR #169 merged Personal orchestration. The new Google bootstrap branch now contains `mira/google_bootstrap.py`, deterministic tests, packet definition, and code-ownership registration.
Deliverable: A tested bootstrap planner/verifier that never treats authorization, declared scopes, code existence, or another Google service as proof that an explicitly selected service is usable.
Expected delivery: Implementation is written; PR and exact-head CI remain.
Blocker: None for M2-M0-032. Android representative-device proof remains independently human-blocked and out of scope.

## Recovery authority

This file is the authoritative execution checkpoint for this branch. Chat context is disposable. Re-read repository instructions, remote main, this branch, open PRs and CI before implementation or merge.

## Active packet

### `M2-M0-032` — Personal Google bootstrap

- **Primary work:** `GOOGLE-BOOTSTRAP-001`
- **Primary features:** `PROVIDER-003`, `ONBOARD-007`
- **Related invariants/features:** `PROVIDER-002`, `SOURCE-001`, `SERVICE-001`
- **Branch:** `work/m2-m0-032-google-bootstrap`
- **Base:** `3ecf6c058aa02032090020c9e8dc2790bb7ad4f9`
- **State:** implementation + deterministic tests written; PR/CI pending
- **Owned surfaces:** `mira/google_bootstrap.py`, `tests/test_google_bootstrap.py`
- **Shared/high-contention surfaces:** `CURRENT_WORK.md`, `BACKLOG.md`, `project/code_ownership.json`
- **Execution invariant:** bootstrap planning and proof perform no provider authorization, provider mutation, or service activation
- **Evidence invariant:** every selected service must independently prove fresh required gates; missing/mismatched/declared-only evidence fails closed

## Session-start alignment verification — 2026-09-26

### `FEATURES.md`

`PROVIDER-003` already requires a deterministic Personal Google bootstrap adapter with strict drift/readback verification. This packet implements a bounded planning/proof slice without redefining provider onboarding or service activation.

### `BACKLOG.md`

`GOOGLE-BOOTSTRAP-001` is the existing queued prerequisite after `MIRA-SKILL-001`. M2-M0-031 satisfied the orchestration prerequisite, so M2-M0-032 is the shortest remaining product-activation step before broader `NONTECH-INSTALL-001` hardening.

### `ROADMAP.md`

The ordinary Personal Google/no-app path remains governing direction. This packet deliberately avoids terminal fallback, private updater behavior, or developer-console ceremony.

### Idea/backlog capture audit

No materially new product idea was introduced. M2-M0-032 implements existing `GOOGLE-BOOTSTRAP-001` / `PROVIDER-003` semantics. `CAPTURE AUDIT COMPLETE`.

### Direction result

ALIGNED

## Next bounded step

1. Open the M2-M0-032 PR.
2. Require exact-head CI and ownership/session gates.
3. Fix real failures only; do not widen into OAuth, live provider mutation, or nontechnical-install UX.
4. Reconcile shared files against current `main` immediately before merge.
5. Merge only after exact-head evidence, then read back remote `main` and post-merge CI.

## Integrated prerequisite — M2-M0-030 / SERVICE-COMPOSE-001

- PR #168 merged to main at `9cb5d12601c9100ef20b265f2797a648dc155171`.
- The production Personal `briefs` bundle derives readiness from `OPS-001`, `OPS-003`, `OPS-004`, `RECOVERY-001`, and `RECOVERY-002`.
- Missing dependency evidence fails closed.
- Readiness never silently activates a service.
- An active service suspends if capability/dependency readiness is lost.

## Waiting packet — Android representative-device proof

The Android proof remains preserved but is not allowed to consume automated product-development cycles:

- `ANDROID-CAPTURE-001` deterministic/integration implementation remains merged/test-verified.
- Live representative-device proof remains unfinished.
- Resume only when a representative Android device and provider consent are actually available.
- Do not treat repeated CI/checkpoint refreshes of this human-only blocker as product progress.

## Next bounded step

1. Open the M2-M0-031 PR.
2. Require exact-head CI and ownership/session gates.
3. Fix real failures only; do not widen scope.
4. Merge only after exact-head evidence and reconcile against current main.
5. Read back merged main and post-merge CI.
6. Then move to `GOOGLE-BOOTSTRAP-001` or `NONTECH-INSTALL-001` based on the remaining shortest path to ordinary-user activation; do not return to human-blocked Android proof unless the required device/provider action becomes available.

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
- Remote `main` was independently re-read this worker cycle as `a1d4f1981fba7f85c65138ab5999e681a755cc38` (`Verify exact VEVOR transmission jack model and full manual`). CI run `35997215732` and Trusted Runner Gate run `35997372909` are green on that exact head.

### Idea/backlog capture audit

This evidence-quality correction introduces no new feature. It tightens evidence classification under existing asset/evidence/knowledge semantics. `CAPTURE AUDIT COMPLETE`.

## Inventory evidence reconciliation — 2026-09-24 worker cycle

- Canonical Tool Inventory readback: row 115 / `TI-0030` is `Transmission jack`, quantity 1, hydraulic, `verified_existing_inventory`; brand/model/date/seller/price/order/receipt remain blank in the legacy row.
- Retained Amazon purchase evidence independently resolves a purchase on 2026-07-09 for $229.32, Amazon order `111-9893607-5225060`, described as `VEVOR Transmission Jack, 1322 LBS Hydraulic Telescoping Transmission Jack, 32\"-67\" High Lift Transmission Jack Stand with Foot Pedal, 360° Swivel Wheel`.
- The Financial Escape purchase evidence independently carries the same date, amount, order number, merchant context, and `VEVOR Hydraulic Transmission Jack` description.
- Fresh manufacturer verification resolves the matching VEVOR product to Item Model Number `HTJ-1322`. The official VEVOR page matches the retained purchase on manufacturer, product class, 1322-lb capacity, hydraulic telescoping/foot-pedal design, high-lift range and swivel-wheel configuration; this is sufficient exact-model evidence rather than a guessed SKU.
- The same official exact-product page exposes `User manual-en (PDF)` under Product guides and documents. This is a full manufacturer user manual, not a setup/QSG artifact, and is eligible manual evidence for `HTJ-1322`.
- Therefore `TI-0030` is now reconciled conceptually to Brand = VEVOR; Model = `HTJ-1322`; variant = 1322 lb hydraulic telescoping high-lift transmission jack; purchase date = 2026-07-09; seller = Amazon; price = $229.32; order = `111-9893607-5225060`; manual status = manufacturer full user manual verified on exact-model product page.
- Protected legacy production data was not mutated in this cycle; the verified reconciliation is checkpointed here for a later bounded write only after the target MIRA evidence surface is explicit.

## Bounded powered/precision evidence pass — 2026-09-24

- Re-read MIRA Durable Operating Addenda, ROADMAP and BACKLOG before continuing the active packet. Direction remains aligned with existing `IDENT-001` / `ASSET-001` / `EVID-001` / `INV-001` semantics; no new feature was introduced.
- Fresh Drive searches for `compressor`, `drill press`, `pressure washer`, `vacuum pump`, `Robinair`, `Bauer`, and `WEN` produced either the legacy Tool Inventory itself, unrelated vehicle-service documents, or no result. None established an exact manufacturer/model identity for a pending powered/precision asset.
- Fresh connected-Gmail searches for powered/precision purchase terms and likely meter/tool brands likewise produced no trustworthy matching receipt/model evidence. A broad Harbor Freight query surfaced unrelated Snap-on correspondence, demonstrating why keyword presence alone is not acceptable identity evidence.
- The Tool Inventory provider remains discoverable and indexed, but the spreadsheet-row connector could not parse the expected tab name during this run. That connector failure was not treated as evidence that rows disappeared or changed.
- No exact model, SKU, serial, receipt link, or manual was attached from these searches. Setup/QSG artifacts remain ineligible as full manuals.
- Protected historical production data was not mutated.
- `CAPTURE AUDIT COMPLETE`.

## Worker reconciliation — 2026-09-24

- Re-read live `main`, open pull requests, CI, `FEATURES.md`, `BACKLOG.md`, and the active resume point before further work.
- Live `main` at cycle start was `a1d4f1981fba7f85c65138ab5999e681a755cc38`; both CI (`35997215732`) and Trusted Runner Gate (`35997372909`) completed successfully on that exact head.
- Open PR #166 remains stale historical finance evidence and is not a merge candidate. No live Git evidence justified replaying or reprioritizing it.
- The active packet remains aligned with `ASSET-001`, `IDENT-001`, `EVID-001`, `INV-001`, and the human-gated Android proof. No new feature or backlog item was introduced. `CAPTURE AUDIT COMPLETE`.
- This checkpoint reconciles stale head/CI references only; it does not claim new provider, inventory, manual, or live-device evidence.

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
3. Persist the verified `TI-0030` exact-model/manual evidence only onto the explicit MIRA evidence surface when that write target is resolved; do not overwrite protected legacy rows merely to reduce backlog counts.
4. Prefer retained purchase evidence with exact product title + order/date/amount or physical label/serial evidence; do not spend repeated cycles on broad brand guesses that have already returned no trustworthy identity.
5. For `TI-0027`, do not attach a Rotary manual until exact/model-family applicability is established by trustworthy evidence.
6. Preserve stale PR #166 as historical finance evidence only; do not merge it blindly.

## Direction result

ALIGNED
