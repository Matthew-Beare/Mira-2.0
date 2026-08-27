# MIRA 2.0 FEATURES

This file is the human-readable canonical feature registry. It is populated and normalized through bounded forensic audit packets. Machine-readable dependency metadata may be added after stable IDs are assigned.

## Feature identity rule

Every durable feature receives a stable semantic ID. IDs do not change merely because roadmap priority or table position changes.

ID families include:

- `CORE-*` — MIRA control plane, canonical state, identity, reconciliation, provenance;
- `MIRROR-*` — companion reality database/state/evidence contracts;
- `OPS-*` — briefs, operational state, deployment-specific operations;
- `CTX-*` — user-selected operating-context models and context recommendation;
- `TRIP-*` — trip occurrence state and trip lifecycle;
- `ROUTE-*` — reusable route knowledge, directional routing and runtime/ETA behavior;
- `WEATHER-*` — context-aware weather and route-hazard gating;
- `MILE-*` — paid-mileage occurrences, pay calculations and mileage authority;
- `TASK-*` — task taxonomy, next actions and completion evidence;
- `RECOVERY-*` — run evidence, checkpoints, resumability, circuit breakers and failure isolation;
- `CAL-*` — calendar, appointments and appointment-window semantics;
- `REMIND-*` — reminder planning, medication reminder safety and sharing boundaries;
- `MAIL-*` — email triage, communication safety, evidence ingestion;
- `ORDER-*` — orders, shipments, replacements, returns, refunds;
- `RECEIPT-*` — receipts, purchases, evidence, payment reconciliation;
- `ASSET-*` — assets, fitment, specifications, manuals, maintenance;
- `INV-*` — inventory, hierarchical locations, movement, scanning, par levels;
- `PROFILE-*` — onboarding, roles, family, customization, accessibility;
- `PROVIDER-*` — Google/Microsoft/Apple/storage/runtime portability;
- `CLIENT-*` — ChatGPT, Android, web, desktop, CLI and device surfaces;
- `DIST-*` — distribution, updates, releases, rollback;
- `ENTERPRISE-*` — locked-down/institutional deployment;
- `DEV-*` — development governance and resumability.

## Evidence levels

Each feature distinguishes requirement status from delivery evidence: `desired`, `specified`, `implemented`, `test_verified`, `integration_verified`, `live_verified`, and `rejected_or_superseded` when applicable. Code existence does not imply completion.

## Seed features established by MIRA 2.0 governance

### `DEV-001` — Git-authoritative development control plane
Git is authoritative for ROADMAP, FEATURES, BACKLOG, CURRENT_WORK, packet policy, and durable engineering decisions. Human dashboards may mirror Git one-way but cannot become independent truth.

**Evidence:** specified/implemented in MIRA 2.0 governance.

### `DEV-002` — Resumable bounded work packets
Development uses bounded packets with explicit acceptance criteria, dependencies, checkpoints and exact resume points. New ideas enter backlog by default; explicit reprioritization checkpoints displaced work first.

**Evidence:** specified/implemented in Project Instructions and project control files.

### `DEV-003` — Dependency-ranked backlog
Priority is recomputed from blockers, prerequisites, leverage, user-visible value and verification needs rather than FIFO arrival order.

**Evidence:** specified/implemented in BACKLOG governance.

### `CORE-001` — MIRA product identity
MIRA is the primary product, assistant and user-facing brand: **Modular Intelligence & Reasoning Assistant**.

**Evidence:** repository README, Project Instructions and branding spec.

### `MIRROR-001` — Companion reality database
MIRROR is MIRA's companion reality database containing durable structured facts, evidence, entities, state, provenance and relationships.

**Evidence:** README, Project Instructions and branding spec.

### `DATA-001` — Legacy production preservation
Legacy MIRA Google spreadsheets, Drive artifacts, briefs, schedules and automations are protected production data. MIRA 2.0 uses separate sandbox state until an explicit migration packet exists.

**Evidence:** Project Instructions and roadmap.

### `ONBOARD-001` — Full-replacement instruction delivery
MIRA supplies whole copy/paste replacement blocks plus nontechnical UI instructions whenever ChatGPT Project/Custom Instructions must change.

**Evidence:** Project Instructions; onboarding implementation pending audit/design.

### `BRAND-001` — Canonical MIRA brand asset system
Canonical vector masters drive symbol, wordmark, lockups, banners, adaptive icon and generated platform derivatives.

**Evidence:** `docs/BRAND_ASSET_SPEC.md`; artwork/integration pending.

## Audited operational features

### `OPS-001` — Canonical twice-daily Ops Brief schedule
**Description:** Exactly two scheduled brief opportunities at 02:45 and 14:45 in named IANA timezone `America/New_York`; device/travel/session timezone and fixed UTC offsets do not reinterpret them. Manual invocation is separate.

**Requirement:** required. **Evidence:** `test_verified` runtime slot semantics; live MIRA 2.0 scheduler/firing unverified. **Dependencies:** named-timezone scheduler/readback, `OPS-003`, `OPS-004`. **Legacy evidence:** runtime/brief policy/tests and PR #31 `MIRA-F009`. **Verification boundary:** provider readback plus observed AM/PM canonical firings.

### `OPS-002` — Single canonical dispatcher and prohibited duplicate schedules
**Description:** One canonical dispatcher rather than parallel legacy/retry/child/diagnostic/shifted duplicates; compatible scheduled work consolidates when safe.

**Requirement:** required. **Evidence:** specified; provider uniqueness unverified. **Dependencies:** `OPS-001`, provider enumeration/readback. **Verification:** enumerate provider tasks and prove intended job uniqueness.

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching
**Description:** Runtime-owned offset-aware clock converted through IANA timezone rules decides bounded scheduled entry; model/device/travel clocks are not authority.

**Requirement:** required by failure evidence. **Evidence:** `test_verified`; live scheduler path unverified. **Dependencies:** runtime clock/timezone DB, `OPS-001`. **Verification:** DST/offset/grace tests plus actual scheduled invocation.

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID
**Description:** Each scheduled brief starts fresh and uses deterministic `OPS-YYYY-MM-DD-AM|PM` identity for output and idempotent Run Log updates.

**Requirement:** required. **Evidence:** `test_verified` ID generation; live standalone delivery unverified. **Dependencies:** `OPS-003`, `RECOVERY-001`, scheduler fresh-run capability.

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides
**Description:** Base HOME/ROAD state comes from canonical weekly transitions and explicit override records; generalized context and active Trip forcing remain separate capabilities.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 state integration unverified. **Dependencies:** canonical state and timezone-aware override semantics.

### `CTX-001` — Configurable operating-context pairs
**Description:** MIRA supports two-label operating contexts such as HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/AWAY and custom labels; HOME/OFFICE is valid through custom configuration.

**Requirement:** accepted direction. **Evidence:** `test_verified` legacy router candidate; MIRA 2.0 integration unverified. **Dependencies:** profile/context authority and explicit selection.

### `CTX-002` — Evidence-gated context recommendation and explicit activation
**Description:** Job/duties may recommend context but never silently enable it; confirmation/user labels control activation and ambiguity remains unresolved.

**Requirement:** required. **Evidence:** `test_verified` legacy router candidate; MIRA 2.0 onboarding/readback unverified. **Dependencies:** profile intake, `CTX-001`, confirmation state.

### `TRIP-001` — Independent trip occurrence lifecycle
**Description:** Trip occurrences are separate from reusable Route knowledge, context and paid mileage, with stable identity and Planned/Active/Arrived/Cancelled lifecycle.

**Requirement:** required. **Evidence:** `test_verified` legacy separation/precedence; MIRA 2.0 persistence unverified. **Dependencies:** Trip authority/stable IDs/context precedence.

### `ROUTE-001` — Learned routes, directional runtime, location and ETA inference
**Description:** Reusable Route knowledge is separate from Trip occurrences; supports directional route/runtime, runtime-derived ETA, location evidence and bounded progress primitives.

**Requirement:** required. **Evidence:** `test_verified` for route-average ETA/primitives; human-facing ahead/behind and MIRA 2.0 integration unverified. **Dependencies:** `TRIP-001` and stable route identity/evidence.

### `WEATHER-001` — Context-gated HOME and ROAD weather intelligence
**Description:** HOME permits relevant home weather; ROAD may activate bounded route/corridor weather and official road-condition checks tied to Trip/watch state.

**Requirement:** required. **Evidence:** `test_verified` deterministic gates/expiry; external NWS/DOT/511 unverified in MIRA 2.0. **Dependencies:** context, `TRIP-001`, `ROUTE-001`, `RECOVERY-002`.

### `MILE-001` — Company-paid mileage and deterministic gross-pay reporting
**Description:** MIRA reports company-paid miles, not map/odometer distance, and computes gross estimate from verified rate. Both Thursday brief slots report the closed cycle with explicit status/correction/missing-evidence handling.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 persistence/live Thursday delivery unverified. **Dependencies:** `MILE-002`, paid-mile/rate evidence, `OPS-001`, `RECOVERY-002`, optional `TRIP-001` linkage.

### `MILE-002` — Separate authoritative Miles & Pay tracker
**Description:** Mileage/pay state lives in a dedicated logical authority preserving stable occurrences, pay-week history, paid miles, rate, gross, provenance/status and corrections; storage backend is an adapter.

**Requirement:** required. **Evidence:** legacy live authority exists; MIRA 2.0 sandbox authority unverified. **Dependencies:** MIRROR state contract, stable IDs, `MILE-001`.

### `TASK-001` — Structured task hierarchy and one-action-per-item rendering
**Description:** Stable Task identity plus priority → classification → optional subsystem → task; each action remains an independent canonical record/bullet with context/window-driven actionability.

**Requirement:** required. **Evidence:** `test_verified`; MIRA 2.0 persistence unverified. **Dependencies:** task authority/stable IDs/context where applicable.

### `TASK-002` — Evidence-grounded next actions and honest completion state
**Description:** Smallest useful next actions derive from canonical open work, deadlines, prerequisites, blocks and context. Partial/completed/missed/removed/blocked state follows evidence; silence never means Done.

**Requirement:** accepted/integrity rule. **Evidence:** specified/skill workflow; generic cross-domain engine not yet test-verified. **Dependencies:** `TASK-001` plus applicable planning evidence.

### `RECOVERY-001` — Phase-aware Run Log, durable checkpoints and circuit-breaker recovery
**Description:** Durable run/recovery evidence uses stable Run IDs, phase/status/health/mutation evidence, bounded retries and verified-state preservation/readback with a specific recovery action.

**Requirement:** required. **Evidence:** `test_verified` core Run Log/selected degradation paths; broader circuit-breaker strongly specified; MIRA 2.0 live scheduled evidence unverified. **Dependencies:** stable run IDs, recovery authority, `OPS-003`, provider readback.

### `RECOVERY-002` — Explicit module dependency boundaries and failure isolation
**Description:** Modules/authorities remain separate failure domains unless an explicit shared dependency exists. Optional failure degrades only the affected module; canonical source state survives downstream projection failure and can re-drive a failed target later.

**Requirement:** required. **Evidence:** `test_verified` across representative legacy mileage/appointment/travel optional-input boundaries; MIRA 2.0 cross-provider isolation unverified. **Dependencies:** explicit dependency declarations, `RECOVERY-001`, idempotent source/readback semantics.

## Category A consistency result

Category A is complete. Scheduling, context, Trip, Route, mileage, task and recovery authorities are explicitly separated. `TASK-002` remains below test-verified pending dedicated generic tests; no category-A feature is promoted to MIRA 2.0 integration/live status from legacy provider claims.

## Audited calendar/reminder features

### `CAL-001` — Saturday AM seven-day appointment lookahead

**Description:** The Saturday 02:45 canonical AM Ops Brief includes appointments from Saturday through Friday using a half-open seven-calendar-day window. Appointment visibility is slot-based and independent of HOME/ROAD mode. This mode-independent rule supersedes older ledger wording that described the weekly lookahead only as a ROAD behavior.

**Why it exists / user outcome:** Once a week the user gets enough appointment horizon to plan the coming week without turning every daily brief into a calendar dump.

**Requirement status:** `required`; later repaired policy generalizes the historical ROAD-only wording to mode-independent Saturday-AM behavior.

**Delivery/evidence:** `test_verified` for deterministic window calculation in legacy policy. **Live Calendar query coverage and MIRA 2.0 brief integration remain unverified.**

**Hard dependencies:** `OPS-001` canonical AM/PM slot semantics; canonical/user timezone semantics; Calendar/evidence adapter for real appointments; `RECOVERY-002` so Calendar failure can remain scoped.

**Enables:** weekly planning, Saturday brief appointment section and reminder reconciliation horizon.

**Legacy evidence:** feature-ledger category B row 1; `ops_policy.py` appointment-window logic; `test_ops_policy.py` verifies Saturday AM seven-calendar-day preview and Saturday PM returning to normal day-before behavior; `brief-run.md` explicitly states appointment rendering is slot-based and mode-independent.

**Acceptance / verification boundary:** Deterministic window tests plus MIRA 2.0 sandbox Calendar/evidence read showing exact Saturday-through-Friday inclusion/exclusion. Provider readback/query evidence is required before integration verification.

---

### `CAL-002` — Day-before and morning-of appointment reminders

**Description:** MIRA provides both day-before and morning-of appointment coverage. The reminder planner produces deterministic reminder candidates at configured local wall times; the Ops Brief independently surfaces tomorrow's appointments on PM briefs and today's appointments on normal AM briefs. Cancelled or per-event-disabled appointments do not remind, equal-time triggers deduplicate, and reminders that would occur at/after event start are suppressed rather than emitted late.

**Why it exists / user outcome:** Appointments should appear when preparation is useful and again when action is imminent, without duplicate nagging or nonsense reminders after the appointment has already started.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in the legacy deterministic planner and brief-window logic. **Calendar projection/readback and actual notification delivery are not MIRA 2.0 integration/live verified.**

**Hard dependencies:** canonical appointment identity/evidence; named IANA timezone; reminder activation state; Calendar/notification projection adapter for delivery; `RECOVERY-002` for adapter isolation.

**Enables:** reliable appointment planning and later Android/Calendar notification delivery.

**Legacy evidence:** feature-ledger category B row 2; `reminder_policy.py`; `test_reminder_policy.py` verifies day-before/morning-of planning, dedupe, suppression and disabled-service behavior; `brief-run.md` defines PM tomorrow / AM today visibility.

**Acceptance / verification boundary:** Planner tests plus MIRA 2.0 sandbox appointment read/write/readback and projection identity/readback. Actual user-facing delivery must be observed separately.

---

### `CAL-003` — Configurable relative appointment reminder, default one hour before

**Description:** Appointment reminder policy includes a configurable relative interval before event start, defaulting to 60 minutes. The planner rejects invalid intervals, suppresses any computed reminder at/after event start, and deduplicates the relative trigger with day/morning triggers when they resolve to the same instant.

**Why it exists / user outcome:** The user gets a final actionable reminder close enough to leave, prepare, or join without creating a dedicated automation for every appointment.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for deterministic default/configurable relative timing, suppression and dedupe. **Provider projection and notification delivery remain unverified in MIRA 2.0.**

**Hard dependencies:** canonical appointment start time/identity; `CAL-002` planner/projection foundation; named timezone.

**Enables:** close-in appointment prompting without per-event ChatGPT tasks.

**Legacy evidence:** feature-ledger category B row 3; `reminder_policy.py` default `relative_minutes_before = 60`; `test_reminder_policy.py` verifies one-hour-before output, dedupe and invalid profile rejection; policy YAML lists 60-minute stock reminder.

**Acceptance / verification boundary:** Deterministic timing tests plus a sandbox projected event readback proving one stable reminder identity and no reminder at/after event start.

---

### `REMIND-001` — Evidence-gated medication reminders

**Description:** Medication reminders are disabled by default and may activate only from an explicitly confirmed schedule supported by an allowed authority: owner confirmation, prescription label, pharmacy, or clinician. Active regimens require stable identity, explicit nonempty schedule times and explicit schedule confirmation. MIRA must not infer medication dose/timing, provide missed-dose advice, silently activate reminders, or use assistant inference as a medication timing source. Paused/ended/disabled regimens do not remind.

**Why it exists / user outcome:** MIRA can reliably remind a user about an already-established regimen without turning a reminder feature into unauthorized medical decision-making.

**Requirement status:** `required safety boundary`.

**Delivery/evidence:** `test_verified` in the legacy deterministic planner for source whitelist, explicit confirmation, schedule validation, disabled/paused suppression, DST failure, and no-inference safety flags. **MIRA 2.0 medication authority/projection and actual notification delivery remain unverified.**

**Hard dependencies:** explicit medication regimen authority/provenance; stable regimen identity; named timezone; reminder activation state; notification/projection adapter.

**Enables:** safe medication reminder delivery and optional later caregiver sharing through `REMIND-002`.

**Legacy evidence:** feature-ledger category B row 4; `reminder_policy.py` source whitelist and explicit schedule rules; `test_reminder_policy.py` verifies confirmed schedule planning, untrusted-source rejection, paused suppression, duplicate/empty-time rejection and DST fail-closed behavior; policy YAML prohibits inference/missed-dose advice.

**Acceptance / verification boundary:** Planner safety tests plus MIRA 2.0 sandbox regimen provenance/readback and explicit activation. Actual notification delivery is separate evidence. No legacy personal regimen data is imported during development.

---

### `REMIND-002` — Explicit opt-in caregiver reminder sharing

**Description:** Reminder audience defaults to the user only. Caregiver sharing is disabled by default and requires explicit activation plus a specific recipient identity. When enabled, only the configured reminder output is shared; enabling a reminder service does not imply permission to share it. The deterministic planner refuses sharing when the recipient field is absent.

**Why it exists / user outcome:** A user can deliberately share reminders with a trusted caregiver without MIRA assuming that family relationship equals permission to disclose private schedule or medication information.

**Requirement status:** `required safety boundary`.

**Delivery/evidence:** `test_verified` for opt-in/default-off behavior and required recipient field. **Exact private-recipient identity resolution, authorization, provider delivery and readback are not verified by the legacy unit test and remain MIRA 2.0 integration requirements.**

**Hard dependencies:** explicit sharing consent; exact recipient identity resolution; `CAL-002`/`CAL-003` and/or `REMIND-001` as source reminder; privacy-scoped delivery adapter.

**Enables:** consented caregiver notification without changing canonical reminder ownership.

**Legacy evidence:** feature-ledger category B row 5; `reminder_policy.py` defaults audience to user and requires recipient when sharing is enabled; `test_reminder_policy.py` verifies default/opt-in gate; `SKILL.md` requires explicit sharing consent and exact private recipient identity.

**Acceptance / verification boundary:** Unit tests prove the gate, not the person. Integration verification requires resolving an approved private recipient, projecting only the intended reminder, provider readback, and proving disabling/revoking sharing stops future caregiver delivery without disabling the user's own reminder.

## Audit status

- Category A is complete through `M2-G0-002D`.
- `M2-G0-003A` audited category-B rows 1-5: `CAL-001`, `CAL-002`, `CAL-003`, `REMIND-001`, `REMIND-002`.
- The complete historical feature inventory is still in progress.
- The next bounded audit begins with category-B row 6: context-aware appointment windows without exposing misleading confirmation state, then mail/communication-safety rows through row 10.
