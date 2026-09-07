# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point. Detailed prior evidence remains preserved in Git history and packet checkpoints.

## Active packet

### `M2-M1-014A` — Financial Escape canonical source/reconciliation

- **Primary work:** `FIN-SOURCE-TRUTH-001`, `FIN-RECEIPT-RECON-001`, `FIN-RETURN-RECON-001`.
- **Related existing work/features:** `RECEIPT-INTAKE-001`, `RECEIPT-TAXONOMY-001`, `SPEND-ROLLUP-001`, `FIN-PROVIDER-INTEGRATION-001`, `FIN-LIVE-VERIFY-001`, `MILE-001`, `MILE-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-014a-financial-source-truth`.
- **Base SHA:** `f05d59d5e3204717d319059df1a4f764332b96d5`.
- **Current status:** implementation checkpoint complete. Canonical reconciliation, query surfaces, high-contrast mobile Dashboard, rolling verified net worth, Drive organization, and the active twice-daily update contract are installed. Packet remains active only until the next real scheduled run is read back successfully.

## Objective

Make Financial Escape trustworthy enough to drive a rapid debt-exit plan. Posted provider transactions remain the authority for money actually moved; receipt/order/email history identifies what was purchased and whether it was returned/refunded; user corrections outrank inferred classifications. The private Sheets are projections/review surfaces, not a second financial authority.

## Acceptance criteria

1. Define and implement a single-source-of-truth reconciliation contract: one economic event is counted once; provider transaction identity controls posted cash; receipt/order evidence enriches item/category/necessity; refund/return evidence reverses or offsets the matched purchase without double counting.
2. Ingest the user-provided full mailbox export as historical evidence without committing private contents to public Git.
3. Reconcile known return/refund examples, including Amazon/order returns, before category/month totals are treated as final.
4. Update current reserve policy to one month of holdout bills plus the separately protected career-transition/emergency amount and other explicit protected commitments, using only private provider/Sheet state for values.
5. Establish monthly whole-household spend composition and month-over-month category metrics from posted transactions, with receipt evidence improving purpose classification but never duplicating transaction amounts.
6. Financial Escape actual progress changes only from posted debt/cash evidence. Forecasts may model future capacity but never pre-credit unposted payments or predicted miles.
7. Preserve the Android packet's exact provider-inspection resume point and do not expand this finance packet into Android implementation.
8. Public Git contains only sanitized contracts/evidence status. No private balances, account IDs, transaction rows, mailbox contents, spreadsheet IDs, email text, or household-specific values.

## Packet split

This refinement is deliberately split so the command center does not become another unbounded spreadsheet rewrite:

- `M2-M1-014A` **ACTIVE — IMPLEMENTATION COMPLETE; LIVE-FIRE VERIFICATION PENDING** — canonical source/reconciliation, mailbox ingestion, returns, reserve correction, stable-ID dedupe, query surfaces, mobile contrast repair, rolling verified net worth, canonical Drive hierarchy, and twice-daily refresh contract.
- `M2-M1-014B` **ABSORBED BY CUSTOMER PRIORITY** — the phone-first contrast/readability repair was completed in this packet; broader visual refinements remain optional future work.
- `M2-M1-014C` **ABSORBED BY CUSTOMER PRIORITY** — the active AM/PM jobs now carry the idempotent refresh/readback contract; only observation of the next actual scheduled firing remains.

## Displaced Android packet checkpoint

`M2-M1-012 — Android representative-device execution proof` is displaced only by explicit customer reprioritization. Its resume point is unchanged:

1. Hold at Google provider inspection until a credible authenticated Google Cloud administration capability exists.
2. Then perform exactly one bounded inspection of the existing Android OAuth client package/SHA-1 and Picker API enabled state.
3. Read provider state back exactly; enable only Picker if inspection proves it disabled and packet authority still permits that mutation.
4. Only after successful provider readback, run one phone test using the already-installed proof APK.
5. If it still fails, checkpoint the exact result before any app-side OAuth/result patch.

Do not repeat phone tests, speculative OAuth patches, or Google Cloud mutations while `M2-M1-014A/B/C` are active.

## Exact next action / resume point

1. Observe the next real enabled AM or PM scheduled run at its configured America/New_York slot.
2. Verify the run refreshed source coverage, upserted by stable identity, preserved one snapshot per date, rebuilt the rolling verified-net-worth projection, and read all integrity gates back successfully.
3. If successful, record the sanitized live-fire evidence and close `M2-M1-014A`; if any gate fails, keep the packet active and report the exact fail-closed Action Required.
4. Resume displaced Android packet `M2-M1-012` only after this finance live-fire acceptance is recorded.

## Recovery protocol

Start by reading this file and `docs/work-packets/M2-M1-014A.md`, verify the branch/head, then continue from the exact next action. Private finance/mail values must be re-read from providers or approved private artifacts; never reconstruct them from public Git or stale chat summaries.
