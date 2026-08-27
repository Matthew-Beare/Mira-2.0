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
- `CAL-*` — calendar, appointments, reminders;
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

Each feature distinguishes requirement status from delivery evidence:

1. `desired`
2. `specified`
3. `implemented`
4. `test_verified`
5. `integration_verified`
6. `live_verified`
7. `rejected_or_superseded` when applicable

Code existence does not imply completion. A feature may have test-verified deterministic logic while its provider integration or live firing remains unverified; that boundary must be stated explicitly.

## Required feature record

Each audited feature contains a stable ID, full user-facing description and outcome, requirement status, evidence level/boundary, dependencies, downstream enables, milestone, evidence paths, acceptance/verification boundary, and compatibility notes where relevant.

## Seed features established by MIRA 2.0 governance

### `DEV-001` — Git-authoritative development control plane
MIRA development uses Git as the authoritative source for ROADMAP, FEATURES, BACKLOG, CURRENT_WORK, packet policy, and durable engineering decisions. Human dashboards may mirror Git one-way but cannot become independent truth.

**Evidence:** specified and implemented in MIRA 2.0 repository governance files.

### `DEV-002` — Resumable bounded work packets
Development work is decomposed into bounded packets with explicit acceptance criteria, dependency/blocker tracking, durable checkpoints, and exact resume points. New customer ideas become backlog by default. Explicit reprioritization checkpoints displaced work before switching.

**Evidence:** specified and implemented in Project Instructions / roadmap / backlog / CURRENT_WORK policy.

### `DEV-003` — Dependency-ranked backlog
Engineering priority is dynamically recomputed from integrity/security blockers, hard prerequisites, architectural leverage, vertical value, and verification requirements rather than FIFO arrival order.

**Evidence:** specified and implemented in BACKLOG governance.

### `CORE-001` — MIRA product identity
**MIRA** is the primary product, assistant, and user-facing brand. MIRA expands to **Modular Intelligence & Reasoning Assistant**.

**Evidence:** specified in repository README, Project Instructions, and branding spec.

### `MIRROR-001` — Companion reality database
MIRROR is MIRA's companion reality database: durable structured facts, evidence, entities, state, provenance, and relationships that MIRA reasons over. MIRROR is a supporting technical component rather than a co-equal primary user-facing brand.

**Evidence:** specified in repository README, Project Instructions, and branding spec.

### `DATA-001` — Legacy production preservation
Existing legacy MIRA Google spreadsheets, Drive artifacts, briefs, schedules, automations, and other live user state are protected production data. MIRA 2.0 development must use separate sandbox state and may not silently overwrite or migrate legacy production artifacts.

**Evidence:** specified in Project Instructions and roadmap.

### `ONBOARD-001` — Full-replacement instruction delivery
Whenever a user must install or change ChatGPT Project Instructions, global Custom Instructions, or another instruction block, MIRA supplies the entire replacement block and simple nontechnical UI steps. Fragment-only instruction patches are prohibited by default.

**Evidence:** specified in Project Instructions; executable onboarding implementation is pending audit/design.

### `BRAND-001` — Canonical MIRA brand asset system
MIRA uses canonical vector source assets for symbol, wordmark, square lockup, wide hero/banner, thin header banner, Android adaptive foreground, and monochrome utility mark. Platform-specific icons are generated deterministically from masters.

**Evidence:** specified in `docs/BRAND_ASSET_SPEC.md`; final artwork and UI integration pending.

## Audited operational features

### `OPS-001` — Canonical twice-daily Ops Brief schedule
**Description:** MIRA's canonical Ops Brief schedule produces exactly two scheduled brief opportunities per calendar day at **02:45** and **14:45** in named IANA timezone `America/New_York`. Device/travel/session timezone and fixed UTC offsets do not reinterpret those wall-clock times. Manual invocation is separate.

**Why it exists / user outcome:** Predictable briefs tied to the operating schedule.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for runtime slot semantics; live scheduler configuration/firing remains unverified in MIRA 2.0.

**Hard dependencies:** named-timezone scheduler/readback; `OPS-003`; `OPS-004`.

**Enables:** scheduled briefs, appointment-slot semantics and Run Log proof.

**Legacy evidence:** `ops_policy.py`; `brief-run.md`; `SKILL.md`; feature-ledger row 1; PR #31 `MIRA-F009`.

**Acceptance / verification boundary:** Scheduler readback plus observed AM and PM canonical-slot firings.

**Compatibility notes:** Future user-configurable timezones still use IANA semantics.

---

### `OPS-002` — Single canonical dispatcher and prohibited duplicate schedules
**Description:** Scheduled Ops work uses one canonical dispatcher rather than parallel legacy, retry, child, diagnostic, shifted or device-local duplicates. Compatible scheduled work should consolidate when safe.

**Why it exists / user outcome:** Prevent duplicate briefs, contradictory mutations and scheduler confusion.

**Requirement status:** `required`.

**Delivery/evidence:** `specified`; provider-wide uniqueness remains unverified.

**Hard dependencies:** `OPS-001`; provider enumeration/readback; stable dispatcher identity.

**Enables:** reliable scheduled behavior and incident diagnosis.

**Legacy evidence:** feature-ledger row 2; `SKILL.md`; PR #31 `MIRA-F009`; scheduler planner contract.

**Acceptance / verification boundary:** Provider enumeration must prove exactly one intended dispatcher and no prohibited active duplicates.

---

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching
**Description:** Scheduled entry uses the runtime's own offset-aware clock, converts through IANA timezone rules, handles DST, records dispatch delay and accepts only bounded intended-slot entry. Model/device/travel clocks are not production authority.

**Why it exists / user outcome:** Prove when scheduled execution actually ran.

**Requirement status:** `required by failure evidence`.

**Delivery/evidence:** `test_verified`; live MIRA 2.0 scheduler path remains unverified.

**Hard dependencies:** runtime clock; timezone database; `OPS-001`.

**Enables:** scheduler-integrity gating, slot derivation and trustworthy logging.

**Legacy evidence:** canonical/live slot functions and regression tests; `brief-run.md`; feature-ledger row 3.

**Acceptance / verification boundary:** DST/offset/grace tests plus actual scheduler invocation through runtime-clock path.

---

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID
**Description:** Each scheduled brief starts fresh from the saved dispatcher and uses deterministic `OPS-YYYY-MM-DD-AM|PM` identity for delivered output and idempotent Run Log updates.

**Why it exists / user outcome:** Distinguish current output from stale chat output and scheduler-entry failure from downstream failure.

**Requirement status:** `required by stale-response incident`.

**Delivery/evidence:** `test_verified` for ID generation; provider standalone delivery/live logging unverified.

**Hard dependencies:** `OPS-003`; `RECOVERY-001`; scheduler fresh-run capability.

**Enables:** self-identifying notifications and scheduler diagnosis.

**Legacy evidence:** `ops_policy.py`; tests; `brief-run.md`; `SKILL.md`; feature-ledger row 4.

**Acceptance / verification boundary:** Real scheduled run creates/updates expected Run Log identity and delivers current output.

---

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides
**Description:** Base HOME/ROAD state comes from canonical weekly transitions and explicit overrides with stable identity/conflict/expiry semantics. Generic contexts and active Trip forcing are separate capabilities.

**Why it exists / user outcome:** Context-sensitive work uses state, not chat guesses.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified`; MIRA 2.0 state integration unverified.

**Hard dependencies:** canonical settings/state; override records; timezone-aware parsing.

**Enables:** mode-specific tasks and travel/weather behavior.

**Legacy evidence:** `ops_policy.py`; tests; `SKILL.md`; feature-ledger row 5.

**Acceptance / verification boundary:** Tests plus MIRA 2.0 sandbox transition/override read-write-readback.

---

### `CTX-001` — Configurable operating-context pairs
**Description:** MIRA supports a two-label operating-context model when environment changes actionable work. Patterns include HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/AWAY and user-defined labels; HOME/OFFICE is valid via custom labels. Context is mutable state, not identity or timezone.

**Why it exists / user outcome:** Users get useful operating boundaries without inheriting one hard-coded lifestyle.

**Requirement status:** `accepted direction`.

**Delivery/evidence:** `test_verified` in legacy router candidate; MIRA 2.0 integration unverified.

**Hard dependencies:** profile/context authority; explicit selection state; downstream context contract.

**Enables:** reusable context-specific behavior.

**Legacy evidence:** feature-ledger row 6; profile/context contract; onboarding router/tests.

**Acceptance / verification boundary:** Sandbox selected-label readback plus downstream consumption without timezone mutation.

---

### `CTX-002` — Evidence-gated context recommendation and explicit activation
**Description:** Job title/duties may recommend context but never silently enable it. Explicit user confirmation/labels control activation; ambiguity remains unresolved/needs-confirmation.

**Why it exists / user outcome:** Helpful onboarding without invented lifestyle state.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in legacy router candidate; MIRA 2.0 onboarding/readback unverified.

**Hard dependencies:** profile intake; `CTX-001`; confirmation state.

**Enables:** safe onboarding.

**Legacy evidence:** feature-ledger row 7; router contract/code/tests including false-match regression.

**Acceptance / verification boundary:** Recommendation cannot become active state without explicit confirmation/readback.

---

### `TRIP-001` — Independent trip occurrence lifecycle
**Description:** Each Trip occurrence is separate from Route knowledge, context and paid mileage, with stable identity and Planned/Active/Arrived/Cancelled states. Context changes/Route learning do not manufacture Trip or Mileage rows.

**Why it exists / user outcome:** Related travel facts stay linked without collapsing distinct state domains.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for core legacy separation/precedence; MIRA 2.0 persistence unverified.

**Hard dependencies:** Trip authority; stable IDs; context precedence.

**Enables:** weather watches, ETA/location, multi-leg cycles and mileage linkage.

**Legacy evidence:** feature-ledger row 8; state-maintenance/route-weather policy; entry tests.

**Acceptance / verification boundary:** Sandbox Trip lifecycle round-trip independent of context/mileage.

---

### `ROUTE-001` — Learned routes, directional runtime, location and ETA inference
**Description:** Reusable endpoint-pair Route knowledge is separate from Trip occurrences; supports directional route/runtime, runtime-derived ETA when stronger ETA is absent, location/time evidence and bounded progress primitives. Multi-leg work remains separate Trips.

**Why it exists / user outcome:** Reuse actual operating knowledge without substituting map distance for real history.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for route-average ETA/primitives; human-facing ahead/behind and MIRA 2.0 integration unverified.

**Hard dependencies:** `TRIP-001`; stable Route IDs/endpoints; supported time/location evidence.

**Enables:** ETA/status, route-weather and runtime learning.

**Legacy evidence:** feature-ledger row 9; route/state policy; runtime/tests.

**Acceptance / verification boundary:** Direction/ETA/location/progress tests plus Route+Trip sandbox round-trip; ahead/behind remains inference until evidenced.

---

### `WEATHER-001` — Context-gated HOME and ROAD weather intelligence
**Description:** HOME permits relevant home weather; ROAD may activate bounded route/corridor weather and official road-condition checks tied to Trip/watch state. Watches expire deterministically; forecast/observed restriction/inferred position remain distinct.

**Why it exists / user outcome:** Relevant weather rather than indiscriminate forecast dumping.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for deterministic gates/expiry; external NWS/DOT/511 is specified but not MIRA 2.0 integration-verified.

**Hard dependencies:** context; `TRIP-001`; `ROUTE-001`; authoritative sources; `RECOVERY-002` for scoped external-evidence failure behavior.

**Enables:** home decisions and route hazard warnings.

**Legacy evidence:** feature-ledger row 10; runtime/tests; route-weather and brief-run policy.

**Acceptance / verification boundary:** Gate tests plus sandbox state/source-grounded external pass. Provider failure degrades weather only.

---

### `MILE-001` — Company-paid mileage and deterministic gross-pay reporting
**Description:** MIRA records/reports company-paid miles, not map/odometer distance, and computes estimated gross from verified applicable rate. Both Thursday brief slots report the closed work cycle; Final/Estimated/Voided states, corrections and missing evidence are handled explicitly.

**Why it exists / user outcome:** Useful weekly pay estimate from employer-paid miles rather than meaningless route distance.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for totals, gross, pay-week boundaries, status splits, zero weeks, missing-mile actions and scoped tracker failure; MIRA 2.0 persistence/live Thursday delivery unverified.

**Hard dependencies:** `TRIP-001` when occurrence-linked; `MILE-002`; verified rate/paid-mile evidence; `OPS-001`; `RECOVERY-002` for scoped tracker failure during broader runs.

**Enables:** weekly reporting, work-cycle closeout, payroll reconciliation/trends.

**Legacy evidence:** feature-ledger row 11; policy YAML; runtime; mileage tests and Thursday HOME regression.

**Acceptance / verification boundary:** Synthetic sandbox mileage/settings round-trip, deterministic totals/validation and both Thursday slots reading one closed-cycle authority.

**Compatibility notes:** Historical rates are mutable state and must not be hard-coded in public source.

---

### `MILE-002` — Separate authoritative Miles & Pay tracker
**Description:** Mileage/pay state lives in a dedicated logical authority rather than Route geometry, chat or Git. It preserves stable occurrences, pay-week history, paid miles, applicable rate, gross, source/status and corrections. Storage is an adapter choice.

**Why it exists / user outcome:** Queryable pay history survives software, route and backend changes.

**Requirement status:** `required`.

**Delivery/evidence:** historical deployment records a live external authority; MIRA 2.0 has not provisioned/read back its own sandbox tracker.

**Hard dependencies:** MIRROR structured-state authority; stable mileage IDs/provenance; `MILE-001`.

**Enables:** historical pay queries and provider migration.

**Legacy evidence:** feature-ledger row 12; state-maintenance/brief-run policy; policy YAML.

**Acceptance / verification boundary:** Provision synthetic tracker, write/read back occurrence/settings, preserve identity/corrections and prove reporting consumes it.

---

### `TASK-001` — Structured task hierarchy and one-action-per-item rendering
**Description:** Canonical tasks use stable identity and priority tier → classification → optional subsystem → individual task. High/Medium/Low are normal tiers, Persistent is available for explicitly always-visible items. Each task is an independent record/bullet; context/windows affect actionability, not identity.

**Why it exists / user outcome:** Scannable, queryable task state rather than prose blobs.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for schema, validation, visibility and grouping; MIRA 2.0 task persistence unverified.

**Hard dependencies:** task authority; stable Task IDs; context when visibility is used.

**Enables:** brief rendering, filtering/search, next actions and Android task mutation.

**Legacy evidence:** feature-ledger row 13; runtime task/grouping functions; tests; state-maintenance policy.

**Acceptance / verification boundary:** Sandbox task round-trip and deterministic separate rendering/rejection of malformed required classification.

---

### `TASK-002` — Evidence-grounded next actions and honest completion state
**Description:** MIRA selects the smallest useful next action from canonical open work, real deadlines, prerequisites, blocks, context and available time. Planned/partial/completed/missed/removed/blocked state follows evidence. Silence never means Done.

**Why it exists / user outcome:** Useful coaching without fictional completion.

**Requirement status:** `accepted` and reinforced as integrity behavior.

**Delivery/evidence:** `specified`/skill workflow; generic cross-domain next-action engine not yet test-verified.

**Hard dependencies:** `TASK-001`; canonical planning state; supported deadlines/prerequisites/context as used.

**Enables:** coaching, study, routines, projects and honest brief status.

**Legacy evidence:** feature-ledger row 14; life-planning-accountability and state-maintenance policy.

**Acceptance / verification boundary:** Dedicated tests for blocked/context/completed exclusion, smallest-action selection, partial evidence and no completion-from-silence; then state-mutation readback.

---

### `RECOVERY-001` — Phase-aware Run Log, durable checkpoints and circuit-breaker recovery
**Description:** MIRA keeps durable execution/recovery evidence so interrupted or failed work resumes from known-good state. Deterministic Run IDs own one Run Log record with phase/status/timestamp/health/mutation evidence. Circuit-breaker conditions bound retries, preserve/read back verified state and provide one specific recovery action.

**Why it exists / user outcome:** Failed work leaves a precise recovery point instead of vanished progress and reconstructed memory.

**Requirement status:** `required by repeated stalls and integrity incidents`.

**Delivery/evidence:** `test_verified` for core Run ID/Run Log fields and selected degraded/error paths; broader circuit-breaker transaction is strongly specified; live MIRA 2.0 scheduled Run Log evidence unverified.

**Hard dependencies:** stable run/work IDs; Run Log/recovery authority; `OPS-003`; provider readback.

**Enables:** resumability, bounded retry, partial-write reconciliation and scheduler proof.

**Legacy evidence:** feature-ledger row 15; runtime/tests; brief-run; module-circuit-breaker-report; state-maintenance.

**Acceptance / verification boundary:** Same-run/phase/fail-degrade tests plus sandbox Run Log write/readback. Live scheduler proof requires actual canonical-slot entry.

**Compatibility notes:** This is workflow recovery; `DEV-002` is development-packet recovery.

---

### `RECOVERY-002` — Explicit module dependency boundaries and failure isolation

**Description:** MIRA treats modules and canonical authorities as separate failure domains unless a workflow explicitly declares a shared dependency. A malformed or unavailable optional input/adapter degrades only the affected module; healthy unrelated modules continue. A required core authority or invariant may block the owning module or whole run only when continuing would make its result invalid or unsafe. Cross-authority projection failure does not roll back verified canonical source state; the failed projection is marked degraded/pending and can be re-derived idempotently later.

**Why it exists / user outcome:** One bad spreadsheet range, calendar item, weather adapter, connector or projection should not make the entire assistant useless, nor should MIRA respond to partial failure by inventing shadow state or undoing known-good work.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for several legacy deterministic failure boundaries, including malformed/missing mileage input, Thursday degraded mileage behavior, invalid/duplicate appointment isolation, route/watch/settings degradation and healthy context/travel behavior continuing despite optional mileage failure. External-provider isolation is additionally `specified` in the policy/circuit-breaker contracts. **MIRA 2.0 cross-provider integration isolation remains unverified.**

**Hard dependencies:** explicit dependency/authority declarations; `RECOVERY-001` for failure recording/recovery; idempotent canonical source and provider readback for mutable cross-authority workflows.

**Enables:** reliable Ops Briefs, partial-service operation during provider outages, safe projection retry, weather/mail/calendar independence and future provider portability.

**Milestone:** foundational reliability prerequisite for every user-visible multi-module vertical slice.

**Legacy evidence:**
- feature-ledger category A row 16;
- `skill/ops-brief-policy/SKILL.md` failure-domain map and source-first cross-authority projection contract;
- `references/module-circuit-breaker-report.md` requires localized write stops while healthy modules continue;
- `scripts/test_ops_policy_entry.py` proves bad mileage input does not destroy ROAD/trip context and Thursday mileage failure degrades rather than globally errors;
- `scripts/test_ops_policy.py` proves missing optional mileage ranges degrade only that module and invalid/duplicate appointments are isolated;
- `brief-run.md` explicitly scopes mileage and non-authoritative Calendar failures instead of treating them as global prerequisites.

**Acceptance / verification boundary:** Unit tests must cover representative independent failure domains and required-vs-optional dependency behavior. Integration verification requires a MIRA 2.0 sandbox run where one external adapter/projection is deliberately unavailable or fails after canonical source commit, while unrelated healthy modules complete and the failed target remains safely recoverable. No feature may claim full multi-module live reliability from unit tests alone.

**Compatibility notes:** `RECOVERY-001` answers “how do we record, stop and recover from failure?” `RECOVERY-002` answers “what is actually allowed to fail without taking everything else down?” Keeping them separate prevents every module from becoming an accidental global dependency.

## Category A consistency result

Category A is now fully audited through behavior 16. The bounded consistency pass found these architectural relationships:

- `OPS-001` schedule semantics depend on `OPS-003` runtime clock integrity and `OPS-004` fresh-run identity; live scheduling still requires provider evidence.
- `OPS-004` depends on `RECOVERY-001` for durable same-run evidence.
- `OPS-005` remains the current deployment's deterministic HOME/ROAD semantics while `CTX-001`/`CTX-002` provide generalized labels and safe recommendation/activation.
- `TRIP-001`, `ROUTE-001` and `MILE-*` are explicitly distinct state authorities linked by IDs rather than implicit co-creation.
- `WEATHER-001` and `MILE-001` depend on `RECOVERY-002` when they participate as modules in a broader run so their failures remain scoped.
- `TASK-002` remains below `test_verified` pending dedicated generic next-action/completion tests; no other category-A record was found to exceed its audited evidence.
- Legacy live-provider claims remain legacy evidence only. No MIRA 2.0 feature is promoted to `integration_verified` or `live_verified` merely because the prior system once used a live Google authority.

## Audit status

- `M2-G0-002A` audited category-A behaviors 1-5.
- `M2-G0-002B` audited category-A behaviors 6-10.
- `M2-G0-002C` audited category-A behaviors 11-15.
- `M2-G0-002D` audited category-A behavior 16 and completed the Slice-A consistency pass.
- **Category A is complete.**
- The complete historical feature inventory is still in progress; category B begins next with calendar/reminder/mail safety features.
