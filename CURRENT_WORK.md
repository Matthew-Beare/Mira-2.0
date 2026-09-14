# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-047` — Historical finance backfill

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `FIN-001`, `RECEIPT-001`.
- **Related invariants/features:** `RECOVERY-001`, `RECOVERY-002`, `ORDER-001`, `ORDER-002`, `ASSET-001`, `ASSET-002`, `ASSET-003`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-047-finance-historical-backfill`.
- **Base SHA:** `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`.

## Recovery contract

- Read `PROJECT_INSTRUCTIONS.md`, then this file.
- Verify remote `main`, this packet branch/head, PR state, and relevant CI before doing work.
- If Git contradicts this checkpoint, reconcile this file first. Never repeat merged work.
- Prior packet `M2-M1-046` / PR #163 is merged into current `main`; its stale ACTIVE checkpoint is superseded by this packet.

## Objective

Close the historical finance coverage gap by reconciling all trustworthy provider-visible history into canonical MIRROR finance state with stable provider transaction identity, provenance, and exact readback. Do not use 2026-09-01 as a history exclusion boundary.

## Verified evidence this packet

- Connected finance accounts were read before transaction conclusions. The provider exposes relevant deposit/credit history back into 2024; the oldest verified row in the broad pre-2026-09-01 retrieval is dated `2024-08-22`.
- Two broad posted, transfer-inclusive retrieval pages produced at least 800 provider-visible rows before 2026-09-01, and the second page still reported more data. This is a lower bound, not a final count.
- Canonical `Financial Escape` / `FinOps Ledger` begins at `2026-01-02`; direct sheet readback found no 2024 or 2025 rows in the canonical range inspected. The historical gap is therefore real and materially larger than previously checkpointed.
- Provider rows expose stable `transaction_id`, account identity, posted date, amount, merchant/name/category data, and transfer semantics suitable for deterministic source identity. Missing check payee/memo/image data remains unknown unless corroborated by another source.
- Remote `main` is verified at `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`. PR #165 is the active packet PR. Initial CI #661 failed only at the repository work-session alignment gate because the checkpoint format did not satisfy the canonical parser; this file repairs that governance defect before additional product writes.

## Acceptance criteria

1. Enumerate provider-visible posted transaction history before the current canonical ledger start until source exhaustion for every relevant linked account/history window.
2. Import missing historical rows into the existing `FinOps Ledger` using stable provider `transaction_id` identity and deterministic `Event ID`; preserve source account/date/amount/vendor/category/provenance and do not overwrite existing production rows.
3. Preserve transfers and zero-economic-spend rows as evidence while keeping their economic-spend treatment explicit; never infer income merely from retrieval inclusion.
4. Reconcile duplicates against existing canonical transaction IDs before each write batch.
5. Exact readback proves imported transaction IDs, dates, amounts, and row counts; unavailable source gaps are recorded explicitly rather than filled by assumption.
6. Historical user corrections already supplied during reconciliation are applied only when identity is sufficiently supported; ambiguous checks remain unresolved.
7. When finance history is fully reconciled or durably bounded by actual source unavailability, checkpoint completion and move next to the Android inventory/scanning vertical reusing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`.

## Session-start alignment verification — 2026-09-14

### `FEATURES.md`

ALIGNED. This packet advances existing finance/recovery/evidence/asset semantics and does not create a parallel ledger or inventory model.

### `BACKLOG.md`

ALIGNED. `FIN-CANON-AUDIT-001` remains the highest-priority blocker. Android inventory/scanning stays next only after historical finance closure or a source-unavailability boundary is actually proved.

### `ROADMAP.md`

ALIGNED. The work preserves provider truth, explicit provenance, canonical state, exact readback, and ordinary-user MIRA behavior rather than defining a convenient artificial history boundary.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Historical reconciliation is existing `FIN-CANON-AUDIT-001` work.
- The next inventory/scanning outcome is already represented by `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, and `ASSET-003`.
- No new material product feature is introduced by this checkpoint repair.

### Direction result

ALIGNED

## Exact resume point

1. Require exact-head CI green on PR #165 after this alignment repair.
2. Continue pre-canonical-start finance pagination to source exhaustion, preferably account-scoped to prove coverage.
3. Read canonical `FinOps Ledger` transaction IDs before every bounded append and import only missing provider identities.
4. Exact-read back every write batch before the next batch.
5. Do not begin Android inventory implementation until the historical finance gate is closed or source unavailability is durably proven.

## Six-line customer status

Objective: Reconcile the complete provider-visible historical finance record into MIRROR before starting inventory scanning.
Progress: Verified the canonical ledger starts 2026-01-02 while connected provider history reaches at least 2024-08-22; stale merged work was reconciled and the active checkpoint now satisfies repository governance.
Last 24h: Historical finance source coverage was proven to extend well before MIRA 2.0 instead of being artificially bounded at September 2026.
Deliverable: Canonical FinOps history backfilled to the provider's actual oldest available boundary with exact transaction-ID readback and explicit unavailable gaps.
Expected delivery: UNKNOWN
Blocker: none
