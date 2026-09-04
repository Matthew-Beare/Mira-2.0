# MIRA 2.0 FEATURES

Canonical feature index. Detailed rationale and evidence remain durable in Git history and packet checkpoints. This file is authoritative for stable semantic feature IDs, current requirement/evidence state, canonical dependencies, and audited service/foundation mappings.

## Rules

Stable semantic IDs do not change with priority, provider, backend, or display order. Requirement and evidence are separate; code existence is not completion. `deps` contains universal semantic prerequisites only. Conditional provider, sharing, deployment, or selected-service requirements belong in mappings/backlog work rather than being promoted to universal dependencies. Completed features/work remain represented with evidence; completion removes them from active selection, not from history.

## Feature index

`ID | Title | requirement | evidence | deps`

- `DEV-001` | Git-authoritative development control plane | governance | implemented/specified | -
- `DEV-002` | Resumable bounded work packets | governance | implemented/specified | -
- `DEV-003` | Dependency-ranked backlog | governance | implemented/specified | -
- `DEV-005` | Machine-readable projection of canonical feature/dependency/evidence state plus backlog work lifecycle state, with reproducible generation and CI drift enforcement; generated/query views never become a second editable product authority | required/governance | specified+legacy-test-verified | DEV-001,DEV-003
- `DEV-006` | Production component ownership and direct-verification inventory with anti-bloat/unowned-code release gate | required/governance | specified+legacy-test-verified | DEV-001
- `DEV-007` | Packet-to-feature-set alignment gate requiring every implementation packet to map itself to canonical user-visible features/invariants before implementation and again before merge, reconcile completion evidence/status, and select next work from unfinished accepted scope so local architecture or stale backlog text cannot silently drift away from product direction | required/governance | specified | DEV-001,DEV-002,DEV-003,DEV-005
- `CORE-001` | MIRA product identity; the assistant/product name is fixed as MIRA and onboarding must not ask the user to rename it | governance | history+specified | -
- `MIRROR-001` | Companion reality database | governance | history | -
- `DATA-001` | Legacy production preservation | governance | history | -
- `AUTH-001` | Canonical Authority Registry and one-authority-per-data-class routing | required/foundational | specified+tested-boundary | RECOVERY-002
- `STORE-001` | Provider-neutral structured-state and evidence-store adapter contracts with verified mutation/readback | required/foundational | specified+tested-boundary+candidate_unmerged | RECOVERY-002
- `API-001` | Versioned authenticated MIRROR client service boundary with bounded commands, queries, synchronization and verified mutation readback | required/foundational | specified+test-supported-boundary+candidate_unmerged | AUTH-001,STORE-001,RECOVERY-002
- `CLIENT-ANDROID-001` | Android native client adapter using the shared API, protected client credentials, offline replay-safe sync and evidence-based device capabilities | required/M2-M1 | specified+test_verified+partial-merged+provider-binding-candidate_unmerged | API-001,RECOVERY-002
- `OBS-001` | Provider-neutral operational observability and read-only dashboard projection that never becomes mutable-state authority | optional/proposed | specified/legacy-architecture | AUTH-001,RECOVERY-002
- `LOCAL-001` | Explicit local-service integration bridge with scoped network/service permissions, verified capability/readback and no assumed cloud reachability or blanket LAN trust | optional/proposed | specified/not_present | API-001,RECOVERY-002
- `VOICE-001` | Optional voice query and command client surface using shared API authorization with explicit confirmation for consequential actions | optional/proposed | specified/not_present | API-001
- `ONBOARD-001` | Full-replacement instruction delivery | governance | implemented/specified | -
- `BRAND-001` | Canonical MIRA brand asset system | governance | history | -
- `OPS-001` | Canonical twice-daily Ops Brief schedule | required | test_verified | OPS-003,OPS-004
- `OPS-002` | Single canonical dispatcher and prohibited duplicate schedules | required | specified | OPS-001
- `OPS-003` | Canonical runtime clock gate with DST-safe slot matching | required by failure evidence | test_verified | -
- `OPS-004` | Fresh standalone run delivery with deterministic Run ID | required | test_verified | OPS-003,RECOVERY-001
- `OPS-005` | Deterministic HOME/ROAD context with explicit overrides | required | test_verified | -
- `CTX-001` | Configurable operating-context pairs | accepted-direction | test_verified | -
- `CTX-002` | Evidence-gated context recommendation and explicit activation | required | test_verified | -
- `TRIP-001` | Independent trip occurrence lifecycle | required | test_verified | -
- `ROUTE-001` | Learned routes, directional runtime, location and ETA inference | required | test_verified | -
- `WEATHER-001` | Context-gated HOME and ROAD weather intelligence | required | test_verified | -
- `WEATHER-002` | Explicit weather delivery preferences and onboarding for selected brief slots, location policy, units, detail and severe-alert behavior | required | specified+legacy-test-supported-boundary | WEATHER-001,ONBOARD-004,ONBOARD-005,SERVICE-001
- `MILE-001` | Company-paid mileage and deterministic gross-pay reporting | required | test_verified | -
- `MILE-002` | Separate authoritative Miles & Pay tracker | required | legacy_live | -
- `TASK-001` | Structured task hierarchy and one-action-per-item rendering | required | test_verified | -
- `TASK-002` | Evidence-grounded next actions and honest completion state | accepted/integrity rule | specified | -
- `RECOVERY-001` | Phase-aware Run Log, durable checkpoints and circuit-breaker recovery | required | test_verified | -
- `RECOVERY-002` | Explicit module dependency boundaries and failure isolation | required | test_verified | -
- `BACKUP-001` | Verified provider-neutral backup and restore lifecycle | required/data-integrity | test_verified+merged-provider-readback+current-resource-scope | RECOVERY-002
- `CAL-001` | Saturday AM seven-day appointment lookahead | required | test_verified | -
- `CAL-002` | Day-before and morning-of appointment reminders | required | test_verified | -
- `CAL-003` | Configurable relative appointment reminder, default one hour before | required | test_verified | -
- `REMIND-001` | Evidence-gated medication reminders | safety-required | test_verified | -
- `REMIND-002` | Explicit opt-in caregiver reminder sharing | safety-required | test_verified | -
- `CAL-004` | Context-aware appointment visibility without fabricated confirmation state | required | partial-test/specified | -
- `MAIL-001` | Evidence-grounded important-mail triage | required | specified | -
- `MAIL-002` | Explicit per-message approval for outbound contact | safety-required | specified | -
- `MAIL-003` | Explicit archive-approval queue with repeat-on-silence | required | specified | -
- `CAREER-001` | Optional qualified job watch with realistic fit filtering | optional | specified | -
- `ORDER-001` | Evidence-grounded order and carrier correlation | required | test_verified | -
- `ORDER-002` | Canonical ordered-to-delivered fulfillment lifecycle with active dedupe | required | test_verified | -
- `ORDER-003` | Explicit cancellation, return, refund and no-settlement lifecycle | required | test_verified | -
- `ORDER-004` | Replacement and supersession without duplicate spend | required | partial-test/specified | -
- `ORDER-005` | Active-only fulfillment brief and stale-shipment escalation | required | partial-support | -
- `RECEIPT-001` | Multi-source canonical receipt intake and evidence dedupe | required | partial-test/specified | -
- `RECEIPT-002` | Searchable expandable purchase history and connected receipt graph | required | test_verified | -
- `SPEND-001` | Evidence-bounded monthly spending rollup | required | specified | -
- `RECEIPT-003` | Generic configurable receipt taxonomy and line classification | accepted/downstream prerequisite | specified | -
- `PAYMENT-001` | Expected merchant charge and settlement reconciliation | accepted/financial-integrity | test_verified | -
- `REIMB-001` | Beneficiary allocation and household reimbursement reconciliation | accepted | specified | -
- `SUB-001` | Optional subscription and free-trial tracking | proposed | not_present | -
- `FIN-001` | Complete connected financial-account ingestion and reconciliation | proposed | not_present | -
- `ASSET-001` | Immutable physical asset identity and idempotent acquisition | required | test_verified | RECEIPT-001
- `FITMENT-001` | Explicit assignment, installation and fitment relationships | required | test_verified | ASSET-001
- `ASSET-002` | Provenance-linked asset acquisition, reference and lifecycle evidence | accepted/required-direction | partial-test/specified | ASSET-001,RECEIPT-001
- `ASSET-003` | Bidirectional receipt, asset and identifier graph queries | required | test_verified | ASSET-001,FITMENT-001,RECEIPT-001,IDENT-001
- `IDENT-001` | Namespaced product and device identifiers with collision safety | required | test_verified | ASSET-001
- `EVID-001` | Multi-source asset evidence enrichment without identity replacement | required | test_verified | ASSET-001,IDENT-001,RECOVERY-002
- `KNOW-001` | Canonical durable Knowledge source identity and retained-source lifecycle | required | test_verified+scope-refined | RECOVERY-002
- `KNOW-002` | Provenance-bound knowledge excerpts and derived facts | required/accepted | specified/not_present | KNOW-001,RECOVERY-002
- `SPEC-001` | Provenance-locked technical specifications with exact applicability | required | test_verified | ASSET-001,KNOW-001,EVID-001
- `SHOP-001` | Active shopping intent distinct from durable purchase history | accepted | test_verified+merged-provider-readback | RECEIPT-001,FITMENT-001
- `INV-001` | Inventory participation reuses canonical Entity UUID identity | accepted | test_verified | ASSET-001
- `LOC-001` | Hierarchical locations with intended placement separate from observed/last-moved state | required | test_verified | INV-001
- `MOVE-001` | QR/barcode-driven inventory movement with explicit event/readback semantics | accepted/required-direction | test_verified+merged-provider-readback | INV-001,IDENT-001,LOC-001
- `INV-002` | Queryable household, loft and shop inventory projection | required | test_verified+merged-provider-readback | INV-001,LOC-001,IDENT-001,ASSET-003
- `PAR-001` | Target/par quantity with opt-in under-level notification | accepted | specified | INV-001
- `PAR-002` | Optional scale-based passive stock sensing | optional/proposed | not_present | PAR-001
- `GROCERY-001` | Grocery list, pantry and freezer stock reconciliation | accepted | test_verified+merged-provider-readback | SHOP-001,INV-001,LOC-001,RECEIPT-001
- `RECIPE-001` | Durable recipe library with structured ingredients and provenance | required | specified | KNOW-001
- `MEAL-001` | Dated meal planning with pantry-aware ingredient-gap and shopping reconciliation | required | specified | RECIPE-001,GROCERY-001,SHOP-001
- `ONBOARD-002` | Sanitized generic starter with no inherited personal production state | required/privacy | test_verified | DATA-001
- `ONBOARD-003` | Four-question Minimum Useful Setup with resumable bounded interview: (1) authoritative IANA timezone, (2) broad life/work/study/caregiving pattern, (3) biggest remembering/organizing/deciding/planning/follow-through goals, and (4) whether appointment help is wanted plus preferred Calendar provider/auto-sync intent; the fixed MIRA product name is never asked. Immediately after question four, MIRA offers a simple choice to continue setup now or start using MIRA; either path preserves the completed Minimum Useful Setup and never forces deeper discovery before use | required | implemented/specified+requirement-refined | ONBOARD-002
- `ONBOARD-004` | Progressive capability, friction, AI-use, work-context and optional life-domain discovery without silent activation: after Minimum Useful Setup the user may continue immediately or use a bounded brief drip of at most one unanswered discovery topic per local day for up to seven topic-days, with explicit opt-out and no inference from silence. Early discovery includes optional fitness/activity/nutrition/weight-goal help with a goals follow-up when accepted, then other already-canonical domains such as meals/groceries, household/routines, education/study, receipts/assets/inventory, travel/work tracking and optional wearables/local integrations | required | partial-test/specified | ONBOARD-003,SERVICE-001,CTX-002
- `ONBOARD-005` | Explicit new-user brief cadence and canonical IANA timezone configuration | required | partial-test/specified | ONBOARD-003,SERVICE-001,OPS-001,OPS-003
- `SERVICE-001` | Explicit finite service activation state separate from capability and recommendation | required | test_verified | -
- `PROFILE-001` | Composable working and self-employed roles with evidence-gated work-context routing | accepted | implemented/partial-test | ONBOARD-004,SERVICE-001,CTX-002
- `PROFILE-002` | Retired role distinct from nonworking with respectful, opt-in support | required | test_verified | SERVICE-001,REMIND-001,REMIND-002,CTX-002
- `PROFILE-003` | Nonworking/between-jobs role distinct from retirement | accepted | implemented/partial-test | SERVICE-001,ONBOARD-004
- `PROFILE-004` | Parent/guardian as a first-class composable role with permission-scoped recommendations | required | test_verified | SERVICE-001
- `PROFILE-005` | Dependent-minor role with primary routing and explicit privacy/permission gates | accepted-direction | test_verified | SERVICE-001,CTX-002
- `PROFILE-006` | Caregiver role with explicit health and sharing boundaries | accepted-direction | implemented | SERVICE-001,REMIND-001,REMIND-002
- `PROFILE-007` | Household-manager role with explicit routine ownership and consolidated delivery | accepted-direction | test_verified | SERVICE-001,TASK-001
- `PROFILE-008` | Student role with explicit HOME/CAMPUS context option | accepted | implemented/partial-test | SERVICE-001,CTX-001,CTX-002,PROFILE-005
- `PROFILE-009` | Mixed/custom role composition preserves underlying roles and explicit primary routing | required | test_verified | SERVICE-001
- `PROFILE-010` | Preference-driven usability and accessibility without demographic inference | accepted-direction | partial-test/specified | SERVICE-001
- `PROFILE-011` | Public “Boomer mode” is rejected; private user-chosen alias remains presentation-only | rejected/public; private-alias accepted | rejected+alias-partial-test | PROFILE-010,ONBOARD-002
- `PROFILE-012` | Canonical per-person identity and explicit relationship graph | accepted | specified | -
- `PROFILE-013` | Explicit permission and sharing scopes separate from relationship labels | required/privacy-critical | specified | PROFILE-012
- `DIST-001` | Private deployment lineage and controlled upstream feature sharing | required | partial-test/specified | ONBOARD-002
- `DIST-002` | Deterministic sanitized starter/distribution from one canonical source revision | required/release | test_verified | ONBOARD-002
- `DEV-004` | Bounded private custom skill/feature creation with declared contracts | accepted-direction | partial-test/specified | DEV-001,DEV-002,DIST-001
- `STUDIO-001` | Integrated MIRA Studio: a guided user-facing surface for continuously improving MIRA through bounded custom features/workflows/preferences with declared contracts, preview/test/rollback, source provenance and optional sanitized sharing of improvements with other users without silently activating imported behavior | required-direction | specified | DEV-004,DIST-001,DEV-005
- `ONBOARD-006` | Browser-only nontechnical installation with no terminal fallback | required | test_verified | DIST-002,ONBOARD-002,SOURCE-001
- `SOURCE-001` | Independent source read, source write and remote-readback capability gates | required | test_verified | DIST-001,DEV-004
- `PROVIDER-001` | Provider-neutral AI runtime capability routing from observed evidence | required | test_verified | SOURCE-001
- `SOURCE-002` | Explicit personal Git, organization Git, managed-central and no-Git/manual source lanes | required | test_verified | SOURCE-001,PROVIDER-001,DIST-002
- `PROVIDER-002` | Browser-only ordinary-user provider onboarding with host/provider-native Connect flow, an obvious Connections surface when the client can render one, automated post-consent discovery/binding/verification, no avoidable technical setup, and exact resource readback | required | test_verified+requirement-refined | ONBOARD-006,PROVIDER-001
- `ONBOARD-007` | Installable provider-neutral MIRA orchestration skill | required | implemented/test_verified | ONBOARD-002,ONBOARD-006,SOURCE-001,PROVIDER-001
- `PROVIDER-003` | Deterministic Personal Google bootstrap adapter with strict drift/readback verification | required | test_verified | ONBOARD-007,PROVIDER-002,SOURCE-001,ONBOARD-005,OPS-003
- `PROVIDER-004` | Context-aware integration discovery and recommendation: onboarding asks what tools and services the user already uses with examples selected from explicit work/lifestyle/goals and currently available provider capabilities; later provenance-bound evidence from already-authorized sources may generate deduplicated, rate-limited recommendations with Connect/Learn more, Not now, and Don't suggest this again. Recommendations never silently install, authorize, activate, migrate, or change canonical authority; finance, health, identity, and other sensitive connections require explicit scoped intent plus benefit/data-access disclosure before authorization | required-direction | specified | ONBOARD-004,PROVIDER-002,SERVICE-001,PROVIDER-001
- `ENTERPRISE-001` | Policy-compliant managed and regulated deployment lane with synthetic-first evaluation, exact organization approval/data-classification gates, managed source/provider resources and no personal-account workarounds | required-direction | specified+legacy-test-supported-boundary | ONBOARD-006,PROVIDER-001,PROVIDER-002,SOURCE-002,DIST-002,PROFILE-013
- `SERVICE-002` | Activatable service bundles over canonical behaviors with dependency-derived readiness | required | test_verified | SERVICE-001,RECOVERY-002,PROVIDER-001
- `CAL-005` | Evidence-safe appointment and provider identity reconciliation, including durable provider identity plus normalized organization/contact and specialty/type attributes such as cardiologist for human-friendly reminders | required | test_verified+merged+personal-starter-wired | -
- `CAL-008` | Multi-source appointment evidence intake from inbound email, user-supplied image/photo or user text with provenance-bound extraction of date/time/timezone/location/provider/provider specialty-or-type/contact details, confidence/ambiguity handling, dedupe and canonical appointment/provider reconciliation | required | specified | CAL-005,RECOVERY-002
- `CAL-006` | Idempotent preferred-Calendar projection/sync/update with exact provider readback; the product must support the user's selected Google, Microsoft/Outlook/M365 or Apple/iCloud Calendar lane through verified provider capability rather than silently substituting another Calendar | required | specified+requirement-refined | CAL-005,RECOVERY-002
- `HEALTH-001` | Non-clinical administrative health organization | accepted-direction | specified | PROFILE-013,CAL-005,REMIND-001,REMIND-002
- `ROUTINE-001` | Recurring and staged routine definition plus occurrence lifecycle | required | specified+tested-boundary | TASK-001,TASK-002
- `REMIND-003` | Consolidated routine and stage reminder planning/projection | required | specified+tested-boundary | ROUTINE-001,RECOVERY-002
- `WEARABLE-001` | Optional activity and wearable data ingestion with explicit authorization, capability/provenance evidence and no dependency from core routine or fitness truth | optional/proposed | not_present | -
- `EDU-001` | Durable education track, academic-work and deadline identity | required | specified | TASK-001,TASK-002,ROUTINE-001,CAL-007
- `CAL-007` | Generic source-linked Calendar projection with stable identity and provider readback | accepted/required-direction | implemented+test_verified+candidate_unmerged+synthetic-readback | RECOVERY-002,PROFILE-013

## Category-F service mappings

- F1 Briefs/action digest | briefs,OPS-001,OPS-003,OPS-004,RECOVERY-001,RECOVERY-002,SERVICE-001,SERVICE-002,f-01 | repair
- F2 Next-action planner | next_actions,TASK-001,TASK-002,SERVICE-001,SERVICE-002,f-02 | -
- F3 Email triage | email_triage,MAIL-001,MAIL-002,MAIL-003,SERVICE-001,SERVICE-002,f-03 | -
- F4 Orders/shipments | orders_shipments,ORDER-001,ORDER-002,ORDER-003,ORDER-005,SERVICE-001,SERVICE-002,f-04 | repair
- F5 Receipt archive | receipt_archive,RECEIPT-001,RECEIPT-002,RECEIPT-003,SERVICE-001,SERVICE-002,f-05 | -
- F6 Personal finance organization | finance,SERVICE-001,SERVICE-002,SPEND-001,PAYMENT-001,REIMB-001,SUB-001,FIN-001 | repair
- F7 Appointments/calendar/reminders | appointments_calendar,CAL-008,CAL-005,CAL-006,CAL-007,CAL-004,appointment_reminders,CAL-002,CAL-003,CAL-001 | repair+multisource-intake
- F8 Administrative health organization | health_organization,HEALTH-001,SERVICE-001,SERVICE-002,medication_reminders,REMIND-001,REMIND-002 | repair
- F9 Shopping/procurement | shopping,SHOP-001,SERVICE-001,SERVICE-002,f-09 | confirmed
- F10 Recipes/meals/groceries | recipes_meals,SERVICE-001,SERVICE-002,RECIPE-001,MEAL-001,GROCERY-001,SHOP-001 | selected-submodule-repair
- F11 Household/errands/admin/maintenance | household_admin,TASK-001,TASK-002,SERVICE-001,SERVICE-002,ASSET-002,SPEC-001 | confirmed
- F12 Laundry stages and drop-off/pickup reminders | household_routines,TASK-001,TASK-002,ROUTINE-001,REMIND-003,household_routines_enabled,household_admin | repair
- F13 Routines/fitness/accountability | routines_fitness,ROUTINE-001,TASK-001,TASK-002,SERVICE-001,SERVICE-002,REMIND-003 | repair
- F14 Education/study/deadlines/offline road preparation | education,SERVICE-001,SERVICE-002,EDU-001,TASK-001,TASK-002,ROUTINE-001,REMIND-003,CAL-007 | repair
- F15 Parent/child school coordination | family_school,SERVICE-001,SERVICE-002,EDU-001,PROFILE-012,PROFILE-013,PROFILE-004,PROFILE-005,CAL-007 | repair
- F16 Travel/vacation/outdoor planning | travel_planning,SERVICE-001,SERVICE-002,TRIP-001,ROUTE-001,TASK-001,TASK-002,CAL-007,WEATHER-001 | confirmed
- F17 Work-trip/route/paid-work tracking | work_trip_tracking,TRIP-001,ROUTE-001,MILE-001,MILE-002 | multi-leg-gap
- F18 Assets/maintenance/warranties/manuals | assets,SERVICE-001,SERVICE-002,ASSET-001,ASSET-003,FITMENT-001,IDENT-001,EVID-001,ASSET-002,KNOW-001,SPEC-001 | selected-path-repair
- F19 Personal knowledge/reference library | knowledge,SERVICE-001,SERVICE-002,KNOW-001,KNOW-002,f-19,g-17,g-18 | provider-projection-repair
- F20 Backup/disaster recovery | recovery,SERVICE-001,SERVICE-002,BACKUP-001,f-20,g-16 | new-canonical-backup-core
- F21 Custom skill/automation builder | STUDIO-001,DEV-004,SKILL-BUILDER-001,FEATURE-SHARE-001,DIST-001,f-21 | integrated-studio-direction
- F22 Activity trackers/wearable data | WEARABLE-001,f-22 | optional-later
- F23 Weather-in-briefs onboarding/preferences | WEATHER-001,WEATHER-002,ONBOARD-004,ONBOARD-005,SERVICE-001,f-23 | generic-onboarding-hardening

## Category-G foundation mappings

- G1 Canonical mutable authority foundation | AUTH-001,STORE-001,DEV-001,SOURCE-001,g-01 | provider-neutral-repair
- G2 Google Workspace and Microsoft 365 state/evidence portability | STORE-001,PROVIDER-001,PROVIDER-002,SOURCE-002,CAL-007,g-02 | covered-by-provider-adapters
- G3 Apple/iCloud and portable-file manual bridge | PROVIDER-002,SOURCE-002,STORE-001,CAL-007,g-03 | manual-lane-no-fabricated-automation
- G4 Locked-down and regulated enterprise/VA deployment lane | ENTERPRISE-001,ONBOARD-006,PROVIDER-001,PROVIDER-002,SOURCE-002,DIST-002,PROFILE-013,g-04 | managed-regulated-boundary
- G5 Deterministic Personal/Public/Institutional release channels | DIST-001,DIST-002,SOURCE-001,g-05 | confirmed-distribution-boundary
- G6 Eventual PostgreSQL/private SQL canonical service | STORE-001,AUTH-001,API-001,g-06 | backend-adapter-choice-not-product-authority
- G7 Policy/data API foundation | API-001,AUTH-001,STORE-001,RECOVERY-002,g-07 | shared-client-prerequisite; PROFILE-013 conditional for cross-person/shared resources
- G8 Operational observability/Grafana dashboards | OBS-001,AUTH-001,RECOVERY-002,g-08 | optional-read-only-projection
- G9 Object storage/NAS evidence and attachments | STORE-001,g-09 | evidence-adapter-choice
- G10 Android/mobile client boundary | CLIENT-ANDROID-001,API-001,RECOVERY-002,g-10 | native-client-repair; PROFILE-013 conditional for cross-person/shared resources
- G11 Home Assistant bridge | LOCAL-001,g-11 | later-local-adapter
- G12 Plex bridge | LOCAL-001,g-12 | later-local-adapter
- G13 Voice queries/commands | VOICE-001,API-001,g-13 | later-client-surface
- G14 NAS/LAN/private-service bridge and VPN access | LOCAL-001,API-001,g-14 | later-private-bridge
- G15 Family site-to-site VPN/redundancy/failover | LOCAL-001,g-15 | deferred-external-infrastructure
- G16 Backup/restore foundation | BACKUP-001,RECOVERY-002,g-16 | provider adapters conditional
- G17 Knowledge ingestion/provenance | KNOW-001,KNOW-002,RECOVERY-002,g-17 | canonical-knowledge-core
- G18 Provider organization/search metadata projection | KNOW-001,KNOW-002,STORE-001,g-18 | noncanonical-provider-projection
- G19 Machine-readable feature catalog, work lifecycle, packet alignment and CI drift enforcement | DEV-005,DEV-007,DEV-001,DEV-003,g-19 | stable-id/generated-projection+packet-alignment+lifecycle-reconciliation
- G20 Production-code ownership inventory and anti-bloat gate | DEV-006,DEV-001,g-20 | component-ownership/language-neutral-repair

## Dependency closeout findings

- Universal feature dependencies are now acyclic on the audited graph. G0-010 removed cycles caused by `OPS-001`/`OPS-003`, `IDENT-001`/`EVID-001`, `PAR-001`/`GROCERY-001`, and `PROFILE-012`/`PROFILE-013`.
- Recipe identity no longer depends on grocery stock; par levels are optional inventory behavior rather than a prerequisite for grocery or meal planning. Selected service paths add those optional relationships when enabled.
- Same-user core API/Android behavior requires `AUTH-001`, `STORE-001`, `RECOVERY-002`, and `API-001`; `PROFILE-013` is conditional when a command/query crosses person or sharing boundaries rather than a universal prerequisite.
- AI-runtime/provider routing (`PROVIDER-001`) is deployment/onboarding capability evidence, not a universal semantic dependency of API, Android, backup, wearables, local bridges, or voice.
- Provider/backend products remain adapters. PostgreSQL, Google, Microsoft, Apple, NAS/object storage, and similar choices never become canonical authority merely by selection.
- `AUTH-001` owns exactly one canonical authority per mutable data class; `STORE-001` owns provider-neutral structured/evidence adapter contracts. Git/source, runtime mutable state, evidence, capabilities, backups, and projections remain separate roles.
- `API-001` is the authenticated client/service boundary in front of `AUTH-001`/`STORE-001`. Mutations require actor/client authentication, least-privilege authorization, compatibility/dependency preflight, stable IDs, mandatory idempotency, conflict handling, canonical write, exact readback, and audit.
- `CLIENT-ANDROID-001` is a client adapter over `API-001`, never a provider/data/source authority. Offline state is a replay queue/cache, not a second writable master.
- `DEV-005` keeps `FEATURES.md` and `BACKLOG.md` canonical and machine-readable views derived; `DEV-006` uses bounded component ownership rather than one-file/one-feature fragmentation; `DEV-007` requires packet-level feature/lifecycle alignment before implementation and merge so passing local tests cannot substitute for preserving accepted product behavior or reconciling completed work.
- `ONBOARD-003` no longer asks the assistant/product name because it is fixed as MIRA. Its fourth kickoff question explicitly offers appointment-reminder help and preferred Calendar auto-sync selection, then immediately offers continue-setup-now versus start-using-MIRA without blocking ordinary use.
- `ONBOARD-004` owns optional progressive post-setup discovery. Silence never counts as an answer; brief delivery is bounded to one discovery topic per local day for up to seven topic-days, and accepted topics feed existing canonical domains/services rather than creating parallel databases.
- `PROVIDER-002` inherits the cross-feature connection-surface invariant: provider setup is an ordinary-language/native-Connect flow with an obvious connection surface where the client controls UI, automated post-consent discovery/binding/readback, and no avoidable manual provider-resource or developer-console work. Host UI limitations may change presentation but do not export engineering work to the user.
- `CAL-008` makes email/photo/text appointment intake explicit rather than assuming `CAL-005` identity reconciliation magically includes evidence ingestion. Extracted provider specialty/type is durable canonical provider metadata so reminders can say useful things such as “cardiologist appointment” without repeatedly re-parsing source evidence.
- `STUDIO-001` is the user-facing continuous-improvement layer over bounded custom feature creation and controlled sharing. Studio may generate/reconcile private changes, but imported/shared behavior never silently activates.
- PR #31 and independent legacy productization code remain selective salvage only. Direct client-to-provider mutation, coarse authorization, dual writable masters, silent schedulers, path identity, collapsed intended/observed location, and CI-implied live/signing/device/provider claims remain rejected.

## Audit status

- Categories A-G recovered feature coverage is complete.
- G0-009 legacy reconciliation is complete.
- G0-010 final dependency graph/ranking closeout is complete.
- M2-G0-011 adds deterministic lifecycle reconciliation over the existing corpus and refines progressive onboarding; it does not restart the historical audit from zero.
