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
| `AUDIT-A` | PREREQUISITE | Brief/time/tasking/operational-state reconstruction. | G0-001 | complete |
| `AUDIT-B` | PREREQUISITE | Calendar/reminders/mail/communication safety. | AUDIT-A | complete |
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | **complete through `M2-G0-004C`** |
| `AUDIT-C1` | PREREQUISITE | Fulfillment lifecycle foundations. | AUDIT-B | complete; `ORDER-001`…`ORDER-005` |
| `AUDIT-C2` | PREREQUISITE | Receipt/history/spend/taxonomy/payment/reimbursement. | AUDIT-C1 | complete; `RECEIPT-001`…`RECEIPT-003`, `SPEND-001`, `PAYMENT-001`, `REIMB-001` |
| `AUDIT-C3` | PREREQUISITE | Optional subscription/full-finance direction and C closure. | AUDIT-C2 | **complete in `M2-G0-004C`**; `SUB-001`, `FIN-001` |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C | **next; split D1-D4** |
| `AUDIT-D1` | PREREQUISITE | D rows 1-5: stable asset identity/fitment; purchase evidence/manual/warranty/maintenance/spec linkage; bidirectional receipt↔asset queries; namespaced identifiers; barcode/photo/email enrichment. | AUDIT-C | **next packet `M2-G0-005A`** |
| `AUDIT-D2` | PREREQUISITE | D rows 6-10: manual discovery/Drive retention; technical specs provenance; shopping intent separate from purchase; immutable inventory/item IDs; hierarchical intended/last-moved locations. | AUDIT-D1 | queued |
| `AUDIT-D3` | PREREQUISITE | D rows 11-15: QR/barcode movement; queryable household/shop inventory; consumable par levels; optional scale sensing; grocery/pantry/freezer flows. | AUDIT-D2 | queued |
| `AUDIT-D4` | PREREQUISITE | D row 16: recipes/meal planning/shopping linkage; then category-D consistency closure. | AUDIT-D3 | queued |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `ORDER-STALE-001` | PREREQUISITE | Implement/test `ORDER-005` five-business-day stale-shipment escalation including weekends, progress/ETA reset and alert dedupe. | `ORDER-002`, business-day semantics | queued; audit gap |
| `SPEND-ROLLUP-001` | HARDENING | Implement deterministic `SPEND-001` monthly evidence-bounded rollup tests. | `RECEIPT-001`, `RECEIPT-003` | queued; audit gap |
| `RECEIPT-TAXONOMY-001` | PREREQUISITE | Implement configuration-backed generic `RECEIPT-003` taxonomy/classifier. | `RECEIPT-001` | queued; audit gap |
| `REIMB-CORE-001` | HARDENING | Implement/test deterministic `REIMB-001` reimbursement lifecycle and net-household-cost math. | `RECEIPT-001`, beneficiary identity/allocation | queued; audit gap |
| `SUBSCRIPTION-TRACK-001` | LATER | Specify/implement opt-in `SUB-001` subscription/free-trial tracking only if promoted by product priority; disabled by default, no per-subscription scheduler or auto-cancel. | stable receipt/finance evidence + explicit activation | deferred optional capability |
| `FINANCE-CONNECTOR-001` | LATER | Design/implement `FIN-001` authorized complete-account ingestion with coverage/sync/readback/privacy semantics. | provider abstraction + privacy model + explicit user authorization | deferred infrastructure |
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

## Category-C closure findings

- `ORDER-*` owns fulfillment/lifecycle; active shipment state is a projection, not durable purchase history.
- `RECEIPT-*` owns canonical one-count purchase/evidence/history/classification identity.
- `SPEND-001` is evidence-bounded until complete financial coverage is proven; `FIN-001` is not a shortcut to claim that coverage today.
- `PAYMENT-001` merchant settlement/refund and `REIMB-001` beneficiary reimbursement are separate authorities.
- `SUB-001` remains optional/proposed. Historical paused automation is not permission to resurrect it.
- `FIN-001` remains deferred complete-account infrastructure. The test-verified merchant payment core does not prove financial-account ingestion.
- C1/C2 implementation gaps remain separately ranked and do not block forensic closure.
- No category-C feature is MIRA 2.0 integration/live verified merely because legacy deployments had connected Google/account state.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
