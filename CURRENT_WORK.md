# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-004B` — Feature Audit Slice C2 — receipt and financial evidence foundations

- **Merged PR:** #8
- **Merge SHA:** `310ce64c5d6c3c733c692b7bca487b7b90d88be7`
- **Audited features:** `RECEIPT-001`, `RECEIPT-002`, `SPEND-001`, `RECEIPT-003`, `PAYMENT-001`, `REIMB-001`
- **Result:** receipt identity/history and merchant-payment core are separated from bounded spending, taxonomy and reimbursement gaps.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-004C`
- **Name:** Feature Audit Slice C3 — optional subscriptions/full-finance direction and category-C closure
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit the final two category-C directions, then reconcile dependencies/evidence across all commerce/receipt/payment/spending features and close category C without beginning asset/inventory work.

## Audit rows in this packet

1. Optional subscription/free-trial tracking.
2. Credit-card linkage / complete financial ingestion direction.
3. Bounded category-C consistency pass across `ORDER-*`, `RECEIPT-*`, `SPEND-*`, `PAYMENT-*`, `REIMB-*` and any new stable IDs created here.

Do not begin category D in this packet.

## Acceptance criteria

1. Subscription/free-trial tracking is classified from current requirement evidence rather than resurrecting a paused historical automation by accident.
2. Complete bank/card ingestion is separated from receipt-derived spending and merchant-payment reconciliation.
3. Privacy, connector scope, account coverage, pending/posted semantics and readback requirements are recorded before any future full-finance implementation can be considered complete.
4. All category-C dependency/evidence contradictions are resolved or explicitly queued.
5. No legacy connected account or Google data is treated as MIRA 2.0 integration/live proof.
6. `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are the only intended changed files.
7. A small PR is scope-verified, merged, and remotely read back.
8. `CURRENT_WORK.md` advances to a bounded first category-D packet.
9. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-004c-finance-direction-close-c` from current `main`. Inspect category-C row 11: **Optional subscription/free-trial tracking**, including whether any current direct requirement supersedes its historical proposed/paused status. Assign a stable feature ID/evidence state before auditing full financial ingestion.

## Next packet boundary

After category C closes, split category D into bounded asset/inventory audit packets before implementation work. The first exact category-D row is **Stable asset identity and item-to-vehicle/equipment fitment**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
