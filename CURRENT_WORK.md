# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and the exact safe resume point.

## Active packet

### `M2-M1-015` — Canonical finance evidence audit and projection repair

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `MIRROR-001`, `AUTH-001`, `RECEIPT-001`, `ASSET-001`.
- **Related features/work:** `RECEIPT-002`, `ASSET-002`, `IDENT-001`, `EVID-001`, `ASSET-SERVICE-001`, `FINANCE-CONNECTOR-001`, `SPEND-ROLLUP-001`, `FIN-EVIDENCE-RECONCILE-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-015-financial-canonical-audit`.
- **Base SHA:** `5075a23c0a3513118b0dceaf711cd041b1d3798a`.
- **Latest sanitized audit checkpoint:** `2452d3c6c64fb097ebc4125d92b1e009af9086bc`.
- **Packet:** `docs/work-packets/M2-M1-015.md`.
- **Latest audit record:** `docs/work-packets/M2-M1-015-audit-checkpoint-2026-09-07.md`.
- **Current status:** private-live one-authority spending, retirement-lever removal, confidence repair, main-dashboard verified-net-worth visibility, current-window transaction identity reconciliation, evidence dedup/disposition invariants and bounded connected-Gmail incremental ingestion are verified. Marketplace reconciliation, full raw-mail archive disposition, pre-2026 projection backfill, allowance reversal proof and evidence-dependent asset enrichment remain open.

## Objective

Make Financial Escape a faithful projection over one canonical MIRROR finance/evidence/entity model; reconcile currently available account, mail, marketplace, receipt/refund and asset evidence without duplicate economic effects; and leave every unresolved coverage gap explicit rather than guessed.

Public Git contains only generalized semantics and sanitized verification claims. Private amounts, account/provider identifiers, email/receipt contents, order identifiers and live document identifiers stay outside the public repository.

## Required invariants

- One canonical authority per mutable data class; dashboards/charts/review forms are projections or bounded input surfaces, never parallel writable truth stores.
- Provider-observed transactions represent money movement. Orders, receipts, shipments, cancellations, returns and refund notices are evidence and must not independently create duplicate spend.
- Refunds change net economic spend only when supported by canonical economic reversal/credit evidence.
- Explicit user corrections control semantic classification; unknown remains unknown when evidence is insufficient.
- Category/purpose, necessity and allowance are independent facts. Blank allowance is unknown; only explicit `NO ALLOWANCE` means no allowance, while `MATTHEW`/`JESSICA` are person assignments.
- Retirement value may remain factual asset/net-worth evidence; contribution reduction is not a payoff lever.
- Allowance allocation is a derived earmark over canonical events; it must not mutate provider cash and must be replay/dedup safe.
- Live Gmail and historical Takeout feed the same canonical evidence index. Source overlap is a dedupe problem, never a second purchase.
- Explicit non-economic/support evidence outranks incidental order numbers or amount-like text during evidence disposition.
- Durable physical acquisitions link to the existing canonical asset/evidence model only with supported identifiers; model/serial/manual/warranty facts are never guessed.
- Continuous reconciliation is not claimed unless an actual scheduler/runtime is implemented and live-verified.

## Acceptance state

- Governance packet specified: **satisfied**.
- One-authority spending integration: **private-live verified**.
- Spending review as bounded input surface: **verified**.
- Spending insights read canonical ledger rather than review input: **verified**.
- Unknown versus explicit no-allowance semantics: **verified**.
- Deterministic allowance debit-key uniqueness: **test-verified at zero duplicates**.
- Retirement-contribution payoff lever removed: **private-live verified**.
- Factual retirement assets retained only as asset/net-worth evidence: **private-live verified**.
- Confidence semantics repaired: **private-live verified**.
- Verified net worth exposed in the Dashboard one-glance panel: **private-live verified**; it references the existing verified-net-worth calculation and creates no second authority.
- Current 2026 transaction identity reconciliation: **integration-verified**; provider transaction identities equal MIRROR transaction identities and transaction→economic-event relations in the active projection window. Economic-event count may be lower because supported reversals collapse into original event lineage.
- Pre-2026 provider-history projection: **open historical backfill**; provider history exists but is not yet represented in the current event projection.
- Canonical evidence dedup invariant: **test-verified**; current index has zero duplicate dedup keys.
- Indexed evidence disposition coverage: **test-verified**; every currently indexed evidence row has one deterministic disposition and the disposition gap is zero.
- Connected-Gmail incremental evidence path: **bounded live verification earned**; current new evidence is admitted to the same Receipt Index and explicit non-economic commerce evidence does not create spend.
- Raw supplied mail archive end-to-end disposition: **pending**; indexed evidence does not yet prove disposition of every raw mailbox message.
- Marketplace purchase/order/refund reconciliation: **pending and next**.
- Person-specific allowance debit plus matched refund/reversal proof: **pending supported live evidence; do not invent an owner assignment**.
- Durable acquisition asset linkage/manual/warranty enrichment: **pending evidence-dependent**.
- Sanitized final cross-source report/readback: **pending**.

## Exact next action / resume point

1. Reconcile the available marketplace purchase archive order-by-order against the canonical Receipt Index and provider-backed economic events without creating spend from order evidence alone.
2. Record cancelled, returned, refunded, unmatched and ambiguous marketplace lineages explicitly. Only provider-backed credits may reverse economic spend.
3. Recover or reconstruct the raw-mail parser/exclusion audit trail so every supplied archive message can receive a deterministic disposition, or record a deliberate durable coverage boundary if the raw source cannot be recovered.
4. Prove a person-specific allowance debit and matched reversal only when supported live owner/reversal evidence exists.
5. Link supported durable acquisitions into the canonical asset/evidence graph with exact identifiers/manual/warranty evidence where available.
6. Read back exact private provider/workbook state, record sanitized counts/invariants, reconcile lifecycle/backlog state and only then close or split remaining runtime work.

## Displaced packet checkpoint

### `M2-M1-012` — Android representative-device execution proof

`M2-M1-012` is intentionally displaced, not closed.

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

Until that recovery signal exists: do not rerun the phone flow, infer provider configuration, create/alter a Cloud project or OAuth client, change Picker state, or burn another Work-mode attempt speculatively.

## Recovery protocol

Start by reading this file, `docs/work-packets/M2-M1-015.md`, `docs/work-packets/M2-M1-015-audit-checkpoint-2026-09-07.md`, and remote branch head. Verify packet/branch/head before writes. If `M2-M1-015` is displaced, checkpoint the exact reconciliation cursor and unresolved exception set first. To resume Android, use only the `M2-M1-012` resume point above and its provider-inspection runbook.
