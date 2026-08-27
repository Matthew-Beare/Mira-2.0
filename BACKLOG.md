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
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence/food planning. | AUDIT-C | **complete through `M2-G0-005D`** |
| `AUDIT-D1` | PREREQUISITE | D rows 1-5: immutable asset identity; fitment relationships; asset evidence; bidirectional graph; identifiers; enrichment. | AUDIT-C | complete in `M2-G0-005A` |
| `AUDIT-D2` | PREREQUISITE | D rows 6-10: manual retention; technical specs; shopping intent; inventory identity; hierarchical locations. | AUDIT-D1 | complete in `M2-G0-005B` |
| `AUDIT-D3` | PREREQUISITE | D rows 11-15: QR/barcode movement; inventory query; par levels; optional scale sensing; grocery/pantry/freezer flows. | AUDIT-D2 | complete in `M2-G0-005C` |
| `AUDIT-D4` | PREREQUISITE | D row 16: recipe library; meal planning; missing-ingredient shopping linkage; category-D closure. | AUDIT-D3 | **complete in `M2-G0-005D`**; `RECIPE-001`, `MEAL-001` |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued; begin with bounded `AUDIT-E1` |
| `AUDIT-E1` | PREREQUISITE | Category-E rows 1-5: generic quarantined starter/no inherited personal data; four-question adaptive first boot; bounded AI/job/pain-point/app discovery; cadence/timezone intake; explicit service activation states. | AUDIT-D | **next packet `M2-G0-006A`** |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `RECIPE-CORE-001` | LATER | Implement/test `RECIPE-001` stable recipe identity, provenance, structured ingredient/yield data, source preservation, dedupe and replay. | ingredient/unit semantics; optional `KNOW-001` source retention | queued; current-required product capability but outside present stock-core milestone |
| `MEAL-CORE-001` | LATER | Implement/test `MEAL-001` dated plan identity, recipe reuse, pantry-aware ingredient gaps, ambiguity handling and deduplicated `SHOP-001` grocery intent without planning-induced stock mutation. | `RECIPE-001`, `GROCERY-CORE-001`, `SHOP-CORE-001` | queued; current-required product capability but outside present stock-core milestone |
| `MOVEMENT-CORE-001` | PREREQUISITE | Salvage/redesign `MOVE-001` as replay-safe movement/observation events with exact identifier/location resolution, scan-in/out semantics and target readback without rewriting intended placement. | `INV-001`, `IDENT-001`, `LOCATION-STATE-001` | queued; PR #31 scanner/relocate path is reference candidate but overwrites one `location_uuid` |
| `INVENTORY-QUERY-001` | HARDENING | Implement/prove `INV-002` canonical household/shop query projection across Entity UUIDs, identifiers, relationships, intended/observed locations and containers without second mutable authority. | `INV-001`, `LOC-001`, `ASSET-003`, `LOCATION-STATE-001` | queued; PR #31 query/UI is unmerged reference candidate |
| `PAR-CORE-001` | ENHANCEMENT | Implement/test `PAR-001` observed quantity, explicit target/par, threshold crossing and replay-safe opt-in consolidated low-stock state. | `INV-001`, canonical quantity observations | queued; no executable par engine located |
| `PAR-SCALE-001` | LATER | Research/implement optional `PAR-002` scale/load-cell adapter with calibration, tare, noise, stale-data and confidence semantics only if promoted by product priority. | `PAR-001`, observation/provenance model | deferred optional; no implementation located |
| `GROCERY-CORE-001` | PREREQUISITE | Implement/test `GROCERY-001` grocery-list versus stock state, pantry/freezer locations, purchase-to-stock reconciliation, consumption/spoilage/transfer and replay-safe quantity updates. | `SHOP-001`, `INV-001`, `LOC-001`, practical quantity/unit model | queued; prerequisite for later meal-planning behavior, no executable core located |
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

## Category-D dependency closure

- `ASSET-001` owns physical identity; `INV-001` reuses that UUID rather than creating another inventory identity system.
- `FITMENT-001` owns assignment/installation/compatibility relationships, not identity.
- `EVID-001`, `KNOW-001` and `SPEC-001` are separate provenance layers with different evidence gates.
- `SHOP-001` is active procurement intent; `RECEIPT-*`/`ORDER-*` are durable commerce history.
- `LOC-001` separates intended home from observed/current placement; `MOVE-001` is event/observation state over those locations.
- `INV-002` is a query projection, never an editable second authority.
- `PAR-001` target stock and observed stock are distinct; `PAR-002` remains optional sensor evidence.
- `GROCERY-001` is practical consumable stock/list state and links to shopping/purchase evidence without becoming serialized durable-asset history.
- `RECIPE-001` is reusable recipe knowledge; `MEAL-001` is dated planning state. A plan may read grocery stock and request missing ingredients through `SHOP-001`, but planning alone cannot consume stock or create purchase truth.
- PR #31 remains salvage/reference evidence. Its inventory relocation model requires repair before any later movement salvage.

## Prior-category closure

Categories A-D are complete. Their recorded implementation gaps/evidence levels remain authoritative. Category E has not yet been audited.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
