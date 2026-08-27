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
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | complete through `M2-G0-004C` |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C | **in progress; D1-D2 complete, D3 next** |
| `AUDIT-D1` | PREREQUISITE | D rows 1-5: immutable asset identity; fitment relationships; asset evidence; bidirectional graph; identifiers; enrichment. | AUDIT-C | **complete in `M2-G0-005A`**; `ASSET-001`, `FITMENT-001`, `ASSET-002`, `ASSET-003`, `IDENT-001`, `EVID-001` |
| `AUDIT-D2` | PREREQUISITE | D rows 6-10: manual discovery/Drive retention; technical specs provenance; shopping intent separate from purchase; immutable inventory IDs; hierarchical intended/last-moved locations. | AUDIT-D1 | **complete in `M2-G0-005B`**; `KNOW-001`, `SPEC-001`, `SHOP-001`, `INV-001`, `LOC-001` |
| `AUDIT-D3` | PREREQUISITE | D rows 11-15: QR/barcode movement; queryable household/shop inventory; consumable par levels; optional scale sensing; grocery/pantry/freezer flows. | AUDIT-D2 | **next packet `M2-G0-005C`** |
| `AUDIT-D4` | PREREQUISITE | D row 16: recipes/meal planning/shopping linkage; category-D closure. | AUDIT-D3 | queued |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `LOCATION-STATE-001` | PREREQUISITE | Implement/test `LOC-001` stable hierarchical locations with explicit intended-home placement separate from current/last-observed movement state, including cycle/container rules and readback. | `INV-001`, location/event schema | queued; PR #31 hierarchy code is salvage/reference only and does not prove intended-vs-observed semantics |
| `SHOP-CORE-001` | PREREQUISITE | Implement/test deterministic `SHOP-001` shopping-intent reconciliation: exact/ambiguous match, owner-confirmed fulfillment, cancellation, replacement, partial fulfillment, idempotent replay, deletion/readback. | `RECEIPT-001`, stable shopping-intent identity | queued; policy is strong but no dedicated deterministic core located |
| `KNOWLEDGE-INTEGRATION-001` | HARDENING | Prove `KNOW-001` synthetic manual discovery, Drive retention/index readback, idempotent Knowledge UUID replay and independent relationship degradation in MIRA 2.0 sandbox. | `KNOW-001`, `DATA-SANDBOX`, Google/MIRROR adapter | queued; deterministic core exists, provider integration unverified |
| `SPEC-INTEGRATION-001` | HARDENING | Prove `SPEC-001` authoritative synthetic/manual-derived specification persistence/readback and reject owner-memory/OCR promotion without required provenance. | `SPEC-001`, `KNOW-001`, `DATA-SANDBOX` | queued; validator core is test-verified, integration unverified |
| `FITMENT-ENGINE-001` | HARDENING | Add deterministic automatic `FITMENT-001` resolution tests/engine for multi-vehicle ambiguity, exclusion evidence, modifications, unique application and no-guess queue behavior. | `ASSET-001`, `IDENT-001`, fitment evidence | queued; explicit relationship core is test-verified but inference engine is not |
| `ASSET-SERVICE-001` | HARDENING | Define/test structured warranty and maintenance lifecycle records under `ASSET-002` instead of relying only on generic evidence links/policy prose. | `ASSET-001`, `EVID-001` | queued; broader evidence graph exists but warranty/maintenance depth is not dedicated/tested |
| `ORDER-STALE-001` | PREREQUISITE | Implement/test `ORDER-005` five-business-day stale-shipment escalation. | `ORDER-002`, business-day semantics | queued |
| `SPEND-ROLLUP-001` | HARDENING | Implement deterministic `SPEND-001` monthly evidence-bounded rollup tests. | `RECEIPT-001`, `RECEIPT-003` | queued |
| `RECEIPT-TAXONOMY-001` | PREREQUISITE | Implement configuration-backed generic `RECEIPT-003` taxonomy/classifier. | `RECEIPT-001` | queued |
| `REIMB-CORE-001` | HARDENING | Implement/test deterministic `REIMB-001` reimbursement lifecycle and net-household-cost math. | `RECEIPT-001`, beneficiary identity/allocation | queued |
| `SUBSCRIPTION-TRACK-001` | LATER | Specify/implement opt-in `SUB-001` only if promoted by product priority. | stable receipt/finance evidence + explicit activation | deferred optional |
| `FINANCE-CONNECTOR-001` | LATER | Design/implement `FIN-001` authorized complete-account ingestion with coverage/sync/readback/privacy semantics. | provider abstraction + privacy model + authorization | deferred infrastructure |
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

## Category-D1/D2 dependency findings

- `ASSET-001` owns immutable physical identity; labels, owners, locations and backends cannot replace Entity UUID.
- `FITMENT-001` is an explicit relationship authority. `assigned_to` is not `installed_on`; automatic fitment inference remains a separate hardening gap.
- `ASSET-002` links purchase/manual/warranty/maintenance/spec evidence but cross-authority failure cannot erase a verified asset. Dedicated warranty/maintenance lifecycle depth is queued separately.
- `ASSET-003` receipt/asset/identifier graph behavior is test-verified and intentionally excludes broad `owned_by` traversal.
- `IDENT-001` preserves global-vs-namespaced identifier meaning, check digits/format, leading zeroes and serial-level collision safety.
- `EVID-001` provider-neutral reconciliation is test-verified; Gmail/photo/OCR adapter execution remains integration work.
- `KNOW-001` owns canonical document/reference identity; asset links are downstream and provider failure does not manufacture a second manual.
- `SPEC-001` verified safety-critical values require exact subject/applicability plus authoritative source tier and source locator; the deterministic validator core is test-verified.
- `SHOP-001` active procurement intent is not purchase history or spend. Dedicated deterministic reconciliation remains queued as `SHOP-CORE-001`.
- `INV-001` reuses canonical Entity UUIDs instead of creating an independent inventory identity authority.
- `LOC-001` must distinguish intended storage placement from observed/current/last-moved location. PR #31 hierarchy code is salvage/reference only; `LOCATION-STATE-001` is the actual required implementation gap.

## Prior-category closure

Categories A-C are complete. Category D is complete through row 10. Their previously recorded gaps/evidence levels remain authoritative.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
