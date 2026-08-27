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
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence/food planning. | AUDIT-C | complete through `M2-G0-005D` |
| `AUDIT-D1` | PREREQUISITE | D rows 1-5: immutable asset identity; fitment relationships; asset evidence; bidirectional graph; identifiers; enrichment. | AUDIT-C | complete in `M2-G0-005A` |
| `AUDIT-D2` | PREREQUISITE | D rows 6-10: manual retention; technical specs; shopping intent; inventory identity; hierarchical locations. | AUDIT-D1 | complete in `M2-G0-005B` |
| `AUDIT-D3` | PREREQUISITE | D rows 11-15: QR/barcode movement; inventory query; par levels; optional scale sensing; grocery/pantry/freezer flows. | AUDIT-D2 | complete in `M2-G0-005C` |
| `AUDIT-D4` | PREREQUISITE | D row 16: recipe library; meal planning; missing-ingredient shopping linkage; category-D closure. | AUDIT-D3 | complete in `M2-G0-005D`; `RECIPE-001`, `MEAL-001` |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | **in progress; E1-E3 complete, E4 next** |
| `AUDIT-E1` | PREREQUISITE | E rows 1-5: sanitized generic starter; bounded four-question first boot; AI/job/pain-point/app discovery; cadence/timezone intake; explicit service activation states. | AUDIT-D | complete in `M2-G0-006A`; `ONBOARD-002`, `ONBOARD-003`, `ONBOARD-004`, `ONBOARD-005`, `SERVICE-001` |
| `AUDIT-E2` | PREREQUISITE | E rows 6-10: working/self-employed; retired; nonworking; parent/guardian; dependent-minor profile foundations. | AUDIT-E1 | complete in `M2-G0-006B`; `PROFILE-001` through `PROFILE-005` |
| `AUDIT-E3` | PREREQUISITE | E rows 11-15: caregiver/household-manager; student/HOME-CAMPUS; mixed/custom roles; older-adult usability; “Boomer mode” nickname/exclusion boundary. | AUDIT-E2 | **complete in `M2-G0-006C`**; `PROFILE-006` through `PROFILE-011` |
| `AUDIT-E4` | PREREQUISITE | E rows 16-20: per-person identity/household-beneficiary relationships/permission scopes; personal fork + reviewed upstream feature sharing; standalone clean starter; self-improving/custom skill builder; automatic instruction updates. | AUDIT-E3 | **next packet `M2-G0-006D`** |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `PROFILE-CARE-001` | HARDENING | Port/test `PROFILE-006` caregiver role composition, recommendations, no silent activation and no inferred health/family authority; later shared-care state requires explicit permission scopes/readback. | `PROFILE-006`, `SERVICE-001`, `REMIND-001`, `REMIND-002`, Person/relationship permission authority (E4 pending) | queued; legacy router implements role but no dedicated caregiver fixture located |
| `PROFILE-HOUSEHOLD-001` | HARDENING | Port/prove `PROFILE-007` household-manager routing, anti-per-chore-scheduler behavior, explicit responsibility/ownership and mixed-role persistence. | `PROFILE-007`, `SERVICE-001`, task/routine authority | queued; legacy anti-fan-out/no-ownership core is test-verified |
| `PROFILE-STUDENT-001` | HARDENING | Port/test `PROFILE-008` student role plus explicit HOME/CAMPUS option, ensuring student status never silently activates away context and dependent-minor precedence remains intact. | `PROFILE-008`, `CTX-001`, `CTX-002`, `SERVICE-001` | queued; role implemented, no dedicated standalone student/HOME-CAMPUS fixture located |
| `PROFILE-MIXED-001` | HARDENING | Port/prove `PROFILE-009` mixed/custom composition, explicit primary-role routing and fail-closed duplicate/contradictory/custom-role behavior with persistence/readback. | `PROFILE-009`, canonical profile authority | queued; legacy deterministic composition core is test-verified |
| `PROFILE-USABILITY-001` | ENHANCEMENT | Define/test `PROFILE-010` explicit usability/accessibility preference schema so presentation/modality follows user preference/device capability rather than age, retirement or demographic inference. | `PROFILE-010`, onboarding preference state, client capability discovery | queued; non-inference sub-boundary test-supported, full preference engine absent |
| `PROFILE-LABEL-001` | HARDENING | Enforce `PROFILE-011`: no public “Boomer mode” role/mode identifier; private aliases remain private presentation-only state and cannot alter roles, permissions, activation or capabilities. | `PROFILE-011`, `ONBOARD-002`, canonical profile alias state | queued; public rejection specified, private alias behavior implemented/test-supported |
| `PROFILE-MINOR-001` | PREREQUISITE | Port/prove `PROFILE-005` dependent-minor routing plus minimum-necessary private data, explicit relationship/permission scopes and shared-authority readback before any dependent-minor feature is promoted. | `PROFILE-005`, `SERVICE-001`, explicit Person/relationship permission authority (E4 pending) | queued; role/context safety is test-verified, custody/sharing authorization is not |
| `PROFILE-PARENT-001` | PREREQUISITE | Port/prove `PROFILE-004` parent/guardian composition and synthetic family relationship state while demonstrating relationship labels never grant calendar/school/health/finance/sharing access. | `PROFILE-004`, `SERVICE-001`, explicit Person/relationship permission authority (E4 pending) | queued; core router tested, family-service/provider permission integration unverified |
| `PROFILE-WORK-001` | HARDENING | Port/test `PROFILE-001` working/self-employed role semantics with dedicated self-employed and mixed-role fixtures, primary-role persistence/readback and no recommendation-driven activation. | `PROFILE-001`, `ONBOARD-004`, `SERVICE-001`, `CTX-002` | queued; working context paths tested, self-employed path lacks dedicated audited fixture |
| `PROFILE-RETIRED-001` | HARDENING | Port/prove `PROFILE-002` retired role, respectful presentation, context bypass, non-inference and opt-in reminder/service semantics in MIRA 2.0 canonical profile state. | `PROFILE-002`, `SERVICE-001` | queued; legacy deterministic core is test-verified |
| `PROFILE-NONWORKING-001` | HARDENING | Port/test `PROFILE-003` nonworking/between-jobs classification, recommendations and transitions among working/nonworking/retired without silent service mutation or state deletion. | `PROFILE-003`, `SERVICE-001` | queued; distinction test exists, full transition/persistence flow unverified |
| `STARTER-SANITIZE-001` | PREREQUISITE | Port/prove `ONBOARD-002` privacy/history audit gates for the MIRA 2.0 starter/distribution and verify synthetic clean lineage with no inherited legacy production state. | `ONBOARD-002`, distribution/starter source | queued; legacy source has CI-enforced scanner but MIRA 2.0 distribution proof is unverified |
| `FIRSTBOOT-CORE-001` | PREREQUISITE | Implement/test `ONBOARD-003` exact ≤4 kickoff flow, durable Interview Ledger resume/defer/silence semantics and Minimum Useful Setup before exhaustive discovery. | `ONBOARD-002`, canonical onboarding state | queued; strong workflow artifacts, complete deterministic flow not test-verified |
| `DISCOVERY-CORE-001` | HARDENING | Implement/test structured `ONBOARD-004` AI-use/pain-point/job/app/constraint discovery with capability reuse, no unsupported claims and recommendation-not-activation semantics. | `ONBOARD-003`, `SERVICE-001`, capability router | queued; important sub-boundaries are tested, full discovery flow is not |
| `ONBOARD-SCHEDULE-001` | PREREQUISITE | Implement/test `ONBOARD-005` new-user cadence/slot/IANA-timezone capture, validation, persistence/readback and enabled-brief routing without inherited personal schedule. | `ONBOARD-003`, `SERVICE-001`, `OPS-003` | queued |
| `SERVICE-STATE-001` | PREREQUISITE | Port/prove `SERVICE-001` finite activation-state machine in MIRA 2.0 canonical configuration, keeping activation separate from catalog presence, recommendation and capability verification. | canonical service catalog/config authority | queued; legacy deterministic core is test-verified |
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

## Category-E1/E2/E3 dependency findings

- `ONBOARD-002` is a privacy/lineage prerequisite. New deployments begin generic and synthetic; protected legacy state remains outside portable/public source.
- `ONBOARD-003` owns bounded interview pacing and durable resume state, not service activation.
- `ONBOARD-004` owns discovery/recommendation. Job titles, duties, existing apps and AI-use evidence may inform recommendations but cannot silently enable services or permissions.
- `ONBOARD-005` owns new-user cadence/timezone capture; scheduler runtime semantics remain under `OPS-*`, and an existing deployment’s schedule is never inherited as a default.
- `SERVICE-001` owns activation state and explicitly separates `unresolved/enabled/disabled/not_applicable/deferred` from capability availability, catalog presence and recommendation.
- `PROFILE-001` through `PROFILE-009` are routing/profile facts, not authorization. Role recommendations cannot mutate service activation.
- Retirement and nonworking remain distinct; neither may imply age, health, disability, financial or competence facts.
- Parent/guardian, caregiver and dependent-minor labels do not grant custody, calendar, school, health, financial or sharing authority. Permission-scoped Person/relationship state remains a separate E4 prerequisite.
- Household-manager does not imply universal chore/property ownership; dedicated legacy tests already prohibit ownership inference and per-chore scheduler fan-out.
- Student role does not silently activate HOME/CAMPUS. Context remains explicit/recommended configuration under `CTX-*`.
- `mixed` preserves underlying roles and explicit primary routing. `custom` cannot erase established role semantics.
- `PROFILE-010` keeps usability/accessibility preference-driven and prohibits demographic inference.
- `PROFILE-011` rejects public “Boomer mode”; private user-chosen aliases remain presentation-only private state.
- Legacy unsafe/rejected universal-onboarding behavior stays rejected and cannot become a default through old branch/code resurrection.

## Prior-category closure

Categories A-D are complete. Category E is complete through row 15. Their recorded implementation gaps/evidence levels remain authoritative.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
