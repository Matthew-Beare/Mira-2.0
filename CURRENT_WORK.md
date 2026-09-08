# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point.

## Active packet

### `M2-M1-015` — Canonical finance evidence audit and projection repair

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `MIRROR-001`, `AUTH-001`, `RECEIPT-001`, `ASSET-001`.
- **Related invariants/features:** `MIRROR-001`, `AUTH-001`, `RECEIPT-001`, `RECEIPT-002`, `ASSET-001`, `ASSET-002`, `IDENT-001`, `EVID-001`, `RECOVERY-002`.
- **Related work:** `ASSET-SERVICE-001`, `FINANCE-CONNECTOR-001`, `SPEND-ROLLUP-001`, `FIN-EVIDENCE-RECONCILE-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-015-financial-canonical-audit`.
- **Base SHA:** `5075a23c0a3513118b0dceaf711cd041b1d3798a`.
- **Latest sanitized packet checkpoint:** `89d65fb0a705c7d00b9fd7e60162946b42cf25ab`.
- **Packet:** `docs/work-packets/M2-M1-015.md`.
- **Current status:** customer-priority override active; private-live canonical finance repair is in progress. One-authority spending integration is implemented and read back; broader retirement/confidence/cross-source evidence work remains open.

## Objective

Make the private Financial Escape system a faithful projection over one canonical MIRROR finance/evidence/entity model, remove obsolete retirement-contribution acceleration modelling, make confidence reporting dimension-specific, activate replay-safe allowance-owner debits, and reconcile the currently available connected-account, mail, marketplace, receipt/refund and asset evidence without double-counting economic events.

Public Git contains only generalized product/engineering semantics and sanitized verification claims. Private amounts, account/provider identifiers, email/receipt contents, order identifiers and live document identifiers stay outside the public repository.

## Required invariants

- One canonical authority per mutable data class; spreadsheets/charts/review forms are projections or bounded input surfaces, never parallel writable truth stores.
- Provider-observed transactions represent money movement. Orders, receipts, shipments, cancellations, returns and refund notices are evidence and must not independently create duplicate spend.
- Refunds change net economic spend only when supported by the canonical economic reversal/credit evidence.
- Explicit user corrections control semantic classification; unknown remains unknown when evidence is insufficient.
- Category/purpose, necessity, and allowance are independent facts. Blank allowance input resolves to unknown; only explicit `NO ALLOWANCE` can represent no allowance, while `MATTHEW`/`JESSICA` are person assignments.
- Retirement account value may remain factual asset/net-worth evidence, but Financial Escape must not model contribution reduction as a payoff lever.
- Allowance allocation is a derived earmark over canonical events; it must not mutate provider cash and must be replay/dedup safe.
- Durable physical acquisitions link to the existing canonical asset/evidence model with exact supported identifiers; model/serial/manual/warranty facts are never guessed.
- Continuous reconciliation is not claimed unless an actual scheduler/runtime is implemented and live-verified.

## Acceptance state

- Customer priority override: **accepted**.
- Governance packet specified: **satisfied** (`M2-M1-015`).
- One-authority spending integration: **private-live readback verified**.
- Spending review is a bounded input surface, not analytics authority: **verified**.
- Spending insights query canonical ledger rather than review input: **verified**; exact readback found zero review-sheet references in the insights projection.
- Unknown versus explicit no-allowance semantics: **implemented and read back**.
- Deterministic allowance debit-key uniqueness: **test-verified at zero duplicates**.
- Person-specific allowance debit live example and matched refund/reversal proof: **pending**.
- Public branch checkpoint for the above: **in progress until remote branch readback and merge/checkpoint reconciliation**.
- Retirement-contribution payoff lever removed: **pending**.
- Confidence semantics repaired: **pending**.
- Connected-account comprehensive reconciliation: **pending**.
- Supplied mail-archive end-to-end disposition audit: **pending**.
- Connected-mail dedupe/reconciliation: **pending**.
- Marketplace purchase/order/refund reconciliation: **pending**.
- Receipt/evidence relation repair: **pending**.
- Durable acquisition asset linkage/manual/warranty enrichment: **pending evidence-dependent**.
- Sanitized cross-source audit report/readback: **pending**.

## Exact next action / resume point

1. Remotely verify the active branch checkpoint containing the one-authority spending repair and this CURRENT_WORK reconciliation.
2. Remove the obsolete retirement-contribution reduction controls/scenarios/charts/formula dependencies from the private Financial Escape projection while retaining factual retirement assets as asset/net-worth evidence.
3. Replace the blanket finance confidence label with precise source/data evidence and trajectory-maturity semantics.
4. Prove replay-safe person-specific allowance debits from canonical positive economic events and a matched economic reversal restoring the allocation projection, without mutating provider cash.
5. Parse and disposition the supplied mail archive end-to-end; reconcile transactional evidence against connected account/card activity, current connected mail and the available marketplace purchase archive.
6. Update canonical receipt/evidence/entity relations and link supported durable physical acquisitions into the asset model with exact identifiers/manual/warranty evidence where available.
7. Read back exact private provider/workbook state, record sanitized evidence/counts in the packet, reconcile lifecycle/backlog state and only then close or split remaining runtime work.

## Displaced packet checkpoint

### `M2-M1-012` — Android representative-device execution proof

`M2-M1-012` is intentionally displaced, not closed. Its previous evidence and hold rule remain valid.

- **Recovery branch:** `work/m2-m1-012-provider-tooling-hold-2`.
- **Stable pre-Financial-Escape checkpoint:** `6e715159feed0b044e3ef3ef610916903e2deb09`.
- **Provider-inspection runbook:** `docs/work-packets/M2-M1-012-provider-inspection-runbook.md`.
- **Earned device proof:** exact stable-development-signed APK installed/launched; native Google account chooser opened; correct account selected; app returned `authorization_cancelled`; no consent screen or Drive Picker appeared.
- **Expected proof identity:** package `com.mira.deviceproof`; signing SHA-1 `AF:E0:18:6B:7C:21:EA:74:D3:4C:4A:33:04:FF:B1:15:EF:DB:A5:6D`.
- **Unknown provider state:** actual Android OAuth registered package/SHA-1 and Google Picker API enabled/disabled state.

### Exact Android resume point

Hold until a credible authenticated provider-access recovery signal exists. Then perform exactly one bounded inspection against the existing development project:

1. read the existing Android OAuth client's registered package name;
2. read its signing SHA-1;
3. compare both to the expected proof identity above;
4. if either mismatches, checkpoint and stop with zero provider mutations;
5. if both match, read Google Picker API enabled/disabled state;
6. enable **only Google Picker API**, only if inspection proves it disabled and packet authority still permits that one mutation;
7. read back final provider state exactly;
8. only then run one phone test with the already-installed exact proof APK;
9. if it still fails, checkpoint the exact live result before any app-side OAuth diagnosis.

Until that recovery signal exists: do not rerun the phone flow, do not infer provider configuration, do not create/alter a Cloud project or OAuth client, do not change Picker state, and do not burn another Work-mode attempt speculatively.

## Session-start alignment verification — 2026-09-07

### `FEATURES.md`

Reviewed before implementation. The active packet is grounded in the canonical one-authority MIRROR model, receipt/evidence provenance, canonical asset acquisition/identity semantics, and recovery/readback requirements. It does not create a finance-specific second authority or silently broaden provider permissions.

### `BACKLOG.md`

Reviewed before implementation. `FIN-CANON-AUDIT-001` is the active integrity blocker. Repeatable future evidence reconciliation is separately queued as `FIN-EVIDENCE-RECONCILE-001`; it is not being misrepresented as already-live background execution.

### `ROADMAP.md`

Reviewed before implementation. The customer-priority financial integrity repair is a bounded interruption with the exact Android M2-M1 resume point preserved. The Personal Google product direction, shared canonical state, and ordinary-user architecture remain unchanged.

### Direction result

**ALIGNED.** `M2-M1-015` is the sole active packet. It repairs private-live projections and reconciles evidence into existing canonical MIRROR semantics without changing the long-term authority model or erasing the displaced Android checkpoint.

## Recovery protocol

Start by reading this file, `docs/work-packets/M2-M1-015.md`, and remote `main`. Verify the active packet/branch/head before writes. If `M2-M1-015` is later displaced, checkpoint its exact audit/reconciliation cursor and unresolved exception set before switching. To resume Android, use only the `M2-M1-012` exact resume point above and its provider-inspection runbook.
