# MIRA 2.0 BACKLOG

Git is authoritative. This backlog is **not FIFO**. Priority follows integrity/security, hard milestone prerequisites, architectural leverage, user-visible vertical value, release hardening, then later/optional work. Completed work remains in this file with evidence; lifecycle selection filters it rather than deleting it.

## Priority classes

1. **BLOCKER** — data integrity, privacy, security, or active acceptance blocker.
2. **PREREQUISITE** — hard dependency for higher-value work.
3. **VERTICAL** — user-visible end-to-end proof for an active milestone.
4. **HARDENING** — reliability, testing, release, migration, observability, recovery.
5. **ENHANCEMENT** — useful but not required for the active proof.
6. **LATER** — valid direction intentionally outside the active milestone.

## Audit / governance work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `AUDIT-A` | PREREQUISITE | Brief/time/tasking/operational-state reconstruction. | G0-001 | complete |
| `AUDIT-B` | PREREQUISITE | Calendar/reminders/mail/communication safety. | AUDIT-A | complete |
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | complete through `M2-G0-004C` |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence/food planning. | AUDIT-C | complete through `M2-G0-005D` |
| `AUDIT-D1` | PREREQUISITE | D rows 1-5. | AUDIT-C | complete in `M2-G0-005A` |
| `AUDIT-D2` | PREREQUISITE | D rows 6-10. | AUDIT-D1 | complete in `M2-G0-005B` |
| `AUDIT-D3` | PREREQUISITE | D rows 11-15. | AUDIT-D2 | complete in `M2-G0-005C` |
| `AUDIT-D4` | PREREQUISITE | D row 16 / category-D closure. | AUDIT-D3 | complete in `M2-G0-005D` |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | complete through `M2-G0-006F` |
| `AUDIT-E1` | PREREQUISITE | E rows 1-5. | AUDIT-D | complete in `M2-G0-006A` |
| `AUDIT-E2` | PREREQUISITE | E rows 6-10. | AUDIT-E1 | complete in `M2-G0-006B` |
| `AUDIT-E3` | PREREQUISITE | E rows 11-15. | AUDIT-E2 | complete in `M2-G0-006C` |
| `AUDIT-E4` | PREREQUISITE | E rows 16-20. | AUDIT-E3 | complete in `M2-G0-006D` |
| `AUDIT-E5` | PREREQUISITE | E rows 21-24. | AUDIT-E4 | complete in `M2-G0-006E` |
| `AUDIT-E6` | PREREQUISITE | E rows 25-26 / category-E closure. | AUDIT-E5 | complete in `M2-G0-006F` |
| `AUDIT-F` | PREREQUISITE | Life-service composition and service-specific dependency audit. | AUDIT-E | complete through `M2-G0-008G` |
| `AUDIT-F1` | PREREQUISITE | F1-F5. | AUDIT-E | complete in `M2-G0-007A` |
| `AUDIT-F2` | PREREQUISITE | F6-F8. | AUDIT-F1 | complete in `M2-G0-007B` |
| `AUDIT-F3` | PREREQUISITE | F9-F10. | AUDIT-F2 | complete in `M2-G0-007C` |
| `AUDIT-F4` | PREREQUISITE | F11-F12. | AUDIT-F3 | complete in `M2-G0-007D` |
| `AUDIT-F5` | PREREQUISITE | F13-F14. | AUDIT-F4 | complete in `M2-G0-007E` |
| `AUDIT-F6` | PREREQUISITE | F15. | AUDIT-F5 | complete in `M2-G0-007F` |
| `AUDIT-F7` | PREREQUISITE | F16-F17. | AUDIT-F6 | complete in `M2-G0-007G` |
| `AUDIT-F8` | PREREQUISITE | F18. | AUDIT-F7 | complete in `M2-G0-007H` |
| `AUDIT-G16-F20` | PREREQUISITE | G16 backup/restore + F20 recovery service. | AUDIT-F8 | complete in `M2-G0-008A` |
| `AUDIT-G17-G18-F19` | PREREQUISITE | G17/G18 knowledge + F19 knowledge service. | AUDIT-G16-F20 | complete in `M2-G0-008B` |
| `AUDIT-G1` | PREREQUISITE | Canonical authority/store foundation. | AUDIT-G17-G18-F19 | complete in `M2-G0-008C` |
| `AUDIT-G7` | PREREQUISITE | Shared policy/data API foundation. | AUDIT-G1 | complete in `M2-G0-008D` |
| `AUDIT-G10` | PREREQUISITE | Android/mobile client boundary. | AUDIT-G7 | complete in `M2-G0-008E` |
| `AUDIT-G19-G20` | PREREQUISITE | Machine-readable feature projection + component ownership integrity. | DEV-001,DEV-003 | complete in `M2-G0-008F` |
| `AUDIT-F21-F23-G2-G15` | PREREQUISITE | Remaining recovered F/G ledger closeout. | AUDIT-G19-G20 | complete in `M2-G0-008G` |
| `AUDIT-G` | PREREQUISITE | Recovered category-G coverage. | AUDIT-F | complete through `M2-G0-008G` |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 and meaningful legacy branches/repos. | audits A-G | complete in `M2-G0-009` |
| `DEP-GRAPH` | PREREQUISITE | Final acyclic feature/work dependency graph, dedupe/supersession map, ranked implementation waves, and first implementation packet selection. | completed forensic registry,DEV-005 | complete in `M2-G0-010`; no implementation prerequisite |

## Ranked M2-M0 / M2-M1 critical path

These waves preserve the shared-state Android path, but ordinary no-app Personal usefulness remains the current priority override until a real user-facing vertical exists.

### Wave 1 — synthetic canonical-state foundation

| Rank | Work ID | Class | Work | Dependencies | Status |
|---:|---|---|---|---|---|
| 1 | `STORE-ADAPTER-001` | PREREQUISITE | Umbrella implementation of `STORE-001`; split into bounded structured-state and evidence-store packets rather than one mega-packet. | STORE-001,RECOVERY-002 | split; children below |
| 1a | `STORE-ADAPTER-001A` | PREREQUISITE | **First implementation packet:** provider-neutral structured-state interface plus deterministic in-memory synthetic adapter; health/schema, exact read, bounded query, idempotent upsert, append event, revision/readback, audit-friendly errors. No network/provider/evidence-store work. | STORE-001,RECOVERY-002 | complete; merged/test-verified |
| 1b | `STORE-ADAPTER-001B` | PREREQUISITE | Provider-neutral evidence-store interface plus synthetic hash-preserving evidence put/read/metadata/retention/export/readback. | STORE-001,RECOVERY-002,STORE-ADAPTER-001A | queued; not required for minimal entity roundtrip |
| 2 | `AUTHORITY-REGISTRY-001` | PREREQUISITE | Persistent `AUTH-001` registry and exact data-class routing using registered adapters; one active canonical authority per mutable class, no direct client/model authority mutation. | AUTH-001,RECOVERY-002,STORE-ADAPTER-001A | complete in `M2-M0-003`; persisted routing provider-readback verified |
| 3 | `API-CORE-001` | BLOCKER | Shared `API-001` runtime with actor/client authentication, same-user resource/action authorization, mandatory idempotency/API-schema preflight, conflict handling, audit, canonical write and exact readback through Authority Registry/structured adapter. Cross-person commands fail closed until `PERMISSION-SCOPE-001`. | API-001,AUTH-001,STORE-001,RECOVERY-002,AUTHORITY-REGISTRY-001,STORE-ADAPTER-001A | complete; merged/test-verified same-user API core |
| 4 | `CORE-SYNETIC-ROUNDTRIP` | PREREQUISITE | Create/read/mutate/replay/read-back one canonical synthetic entity through `API-CORE-001`; prove conflict/idempotency/readback without external provider state. | API-CORE-001,AUTHORITY-REGISTRY-001,STORE-ADAPTER-001A | complete; merged/test-verified |

### Wave 1.5 — repository growth gates

| Rank | Work ID | Class | Work | Dependencies | Status |
|---:|---|---|---|---|---|
| 5 | `FEATURE-REGISTRY-001` | PREREQUISITE | Implement `DEV-005` parser/generator/drift gate from canonical `FEATURES.md`; authored semantic IDs only. | DEV-005,DEV-001,DEV-003 | complete; CI-enforced |
| 6 | `CODE-OWNERSHIP-001` | PREREQUISITE | Implement `DEV-006` component ownership/direct-evidence manifest and central unowned/overlap gate; language-specific static rules remain profiles. | DEV-006,DEV-001 | complete; CI-enforced |
| 6a | `FEATURE-ALIGN-001` | HARDENING | Implement `DEV-007` packet-to-feature alignment and product-lifecycle verification, including generated feature/work projection, completed-work filtering and session-start/session-end authority checks. | DEV-007,DEV-005,DEV-002,DEV-003 | complete in PR #61 at `c776db72d4f3a0e37b0be5004ac1a15141df14e8`; lifecycle projection, stale-status reconciliation and CI/session alignment verified |

### Wave 2 — Google Workspace-first stock ChatGPT proof (M2-M0)

| Rank | Work ID | Class | Work | Dependencies | Status |
|---:|---|---|---|---|---|
| 7 | `DATA-SANDBOX` | PREREQUISITE | Create an isolated MIRA 2.0 Google/MIRROR development namespace with synthetic data only; inventory/read back exact resources and prove legacy production untouched. Full Personal Google service fan-out remains out of scope. | DATA-001,AUTHORITY-REGISTRY-001 | complete; isolated synthetic Google namespace provider-readback verified |
| 8 | `GOOGLE-STORE-ADAPTER-001` | PREREQUISITE | Implement the minimal Google structured-state adapter needed for the first canonical entity proof against `DATA-SANDBOX`; exact identity/schema/read/write/readback, no Gmail/Calendar/scheduler fan-out. | STORE-ADAPTER-001A,AUTHORITY-REGISTRY-001,DATA-SANDBOX | complete in `M2-M0-002`; adapter test-verified + provider readback |
| 9 | `API-DEPLOYMENT-001` | PREREQUISITE | Umbrella ordinary-user deployment/runtime proof. Personal baseline must require no self-hosted server or terminal; stronger managed/self-hosted execution remains available for multi-client or advanced profiles without changing Authority/store semantics. | API-CORE-001,CORE-SYNTHETIC-ROUNDTRIP | split; Personal `001A` core proof complete, advanced `001B` preserved |
| 9a | `API-DEPLOYMENT-001A` | PREREQUISITE | **Default Personal first-run:** clean copyable Google Workspace starter with Sheets as initial structured MIRROR authority; stock ChatGPT uses the official authenticated same-user Google Drive/Sheets connection and deterministic native protocol. Bound Apps Script is optional embedded Google-side initialization/validation/automation, not the required public API gateway. Browser-only; no Cloud Run/Linux/SQL/terminal/tunnel/paid OpenAI API prerequisite. | API-CORE-001,CORE-SYNTHETIC-ROUNDTRIP,GOOGLE-STORE-ADAPTER-001,DATA-SANDBOX,ONBOARD-002 | complete for M2-M0 in `M2-M0-006`; PRs #50/#51/#52 green; clean-copy bootstrap + live provider roundtrip verified |
| 9b | `API-DEPLOYMENT-001B` | HARDENING | Advanced Cloud Run deployment profile with dedicated runtime/build identities, Secret Manager bearer, single-writer scaling/concurrency invariants, HTTPS/provider/restart proof. Valid for users/institutions that need managed infrastructure; not required for the Personal baseline. | API-CORE-001,CORE-SYNTHETIC-ROUNDTRIP | paused; code/readiness/operator merged in PRs #48/#49, live provider proof checkpoint `c392b9b829fab989be8856c9272294c9907e409e` preserved |
| 10 | `CHATGPT-API-CLIENT-001` | PREREQUISITE | Prove stock ChatGPT's supported Personal client path using its official same-user Google Drive/Sheets authorization boundary while preserving MIRA Authority, revision, idempotency and exact-readback semantics through a deterministic native connector protocol. This proof is single-writer only and does not authorize concurrent Android mutation. | API-DEPLOYMENT-001A | complete in `M2-M0-006`; live synthetic + clean-copy provider proof, protocol PR #51 green/merged |
| 11 | `CORE-ROUNDTRIP` | VERTICAL | **M2-M0:** stock ChatGPT bootstraps a clean copied Workspace starter, then create/read/replay/mutate/read-back one Google-backed canonical MIRROR entity through the Personal native Google path with exact provider verification. | CORE-SYNTHETIC-ROUNDTRIP,DATA-SANDBOX,GOOGLE-STORE-ADAPTER-001,API-DEPLOYMENT-001A,CHATGPT-API-CLIENT-001 | complete in `M2-M0-006`; clean-copy live proof + merged deterministic protocol/bootstrap |

### Wave 3 — Android shared-state proof (M2-M1)

| Rank | Work ID | Class | Work | Dependencies | Status |
|---:|---|---|---|---|---|
| 12a | `ANDROID-COMMAND-BOUNDARY-001` | PREREQUISITE | Stronger shared canonical mutation seam: provider-neutral serialized command contract plus Google Workspace `Commands` inbox/time-driven `ScriptLock` worker, replay/revision/crash recovery, and direct-native mutation guard when queued mode activates. | CLIENT-ANDROID-001,API-CORE-001,CORE-ROUNDTRIP | partial; synthetic implementation/test proof complete in PRs #54/#55, **live isolated Google worker proof pending** |
| 12 | `ANDROID-CLIENT-CORE-001` | PREREQUISITE | MIRA 2.0 Android shared client: use the verified concurrent execution boundary, preserve API compatibility, enrollment/session identity, revocation, OS-protected credentials, bounded reads, canonical commands, replay-safe offline queue, reconnect/cursor sync and server conflict/readback handling. | CLIENT-ANDROID-001,API-CORE-001,CORE-ROUNDTRIP,ANDROID-COMMAND-BOUNDARY-001 | queued immediately after live command-boundary proof; no Android UI implementation yet |
| 13 | `ANDROID-SYNC` | VERTICAL | **M2-M1:** Android reads/mutates the exact M2-M0 canonical entity through the stronger shared execution boundary; stock ChatGPT reads the Android mutation back from the same authority. | CORE-ROUNDTRIP,ANDROID-CLIENT-CORE-001 | provisional target |
| 14 | `ANDROID-NATIVE-DELIVERY-001` | HARDENING | Android visual notification + opt-in TTS over canonical reminder intents with replay suppression, timing/privacy truth and representative-device evidence. | ANDROID-CLIENT-CORE-001, canonical reminder semantics | queued |
| 15 | `ANDROID-CAPTURE-001` | HARDENING | Camera/barcode/QR/NFC/BLE capture as nonauthoritative API observations; passive reads never silently move assets. Appointment-photo capture will use the same Android evidence-capture surface but routes through `CAL-008`, not inventory semantics. | ANDROID-CLIENT-CORE-001,API-001,EVID-001,IDENT-001 | queued |
| 16 | `ANDROID-RELEASE-001` | HARDENING | Reproducible debug/release build, permanent signing identity outside Git, APK/AAB signature/version provenance and representative-device smoke evidence. | ANDROID-CLIENT-CORE-001, distribution/release policy | queued |

## Other preserved implementation work

These rows remain valid and dependency-ranked below the active M2-M0/M2-M1 path unless selected capability work becomes a hard dependency.

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `WEATHER-ONBOARD-001` | HARDENING | Implement `WEATHER-002` explicit slot/location/units/detail/severe-alert preferences with failure isolation. | WEATHER-002,WEATHER-001,ONBOARD-004,ONBOARD-005,SERVICE-001 | queued |
| `WEARABLE-ADAPTER-001` | LATER | Optional authorized wearable/activity adapters with provenance/capability/readback honesty. | WEARABLE-001 | deferred optional |
| `OBSERVABILITY-001` | HARDENING | Read-only operational telemetry/dashboard projection. | OBS-001,AUTH-001,RECOVERY-002,core runtime | queued after core |
| `VOICE-CLIENT-001` | LATER | Optional voice query and command surface over shared API with consequential-action confirmation. | VOICE-001,API-CORE-001 | deferred |
| `SERVICE-COMPOSE-001` | PREREQUISITE | Port/prove service composition/readiness with activation separate from readiness. | SERVICE-001,SERVICE-002,canonical dependency registry,RUNTIME-ROUTER-001 | queued |
| `SERVICE-DEPS-001` | PREREQUISITE | F1 Briefs/Orders dependency repair. | SERVICE-002,OPS-002,ORDER-004,dependency registry | queued |
| `SERVICE-DEPS-002` | PREREQUISITE | F2 finance/calendar/health selected-goal readiness. | SERVICE-002,CAL-005,CAL-006,CAL-008,HEALTH-001,category-C finance features | queued |
| `SERVICE-DEPS-003` | PREREQUISITE | F3 shopping/recipe/meal/grocery selected-submodule readiness. | SERVICE-002,SHOP-001,GROCERY-001,RECIPE-001,MEAL-001 | queued |
| `SERVICE-DEPS-004` | PREREQUISITE | F4 household/routine readiness and anti-fan-out. | SERVICE-002,TASK-001,TASK-002,ROUTINE-001,REMIND-003 | queued |
| `SERVICE-DEPS-005` | PREREQUISITE | F5 routines/fitness/education; wearable/Calendar/offline paths optional. | SERVICE-002,ROUTINE-001,TASK-001,TASK-002,REMIND-003,EDU-001,CAL-007 | queued |
| `SERVICE-DEPS-006` | PREREQUISITE | F6 family-school readiness around exact actor/subject/scope. | SERVICE-001,SERVICE-002,EDU-001,PROFILE-012,PROFILE-013 | queued |
| `SERVICE-DEPS-007` | PREREQUISITE | F7 travel/work-trip bundles and paid-mileage separation. | SERVICE-001,SERVICE-002,TRIP-001,ROUTE-001,MILE-001,MILE-002 | queued |
| `SERVICE-DEPS-008` | PREREQUISITE | F8 assets selected-path readiness. | SERVICE-001,SERVICE-002,ASSET-001,ASSET-003 | queued |
| `SERVICE-DEPS-009` | PREREQUISITE | F20 recovery readiness around verified backup/restore state. | SERVICE-001,SERVICE-002,BACKUP-001 | queued |
| `SERVICE-DEPS-010` | PREREQUISITE | F19 knowledge readiness around canonical knowledge + optional provider projection. | SERVICE-002,KNOW-001,KNOW-002 | queued |
| `AUTHORITY-MIGRATION-001` | PREREQUISITE | Staged provider/backend cutover without dual writable masters; parity/readback/recovery/rollback. This is the protected upgrade path from the default Google Workspace backend to Linux/SQL/managed backends. | AUTH-001,STORE-001,BACKUP-001,AUTHORITY-REGISTRY-001,STORE-ADAPTER-001A | queued; portability invariant applies from Personal baseline onward |
| `BACKUP-CORE-001` | PREREQUISITE | Implement `BACKUP-001` backup/restore lifecycle and independent restore verification. | BACKUP-001,RECOVERY-002,STORE-ADAPTER-001A | queued; PR31 partial candidate only |
| `KNOWLEDGE-CORE-001` | PREREQUISITE | Provider-neutral general Knowledge source identity and typed relationships. | KNOW-001,RECOVERY-002,canonical identity/relationship model | queued |
| `KNOWLEDGE-PROVENANCE-001` | PREREQUISITE | `KNOW-002` excerpt/derived-fact provenance lifecycle. | KNOW-002,KNOW-001,RECOVERY-002 | queued |
| `KNOWLEDGE-PROJECTION-001` | HARDENING | Provider organization/search projection with exact readback and no path identity. | KNOW-001,KNOW-002,selected evidence provider | queued |
| `TRIP-ROUTE-CORE-001` | PREREQUISITE | Canonical Trip/Route state and optional ordered multi-leg grouping. | TRIP-001,ROUTE-001,RECOVERY-002,canonical time/state semantics | queued |
| `ROUTINE-CORE-001` | PREREQUISITE | Recurring/staged routine definition and occurrence lifecycle. | TASK-001,TASK-002,canonical Person/time semantics | queued |
| `ROUTINE-REMINDER-001` | PREREQUISITE | Consolidated routine/stage/accountability reminder planning/projection. | ROUTINE-001,RECOVERY-002,canonical time semantics,verified delivery adapters | queued |
| `APPOINTMENT-IDENTITY-001` | PREREQUISITE | Appointment/provider identity reconciliation with normalized provider organization/contact and specialty/type metadata so reminders use durable semantics such as “cardiologist appointment” rather than source-text fragments. | CAL-005,canonical appointment/source identity,evidence/provenance | queued |
| `APPOINTMENT-INTAKE-001` | VERTICAL | Evidence-first appointment capture from inbound email, user-supplied photo/image, or user text. Detect appointment intent; extract date/time/timezone/location/provider/contact/specialty-type with provenance/confidence; reconcile provider + appointment identities; ask only when materially ambiguous; dedupe repeated source evidence; after explicit service/calendar opt-in, project/update the preferred Calendar. Outbound emailing to negotiate/schedule with a provider is **not** implied and remains subject to `MAIL-002`. | CAL-008,APPOINTMENT-IDENTITY-001,CALENDAR-PROJECTION-001 | queued user-visible appointment slice |
| `APPOINTMENT-ONBOARD-001` | PREREQUISITE | Implement the fourth `ONBOARD-003` kickoff question: whether the user wants appointment/reminder help, and if yes which Calendar lane should auto-sync (Google, Microsoft/Outlook/M365, Apple/iCloud, or explicit other/manual fallback). Record consent/preference without silently activating unavailable provider capability. | ONBOARD-003,CAL-006,SERVICE-001 | complete in PR #58; direct onboarding tests verify preference without fake provider activation |
| `CALENDAR-PROJECTION-001` | PREREQUISITE | Generic source-linked preferred-Calendar projection and exact provider readback. Adapter/capability proof must cover selected Google, Microsoft/Outlook/M365 and Apple/iCloud lanes without silently substituting a different Calendar; unsupported capability must be disclosed/fail closed. | CAL-007,CAL-006,provider Calendar write/readback,RECOVERY-002 | queued |
| `EDUCATION-CORE-001` | PREREQUISITE | Education track/work/deadline lifecycle. | EDU-001,TASK-001,TASK-002,provenance/evidence authority | queued |
| `HEALTH-ADMIN-001` | ENHANCEMENT | Non-clinical health-administration schema/safety gates. | HEALTH-001,PROFILE-013,evidence authority | queued |
| `SERVICE-MIGRATION-001` | HARDENING | Migrate legacy service activation without broadening intent. | SERVICE-001,SERVICE-002,canonical service/submodule IDs | queued |
| `MIRA-SKILL-001` | PREREQUISITE | Full provider-neutral MIRA orchestration skill. | ONBOARD-007,DIST-STARTER-001,SOURCE-GATES-001,RUNTIME-ROUTER-001,SERVICE-COMPOSE-001 | queued; not required for completed minimal M2-M0 Workspace proof |
| `PROVIDER-ONBOARD-001` | PREREQUISITE | Browser provider onboarding with exact resource/scope/readback. | PROVIDER-002,ONBOARD-006,RUNTIME-ROUTER-001 | queued; broader onboarding hardening after baseline Workspace proof |
| `GOOGLE-BOOTSTRAP-001` | PREREQUISITE | Full deterministic Personal Google blueprint/plan/verifier across selected Workspace services. | PROVIDER-003,MIRA-SKILL-001,PROVIDER-ONBOARD-001,SOURCE-GATES-001 | queued after M2-M0 baseline; full Calendar/Gmail/service bootstrap is not implied by the minimal Sheet proof |
| `NONTECH-INSTALL-001` | PREREQUISITE | Full browser-only ordinary-user installation, upgrade/recovery and exact readback. | ONBOARD-006,DIST-STARTER-001,SOURCE-GATES-001,MIRA-SKILL-001,PROVIDER-ONBOARD-001 | queued hardening; no terminal fallback allowed |
| `SOURCE-GATES-001` | PREREQUISITE | Independent source read/write/remote-readback gates. | SOURCE-001,source connector/runtime capability | queued |
| `RUNTIME-ROUTER-001` | PREREQUISITE | Provider-neutral runtime capability router. | PROVIDER-001,SOURCE-GATES-001,data-classification/approval state | queued |
| `SOURCE-LANES-001` | PREREQUISITE | Personal/organization/managed/no-Git source lanes. | SOURCE-002,SOURCE-GATES-001,RUNTIME-ROUTER-001,DIST-STARTER-001 | queued |
| `PERSON-GRAPH-001` | PREREQUISITE | Canonical Person UUIDs and relationship graph. | PROFILE-012,canonical MIRROR identity authority | queued |
| `PERMISSION-SCOPE-001` | BLOCKER | Exact cross-person actor/resource/action grants with revoke/narrow/provider/API readback. | PROFILE-012,PROFILE-013,AUTHORITY-REGISTRY-001 | queued; blocks shared/family/minor/caregiver paths, **not same-user M2-M0** |
| `FEATURE-SHARE-001` | HARDENING | Private feature ownership/reconciliation and optional sanitized publication/import path used by MIRA Studio; shared improvements carry provenance/dependencies/compatibility and never silently activate on another user's MIRA. | DIST-001,ONBOARD-002,SOURCE-GATES-001,DEV-005 | queued |
| `DIST-STARTER-001` | PREREQUISITE | Deterministic MIRA 2.0 starter/distributions from one source SHA. | DIST-002,ONBOARD-002,clean source lineage | complete in PR #62 at `9bf241f694e9bd52c846416336e0704a31fe7d8c`; Git-backed blueprint, deterministic source-SHA manifest, CI validation and independent clean Google substrate readback verified |
| `SKILL-BUILDER-001` | ENHANCEMENT | Bounded private custom skill/feature creation with declared contracts, preview/test evidence and rollback; this is the engine beneath the user-facing MIRA Studio rather than the final Studio UX itself. | DEV-004,DEV-001,DEV-002,FEATURE-REGISTRY-001,SOURCE-GATES-001 | queued |
| `MIRA-STUDIO-001` | VERTICAL | Implement `STUDIO-001` as an integrated user-facing Studio for continuously improving MIRA: guided creation/refinement of preferences, workflows and bounded features; preview/test/rollback; source/feature dependency awareness; and optional sanitized sharing/import through `FEATURE-SHARE-001`. Onboarding introduces Studio but does not force use. | STUDIO-001,SKILL-BUILDER-001,FEATURE-SHARE-001 | queued after core first-boot/source gates; accepted product feature |
| `PROFILE-CARE-001` | HARDENING | Caregiver composition without inferred authority. | PROFILE-006,SERVICE-001,PROFILE-012,PROFILE-013,PERMISSION-SCOPE-001 | queued |
| `PROFILE-HOUSEHOLD-001` | HARDENING | Household-manager routing/anti-fan-out. | PROFILE-007,SERVICE-001,task/routine authority | queued |
| `PROFILE-STUDENT-001` | HARDENING | Student role/HOME-CAMPUS context option. | PROFILE-008,CTX-001,CTX-002,SERVICE-001 | queued |
| `PROFILE-MIXED-001` | HARDENING | Mixed/custom role composition and primary-role routing. | PROFILE-009,canonical profile authority | queued |
| `PROFILE-USABILITY-001` | ENHANCEMENT | Explicit usability/accessibility preferences. | PROFILE-010,onboarding preference state,client capability discovery | queued |
| `PROFILE-LABEL-001` | HARDENING | Public-label rejection/private-alias boundary. | PROFILE-011,ONBOARD-002 | queued |
| `PROFILE-MINOR-001` | PREREQUISITE | Dependent-minor routing plus exact relationship/permission scopes. | PROFILE-005,PROFILE-012,PROFILE-013,PERSON-GRAPH-001,PERMISSION-SCOPE-001 | queued |
| `PROFILE-PARENT-001` | PREREQUISITE | Parent/guardian composition without relationship-derived authority. | PROFILE-004,PROFILE-012,PROFILE-013,PERSON-GRAPH-001,PERMISSION-SCOPE-001 | queued |
| `PROFILE-WORK-001` | HARDENING | Working/self-employed role semantics. | PROFILE-001,ONBOARD-004,SERVICE-001,CTX-002 | queued |
| `PROFILE-RETIRED-001` | HARDENING | Retired role/opt-in support. | PROFILE-002,SERVICE-001 | queued |
| `PROFILE-NONWORKING-001` | HARDENING | Nonworking/between-jobs semantics/transitions. | PROFILE-003,SERVICE-001 | queued |
| `STARTER-SANITIZE-001` | PREREQUISITE | Starter privacy/history audit gates. | ONBOARD-002,DIST-002 | complete in PR #62 at `9bf241f694e9bd52c846416336e0704a31fe7d8c`; deterministic clean-state/privacy verifier and independently created Google substrate proof verified |
| `FIRSTBOOT-CORE-001` | PREREQUISITE | Port/test `ONBOARD-003`: exactly four kickoff questions with fixed MIRA name omitted: (1) authoritative IANA timezone, (2) broad life/work/study/caregiving pattern, (3) biggest remembering/organizing/deciding/planning/follow-through goals, (4) appointment-reminder interest + preferred Calendar auto-sync intent. Persist durable resumable Interview Ledger; after four, offer continue setup now versus start using MIRA and introduce integrated MIRA Studio + optional sharing. Evidence-first reuse remains mandatory; preferences/permissions are never inferred. | ONBOARD-002,ONBOARD-003,canonical onboarding state | complete in PR #58 at `a60e8879e71b8f464eb1de1ea8cc15cbd309eccb`; direct tests + isolated Google persistence/readback verified |
| `DISCOVERY-CORE-001` | HARDENING | Structured discovery without recommendation-driven activation, including progressive post-setup domain discovery plus later current AI-use/friction discovery and inspection of accessible conversation/files/connected evidence before asking the user to rebuild history. MIRA supports user-invoked continuation while preserving the Interview Ledger. | ONBOARD-003,ONBOARD-004,SERVICE-001,RUNTIME-ROUTER-001 | partial; progressive continue-now/brief-drip slice merged/test-verified in PR #61, with once-per-later-day repeat-without-advance behavior added/tested in PR #63; broader evidence-aware history/capability discovery remains unfinished |
| `ONBOARD-SCHEDULE-001` | PREREQUISITE | Cadence/slot/IANA-timezone onboarding. | ONBOARD-003,SERVICE-001,OPS-003 | queued |
| `SERVICE-STATE-001` | PREREQUISITE | Finite service activation-state machine. | canonical service catalog/config authority | complete in PR #59 at `2fd34e1bd66bcb3a73c632e60457564f9e4a859c`; direct tests + isolated Google persistence/readback verified |
| `RECIPE-CORE-001` | LATER | Stable recipe identity/provenance/structured ingredients. | RECIPE-001 | queued |
| `MEAL-CORE-001` | LATER | Dated meal planning and shopping reconciliation. | RECIPE-001,GROCERY-CORE-001,SHOP-CORE-001 | queued |
| `MOVEMENT-CORE-001` | PREREQUISITE | Replay-safe movement/observation events; never collapse intended/observed location. | INV-001,IDENT-001,LOCATION-STATE-001 | complete in PR #71 at `86778802e0f32cf7d4e83c78063231a6e6e68a31`; exact-head CI `33342460536` and post-merge `main` CI `33342490468` green; fresh isolated Google event-first/projection-second movement readback and zero-write replay verified |
| `INVENTORY-QUERY-001` | HARDENING | Canonical inventory query projection. | INV-001,LOC-001,ASSET-003,LOCATION-STATE-001 | complete in PR #70 at `95728763816b2ab26e29973dd2e204d7c4bdbe9c`; exact-head CI `33341004699` and post-merge main CI `33341027064` green; fresh isolated Google tracked-vs-untracked identifier/location query and zero-write readback verified |
| `PAR-CORE-001` | ENHANCEMENT | Observed quantity/target/threshold state. | INV-001 | queued |
| `PAR-SCALE-001` | LATER | Optional scale-based passive stock sensing. | PAR-001 | deferred optional |
| `GROCERY-CORE-001` | PREREQUISITE | Grocery-list versus stock reconciliation. | SHOP-001,INV-001,LOC-001 | active in `M2-M0-019`; provider-neutral read-only grocery-vs-known-stock reconciliation |
| `LOCATION-STATE-001` | PREREQUISITE | Canonical inventory participation over the existing asset Entity UUID plus stable hierarchical locations with intended-home placement separate from latest supported observed location. Movement-event history and scanning remain separate. | INV-001,ASSET-001,STORE-001,RECOVERY-002 | complete in PR #67 at `7c2675836d2958d23ac37ad471cae8e14017b894`; exact-head CI `33329282677` green and fresh isolated Google asset-UUID participation/hierarchical intended-versus-observed location readback verified |
| `SHOP-CORE-001` | PREREQUISITE | Deterministic shopping-intent reconciliation. | RECEIPT-001 | complete in PR #72 at `b02e723396c4deb16394c59c63ed37071cdf59c7`; exact-head CI `33347846273` and post-merge `main` CI `33347884489` green; fresh isolated Google active-create, zero-write replay, exact captured-receipt-line fulfillment, receipt immutability and terminal zero-write replay verified |
| `KNOWLEDGE-INTEGRATION-001` | HARDENING | Retained-source/provider readback integration. | KNOW-001,selected provider adapter/sandbox | queued |
| `SPEC-INTEGRATION-001` | HARDENING | Authoritative specification persistence/readback. | SPEC-001,KNOW-001,selected provider adapter/sandbox | queued |
| `ASSET-ACQUISITION-001` | VERTICAL | Canonical receipt-linked physical asset acquisition with immutable RFC 4122 Entity UUID, source-identity dedupe/replay, explicit individual-vs-lot quantity semantics and provenance to the canonical receipt/line. Does not include fitment, identifier enrichment, warranty/maintenance, location or movement. | ASSET-001,ASSET-002,RECEIPT-001,RECEIPT-002,STORE-001,RECOVERY-002 | complete in PR #65 at `36645003e885b6562bb5c7ceeec4430838e148d8`; exact-head CI `33298434246` green and isolated Google receipt-to-asset revision-1/replay-boundary/revision-2 readback verified |
| `ASSET-IDENTIFIER-001` | VERTICAL | Canonical namespaced identifiers attached to existing asset UUIDs with exact source value plus normalized search value, validation for UPC/EAN/GTIN, IMEI and MAC, explicit namespace for merchant SKU/manufacturer part/model/serial identifiers, serial-level collision safety and deterministic identifier-to-asset lookup. Does not include OCR acquisition, automatic fitment, location/movement, or Android scanning. | IDENT-001,ASSET-001,STORE-001,RECOVERY-002 | complete in PR #66 at `6833d27e20d746d37e389b1756a6f6147225d043`; exact-head CI `33300160170` green and isolated Google leading-zero UPC, serial observed-to-verified revision, and identifier-to-canonical-asset readback verified |
| `FITMENT-ENGINE-001` | HARDENING | Deterministic automatic fitment resolution. | ASSET-001,IDENT-001,fitment evidence | queued |
| `ASSET-SERVICE-001` | HARDENING | Structured warranty/maintenance lifecycle. | ASSET-001,EVID-001 | queued |
| `ORDER-STALE-001` | PREREQUISITE | Five-business-day stale-shipment escalation. | ORDER-002,business-day semantics | queued |
| `SPEND-ROLLUP-001` | HARDENING | Monthly evidence-bounded spending rollup. | RECEIPT-001,RECEIPT-003 | queued |
| `RECEIPT-INTAKE-001` | VERTICAL | Canonical no-app receipt capture from normalized email/photo/text evidence with provenance fingerprints, transaction-level dedupe, exact money semantics and queryable purchase-history readback. Raw source content stays in its provider/evidence location; this slice does not silently create assets, inventory, orders, spend allocations or provider-side archives. | RECEIPT-001,RECEIPT-002,STORE-001,RECOVERY-002 | complete in PR #64 at `804a664f343934cc813d9cc45b471a6756a15697`; exact-head CI `33284284178` green and isolated Google receipt revision-1/revision-2 multi-source readback verified |
| `RECEIPT-TAXONOMY-001` | PREREQUISITE | Generic receipt taxonomy/classifier. | RECEIPT-001 | queued |
| `REIMB-CORE-001` | HARDENING | Deterministic reimbursement lifecycle. | RECEIPT-001,PROFILE-012 | queued |
| `SUBSCRIPTION-TRACK-001` | LATER | Optional subscription/free-trial tracking. | stable receipt/finance evidence + explicit activation | deferred optional |
| `FINANCE-CONNECTOR-001` | LATER | Authorized complete-account ingestion. | provider abstraction + privacy/authorization | deferred infrastructure |
| `OPS-BRIEF-VSLICE` | VERTICAL | First real task-centered no-app MIRA Ops Brief from canonical MIRA 2.0 state with deterministic local slots/run identity, immutable composed checkpoint, one-action-per-task rendering, explicit non-delivery truth and optional bounded progressive-discovery prompt. | STORE-001,TASK-001,TASK-002,OPS-003,OPS-004,RECOVERY-001 | complete in PR #63 at `f96b227e009eb144235dccfef2ca0b8570e0801b`; 189 Python + 15 Apps Script tests green and isolated Google task/run exact readback verified |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA source artwork/platform derivatives. | branding source delivered | queued |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Source-backed full instruction replacement delivery. | ONBOARD-001,audited onboarding,current instruction capability verification | complete in PR #60 at `71ab2278a6a45925f6bb74f9d3628f859d25ab71`; complete no-app protocol bundled/validated and fresh-copy first-boot provider proof passed |
| `GOV-RESP-001` | ENHANCEMENT | Customer action/continuation fallback for next full instruction replacement. | next legitimate full replacement | queued |
| `LEGACY-MIGRATION` | LATER | Selected legacy production migration after stable schema/vertical proof. | stable schema + rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI parity after shared core/API. | CORE-ROUNDTRIP | deferred; legacy client code reference only |
| `RFID` | LATER | RFID inventory capture/specialized hardware. | stable inventory schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | `LOCAL-001` bridge then Home Assistant/Plex/Paperless/Node-RED/MQTT/NAS adapters with scoped permissions/readback. | LOCAL-001,API-CORE-001 | deferred |
| `ENTERPRISE` | LATER | `ENTERPRISE-001` managed/regulated deployment lane. | ENTERPRISE-001,stock core,provider abstraction | deferred |

## Lifecycle reconciliation findings — 2026-08-29/30

- Completed work remains present with merge/test/provider evidence; it is filtered from next-work selection by the generated product lifecycle ledger rather than deleted.
- `FIRSTBOOT-CORE-001`, `SERVICE-STATE-001`, `APPOINTMENT-ONBOARD-001`, and `ONBOARD-INSTRUCTIONS` remain completed with evidence from PRs #58-#60.
- `FEATURE-ALIGN-001` remains completed by PR #61; feature/work lifecycle and session alignment share one canonical backlog parser.
- `DIST-STARTER-001` and `STARTER-SANITIZE-001` are completed by PR #62 at `9bf241f694e9bd52c846416336e0704a31fe7d8c`; source-derived distribution plus clean Google substrate provider proof are durable evidence.
- `OPS-BRIEF-VSLICE` is completed by PR #63 at `f96b227e009eb144235dccfef2ca0b8570e0801b`; this is the first real canonical no-app task/brief vertical.
- `RECEIPT-INTAKE-001` is completed by PR #64 at `804a664f343934cc813d9cc45b471a6756a15697`; canonical multi-source receipt/purchase truth is now available as a prerequisite for asset work.
- `ASSET-ACQUISITION-001` is completed by PR #65 at `36645003e885b6562bb5c7ceeec4430838e148d8`; immutable receipt-linked physical asset identity is now available for identifier, fitment and inventory layers.
- `ASSET-IDENTIFIER-001` is completed by PR #66 at `6833d27e20d746d37e389b1756a6f6147225d043`; canonical validated identifier attachment and identifier-origin asset lookup are now available for fitment, scanning and inventory layers.
- `LOCATION-STATE-001` is completed by PR #67 at `7c2675836d2958d23ac37ad471cae8e14017b894`; it reuses the asset Entity UUID for inventory participation and verifies hierarchical intended-versus-observed location state while movement-event history and scanning remain unfinished.
- `INVENTORY-QUERY-001` is completed by PR #70 at `95728763816b2ab26e29973dd2e204d7c4bdbe9c`; exact-head CI `33341004699`, post-merge `main` CI `33341027064`, no-app release guards and fresh isolated Google read-only query/zero-write proof are durable evidence.
- `MOVEMENT-CORE-001` is completed by PR #71 at `86778802e0f32cf7d4e83c78063231a6e6e68a31`; exact-head CI `33342460536`, post-merge `main` CI `33342490468`, no-app release guards, direct crash-recovery tests and fresh isolated Google movement/read-only replay proof are durable evidence.
- `SHOP-CORE-001` is completed by PR #72 at `b02e723396c4deb16394c59c63ed37071cdf59c7`; exact-head CI `33347846273`, post-merge `main` CI `33347884489`, direct/release tests and fresh isolated Google create/replay/receipt-line fulfillment/receipt-immutability proof are durable evidence.
- `GROCERY-CORE-001` is the one active work packet in `M2-M0-019`; it composes shopping intent with canonical inventory/location truth while leaving par quantity, recipes/meals, automatic purchasing, finance, scanning and Android unfinished.
- `DISCOVERY-CORE-001` remains partial: progressive discovery is test-verified and PR #63 adds repeated same-unanswered-topic daily prompting plus pending-goals follow-up behavior; broader evidence-aware AI-use/friction/history discovery remains unfinished.
- Stock ChatGPT Automations has been read-only verified as a technically viable exact-schedule no-server delivery provider; existing user MIRA brief automations are protected production and were not modified.
- `API-DEPLOYMENT-001B` remains explicitly paused; its Cloud Run live proof checkpoint is preserved.
- `ANDROID-COMMAND-BOUNDARY-001` remains explicitly partial; synthetic proof is complete but live Google worker proof is still pending.

## G0-010 dependency / dedupe findings

- The audited semantic graph is acyclic after removing universal cycles: `OPS-003` no longer depends on `OPS-001`; `IDENT-001` no longer depends on `EVID-001`; `PAR-001` no longer depends on `GROCERY-001`; `PROFILE-012` no longer depends on `PROFILE-013`; recipe/par relationships are selected behavior rather than universal grocery/meal prerequisites.
- The direct work cycle `STORE-ADAPTER-001` ↔ `DATA-SANDBOX` is removed. Synthetic adapter correctness comes first; Google sandbox/provider integration comes later.
- `DEP-GRAPH` no longer depends on `FEATURE-REGISTRY-001`. G0-010 is derived directly from canonical `FEATURES.md`/`BACKLOG.md`; generated machine-readable registries remain derived views, not editable authorities.
- **Feature alignment refinement (2026-08-29):** `DEV-007` requires every packet to read the canonical feature/work set before implementation and before merge, record required user-visible behavior/preserved invariants/deferred related features in `CURRENT_WORK`, and reject locally green solutions that structurally contradict accepted product features. M2-G0-011 additionally makes completed/partial/paused lifecycle state machine-queryable.
- **Superseded priority finding (2026-08-29):** the earlier decision that browser-only installation / Personal Google first-run could wait until after M2-M0 was wrong for the intended product. The default M2-M0 path required the minimal Google Workspace browser-only proof in `API-DEPLOYMENT-001A`; that proof is complete. Full Gmail/Calendar/scheduler/service onboarding remains separate hardening.
- **M2-M0 client finding (2026-08-29):** stock ChatGPT's official Google Drive/Sheets connection is the authenticated Personal client boundary. Apps Script remains useful embedded automation but is not the required stock-ChatGPT public API gateway. The native path is explicitly single writer; this finding does not weaken the stronger execution requirement for Android/multi-client mutation.
- **M2-M1 command-boundary finding (2026-08-29):** provider-neutral sequencer PR #54 and synthetic Workspace queued-writer PR #55 are merged/green. Android is blocked on live isolated Google worker proof and then Android client enrollment/sync, not on inventing a concurrency architecture from scratch.
- `PROFILE-013`/`PERMISSION-SCOPE-001` remain mandatory for cross-person/shared resources but do not over-block a same-user core entity roundtrip.
- `API-DEPLOYMENT-001` is an umbrella: `001A` is the completed ordinary-user Google Workspace baseline proof; `001B` preserves the already-built Cloud Run advanced profile.
- The audited onboarding interview remains preserved as semantic/source evidence. `FIRSTBOOT-CORE-001` is complete; post-four progressive discovery remains under `DISCOVERY-CORE-001`/`ONBOARD-004`.
- Appointment capture is explicit under `CAL-008`/`APPOINTMENT-INTAKE-001`: inbound email, user-supplied image/photo, and user text can become provenance-bound canonical appointment/provider state. Preferred Calendar sync remains a separate verified projection so evidence intake does not silently equal provider write success.
- MIRA Studio is explicitly user-facing (`STUDIO-001`/`MIRA-STUDIO-001`) and composes the existing bounded skill builder + controlled feature sharing. Shared improvements remain opt-in, sanitized, provenance/dependency aware, and never auto-activate.
- Provider/backend portability is an acceptance concern from the first Workspace deployment onward. `AUTHORITY-MIGRATION-001` later proves actual cutover to Linux/SQL/managed backends without dual writable masters.
- `STORE-ADAPTER-001A` was selected as the first implementation packet because every safe API/Android path depends on deterministic canonical structured-state semantics and it can be completed/tested without provider state. It is complete; `CURRENT_WORK.md` is authoritative for current work.

## Historical first implementation packet selection

**Packet:** `M2-G1-001A` — Synthetic structured-state adapter core  
**Related feature/work:** `STORE-001` / `STORE-ADAPTER-001A`  
**Status:** completed; no longer active. See `CURRENT_WORK.md` for current work.  
**Objective:** implement the smallest provider-neutral structured-state contract and deterministic in-memory adapter needed to prove exact read/write/readback semantics.

Acceptance criteria for the historical packet:
1. bounded structured-state interface only; evidence store, Google, API, Android and provider provisioning are out of scope;
2. health/schema inspection;
3. exact read by stable ID and deterministic bounded query;
4. idempotent create/upsert with stable ID and monotonically meaningful revision/version semantics;
5. append-only event support sufficient for later replay/audit;
6. exact read-after-write material-state verification;
7. deterministic duplicate/replay behavior and explicit conflict/error results;
8. synthetic fixtures only; zero provider/legacy production writes;
9. direct tests for success, replay, missing record, stale/conflicting mutation and malformed input;
10. component responsibility/evidence recorded in Git even before `CODE-OWNERSHIP-001` automation exists;
11. branch/checkpoint/PR/merge/readback discipline.

## New-idea triage rule

New ideas are captured with stable feature/work IDs, dependency-ranked, and do not expand the active packet unless required for acceptance or explicitly reprioritized. Generated lifecycle views are used to avoid selecting already completed work, but Git remains authoritative.