# MIRA 2.0 FEATURES

Canonical feature index. Detailed descriptions, rationale, evidence paths/tests, and verification boundaries remain durable in Git history and packet checkpoints. This index is authoritative for stable IDs, current requirement/evidence status, canonical dependencies, and audited service mappings.

## Rules

Stable semantic IDs do not change with priority/provider/backend/order. Requirement and evidence are separate; code existence is not completion.

## Feature index

`ID | Title | requirement | evidence | deps`

- `DEV-001` | Git-authoritative development control plane | governance | implemented/specified | -
- `DEV-002` | Resumable bounded work packets | governance | implemented/specified | -
- `DEV-003` | Dependency-ranked backlog | governance | implemented/specified | -
- `CORE-001` | MIRA product identity | governance | history | -
- `MIRROR-001` | Companion reality database | governance | history | -
- `DATA-001` | Legacy production preservation | governance | history | -
- `ONBOARD-001` | Full-replacement instruction delivery | governance | implemented/specified | -
- `BRAND-001` | Canonical MIRA brand asset system | governance | history | -
- `OPS-001` | Canonical twice-daily Ops Brief schedule | required | test_verified | OPS-003,OPS-004
- `OPS-002` | Single canonical dispatcher and prohibited duplicate schedules | required | specified | OPS-001
- `OPS-003` | Canonical runtime clock gate with DST-safe slot matching | required by failure evidence | test_verified | OPS-001
- `OPS-004` | Fresh standalone run delivery with deterministic Run ID | required | test_verified | OPS-003,RECOVERY-001
- `OPS-005` | Deterministic HOME/ROAD context with explicit overrides | required | test_verified | -
- `CTX-001` | Configurable operating-context pairs | accepted-direction | test_verified | -
- `CTX-002` | Evidence-gated context recommendation and explicit activation | required | test_verified | -
- `TRIP-001` | Independent trip occurrence lifecycle | required | test_verified | -
- `ROUTE-001` | Learned routes, directional runtime, location and ETA inference | required | test_verified | -
- `WEATHER-001` | Context-gated HOME and ROAD weather intelligence | required | test_verified | -
- `MILE-001` | Company-paid mileage and deterministic gross-pay reporting | required | test_verified | -
- `MILE-002` | Separate authoritative Miles & Pay tracker | required | legacy_live | -
- `TASK-001` | Structured task hierarchy and one-action-per-item rendering | required | test_verified | -
- `TASK-002` | Evidence-grounded next actions and honest completion state | accepted/integrity rule | specified | -
- `RECOVERY-001` | Phase-aware Run Log, durable checkpoints and circuit-breaker recovery | required | test_verified | -
- `RECOVERY-002` | Explicit module dependency boundaries and failure isolation | required | test_verified | -
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
- `IDENT-001` | Namespaced product and device identifiers with collision safety | required | test_verified | ASSET-001,EVID-001
- `EVID-001` | Multi-source asset evidence enrichment without identity replacement | required | test_verified | ASSET-001,IDENT-001,RECOVERY-002
- `KNOW-001` | Canonical manual/reference knowledge identity and retained-document lifecycle | required | test_verified | EVID-001,ASSET-001,RECOVERY-002
- `SPEC-001` | Provenance-locked technical specifications with exact applicability | required | test_verified | ASSET-001,KNOW-001,EVID-001
- `SHOP-001` | Active shopping intent distinct from durable purchase history | accepted | specified | RECEIPT-001,FITMENT-001
- `INV-001` | Inventory participation reuses canonical Entity UUID identity | accepted | test_verified | ASSET-001
- `LOC-001` | Hierarchical locations with intended placement separate from observed/last-moved state | required / under active design | specified | INV-001
- `MOVE-001` | QR/barcode-driven inventory movement with explicit event/readback semantics | accepted/required-direction | candidate_unmerged | INV-001,IDENT-001,LOC-001,LOCATION-STATE-001
- `INV-002` | Queryable household, loft and shop inventory projection | required | candidate_unmerged | INV-001,LOC-001,IDENT-001,ASSET-003,LOCATION-STATE-001
- `PAR-001` | Target/par quantity with opt-in under-level notification | accepted | specified | INV-001,GROCERY-001
- `PAR-002` | Optional scale-based passive stock sensing | optional/proposed | not_present | PAR-001
- `GROCERY-001` | Grocery list, pantry and freezer stock reconciliation | accepted | specified | SHOP-001,INV-001,LOC-001,PAR-001,RECEIPT-001
- `RECIPE-001` | Durable recipe library with structured ingredients and provenance | required | specified | KNOW-001,GROCERY-001
- `MEAL-001` | Dated meal planning with pantry-aware ingredient-gap and shopping reconciliation | required | specified | RECIPE-001,GROCERY-001,SHOP-001,PAR-001
- `ONBOARD-002` | Sanitized generic starter with no inherited personal production state | required/privacy | test_verified | DATA-001
- `ONBOARD-003` | Four-question Minimum Useful Setup with resumable bounded interview | required | implemented/specified | ONBOARD-002
- `ONBOARD-004` | Capability, friction, AI-use and work-context discovery without silent activation | required | partial-test/specified | ONBOARD-003,SERVICE-001,CTX-002
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
- `PROFILE-012` | Canonical per-person identity and explicit relationship graph | accepted | specified | PROFILE-013
- `PROFILE-013` | Explicit permission and sharing scopes separate from relationship labels | required/privacy-critical | specified | PROFILE-012
- `DIST-001` | Private deployment lineage and controlled upstream feature sharing | required | partial-test/specified | ONBOARD-002
- `DIST-002` | Deterministic sanitized starter/distribution from one canonical source revision | required/release | test_verified | ONBOARD-002
- `DEV-004` | Bounded private custom skill/feature creation with declared contracts | accepted-direction | partial-test/specified | DEV-001,DEV-002,DIST-001
- `ONBOARD-006` | Browser-only nontechnical installation with no terminal fallback | required | test_verified | DIST-002,ONBOARD-002,SOURCE-001
- `SOURCE-001` | Independent source read, source write and remote-readback capability gates | required | test_verified | DIST-001,DEV-004
- `PROVIDER-001` | Provider-neutral AI runtime capability routing from observed evidence | required | test_verified | SOURCE-001
- `SOURCE-002` | Explicit personal Git, organization Git, managed-central and no-Git/manual source lanes | required | test_verified | SOURCE-001,PROVIDER-001,DIST-002
- `PROVIDER-002` | Browser-only provider authority onboarding with exact resource readback | required | test_verified | ONBOARD-006,PROVIDER-001
- `ONBOARD-007` | Installable provider-neutral MIRA orchestration skill | required | implemented/test_verified | ONBOARD-002,ONBOARD-006,SOURCE-001,PROVIDER-001
- `PROVIDER-003` | Deterministic Personal Google bootstrap adapter with strict drift/readback verification | required | test_verified | ONBOARD-007,PROVIDER-002,SOURCE-001,ONBOARD-005,OPS-003
- `SERVICE-002` | Activatable service bundles over canonical behaviors with dependency-derived readiness | required | test_verified | SERVICE-001,RECOVERY-002,PROVIDER-001
- `CAL-005` | Evidence-safe appointment and provider identity reconciliation | required | partial-test | -
- `CAL-006` | Idempotent linked Calendar projection, update and exact provider readback | required | specified | CAL-005,RECOVERY-002
- `HEALTH-001` | Non-clinical administrative health organization | accepted-direction | specified | PROFILE-013,CAL-005,REMIND-001,REMIND-002
- `ROUTINE-001` | Recurring and staged routine definition plus occurrence lifecycle | required | specified+tested-boundary | TASK-001,TASK-002
- `REMIND-003` | Consolidated routine and stage reminder planning/projection | required | specified+tested-boundary | ROUTINE-001,RECOVERY-002
- `EDU-001` | Durable education track, academic-work and deadline identity | required | specified | TASK-001,TASK-002,ROUTINE-001,CAL-007
- `CAL-007` | Generic source-linked Calendar projection with stable identity and provider readback | accepted/required-direction | specified | RECOVERY-002,PROFILE-013

## Category-F service mappings

- F1 Briefs/action digest | briefs,OPS-001,OPS-003,OPS-004,RECOVERY-001,RECOVERY-002,SERVICE-001,SERVICE-002,f-01 | repair
- F2 Next-action planner | next_actions,TASK-001,TASK-002,SERVICE-001,SERVICE-002,f-02 | -
- F3 Email triage | email_triage,MAIL-001,MAIL-002,MAIL-003,SERVICE-001,SERVICE-002,f-03 | -
- F4 Orders/shipments | orders_shipments,ORDER-001,ORDER-002,ORDER-003,ORDER-005,SERVICE-001,SERVICE-002,f-04 | repair
- F5 Receipt archive | receipt_archive,RECEIPT-001,RECEIPT-002,RECEIPT-003,SERVICE-001,SERVICE-002,f-05 | -
- F6 Personal finance organization | finance,SERVICE-001,SERVICE-002,SPEND-001,PAYMENT-001,REIMB-001,SUB-001,FIN-001 | repair
- F7 Appointments/calendar/reminders | appointments_calendar,CAL-005,CAL-006,CAL-004,appointment_reminders,CAL-002,CAL-003,CAL-001 | repair
- F8 Administrative health organization | health_organization,HEALTH-001,SERVICE-001,SERVICE-002,medication_reminders,REMIND-001,REMIND-002 | repair
- F9 Shopping/procurement | shopping,SHOP-001,SERVICE-001,SERVICE-002,f-09 | confirmed
- F10 Recipes/meals/groceries | recipes_meals,SERVICE-001,SERVICE-002,RECIPE-001,MEAL-001,GROCERY-001,SHOP-001 | repair+migration
- F11 Household/errands/admin/maintenance | household_admin,TASK-001,TASK-002,SERVICE-001,SERVICE-002,ASSET-002,SPEC-001 | confirmed
- F12 Laundry stages and drop-off/pickup reminders | household_routines,TASK-001,TASK-002,ROUTINE-001,REMIND-003,household_routines_enabled,household_admin | repair
- F13 Routines/fitness/accountability | routines_fitness,ROUTINE-001,TASK-001,TASK-002,SERVICE-001,SERVICE-002,REMIND-003 | repair
- F14 Education/study/deadlines/offline road preparation | education,SERVICE-001,SERVICE-002,EDU-001,TASK-001,TASK-002,ROUTINE-001,REMIND-003,CAL-007 | repair
- F15 Parent/child school coordination | family_school,SERVICE-001,SERVICE-002,EDU-001,PROFILE-012,PROFILE-013,PROFILE-004,PROFILE-005,CAL-007 | repair
- F16 Travel/vacation/outdoor planning | travel_planning,SERVICE-001,SERVICE-002,TRIP-001,ROUTE-001,TASK-001,TASK-002,CAL-007,WEATHER-001 | confirmed
- F17 Work-trip/route/paid-work tracking | work_trip_tracking,TRIP-001,ROUTE-001,MILE-001,MILE-002 | multi-leg-gap
- F18 Assets/maintenance/warranties/manuals | assets,SERVICE-001,SERVICE-002,ASSET-001,ASSET-003,FITMENT-001,IDENT-001,EVID-001,ASSET-002,KNOW-001,SPEC-001 | selected-path-repair

## F7 integrity

- F16 `travel_planning` = `TRIP-001` + `ROUTE-001`; no `TRAVEL-*` authority.
- F17 `work_trip_tracking` adds `MILE-001` + `MILE-002` only for selected paid-work tracking.
- Ordered multi-leg grouping/revision is not implemented; `TRIP-ROUTE-CORE-001` owns the gap.
- Generic travel does not imply paid work, ROAD context, weather watch, Calendar, reservations, documents, equipment, or budgets.

## F8 integrity

- F18 service key is `assets`; no new asset, maintenance, warranty, manual or specification authority is created.
- Base asset registry/query uses `ASSET-001` + `ASSET-003`; fitment, identifier/evidence enrichment, maintenance/warranty evidence, retained manuals and verified specs are selected paths with their existing canonical authorities.
- Legacy `f-18` hard-requires D1-D7; MIRA 2.0 repairs that to selected-path readiness so missing manual/spec/fitment/warranty capability does not block basic asset use.
- `ASSET-SERVICE-001` remains the implementation gap for structured maintenance/warranty lifecycle; `KNOW-001` and `SPEC-001` retain their own provider/provenance boundaries.
- Service activation or recommendation cannot infer ownership, installation, warranty coverage, maintenance completion, retained manual state, or verified specification correctness.
- F19 is deferred because it depends on unaudited G17/G18.

## Audit status

- Categories A-E complete.
- F1-F18 audited through `M2-G0-007H`; F19 waits on G17/G18 dependency audit.
- Category G unaudited.
