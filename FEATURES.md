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
- `CAREER-*` — optional career/job monitoring and fit evaluation;
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

**Hard dependencies:** `OPS-001`; canonical/user timezone; Calendar/evidence adapter; `RECOVERY-002`.

**Legacy evidence:** feature-ledger category B row 1; appointment-window runtime/tests; `brief-run.md`.

**Acceptance / verification boundary:** Deterministic window tests plus MIRA 2.0 sandbox Calendar/evidence read showing exact Saturday-through-Friday inclusion/exclusion.

### `CAL-002` — Day-before and morning-of appointment reminders

**Description:** MIRA provides day-before and morning-of appointment coverage through deterministic reminder candidates and Ops Brief visibility. Cancelled/disabled appointments do not remind, overlapping triggers deduplicate, and late reminders are suppressed.

**Requirement:** required. **Evidence:** `test_verified`; Calendar projection/readback and user delivery unverified. **Dependencies:** appointment identity/evidence, timezone, activation, delivery adapter, `RECOVERY-002`.

### `CAL-003` — Configurable relative appointment reminder, default one hour before

**Description:** Appointment policy includes a configurable relative interval, default 60 minutes, with invalid-interval rejection, at/after-start suppression and trigger dedupe.

**Requirement:** required. **Evidence:** `test_verified`; provider projection/delivery unverified. **Dependencies:** appointment identity/start, `CAL-002`, timezone.

### `REMIND-001` — Evidence-gated medication reminders

**Description:** Medication reminders are default-off and may activate only from explicitly confirmed schedules supported by owner confirmation, prescription label, pharmacy, or clinician evidence. No inferred dose/timing, missed-dose advice, silent activation or assistant-inferred timing source is permitted.

**Requirement:** required safety boundary. **Evidence:** `test_verified` deterministic safety planner; MIRA 2.0 regimen authority/projection/delivery unverified. **Dependencies:** regimen authority/provenance, stable ID, timezone, activation, delivery adapter.

### `REMIND-002` — Explicit opt-in caregiver reminder sharing

**Description:** Reminder audience defaults to the user. Caregiver sharing is default-off and requires explicit activation plus a specific recipient identity; service activation alone never implies sharing permission.

**Requirement:** required safety boundary. **Evidence:** `test_verified` permission/recipient-required gate; real recipient resolution/authorization/provider delivery unverified. **Dependencies:** explicit consent, recipient identity resolution, source reminder, privacy-scoped delivery adapter.

## Audited appointment/mail communication-safety features

### `CAL-004` — Context-aware appointment visibility without fabricated confirmation state

**Description:** MIRA selects appointment visibility from deterministic brief-slot/calendar windows and current configured context rules without inventing or exposing a hidden “confirmed with user” state. Appointment presentation may include supported title, time and preparation evidence, but the system must not imply that the user has acknowledged, confirmed, accepted, or dismissed an appointment unless an authoritative source explicitly records that fact. Malformed/duplicate/unavailable appointment evidence is isolated rather than guessed into a valid event.

**Why it exists / user outcome:** The brief should show the right appointments without quietly manufacturing social state such as “confirmed” merely because the event exists or appeared in a prior brief.

**Requirement status:** `required`.

**Delivery/evidence:** deterministic appointment windows, filtering, duplicate/range isolation and mode-independent rendering are `test_verified`; the specific no-misleading-confirmation rule is `specified` in legacy policy rather than independently proven by a dedicated confirmation-state test. **MIRA 2.0 Calendar integration remains unverified.**

**Hard dependencies:** `CAL-001`/`CAL-002` appointment-window semantics; canonical appointment evidence; `RECOVERY-002` for malformed/unavailable Calendar isolation.

**Enables:** trustworthy appointment sections and future Calendar/reminder projections without hidden anti-nag state leaking into user-facing claims.

**Legacy evidence:** feature-ledger category B row 6; `brief-run.md` appointment rendering contract; `ops_policy.py` appointment filtering; `test_ops_policy.py` window and malformed/duplicate-event isolation.

**Acceptance / verification boundary:** Add/retain tests proving hidden acknowledgement/confirmation metadata cannot change the user-visible appointment claim unless that state is an explicit authoritative field; then verify a MIRA 2.0 sandbox Calendar read with malformed/unavailable evidence degrading only the appointment module.

---

### `MAIL-001` — Evidence-grounded important-mail triage

**Description:** MIRA performs a bounded important-mail pass for materially relevant school/education, employer/work, job/career, financial, medical, vendor/service, fraud and security messages. It reads materially relevant threads completely before conclusions, surfaces concise actionable changes, and avoids treating Promotions/sales noise as important by default. Email remains evidence, not the sole canonical record of downstream business facts.

**Why it exists / user outcome:** The user gets the few messages that actually matter without receiving an “AI summary” of the entire inbox or losing important context from half-read threads.

**Requirement status:** `required`.

**Delivery/evidence:** `specified`/skill-workflow. The legacy policy defines bounded searches, complete-thread reading and material categories, but this audit found no dedicated deterministic classifier test suite sufficient to promote general mail triage to `test_verified`. **MIRA 2.0 Gmail integration is unverified.**

**Hard dependencies:** connected mail/evidence adapter; bounded query policy; `RECOVERY-002` for mail-adapter failure isolation; canonical downstream authorities when a message changes orders, appointments, finance, etc.

**Enables:** Important Email brief section, archive-review queue, job-watch inputs and evidence-driven downstream reconciliation.

**Legacy evidence:** feature-ledger category B row 7; `brief-run.md` Gmail bounded-evidence pass; `email-reconciliation.md` complete-message/evidence rules and `Ops/Archive Approval` behavior; `SKILL.md` important-mail categories.

**Acceptance / verification boundary:** Before `test_verified`, add deterministic fixtures covering material/nonmaterial classification, thread completeness, duplicate/repeated evidence and unsupported ambiguity. Integration verification requires bounded reads against a synthetic/test mailbox or approved non-production fixture with no private mail committed to Git.

---

### `MAIL-002` — Explicit per-message approval for outbound contact

**Description:** MIRA may investigate an external-contact need, validate the recipient/channel, and draft the complete proposed message, but it must never send email or contact a vendor/employer/service automatically. Every send requires explicit approval for the exact current recipient/message/attachments. Before proposing contact, MIRA checks From/Reply-To/body/footer for unmonitored/no-reply instructions and uses an authoritative alternate support channel when needed. Any material change after approval requires fresh approval. The user-facing confirmation request is `Do you want me to send this email?`.

**Why it exists / user outcome:** MIRA can do the tedious research and drafting without becoming the sort of autonomous assistant that emails a vendor at 3 AM because it felt “confident.”

**Requirement status:** `required safety invariant`.

**Delivery/evidence:** `specified`/skill contract. The safety rule is explicit and repeated across legacy policy; this audit does not claim a complete test-verified send gate or MIRA 2.0 provider integration.

**Hard dependencies:** explicit user approval; validated recipient/channel; current issue evidence; outbound provider capability only after approval; audit/event recording after send.

**Enables:** safe vendor/employer/service contact proposals and later bounded outbound integrations.

**Legacy evidence:** feature-ledger category B row 8; `vendor-contact.md`; `email-reconciliation.md` contact-safety section; `SKILL.md` no-auto-email invariant.

**Acceptance / verification boundary:** Dedicated tests must prove no-send without approval, stale approval cannot authorize changed recipient/body/attachments, no-reply/unmonitored routes are rejected, and a permitted send uses exactly the approved payload. Integration verification requires provider readback after an explicitly approved synthetic/test send; no production send is part of this audit.

---

### `MAIL-003` — Explicit archive-approval queue with repeat-on-silence

**Description:** Important or decision-bearing mail remains in the inbox under the archive-review queue until the user explicitly approves archival. The brief groups the pending decisions compactly and ends the section with the exact prompt `Is it OK to archive these emails?`. Silence, failure to answer, or appearance in a previous brief is never approval; the unresolved queue repeats unchanged on later runs. Narrow separately-authorized retention/deletion policies do not override messages currently held for archive approval.

**Why it exists / user outcome:** MIRA can keep the inbox clean without silently hiding messages the user still needs to decide about.

**Requirement status:** `required`.

**Delivery/evidence:** `specified`/skill-workflow. The exact prompt and silence behavior are explicit in legacy run policy, but MIRA 2.0 Gmail label/archive mutation and readback are unverified.

**Hard dependencies:** `MAIL-001`; mail adapter with label/archive readback; explicit user approval identity/scope; `RECOVERY-002` for filing failure isolation.

**Enables:** safe inbox cleanup and durable archive decisions without auto-archiving important mail.

**Legacy evidence:** feature-ledger category B row 9; `brief-run.md` Important Email output contract; `email-reconciliation.md` important/unknown-mail section and Gmail filing order.

**Acceptance / verification boundary:** Tests must prove silence/repeated runs do not change archive state, approval is bounded to the displayed queue, and filing failure leaves messages pending. Integration verification requires synthetic/test-mail label/archive mutation plus provider readback.

---

### `CAREER-001` — Optional qualified job watch with realistic fit filtering

**Description:** MIRA can run an optional career/job-monitoring service that searches configured opportunity sources and evaluates candidate fit only against owner-approved canonical qualifications/settings. Mandatory requirements can reject a role; preferred qualifications alone cannot. Ambiguous postings become `Needs Review` rather than guessed. The service deduplicates by source/application/employer-title-location identity, reports only new realistic fits or specific review blockers, never applies/contacts anyone automatically, and normally runs as a phase of an existing MIRA control cycle rather than as a duplicate scheduler.

**Why it exists / user outcome:** The user sees realistic opportunities instead of a firehose of jobs whose title merely contains “IT,” while MIRA does not quietly rewrite the user's qualifications to make a posting look attractive.

**Requirement status:** `required personal service` for the legacy deployment; **optional per-user capability** in the general MIRA product.

**Delivery/evidence:** `specified`/skill workflow with explicit state/dedupe/fit rules. The audit found no dedicated executable fit-engine test suite sufficient to mark the general capability `test_verified`. **MIRA 2.0 mail/search/provider integration is unverified.**

**Hard dependencies:** explicit service activation; canonical candidate configuration/qualification authority; mail/search evidence adapter; stable Job Watch identity/state; `MAIL-002` for any later external contact; `RECOVERY-002` for module failure isolation.

**Enables:** compact PM career opportunities and review decisions without separate task/scheduler proliferation.

**Legacy evidence:** feature-ledger category B row 10; `qualified-job-watch.md`; `SKILL.md` consolidated-control-cycle routing.

**Acceptance / verification boundary:** Before `test_verified`, add deterministic fixtures for mandatory-vs-preferred requirements, seniority/role exclusions, experience ceilings, ambiguity, dedupe and no-contact behavior. Integration verification requires a synthetic/approved opportunity source plus canonical settings readback. The feature must remain disabled/unconfigured for users who do not opt in.

## Category B consistency result

Category B is fully audited through row 10.

- Appointment visibility (`CAL-*`) is distinct from reminder delivery/safety (`REMIND-*`).
- Mail triage (`MAIL-001`) does not itself authorize filing or contact.
- Outbound-contact permission (`MAIL-002`) is provider-independent and remains an explicit per-action gate even if Gmail is later replaced or supplemented.
- Archive approval (`MAIL-003`) treats silence as no permission and remains separate from narrow retention/deletion exceptions.
- Job watch (`CAREER-001`) is an optional personal service and cannot become a universal default merely because it existed in the legacy deployment.
- No category-B feature is promoted to MIRA 2.0 integration/live verification from legacy provider state.

## Audit status

- Category A is complete through `M2-G0-002D`.
- `M2-G0-003A` audited category-B rows 1-5.
- `M2-G0-003B` audited category-B rows 6-10.
- **Category B is complete.**
- The next audit category is C: orders, shipments, receipts, payments and spending, which must be split into bounded packets before work begins.
