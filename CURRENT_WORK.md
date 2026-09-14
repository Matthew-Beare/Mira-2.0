# CURRENT_WORK.md

## Recovery Contract
- Read `PROJECT_INSTRUCTIONS.md`, then this file.
- Verify remote `main`, this packet branch/head, PR state, and relevant CI before doing work.
- If Git contradicts this checkpoint, reconcile this file first. Never repeat merged work.

## Current Packet
- Packet: `M2-M1-047`
- Branch: `work/m2-m1-047-finance-historical-backfill`
- Base: remote `main` at `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`
- State: ACTIVE
- Prior packet `M2-M1-046` / PR #116 is merged; its stale ACTIVE checkpoint was reconciled here.

## Objective
Close the historical finance coverage gap by reconciling all trustworthy provider-visible history into canonical MIRROR finance state with stable provider transaction identity, provenance, and exact readback. Do not use 2026-09-01 as a history exclusion boundary.

## Verified Evidence This Packet
- Connected finance accounts were read before transaction conclusions. The provider currently exposes transaction history for the relevant deposit and credit accounts back into 2024; account-specific reported history windows vary, with the oldest verified returned transaction in the broad pre-2026-09-01 retrieval dated `2024-08-22`.
- A broad posted, transfer-inclusive query for dates before `2026-09-01` returned 400 rows and `has_more=true`; the next page returned another 400 rows and still reported `has_more=true`. Therefore at least 800 provider-visible historical rows exist before the recurring-process boundary. This is a lower bound, not a final count.
- Canonical `Financial Escape` / `FinOps Ledger` currently begins at `2026-01-02`; direct sheet readback confirms no 2024 or 2025 ledger rows in the scanned canonical range. The historical gap is therefore real and materially larger than previously checkpointed.
- Provider rows include stable `transaction_id`, account identity, posted date, amount, merchant/name/category data, and transfer semantics sufficient to preserve source identity during import. Some historical check rows do not expose payee/memo/check-image data; those fields must remain explicitly unknown unless corroborated by another source.

## Acceptance Criteria
1. Enumerate all provider-visible posted transaction history before the current canonical ledger start using pagination until `has_more=false` for every relevant linked account/history window.
2. Import missing historical rows into the existing `FinOps Ledger` using stable provider `transaction_id` identity and deterministic `Event ID`; preserve source account/date/amount/vendor/category/provenance and do not overwrite existing production rows.
3. Preserve transfers and zero-economic-spend rows as evidence while keeping their economic-spend treatment explicit; never infer income merely from retrieval inclusion.
4. Reconcile duplicates against existing canonical transaction IDs before each write batch.
5. Exact readback proves imported transaction IDs, dates, amounts, and row counts; unavailable source gaps are recorded explicitly rather than filled by assumption.
6. Historical user corrections already supplied during reconciliation are applied only when identity is sufficiently supported; ambiguous checks remain unresolved.
7. When finance history is fully reconciled or durably bounded by actual provider unavailability, checkpoint completion and move next to the Android inventory/scanning vertical reusing INV-001, INV-002, MOVE-001, IDENT-001, ASSET-001/002/003.

## Exact Resume Point
Continue the pre-`2026-09-01` finance pagination from the verified 800-row lower bound until exhaustion, preferably account-scoped using linked-account history windows to prove coverage. Then deduplicate against canonical `FinOps Ledger` transaction IDs and append missing rows in bounded batches with exact readback after every batch. Do not begin Android inventory work until this finance gate is closed or source-unavailability is durably proven.

## Six-Line Customer Status
Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: Verified the canonical ledger starts 2026-01-02 while the connected provider exposes at least 800 older rows reaching 2024-08-22; the stale merged checkpoint is reconciled.
Last 24h: Historical finance source coverage was proven to extend well before MIRA 2.0 instead of being artificially bounded at September 2026.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
