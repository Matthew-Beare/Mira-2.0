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
| `AUDIT-D4` | PREREQUISITE | D row 16: manual retention; technical specs; shopping intent; inventory identity; hierarchical locations through recipes/meal planning closure. | AUDIT-D3 | complete in `M2-G0-005D`; `RECIPE-001`, `MEAL-001` |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | complete through `M2-G0-006F` |
| `AUDIT-E1` | PREREQUISITE | E rows 1-5: sanitized generic starter; bounded four-question first boot; AI/job/pain-point/app discovery; cadence/timezone intake; explicit service activation states. | AUDIT-D | complete in `M2-G0-006A`; `ONBOARD-002`, `ONBOARD-003`, `ONBOARD-004`, `ONBOARD-005`, `SERVICE-001` |
| `AUDIT-E2` | PREREQUISITE | E rows 6-10: working/self-employed; retired; nonworking; parent/guardian; dependent-minor profile foundations. | AUDIT-E1 | complete in `M2-G0-006B`; `PROFILE-001` through `PROFILE-005` |
| `AUDIT-E3` | PREREQUISITE | E rows 11-15: caregiver/household-manager; student/HOME-CAMPUS; mixed/custom roles; older-adult usability; public “Boomer mode” rejection/private alias boundary. | AUDIT-E2 | complete in `M2-G0-006C`; `PROFILE-006` through `PROFILE-011` |
| `AUDIT-E4` | PREREQUISITE | E rows 16-20: Person/relationship identity and permission scopes; private/upstream feature sharing; clean distribution boundary; custom skill builder; instruction-update behavior. | AUDIT-E3 | complete in `M2-G0-006D`; `PROFILE-012`, `PROFILE-013`, `DIST-001`, `DIST-002`, `DEV-004`, `ONBOARD-001` refinement |
| `AUDIT-E5` | PREREQUISITE | E rows 21-24: browser-only nontechnical installation; independent source read/write gates; provider-neutral AI-runtime routing; personal/organization/managed/no-Git source lanes. | AUDIT-E4 | complete in `M2-G0-006E`; `ONBOARD-006`, `SOURCE-001`, `PROVIDER-001`, `SOURCE-002` |
| `AUDIT-E6` | PREREQUISITE | E rows 25-26: browser-only provider account/resource onboarding; installable provider-neutral MIRA skill; deterministic Personal Google bootstrap; category-E closure. | AUDIT-E5 | complete in `M2-G0-006F`; `PROVIDER-002`, `ONBOARD-007`, `PROVIDER-003` |
| `AUDIT-F` | PREREQUISITE | Life-service module composition, activation/readiness, dependency mapping and service-specific evidence. | AUDIT-E | complete through `M2-G0-008G` |
| `AUDIT-F1` | PREREQUISITE | F rows 1-5: Briefs/action digest; Next-action planner; Email triage; Orders/shipments; Receipt archive; generic service-composition boundary. | AUDIT-E | complete in `M2-G0-007A`; `SERVICE-002` plus canonical OPS/TASK/MAIL/ORDER/RECEIPT mappings |
| `AUDIT-F2` | PREREQUISITE | F rows 6-8: Personal finance organization; Appointments/calendar/reminders; Administrative health organization; goal/submodule-scoped service readiness and sensitive-state boundaries. | AUDIT-F1 | complete in `M2-G0-007B`; `CAL-005`, `CAL-006`, `HEALTH-001` |
| `AUDIT-F3` | PREREQUISITE | F rows 9-10: Shopping/procurement and Recipes/meals/groceries service composition. | AUDIT-F2 | complete in `M2-G0-007C`; `SHOP-001`, `GROCERY-001`, `RECIPE-001`, `MEAL-001` |
| `AUDIT-F4` | PREREQUISITE | F rows 11-12: Household/errands/admin/maintenance and Laundry stages/drop-off/pickup reminders. | AUDIT-F3 | complete in `M2-G0-007D`; `ROUTINE-001`, `REMIND-003` |
| `AUDIT-F5` | PREREQUISITE | F rows 13-14: Routines/fitness/accountability and Education/study/deadlines/offline preparation. | AUDIT-F4 | complete in `M2-G0-007E`; `EDU-001`, `CAL-007` |
| `AUDIT-F6` | PREREQUISITE | F row 15: Parent/child school coordination and permission boundaries. | AUDIT-F5 | complete in `M2-G0-007F` |
| `AUDIT-F7` | PREREQUISITE | F rows 16-17: Travel/vacation/outdoor planning and Work-trip/route/paid-work tracking. | AUDIT-F6 | complete in `M2-G0-007G` |
| `AUDIT-F8` | PREREQUISITE | F row 18: Assets/maintenance/warranties/manuals selected-path service composition. | AUDIT-F7 | complete in `M2-G0-007H` |
| `AUDIT-G16-F20` | PREREQUISITE | G16 backup/restore foundation plus F20 Backup/disaster recovery. | AUDIT-F8 | complete in `M2-G0-008A`; `BACKUP-001` |
| `AUDIT-G17-G18-F19` | PREREQUISITE | G17 knowledge ingestion/provenance + G18 provider projection + F19 knowledge service. | AUDIT-G16-F20 | complete in `M2-G0-008B`; `KNOW-001`, `KNOW-002` |
| `AUDIT-G1` | PREREQUISITE | G1 canonical mutable-authority foundation. | AUDIT-G17-G18-F19 | complete in `M2-G0-008C`; `AUTH-001`, `STORE-001` |
| `AUDIT-G7` | PREREQUISITE | G7 provider-neutral policy/data API foundation. | `AUDIT-G1`, `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001` | complete in `M2-G0-008D`; `API-001` |
| `AUDIT-G10` | PREREQUISITE | G10 Android/mobile client boundary. | `AUDIT-G7`, `API-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001` | complete in `M2-G0-008E`; `CLIENT-ANDROID-001`; direct-Google client path rejected |
| `AUDIT-G19-G20` | PREREQUISITE | G19/G20 repository integrity: stable feature projection and component ownership/evidence gates. | `DEV-001`, `DEV-003` | complete in `M2-G0-008F`; `DEV-005`, `DEV-006` |
| `AUDIT-F21-F23-G2-G15` | PREREQUISITE | Remaining recovered ledger closeout. | `AUDIT-G19-G20` | complete in `M2-G0-008G`; `WEATHER-002`, `WEARABLE-001`, `ENTERPRISE-001`, `OBS-001`, `LOCAL-001`, `VOICE-001` |
| `AUDIT-G` | PREREQUISITE | Category-G platform/integration/recovery/infrastructure ledger coverage. | AUDIT-F | complete through `M2-G0-008G`; all recovered G1-G20 rows mapped |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | complete in `M2-G0-009`; PR #31 selective salvage only, PR #34 superseded, generated mirrors noncanonical, independent productization branch mapped/rejected as architecture |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog from stable semantic feature IDs. | completed forensic registry + `DEV-005` + `FEATURE-REGISTRY-001` | queued; G0-010 next |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `FEATURE-REGISTRY-001` | PREREQUISITE | Implement/test `DEV-005` machine-readable projection from canonical `FEATURES.md` with authored semantic IDs, dependency validation, deterministic projections and material-drift CI failure. | `DEV-005`, `DEV-001`, `DEV-003` | queued |
| `CODE-OWNERSHIP-001` | PREREQUISITE | Implement/test `DEV-006` production component ownership/evidence manifest and fail unowned/overlapping production artifacts centrally. | `DEV-006`, `DEV-001` | queued |
| `WEATHER-ONBOARD-001` | HARDENING | Implement/test `WEATHER-002` explicit weather preferences/onboarding with failure isolation. | `WEATHER-002`, `WEATHER-001`, `ONBOARD-004`, `ONBOARD-005`, `SERVICE-001` | queued |
| `WEARABLE-ADAPTER-001` | LATER | Optional authorized `WEARABLE-001` adapters with provenance/capability/readback honesty. | `WEARABLE-001`, `PROVIDER-001` | deferred optional |
| `OBSERVABILITY-001` | HARDENING | Implement `OBS-001` read-only telemetry/dashboard projection. | `OBS-001`, `AUTH-001`, `RECOVERY-002`, core runtime | queued after core |
| `VOICE-CLIENT-001` | LATER | Implement `VOICE-001` over shared API with normal authorization and consequential-action confirmation. | `VOICE-001`, `API-CORE-001` | deferred until shared API/client core |
| `SERVICE-COMPOSE-001` | PREREQUISITE | Port/prove `SERVICE-002` service composition/readiness with activation separate from readiness. | `SERVICE-001`, `SERVICE-002`, canonical dependency registry, `RUNTIME-ROUTER-001` | queued |
| `SERVICE-DEPS-001` | PREREQUISITE | Repair/test F1 Briefs and Orders/shipments dependency bundles. | `SERVICE-002`, `OPS-002`, `ORDER-004`, dependency registry | queued |
| `SERVICE-DEPS-002` | PREREQUISITE | Normalize/test F2 finance/calendar/health selected-goal readiness. | `SERVICE-002`, `CAL-005`, `CAL-006`, `HEALTH-001`, category-C finance features, dependency registry | queued |
| `SERVICE-DEPS-003` | PREREQUISITE | Normalize/test F3 shopping and recipe/meal/grocery readiness. | `SERVICE-002`, `SHOP-001`, `GROCERY-001`, `RECIPE-001`, `MEAL-001`, dependency registry | queued |
| `SERVICE-DEPS-004` | PREREQUISITE | Normalize/test F4 household/routine readiness and anti-fan-out. | `SERVICE-002`, `TASK-001`, `TASK-002`, `ROUTINE-001`, `REMIND-003`, dependency registry | queued |
| `SERVICE-DEPS-005` | PREREQUISITE | Normalize/test F5 routines/fitness/education with optional wearable/Calendar/offline paths. | `SERVICE-002`, `ROUTINE-001`, `TASK-001`, `TASK-002`, `REMIND-003`, `EDU-001`, `CAL-007`, dependency registry | queued |
| `SERVICE-DEPS-006` | PREREQUISITE | Normalize/test F6 family-school readiness around exact actor/subject/scope. | `SERVICE-001`, `SERVICE-002`, `EDU-001`, `PROFILE-012`, `PROFILE-013`, dependency registry | queued |
| `SERVICE-DEPS-007` | PREREQUISITE | Normalize/test F7 travel/work-trip bundles and paid-mileage separation. | `SERVICE-001`, `SERVICE-002`, `TRIP-001`, `ROUTE-001`, `MILE-001`, `MILE-002`, dependency registry | queued |
| `SERVICE-DEPS-008` | PREREQUISITE | Normalize/test F8 assets selected-path readiness. | `SERVICE-001`, `SERVICE-002`, `ASSET-001`, `ASSET-003`, dependency registry | queued |
| `SERVICE-DEPS-009` | PREREQUISITE | Normalize/test F20 recovery-service readiness. | `SERVICE-001`, `SERVICE-002`, `BACKUP-001`, dependency registry | queued |
| `SERVICE-DEPS-010` | PREREQUISITE | Normalize/test F19 knowledge-service readiness. | `SERVICE-001`, `SERVICE-002`, `KNOW-001`, `KNOW-002`, dependency registry | queued |
| `AUTHORITY-REGISTRY-001` | PREREQUISITE | Implement/test persistent `AUTH-001` Authority Registry and exact data-class routing/readback. | `AUTH-001`, `RECOVERY-002`, `STORE-001` | queued |
| `STORE-ADAPTER-001` | PREREQUISITE | Implement/test `STORE-001` provider-neutral structured/evidence adapters with synthetic-first read/write/readback. | `STORE-001`, `RECOVERY-002`, `DATA-SANDBOX` | queued; legacy main + productization/PR31 candidates available |
| `API-CORE-001` | BLOCKER | Implement/prove shared `API-001` runtime for ChatGPT/Android with scoped authz, mandatory idempotency/version preflight, canonical conflict handling, audit and `AUTH-001`/`STORE-001` routing. | `API-001`, `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001`, `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001` | queued; legacy PR31/productization candidates selective salvage only |
| `ANDROID-CLIENT-CORE-001` | PREREQUISITE | Implement/prove MIRA 2.0 Android API client core, protected credentials, replay-safe offline queue, reconnect and server conflict/readback handling. | `CLIENT-ANDROID-001`, `API-CORE-001`, `RUNTIME-ROUTER-001` | queued; legacy PR31 Android candidate selective salvage |
| `ANDROID-NATIVE-DELIVERY-001` | HARDENING | Port/redesign Android visual notification + opt-in TTS delivery with device evidence. | `CLIENT-ANDROID-001`, `ANDROID-CLIENT-CORE-001`, canonical reminder semantics | queued |
| `ANDROID-CAPTURE-001` | HARDENING | Port/redesign Android camera/barcode/QR/NFC/BLE capture as nonauthoritative API observations. | `CLIENT-ANDROID-001`, `ANDROID-CLIENT-CORE-001`, `API-001`, `EVID-001`, `IDENT-001` | queued |
| `ANDROID-RELEASE-001` | HARDENING | Establish reproducible Android build/signing/version/provenance/device smoke evidence. | `CLIENT-ANDROID-001`, `ANDROID-CLIENT-CORE-001`, distribution/release policy | queued |
| `AUTHORITY-MIGRATION-001` | PREREQUISITE | Implement staged provider/backend cutover without dual writable masters. | `AUTH-001`, `STORE-001`, `BACKUP-001`, `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001`, `DATA-SANDBOX` | queued |
| `BACKUP-CORE-001` | PREREQUISITE | Implement/test `BACKUP-001` backup/restore lifecycle and restore verification. | `BACKUP-001`, `PROVIDER-001`, `RECOVERY-002`, `DATA-SANDBOX`, canonical storage adapters | queued; PR31 partial candidate only |
| `KNOWLEDGE-CORE-001` | PREREQUISITE | Port `KNOW-001` general Knowledge identity/relationship core. | `KNOW-001`, `RECOVERY-002`, canonical identity/relationship model, `DATA-SANDBOX` | queued |
| `KNOWLEDGE-PROVENANCE-001` | PREREQUISITE | Implement `KNOW-002` excerpt/derived-fact provenance lifecycle. | `KNOW-002`, `KNOW-001`, `RECOVERY-002`, canonical provenance model | queued |
| `KNOWLEDGE-PROJECTION-001` | HARDENING | Normalize provider organization/search projection with exact readback and no path identity. | `KNOW-001`, `KNOW-002`, `DATA-SANDBOX`, selected evidence/document provider | queued |
| `TRIP-ROUTE-CORE-001` | PREREQUISITE | Port/prove canonical Trip/Route state and optional ordered multi-leg grouping. | `TRIP-001`, `ROUTE-001`, `RECOVERY-002`, canonical state/time semantics, `DATA-SANDBOX` | queued |
| `ROUTINE-CORE-001` | PREREQUISITE | Implement/test recurring/staged routine definition and occurrence lifecycle. | `TASK-001`, `TASK-002`, canonical Person/time semantics | queued |
| `ROUTINE-REMINDER-001` | PREREQUISITE | Implement consolidated routine/stage/accountability reminder planning/projection. | `ROUTINE-001`, `RECOVERY-002`, canonical time semantics, verified delivery adapters | queued |
| `APPOINTMENT-IDENTITY-001` | HARDENING | Port/prove appointment/provider identity reconciliation. | `CAL-005`, canonical appointment/source identity, evidence/provenance | queued |
| `CALENDAR-PROJECTION-001` | PREREQUISITE | Implement generic source-linked Calendar projection/readback. | `CAL-007`, `CAL-006`, provider Calendar write/readback, `DATA-SANDBOX`, `RECOVERY-002` | queued |
| `EDUCATION-CORE-001` | PREREQUISITE | Implement education track/work/deadline lifecycle. | `EDU-001`, `TASK-001`, `TASK-002`, provenance/evidence authority | queued |
| `HEALTH-ADMIN-001` | ENHANCEMENT | Define/test non-clinical health-administration schema/safety gates. | `HEALTH-001`, `PROFILE-013`, evidence authority | queued |
| `SERVICE-MIGRATION-001` | HARDENING | Define/test legacy service activation migration without broadening intent. | `SERVICE-001`, `SERVICE-002`, canonical service/submodule IDs, onboarding migration path | queued |
| `MIRA-SKILL-001` | PREREQUISITE | Port/prove provider-neutral MIRA orchestration skill. | `ONBOARD-007`, `DIST-STARTER-001`, `SOURCE-GATES-001`, `RUNTIME-ROUTER-001`, `SERVICE-COMPOSE-001` | queued |
| `PROVIDER-ONBOARD-001` | PREREQUISITE | Port/prove browser provider onboarding with exact resource/scope/readback. | `PROVIDER-002`, `ONBOARD-006`, `RUNTIME-ROUTER-001`, provider adapters/Authority Registry | queued |
| `GOOGLE-BOOTSTRAP-001` | PREREQUISITE | Port/prove deterministic Personal Google blueprint/plan/verifier in synthetic MIRA 2.0 namespace. | `PROVIDER-003`, `MIRA-SKILL-001`, `PROVIDER-ONBOARD-001`, `SOURCE-GATES-001` | queued |
| `NONTECH-INSTALL-001` | PREREQUISITE | Port/prove browser-only installation and exact readback with no terminal fallback. | `ONBOARD-006`, `DIST-STARTER-001`, `SOURCE-GATES-001`, `MIRA-SKILL-001`, `PROVIDER-ONBOARD-001` | queued |
| `SOURCE-GATES-001` | PREREQUISITE | Port/prove independent source read/write/remote-readback gates. | `SOURCE-001`, source connector/runtime capability | queued |
| `RUNTIME-ROUTER-001` | PREREQUISITE | Port/prove provider-neutral runtime capability router. | `PROVIDER-001`, `SOURCE-GATES-001`, data-classification/approval state | queued |
| `SOURCE-LANES-001` | PREREQUISITE | Port/prove personal/organization/managed/no-Git source lanes. | `SOURCE-002`, `SOURCE-GATES-001`, `RUNTIME-ROUTER-001`, `DIST-STARTER-001` | queued |
| `PERSON-GRAPH-001` | PREREQUISITE | Implement canonical Person UUIDs/relationship graph. | `PROFILE-012`, canonical MIRROR identity authority, `DATA-SANDBOX` | queued |
| `PERMISSION-SCOPE-001` | BLOCKER | Implement explicit actor/resource/action grants and revoke/narrow/readback semantics. | `PROFILE-012`, Authority Registry, provider identity/readback | queued; privacy-critical |
| `FEATURE-SHARE-001` | HARDENING | Port/prove private feature ownership/reconciliation and sanitized publication path. | `DIST-001`, `ONBOARD-002`, feature/dependency manifests, `SOURCE-GATES-001` | queued |
| `DIST-STARTER-001` | PREREQUISITE | Port/prove deterministic MIRA 2.0 starter/distributions from one source SHA. | `DIST-002`, `ONBOARD-002`, clean source lineage | queued |
| `SKILL-BUILDER-001` | ENHANCEMENT | Implement bounded private custom-feature workflow. | `DEV-004`, `DEV-001`, `DEV-002`, feature/dependency registry, `SOURCE-GATES-001` | queued |
| `PROFILE-CARE-001` | HARDENING | Port/test caregiver composition without inferred authority. | `PROFILE-006`, `SERVICE-001`, `REMIND-001`, `REMIND-002`, `PROFILE-012`, `PROFILE-013`, `PERMISSION-SCOPE-001` | queued |
| `PROFILE-HOUSEHOLD-001` | HARDENING | Port/prove household-manager routing/anti-fan-out. | `PROFILE-007`, `SERVICE-001`, task/routine authority | queued |
| `PROFILE-STUDENT-001` | HARDENING | Port/test student role/HOME-CAMPUS option. | `PROFILE-008`, `CTX-001`, `CTX-002`, `SERVICE-001` | queued |
| `PROFILE-MIXED-001` | HARDENING | Port/prove mixed/custom composition and primary-role routing. | `PROFILE-009`, canonical profile authority | queued |
| `PROFILE-USABILITY-001` | ENHANCEMENT | Define/test explicit usability/accessibility preferences. | `PROFILE-010`, onboarding preference state, client capability discovery | queued |
| `PROFILE-LABEL-001` | HARDENING | Enforce public-label rejection/private-alias boundary. | `PROFILE-011`, `ONBOARD-002`, canonical profile alias state | queued |
| `PROFILE-MINOR-001` | PREREQUISITE | Port/prove dependent-minor routing plus explicit relationship/permission scopes. | `PROFILE-005`, `SERVICE-001`, `PROFILE-012`, `PROFILE-013`, `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001` | queued |
| `PROFILE-PARENT-001` | PREREQUISITE | Port/prove parent/guardian composition without relationship-derived authority. | `PROFILE-004`, `SERVICE-001`, `PROFILE-012`, `PROFILE-013`, `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001` | queued |
| `PROFILE-WORK-001` | HARDENING | Port/test working/self-employed role semantics. | `PROFILE-001`, `ONBOARD-004`, `SERVICE-001`, `CTX-002` | queued |
| `PROFILE-RETIRED-001` | HARDENING | Port/prove retired role/opt-in support. | `PROFILE-002`, `SERVICE-001` | queued |
| `PROFILE-NONWORKING-001` | HARDENING | Port/test nonworking/between-jobs semantics/transitions. | `PROFILE-003`, `SERVICE-001` | queued |
| `STARTER-SANITIZE-001` | PREREQUISITE | Port/prove starter privacy/history audit gates. | `ONBOARD-002`, `DIST-002` | queued |
| `FIRSTBOOT-CORE-001` | PREREQUISITE | Implement ≤4-question kickoff and resumable Interview Ledger/Minimum Useful Setup. | `ONBOARD-002`, canonical onboarding state | queued |
| `DISCOVERY-CORE-001` | HARDENING | Implement structured discovery without recommendation-driven activation. | `ONBOARD-003`, `SERVICE-001`, `RUNTIME-ROUTER-001` | queued |
| `ONBOARD-SCHEDULE-001` | PREREQUISITE | Implement cadence/slot/IANA-timezone onboarding. | `ONBOARD-003`, `SERVICE-001`, `OPS-003` | queued |
| `SERVICE-STATE-001` | PREREQUISITE | Port/prove finite service activation-state machine. | canonical service catalog/config authority | queued |
| `RECIPE-CORE-001` | LATER | Implement stable recipe identity/provenance/structured ingredients. | ingredient/unit semantics; optional `KNOW-001` | queued |
| `MEAL-CORE-001` | LATER | Implement dated meal planning and shopping reconciliation. | `RECIPE-001`, `GROCERY-CORE-001`, `SHOP-CORE-001` | queued |
| `MOVEMENT-CORE-001` | PREREQUISITE | Salvage/redesign movement/observation events. | `INV-001`, `IDENT-001`, `LOCATION-STATE-001` | queued; PR31 candidate selective salvage |
| `INVENTORY-QUERY-001` | HARDENING | Implement canonical inventory query projection. | `INV-001`, `LOC-001`, `ASSET-003`, `LOCATION-STATE-001` | queued; PR31 candidate selective salvage |
| `PAR-CORE-001` | ENHANCEMENT | Implement observed quantity/target/threshold state. | `INV-001`, canonical quantity observations | queued |
| `PAR-SCALE-001` | LATER | Optional scale/load-cell adapter. | `PAR-001`, observation/provenance model | deferred optional |
| `GROCERY-CORE-001` | PREREQUISITE | Implement grocery-list versus stock reconciliation. | `SHOP-001`, `INV-001`, `LOC-001`, quantity/unit model | queued |
| `LOCATION-STATE-001` | PREREQUISITE | Implement intended versus observed hierarchical location state. | `INV-001`, location/event schema | queued; PR31 move model must not be copied verbatim |
| `SHOP-CORE-001` | PREREQUISITE | Implement deterministic shopping-intent reconciliation. | `RECEIPT-001`, stable shopping-intent identity | queued |
| `KNOWLEDGE-INTEGRATION-001` | HARDENING | Prove retained-source/provider readback integration. | `KNOW-001`, `DATA-SANDBOX`, Google/MIRROR adapter | queued |
| `SPEC-INTEGRATION-001` | HARDENING | Prove authoritative specification persistence/readback. | `SPEC-001`, `KNOW-001`, `DATA-SANDBOX` | queued |
| `FITMENT-ENGINE-001` | HARDENING | Add deterministic automatic fitment resolution engine/tests. | `ASSET-001`, `IDENT-001`, fitment evidence | queued |
| `ASSET-SERVICE-001` | HARDENING | Define structured warranty/maintenance lifecycle records. | `ASSET-001`, `EVID-001` | queued |
| `ORDER-STALE-001` | PREREQUISITE | Implement five-business-day stale-shipment escalation. | `ORDER-002`, business-day semantics | queued |
| `SPEND-ROLLUP-001` | HARDENING | Implement monthly evidence-bounded spending rollup. | `RECEIPT-001`, `RECEIPT-003` | queued |
| `RECEIPT-TAXONOMY-001` | PREREQUISITE | Implement generic receipt taxonomy/classifier. | `RECEIPT-001` | queued |
| `REIMB-CORE-001` | HARDENING | Implement deterministic reimbursement lifecycle. | `RECEIPT-001`, `PROFILE-012`, beneficiary allocation | queued |
| `SUBSCRIPTION-TRACK-001` | LATER | Optional subscription/free-trial tracking. | stable receipt/finance evidence + explicit activation | deferred optional |
| `FINANCE-CONNECTOR-001` | LATER | Authorized complete-account ingestion. | provider abstraction + privacy model + authorization | deferred infrastructure |
| `DATA-SANDBOX` | PREREQUISITE | Create separate synthetic MIRA 2.0 Google/MIRROR sandbox and prove no legacy production modification. | `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001`, `GOOGLE-BOOTSTRAP-001` | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Stock ChatGPT create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity through shared API. | `DEP-GRAPH`, `DATA-SANDBOX`, `GOOGLE-BOOTSTRAP-001`, `API-CORE-001` | provisional |
| `ANDROID-SYNC` | VERTICAL | Android reads/mutates the same canonical entity through `API-001`. | `CORE-ROUNDTRIP`, `ANDROID-CLIENT-CORE-001` | provisional; M2-M1 proof |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | `SERVICE-COMPOSE-001`, `SERVICE-DEPS-001`, core + audited prerequisites | provisional |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA source artwork/platform derivatives. | branding source delivered | queued; old branding branches are historical only |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Implement source-backed full instruction replacement delivery. | `ONBOARD-001`, audited onboarding, current instruction capability verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Require customer action or exact continuation fallback on next full instruction replacement. | next legitimate full replacement | queued |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy production data only after stable schema/vertical proof. | stable schema + rollback/reconciliation | deferred; PR31 migration code selective reference only |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI parity and packaging after shared API/core. | core verticals | deferred; PR31 client code selective reference only |
| `RFID` | LATER | RFID inventory capture/specialized hardware. | stable inventory schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Implement `LOCAL-001` bridge then local-service adapters with scoped permissions/readback. | `LOCAL-001`, `API-CORE-001`, stable authority/integration contracts | deferred; PR31 contracts selective reference only |
| `ENTERPRISE` | LATER | Implement/prove `ENTERPRISE-001` managed/regulated lane. | `ENTERPRISE-001`, stock core, provider abstraction | deferred |

## Canonical dependency findings

- `AUTH-001` + `STORE-001` own canonical mutable-authority routing and provider-neutral storage/evidence adapter contracts. Provider brands/backend products never become authority merely by selection.
- `API-CORE-001` remains the security/data-integrity blocker for stock ChatGPT and Android mutation. Android remains downstream of the shared API and never receives direct provider/database/source authority.
- `FEATURE-REGISTRY-001` is a prerequisite for `DEP-GRAPH` so final dependency closeout is built from stable authored semantic IDs.
- `CODE-OWNERSHIP-001` is a central growth/release gate, not a prose dependency copied into every implementation row.

## Legacy reconciliation findings

- Open legacy PRs are PR #31 and PR #34. PR #31 is **selective salvage only / never wholesale merge**. PR #34 is **superseded by authoritative Mira-2.0 governance / reject merge**.
- Public and Institutional Experimental repositories explicitly declare themselves generated non-canonical distributions. They do not create independent feature authority.
- Representative architecture/dependency/reconciliation/distribution-fix branches are ancestors of legacy `main` and contain no unique unmerged work.
- Diverged manual-brief/distribution-build/install-cleanup branches are semantically superseded by newer legacy-main behavior.
- `mira-mirror-branding` is historical branding evidence only; current `BRAND-001`/approved brand assets win.
- `feature/productization-docker-oauth-full-ui` is a genuine 4-commit independent code quarry. Salvage repository abstraction/revisioned upserts, compatibility, pairing and idempotency patterns into `STORE-ADAPTER-001`/`API-CORE-001`; reject its coarse auth, direct Google wiring, non-registry backend selection, single-location overwrite model and wholesale parallel service stack.
- PR #31 salvage maps to existing API/storage/Android/backup/inventory/receipt/local-integration/distribution/migration/desktop work. Its direct client-to-provider paths, dual-authority risks, permissive mutation semantics, silent scheduler patterns, path identity, unverified restore/signing/device/live-provider claims and old branding are explicitly rejected.
- No new semantic feature IDs were created by G0-009. Legacy evidence remains `legacy_*`/`candidate_unmerged` until MIRA 2.0 implementation and verification occur.

## Prior-category closure

Categories A-G forensic feature coverage and G0-009 legacy reconciliation are complete. The **only remaining G0 stage is `DEP-GRAPH` / G0-010**: final dependency/enables graph, dedupe/supersession map and ranked implementation backlog.

After G0-010 merges, new MIRA 2.0 implementation begins.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
