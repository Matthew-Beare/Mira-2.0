# MIRA 2.0 BACKLOG

This backlog is **not FIFO**. Arrival order never determines implementation order. Priority is recomputed from blockers, dependencies, milestone value, architectural leverage, user-visible value, and verification needs.

## Priority classes

1. **BLOCKER** — data integrity, privacy, security, or active acceptance blocker.
2. **PREREQUISITE** — hard dependency for higher-value work.
3. **VERTICAL** — user-visible end-to-end slice for active milestone.
4. **HARDENING** — reliability, testing, migration, observability, recovery.
5. **ENHANCEMENT** — useful but not required for active proof.
6. **LATER** — valid direction intentionally outside current milestone.

## Audit work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `AUDIT-A` | PREREQUISITE | Brief/time/tasking/operational-state reconstruction. | G0-001 | complete through `M2-G0-002D` |
| `AUDIT-B` | PREREQUISITE | Calendar/reminders/mail/communication safety. | AUDIT-A | complete through `M2-G0-003B` |
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | **in progress; C1-C2 complete, C3 next** |
| `AUDIT-C1` | PREREQUISITE | C rows 1-5: fulfillment lifecycle foundations. | AUDIT-B | complete in `M2-G0-004A`; `ORDER-001`…`ORDER-005` |
| `AUDIT-C2` | PREREQUISITE | C rows 6-10: receipt intake/history, bounded spending, taxonomy, merchant payment and reimbursement. | AUDIT-C1 | **complete in `M2-G0-004B`**; `RECEIPT-001`…`RECEIPT-003`, `SPEND-001`, `PAYMENT-001`, `REIMB-001` |
| `AUDIT-C3` | PREREQUISITE | C rows 11-12: optional subscription/free-trial tracking; credit-card/complete financial-ingestion direction; category-C consistency closure. | AUDIT-C2 | **next packet `M2-G0-004C`** |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C | queued |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `ORDER-STALE-001` | PREREQUISITE | Implement/test `ORDER-005` five-business-day stale-shipment escalation including weekends, progress/ETA reset and alert dedupe. | `ORDER-002`, business-day semantics | queued; audit gap |
| `SPEND-ROLLUP-001` | HARDENING | Implement deterministic `SPEND-001` monthly evidence-bounded rollup tests for duplicate evidence, mixed receipts, revisions/refunds, unresolved classification and coverage labeling. | `RECEIPT-001`, `RECEIPT-003` | queued; no dedicated audited rollup engine/test |
| `RECEIPT-TAXONOMY-001` | PREREQUISITE | Implement configuration-backed generic `RECEIPT-003` taxonomy/classifier with mixed-receipt, user-added-category and correction tests. | `RECEIPT-001` | queued; currently specification-level |
| `REIMB-CORE-001` | HARDENING | Implement/test deterministic `REIMB-001` reimbursement lifecycle, beneficiary allocations and exact net-household-cost math without conflating merchant refunds. | `RECEIPT-001`, beneficiary identity/allocation model | queued; currently specification-level |
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | G0 audit + canonical state contract | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Stock ChatGPT create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity. | dependency graph + sandbox | provisional |
| `ANDROID-SYNC` | VERTICAL | Android reads/mutates same canonical entity without second authority. | CORE-ROUNDTRIP | provisional |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | core + audited prerequisites | provisional |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA source artwork and generated platform derivatives. | branding source delivered | queued |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Boomer-safe onboarding for full replacement ChatGPT instructions without CLI. | audited onboarding + current UI verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Next full Project Instructions replacement must require customer action or exact fallback `Just tell me to continue.` before final packet line. | next legitimate full replacement | queued; conversation behavior applies now |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy data after stable schema/vertical proof. | stable schema + rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI parity and packaging. | core verticals | deferred |
| `RFID` | LATER | RFID inventory capture/specialized hardware. | stable inventory schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Home Assistant/Plex/Paperless/Node-RED/MQTT integrations. | stable authority/integration contracts | deferred |
| `ENTERPRISE` | LATER | Institutional/locked-down deployment. | stock core + provider abstraction | deferred |

## Category-C2 dependency findings

- `RECEIPT-001` owns canonical transaction/evidence convergence; email, file, photo and chat are intake surfaces, not separate purchase databases.
- `RECEIPT-002` connected graph behavior is test-verified, but live user-facing Receipt Browser/provider readback remains integration work.
- `SPEND-001` must remain explicitly evidence-bounded unless a complete financial authority is proven. `SPEND-ROLLUP-001` captures its missing deterministic rollup tests.
- `RECEIPT-003` generic taxonomy remains specification-level and is now explicit prerequisite work instead of being mistaken for an implemented classifier.
- `PAYMENT-001` merchant settlement core is test-verified, but connected-account matching/readback remains an integration boundary.
- `REIMB-001` is a different authority from merchant refund/settlement and still needs deterministic implementation/tests.
- PR #31 receipt-processing code is an unmerged self-hosted candidate. It may inform later design but does not change the stock ChatGPT+Google milestone or earn MIRA 2.0 completion evidence.

## Category-C1 dependency findings

- Evidence correlation, canonical commerce history and active fulfillment projection are separate authorities.
- Cancellation/return fulfillment is separate from financial settlement/refund evidence.
- Same-order revision is separate from true replacement; duplicate-spend prevention requires stable Receipt identity and balanced allocation.
- `ORDER-005` stale-shipment escalation remains queued as `ORDER-STALE-001`.

## Prior-category closure

- Categories A and B are complete and retain their previously recorded dependency/evidence boundaries.
- Legacy live-provider claims do not promote MIRA 2.0 evidence levels.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
