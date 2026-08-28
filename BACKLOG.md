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
| `AUDIT-F2` | PREREQUISITE | F rows 6-8: Personal finance organization; Appointments/calendar/reminders; Administrative health organization; goal/submodule-scoped service readiness and sensitive-state boundaries. | AUDIT-F1 | complete in `M2-G0-007B`; `SERVICE-002` refinement, `CAL-005`, `CAL-006`, `HEALTH-001` |
| `AUDIT-F3` | PREREQUISITE | F rows 9-10: Shopping/procurement and Recipes/meals/groceries service composition; recipe-library versus meal-planning submodule and migration boundaries. | AUDIT-F2 | complete in `M2-G0-007C`; canonical `SHOP-001`, `GROCERY-001`, `RECIPE-001`, `MEAL-001` mappings |
| `AUDIT-F4` | PREREQUISITE | F rows 11-12: Household/errands/admin/maintenance and Laundry stages/drop-off/pickup reminders; routine lifecycle, anti-fan-out and responsibility boundaries. | AUDIT-F3 | complete in `M2-G0-007D`; `ROUTINE-001`, `REMIND-003` |
| `AUDIT-F5` | PREREQUISITE | F rows 13-14: Routines/fitness/accountability and Education/study/deadlines/offline preparation. | AUDIT-F4 | complete in `M2-G0-007E`; `EDU-001`, `CAL-007` |
| `AUDIT-F6` | PREREQUISITE | F row 15: Parent/child school coordination; actor/subject permission, education-authority and role-versus-readiness boundaries. | AUDIT-F5 | complete in `M2-G0-007F` |
| `AUDIT-F7` | PREREQUISITE | F rows 16-17: Travel/vacation/outdoor planning and Work-trip/route/paid-work tracking; shared Trip/Route core and paid-mileage specialization. | AUDIT-F6 | complete in `M2-G0-007G` |
| `AUDIT-F8` | PREREQUISITE | F row 18: Assets/maintenance/warranties/manuals service composition; selected-path readiness over canonical category-D authorities. | AUDIT-F7 | complete in `M2-G0-007H` |
| `AUDIT-G16-F20` | PREREQUISITE | G16 backup/restore foundation plus F20 Backup/disaster recovery service composition. | AUDIT-F8 | complete in `M2-G0-008A`; `BACKUP-001` |
| `AUDIT-G17-G18-F19` | PREREQUISITE | G17 knowledge ingestion/provenance plus G18 provider organization/search metadata and F19 Personal knowledge/reference service composition. | AUDIT-G16-F20 | complete in `M2-G0-008B`; `KNOW-001`, `KNOW-002` |
| `AUDIT-G1` | PREREQUISITE | G1 canonical mutable-authority foundation. | AUDIT-G17-G18-F19 | complete in `M2-G0-008C`; `AUTH-001`, `STORE-001` |
| `AUDIT-G7` | PREREQUISITE | G7 provider-neutral policy/data API foundation. | `AUDIT-G1`, `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001` | complete in `M2-G0-008D`; `API-001` |
| `AUDIT-G10` | PREREQUISITE | G10 Android/mobile client boundary. | `AUDIT-G7`, `API-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001` | complete in `M2-G0-008E`; `CLIENT-ANDROID-001`; direct-Google client path rejected |
| `AUDIT-G19-G20` | PREREQUISITE | G19/G20 repository integrity: stable feature projection and production-component ownership/evidence gates. | `DEV-001`, `DEV-003` | complete in `M2-G0-008F`; `DEV-005`, `DEV-006` |
| `AUDIT-F21-F23-G2-G15` | PREREQUISITE | Remaining recovered ledger closeout: F21 custom skill builder, F22 wearables, F23 weather onboarding, G2-G6 portability/enterprise/release/storage topology, G8-G9 observability/evidence storage, G11-G15 local/voice/network infrastructure. | `AUDIT-G19-G20` | complete in `M2-G0-008G`; new `WEATHER-002`, `WEARABLE-001`, `ENTERPRISE-001`, `OBS-001`, `LOCAL-001`, `VOICE-001`; provider/backend/topology rows deduped into existing authorities |
| `AUDIT-G` | PREREQUISITE | Category-G platform/integration/recovery/infrastructure ledger coverage. | AUDIT-F | complete through `M2-G0-008G`; all recovered G1-G20 rows mapped |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; G0-009 next |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog from stable semantic feature IDs. | completed forensic registry + `DEV-005` + `FEATURE-REGISTRY-001` | queued; G0-010 |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `FEATURE-REGISTRY-001` | PREREQUISITE | Implement/test `DEV-005` machine-readable projection from canonical `FEATURES.md`: parse authored semantic IDs without renumbering, validate requirement/evidence/dependency fields and referenced IDs, generate deterministic projections tied to exact source hash/revision, and fail CI on material drift or hand-edited generated outputs. | `DEV-005`, `DEV-001`, `DEV-003` | queued; legacy generator/drift CI test-verified but row-position IDs/title-regex evidence rejected |
| `CODE-OWNERSHIP-001` | PREREQUISITE | Implement/test `DEV-006` production component ownership/evidence manifest with bounded responsibility, owned paths/surfaces, related feature/work IDs and direct verification evidence; fail unowned/overlapping ownership and accidental debug/test payloads centrally. | `DEV-006`, `DEV-001` | queued; legacy Python inventory test-verified, language-neutral MIRA 2.0 gate unimplemented |
| `WEATHER-ONBOARD-001` | HARDENING | Implement/test `WEATHER-002` explicit weather preferences/onboarding: selected brief slots, location policy, units, detail, severe-alert override behavior, explicit service activation, provider-capability honesty and failure isolation. Weather-provider failure cannot corrupt brief/core state. | `WEATHER-002`, `WEATHER-001`, `ONBOARD-004`, `ONBOARD-005`, `SERVICE-001` | queued; legacy starter questions/contract are test-supported, MIRA 2.0 implementation unverified |
| `WEARABLE-ADAPTER-001` | LATER | Design/implement optional `WEARABLE-001` adapters for explicitly authorized activity/wearable data with provenance, capability/readback, stale/partial-coverage honesty and no dependency from core routine/fitness truth. | `WEARABLE-001`, `PROVIDER-001` | deferred optional; no executable legacy adapter located |
| `OBSERVABILITY-001` | HARDENING | Implement `OBS-001` provider-neutral telemetry/read-only dashboard projection for health/status/audit metrics; dashboards and alerts never become mutable authority or fabricate tasks/reminders/scheduler truth. | `OBS-001`, `AUTH-001`, `RECOVERY-002`, core runtime | queued after core; legacy Grafana architecture only |
| `VOICE-CLIENT-001` | LATER | Implement `VOICE-001` optional voice query/command surface over `API-001` with normal authentication, authorization, idempotency/readback and explicit confirmation for consequential actions. | `VOICE-001`, `API-CORE-001` | deferred until shared API/client core |
| `SERVICE-COMPOSE-001` | PREREQUISITE | Port/prove `SERVICE-002` service catalog/dependency composition in MIRA 2.0 with activation separate from readiness and module-scoped failure isolation. | `SERVICE-001`, `SERVICE-002`, canonical dependency registry, `RUNTIME-ROUTER-001` | queued |
| `SERVICE-DEPS-001` | PREREQUISITE | Repair/test F1 bundles: Briefs require `OPS-002`; Orders/shipments require `ORDER-004`; prove aggregate readiness cannot bypass duplicate-schedule or replacement/supersession safety. | `SERVICE-002`, `OPS-002`, `ORDER-004`, dependency registry | queued |
| `SERVICE-DEPS-002` | PREREQUISITE | Normalize/test F2 finance, appointments/calendar/reminders and administrative-health selected-goal readiness. | `SERVICE-002`, `CAL-005`, `CAL-006`, `HEALTH-001`, category-C finance features, dependency registry | queued |
| `SERVICE-DEPS-003` | PREREQUISITE | Normalize/test F3 shopping and recipe/meal/grocery selected-submodule readiness. | `SERVICE-002`, `SHOP-001`, `GROCERY-001`, `RECIPE-001`, `MEAL-001`, dependency registry | queued |
| `SERVICE-DEPS-004` | PREREQUISITE | Normalize/test F4 household admin/routine readiness and reminder anti-fan-out. | `SERVICE-002`, `TASK-001`, `TASK-002`, `ROUTINE-001`, `REMIND-003`, dependency registry | queued |
| `SERVICE-DEPS-005` | PREREQUISITE | Normalize/test F5 routines/fitness and education; wearable input, Calendar and offline providers remain optional selected paths. | `SERVICE-002`, `ROUTINE-001`, `TASK-001`, `TASK-002`, `REMIND-003`, `EDU-001`, `CAL-007`, dependency registry | queued |
| `SERVICE-DEPS-006` | PREREQUISITE | Normalize/test F6 `family_school` readiness around exact actor/subject/scope rather than role tokens. | `SERVICE-001`, `SERVICE-002`, `EDU-001`, `PROFILE-012`, `PROFILE-013`, dependency registry | queued |
| `SERVICE-DEPS-007` | PREREQUISITE | Normalize/test F7 travel/work-trip bundles and paid-mileage separation. | `SERVICE-001`, `SERVICE-002`, `TRIP-001`, `ROUTE-001`, `MILE-001`, `MILE-002`, dependency registry | queued |
| `SERVICE-DEPS-008` | PREREQUISITE | Normalize/test F8 assets selected-path readiness. | `SERVICE-001`, `SERVICE-002`, `ASSET-001`, `ASSET-003`, dependency registry | queued |
| `SERVICE-DEPS-009` | PREREQUISITE | Normalize/test F20 recovery-service readiness around `BACKUP-001` plus verified backup-target/restore capability. | `SERVICE-001`, `SERVICE-002`, `BACKUP-001`, dependency registry | queued |
| `SERVICE-DEPS-010` | PREREQUISITE | Normalize/test F19 knowledge-service readiness around `KNOW-001`/`KNOW-002` and optional provider projection. | `SERVICE-001`, `SERVICE-002`, `KNOW-001`, `KNOW-002`, dependency registry | queued |
| `AUTHORITY-REGISTRY-001` | PREREQUISITE | Implement/test `AUTH-001` persistent Authority Registry and exact data-class routing with one active canonical authority per mutable class and deterministic readback. | `AUTH-001`, `RECOVERY-002`, `STORE-001` | queued |
| `STORE-ADAPTER-001` | PREREQUISITE | Implement/test `STORE-001` provider-neutral structured-state/evidence-store adapter interfaces with synthetic adapters first, idempotent writes, audit/export and exact material readback. | `STORE-001`, `RECOVERY-002`, `DATA-SANDBOX` | queued |
| `API-CORE-001` | BLOCKER | Implement/prove `API-001` shared provider-neutral MIRA/MIRROR service runtime for ChatGPT, Android and later clients with authenticated actor/client identity, least-privilege authorization, canonical query/command envelopes, mandatory mutation idempotency/version preflight, conflict handling, audit and exact read-after-write routed only through `AUTH-001`/`STORE-001`. | `API-001`, `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, `PROVIDER-001`, `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001` | queued; security/data-integrity blocker for safe remote/native mutation |
| `ANDROID-CLIENT-CORE-001` | PREREQUISITE | Implement/prove `CLIENT-ANDROID-001` MIRA 2.0 core: API compatibility, enrollment/session identity, revocation, scoped auth, Android protected credential storage, bounded reads, canonical commands, replay-safe offline queue, reconnect/cursor sync and server conflict/readback handling. | `CLIENT-ANDROID-001`, `API-CORE-001`, `RUNTIME-ROUTER-001` | queued; M2-M1 prerequisite |
| `ANDROID-NATIVE-DELIVERY-001` | HARDENING | Port/redesign Android visual notification and opt-in TTS delivery over canonical reminder intents with duplicate suppression, timing truth, privacy policy and observed-device evidence. | `CLIENT-ANDROID-001`, `ANDROID-CLIENT-CORE-001`, canonical reminder semantics | queued |
| `ANDROID-CAPTURE-001` | HARDENING | Port/redesign Android camera/barcode/QR, NFC and BLE/RFID capture as nonauthoritative observation/evidence adapters through `API-001`. | `CLIENT-ANDROID-001`, `ANDROID-CLIENT-CORE-001`, `API-001`, `EVID-001`, `IDENT-001` | queued |
| `ANDROID-RELEASE-001` | HARDENING | Establish MIRA 2.0 Android reproducible build/signing/version/provenance and representative-device smoke evidence. | `CLIENT-ANDROID-001`, `ANDROID-CLIENT-CORE-001`, distribution/release policy | queued; no current MIRA 2.0 signed artifact |
| `AUTHORITY-MIGRATION-001` | PREREQUISITE | Implement/prove staged provider/backend cutover without dual writable masters, with export/parity/readback/recovery/rollback evidence. | `AUTH-001`, `STORE-001`, `BACKUP-001`, `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001`, `DATA-SANDBOX` | queued |
| `BACKUP-CORE-001` | PREREQUISITE | Implement/test `BACKUP-001` provider-neutral backup/restore lifecycle with integrity/target readback, retention/encryption/RPO/RTO policy and isolated restore verification. | `BACKUP-001`, `PROVIDER-001`, `RECOVERY-002`, `DATA-SANDBOX`, canonical storage adapters | queued |
| `KNOWLEDGE-CORE-001` | PREREQUISITE | Refactor/port `KNOW-001` as provider-neutral general Knowledge source identity and typed relationship core. | `KNOW-001`, `RECOVERY-002`, canonical identity/relationship model, `DATA-SANDBOX` | queued |
| `KNOWLEDGE-PROVENANCE-001` | PREREQUISITE | Implement/test `KNOW-002` stable excerpt/derived-fact provenance lifecycle. | `KNOW-002`, `KNOW-001`, `RECOVERY-002`, canonical provenance model | queued |
| `KNOWLEDGE-PROJECTION-001` | HARDENING | Normalize provider organization/search projection with exact provider readback and no folder-path identity. | `KNOW-001`, `KNOW-002`, `DATA-SANDBOX`, selected evidence/document provider | queued |
| `TRIP-ROUTE-CORE-001` | PREREQUISITE | Port/prove canonical `TRIP-001`/`ROUTE-001` state, precedence/provenance and optional ordered multi-leg grouping. | `TRIP-001`, `ROUTE-001`, `RECOVERY-002`, canonical state/time semantics, `DATA-SANDBOX` | queued |
| `ROUTINE-CORE-001` | PREREQUISITE | Implement/test `ROUTINE-001` recurring/staged routine definitions and occurrence lifecycle. | `TASK-001`, `TASK-002`, canonical Person/time semantics | queued |
| `ROUTINE-REMINDER-001` | PREREQUISITE | Implement/test `REMIND-003` consolidated routine/stage/accountability reminder planning/projection. | `ROUTINE-001`, `RECOVERY-002`, canonical time semantics, verified delivery adapters | queued |
| `APPOINTMENT-IDENTITY-001` | HARDENING | Port/prove `CAL-005` appointment/provider identity reconciliation. | `CAL-005`, canonical appointment/source identity, evidence/provenance | queued |
| `CALENDAR-PROJECTION-001` | PREREQUISITE | Implement/prove `CAL-007` generic source-linked Calendar projection and exact provider readback. | `CAL-007`, `CAL-006`, provider Calendar write/readback, `DATA-SANDBOX`, `RECOVERY-002` | queued |
| `EDUCATION-CORE-001` | PREREQUISITE | Implement/test `EDU-001` durable program/course/certification and academic-work/deadline lifecycle. | `EDU-001`, `TASK-001`, `TASK-002`, provenance/evidence authority | queued |
| `HEALTH-ADMIN-001` | ENHANCEMENT | Define/test `HEALTH-001` non-clinical administrative health schema and safety gates. | `HEALTH-001`, `PROFILE-013`, evidence authority | queued |
| `SERVICE-MIGRATION-001` | HARDENING | Define/test migration of legacy service activation fields without silently broadening intent. | `SERVICE-001`, `SERVICE-002`, canonical service/submodule IDs, onboarding migration path | queued |
| `MIRA-SKILL-001` | PREREQUISITE | Port/prove `ONBOARD-007` provider-neutral MIRA orchestration skill. | `ONBOARD-007`, `DIST-STARTER-001`, `SOURCE-GATES-001`, `RUNTIME-ROUTER-001`, `SERVICE-COMPOSE-001` | queued |
| `PROVIDER-ONBOARD-001` | PREREQUISITE | Port/prove `PROVIDER-002` browser provider onboarding with exact identity/resource/scope, bounded write/readback and honest Apple/manual degradation. | `PROVIDER-002`, `ONBOARD-006`, `RUNTIME-ROUTER-001`, provider adapters/Authority Registry | queued |
| `GOOGLE-BOOTSTRAP-001` | PREREQUISITE | Port/prove `PROVIDER-003` deterministic Personal Google blueprint/plan/verifier using only a separate synthetic MIRA 2.0 namespace for integration proof. | `PROVIDER-003`, `MIRA-SKILL-001`, `PROVIDER-ONBOARD-001`, `SOURCE-GATES-001` | queued |
| `NONTECH-INSTALL-001` | PREREQUISITE | Port/prove `ONBOARD-006` browser-only MIRA 2.0 installation with private source creation, exact readback and no terminal fallback. | `ONBOARD-006`, `DIST-STARTER-001`, `SOURCE-GATES-001`, `MIRA-SKILL-001`, `PROVIDER-ONBOARD-001` | queued |
| `SOURCE-GATES-001` | PREREQUISITE | Port/prove `SOURCE-001` independent source read/write/remote-readback gates. | `SOURCE-001`, source connector/runtime capability | queued |
| `RUNTIME-ROUTER-001` | PREREQUISITE | Port/prove `PROVIDER-001` provider-neutral runtime capability manifest/router. | `PROVIDER-001`, `SOURCE-GATES-001`, data-classification/approval state | queued |
| `SOURCE-LANES-001` | PREREQUISITE | Port/prove `SOURCE-002` personal Git, organization Git, managed-central and no-Git/manual lanes. | `SOURCE-002`, `SOURCE-GATES-001`, `RUNTIME-ROUTER-001`, `DIST-STARTER-001` | queued |
| `PERSON-GRAPH-001` | PREREQUISITE | Implement/test `PROFILE-012` canonical Person UUIDs and explicit relationship graph. | `PROFILE-012`, canonical MIRROR identity authority, `DATA-SANDBOX` | queued |
| `PERMISSION-SCOPE-001` | BLOCKER | Implement/prove `PROFILE-013` explicit actor/resource/action grants, revoke/narrow semantics and provider/API sharing readback. | `PROFILE-012`, Authority Registry, provider identity/readback | queued; privacy-critical |
| `FEATURE-SHARE-001` | HARDENING | Port/prove `DIST-001` private feature ownership/reconciliation plus sanitized public-candidate extraction and separate publication approval/readback. | `DIST-001`, `ONBOARD-002`, feature/dependency manifests, `SOURCE-GATES-001` | queued |
| `DIST-STARTER-001` | PREREQUISITE | Port/prove `DIST-002` deterministic MIRA 2.0 starter/distributions from one source SHA. | `DIST-002`, `ONBOARD-002`, clean source lineage | queued |
| `SKILL-BUILDER-001` | ENHANCEMENT | Implement/test `DEV-004` bounded private custom-feature workflow with source/dependency/test/privacy/readback gates. | `DEV-004`, `DEV-001`, `DEV-002`, feature/dependency registry, `SOURCE-GATES-001` | queued |
| `PROFILE-CARE-001` | HARDENING | Port/test `PROFILE-006` caregiver composition without inferred authority. | `PROFILE-006`, `SERVICE-001`, `REMIND-001`, `REMIND-002`, `PROFILE-012`, `PROFILE-013`, `PERMISSION-SCOPE-001` | queued |
| `PROFILE-HOUSEHOLD-001` | HARDENING | Port/prove `PROFILE-007` household-manager routing and anti-fan-out behavior. | `PROFILE-007`, `SERVICE-001`, task/routine authority | queued |
| `PROFILE-STUDENT-001` | HARDENING | Port/test `PROFILE-008` student role and explicit HOME/CAMPUS option. | `PROFILE-008`, `CTX-001`, `CTX-002`, `SERVICE-001` | queued |
| `PROFILE-MIXED-001` | HARDENING | Port/prove `PROFILE-009` mixed/custom composition and primary-role routing. | `PROFILE-009`, canonical profile authority | queued |
| `PROFILE-USABILITY-001` | ENHANCEMENT | Define/test `PROFILE-010` usability/accessibility preferences without demographic inference. | `PROFILE-010`, onboarding preference state, client capability discovery | queued |
| `PROFILE-LABEL-001` | HARDENING | Enforce `PROFILE-011` public-label rejection/private-alias-only boundary. | `PROFILE-011`, `ONBOARD-002`, canonical profile alias state | queued |
| `PROFILE-MINOR-001` | PREREQUISITE | Port/prove `PROFILE-005` dependent-minor routing plus explicit relationship/permission scopes. | `PROFILE-005`, `SERVICE-001`, `PROFILE-012`, `PROFILE-013`, `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001` | queued |
| `PROFILE-PARENT-001` | PREREQUISITE | Port/prove `PROFILE-004` parent/guardian composition without relationship-derived authority. | `PROFILE-004`, `SERVICE-001`, `PROFILE-012`, `PROFILE-013`, `PERSON-GRAPH-001`, `PERMISSION-SCOPE-001` | queued |
| `PROFILE-WORK-001` | HARDENING | Port/test `PROFILE-001` working/self-employed role semantics. | `PROFILE-001`, `ONBOARD-004`, `SERVICE-001`, `CTX-002` | queued |
| `PROFILE-RETIRED-001` | HARDENING | Port/prove `PROFILE-002` retired-role semantics and opt-in support. | `PROFILE-002`, `SERVICE-001` | queued |
| `PROFILE-NONWORKING-001` | HARDENING | Port/test `PROFILE-003` nonworking/between-jobs semantics and transitions. | `PROFILE-003`, `SERVICE-001` | queued |
| `STARTER-SANITIZE-001` | PREREQUISITE | Port/prove `ONBOARD-002` privacy/history audit gates for MIRA 2.0 starter/distribution. | `ONBOARD-002`, `DIST-002` | queued |
| `FIRSTBOOT-CORE-001` | PREREQUISITE | Implement/test `ONBOARD-003` ≤4-question kickoff, durable Interview Ledger resume/defer/silence semantics and Minimum Useful Setup. | `ONBOARD-002`, canonical onboarding state | queued |
| `DISCOVERY-CORE-001` | HARDENING | Implement/test structured `ONBOARD-004` discovery without recommendation-driven activation. | `ONBOARD-003`, `SERVICE-001`, `RUNTIME-ROUTER-001` | queued |
| `ONBOARD-SCHEDULE-001` | PREREQUISITE | Implement/test `ONBOARD-005` cadence/slot/IANA-timezone capture and enabled-brief routing. | `ONBOARD-003`, `SERVICE-001`, `OPS-003` | queued |
| `SERVICE-STATE-001` | PREREQUISITE | Port/prove `SERVICE-001` finite activation-state machine. | canonical service catalog/config authority | queued |
| `RECIPE-CORE-001` | LATER | Implement/test `RECIPE-001` stable recipe identity/provenance/structured ingredients. | ingredient/unit semantics; optional `KNOW-001` | queued |
| `MEAL-CORE-001` | LATER | Implement/test `MEAL-001` dated planning, pantry-aware gaps and deduplicated shopping intent. | `RECIPE-001`, `GROCERY-CORE-001`, `SHOP-CORE-001` | queued |
| `MOVEMENT-CORE-001` | PREREQUISITE | Salvage/redesign `MOVE-001` as replay-safe movement/observation events. | `INV-001`, `IDENT-001`, `LOCATION-STATE-001` | queued |
| `INVENTORY-QUERY-001` | HARDENING | Implement/prove `INV-002` inventory projection without second mutable authority. | `INV-001`, `LOC-001`, `ASSET-003`, `LOCATION-STATE-001` | queued |
| `PAR-CORE-001` | ENHANCEMENT | Implement/test `PAR-001` observed quantity/target/threshold state. | `INV-001`, canonical quantity observations | queued |
| `PAR-SCALE-001` | LATER | Optional `PAR-002` scale/load-cell adapter. | `PAR-001`, observation/provenance model | deferred optional |
| `GROCERY-CORE-001` | PREREQUISITE | Implement/test `GROCERY-001` grocery-list versus stock reconciliation. | `SHOP-001`, `INV-001`, `LOC-001`, quantity/unit model | queued |
| `LOCATION-STATE-001` | PREREQUISITE | Implement/test `LOC-001` hierarchical intended versus observed location state. | `INV-001`, location/event schema | queued |
| `SHOP-CORE-001` | PREREQUISITE | Implement/test deterministic `SHOP-001` shopping-intent reconciliation. | `RECEIPT-001`, stable shopping-intent identity | queued |
| `KNOWLEDGE-INTEGRATION-001` | HARDENING | Prove synthetic `KNOW-001` retained-source/provider readback integration. | `KNOW-001`, `DATA-SANDBOX`, Google/MIRROR adapter | queued |
| `SPEC-INTEGRATION-001` | HARDENING | Prove `SPEC-001` authoritative specification persistence/readback. | `SPEC-001`, `KNOW-001`, `DATA-SANDBOX` | queued |
| `FITMENT-ENGINE-001` | HARDENING | Add deterministic automatic `FITMENT-001` resolution tests/engine. | `ASSET-001`, `IDENT-001`, fitment evidence | queued |
| `ASSET-SERVICE-001` | HARDENING | Define/test structured warranty and maintenance lifecycle records under `ASSET-002`. | `ASSET-001`, `EVID-001` | queued |
| `ORDER-STALE-001` | PREREQUISITE | Implement/test `ORDER-005` five-business-day stale-shipment escalation. | `ORDER-002`, business-day semantics | queued |
| `SPEND-ROLLUP-001` | HARDENING | Implement deterministic `SPEND-001` monthly evidence-bounded rollup tests. | `RECEIPT-001`, `RECEIPT-003` | queued |
| `RECEIPT-TAXONOMY-001` | PREREQUISITE | Implement configuration-backed generic `RECEIPT-003` taxonomy/classifier. | `RECEIPT-001` | queued |
| `REIMB-CORE-001` | HARDENING | Implement/test deterministic `REIMB-001` reimbursement lifecycle. | `RECEIPT-001`, `PROFILE-012`, beneficiary allocation | queued |
| `SUBSCRIPTION-TRACK-001` | LATER | Specify/implement opt-in `SUB-001` only if promoted. | stable receipt/finance evidence + explicit activation | deferred optional |
| `FINANCE-CONNECTOR-001` | LATER | Design/implement `FIN-001` authorized complete-account ingestion. | provider abstraction + privacy model + authorization | deferred infrastructure |
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | `AUTHORITY-REGISTRY-001`, `STORE-ADAPTER-001`, `GOOGLE-BOOTSTRAP-001` | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Stock ChatGPT create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity through the shared API boundary. | `DEP-GRAPH`, `DATA-SANDBOX`, `GOOGLE-BOOTSTRAP-001`, `API-CORE-001` | provisional |
| `ANDROID-SYNC` | VERTICAL | Android reads/mutates the same canonical entity through `API-001` without second authority or direct provider mutation. | `CORE-ROUNDTRIP`, `ANDROID-CLIENT-CORE-001` | provisional; M2-M1 proof target |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | `SERVICE-COMPOSE-001`, `SERVICE-DEPS-001`, core + audited prerequisites | provisional |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA source artwork and generated platform derivatives. | branding source delivered | queued |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Implement/test `ONBOARD-001` complete source-backed Project/Custom Instructions replacement delivery. | `ONBOARD-001`, audited onboarding, current instruction-surface capability verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Next full Project Instructions replacement must require customer action or exact fallback `Just tell me to continue.` before final packet line. | next legitimate full replacement | queued |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy data after stable schema/vertical proof. | stable schema + rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI parity and packaging. | core verticals | deferred |
| `RFID` | LATER | RFID inventory capture/specialized hardware. | stable inventory schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Implement `LOCAL-001` explicit local-service bridge, then Home Assistant/Plex/Paperless/Node-RED/MQTT/NAS adapters with scoped network/service permissions, capability/readback and no blanket LAN/root/cloud-reachability assumption. | `LOCAL-001`, `API-CORE-001`, stable authority/integration contracts | deferred; no dedicated adapter implementation located |
| `ENTERPRISE` | LATER | Implement/prove `ENTERPRISE-001` managed/regulated deployment lane with synthetic-first pilot, current organization approval/data-classification evidence, approved managed source/provider resources, no personal-account workaround and exact capability/readback. | `ENTERPRISE-001`, stock core, provider abstraction | deferred until stock core/provider paths are proven |

## Canonical dependency findings

- `AUTH-001` + `STORE-001` own canonical mutable-authority routing and provider-neutral storage/evidence adapter contracts. Provider brands and backend products never become authority merely by selection.
- `API-CORE-001` remains the security/data-integrity blocker for stock ChatGPT and Android mutation. Android remains downstream of the shared API and never receives direct provider/database/source authority.
- `FEATURE-REGISTRY-001` is a prerequisite for `DEP-GRAPH` so final dependency closeout is built from stable authored semantic IDs rather than legacy row-position identity.
- `CODE-OWNERSHIP-001` is a central growth/release gate, not a prose dependency copied into every implementation row.
- Legacy and PR #31 evidence remain salvage/reference only unless MIRA 2.0 implementation, integration and live/provider readback are separately proven.

## Remaining-ledger closeout findings

- F21 reuses `DEV-004`/`SKILL-BUILDER-001`; F22 is optional `WEARABLE-001`; F23 adds `WEATHER-002` preferences over `WEATHER-001` rather than a second weather engine.
- G2/G3 provider portability is adapter/capability routing under `STORE-001`, `PROVIDER-*` and `SOURCE-002`; Apple/iCloud remains manual unless an exact adapter proves more.
- G4 creates `ENTERPRISE-001`; organization approval remains mutable external evidence and is never manufactured by configuration.
- G5 is `DIST-001`/`DIST-002`. G6 PostgreSQL and G9 object/NAS storage are backend adapter/topology choices under `STORE-001`, not product authorities.
- G8 creates `OBS-001` as read-only operational projection.
- G11/G12/G14 share `LOCAL-001`; specific local services are later adapters. G13 creates `VOICE-001`. G15 family VPN/redundancy remains external/deferred infrastructure.
- None of F22, G6, G8-G9 or G11-G15 becomes a new blocker for M2-M0/M2-M1.

## Prior-category closure

Categories A-E are complete. Category F is complete through F23: F1-F18 were closed in `M2-G0-007A` through `M2-G0-007H`, F19/G17/G18 in `M2-G0-008B`, F20/G16 in `M2-G0-008A`, and F21-F23 in `M2-G0-008G`. Category G is complete through G20 in `M2-G0-008G`; every recovered G row is mapped to a stable semantic feature, an existing provider/backend adapter boundary, or explicit deferred external infrastructure.

Next G0 work is `AUDIT-LEGACY` (G0-009), then `DEP-GRAPH` (G0-010). New product implementation begins only after that closeout.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
