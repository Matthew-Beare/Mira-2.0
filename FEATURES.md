# MIRA 2.0 FEATURES

This file is the human-readable canonical feature registry. It is populated and normalized through bounded forensic audit packets. Machine-readable dependency metadata may be added after stable IDs are assigned.

## Feature identity rule

Every durable feature receives a stable semantic ID. IDs do not change merely because roadmap priority or table position changes.

ID families include:

- `CORE-*` — MIRA control plane, canonical state, identity, reconciliation, provenance;
- `MIRROR-*` — companion reality database/state/evidence contracts;
- `OPS-*` — briefs, operational state, tasks, run logs, deployment-specific operations;
- `CTX-*` — user-selected operating-context models and context recommendation;
- `TRIP-*` — trip occurrence state and trip lifecycle;
- `ROUTE-*` — reusable route knowledge, directional routing and runtime/ETA behavior;
- `WEATHER-*` — context-aware weather and route-hazard gating;
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

Each audited feature contains:

- stable feature ID;
- name;
- full user-facing description;
- why it exists / user outcome;
- current requirement status;
- delivery/evidence level and boundary;
- hard dependencies;
- downstream capabilities enabled;
- milestone association;
- known implementation/evidence paths;
- acceptance criteria / verification boundary;
- migration/compatibility notes when relevant;
- superseded/rejected relationship if applicable.

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

**Description:** MIRA's canonical Ops Brief schedule produces exactly two scheduled brief opportunities per calendar day at **02:45** and **14:45** in the named IANA timezone `America/New_York`. Travel location, device timezone, session timezone, and fixed UTC offsets must not reinterpret those wall-clock times. Manual brief invocation is a separate on-demand path and does not count as an extra scheduled brief.

**Why it exists / user outcome:** The user needs predictable briefs tied to the operating schedule rather than whatever timezone a device, truck, cloud worker, or model happens to think is fashionable that day.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for repository policy/runtime slot semantics; **live scheduler configuration and actual 02:45/14:45 firing are not yet MIRA 2.0 live-verified**.

**Hard dependencies:** a scheduler/provider capable of named-timezone recurrence and readback; `OPS-003` canonical clock gate for runtime integrity; `OPS-004` for fresh identifiable run delivery.

**Enables:** appointment-slot semantics, scheduled Ops Brief delivery, scheduled run-log proof, recurring operational reconciliation phases.

**Milestone:** foundation for the future Ops Brief vertical slice.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py` defines `TZ_NAME = "America/New_York"` and canonical brief slots `((2,45),(14,45))`;
- `skill/ops-brief-policy/references/brief-run.md` defines scheduled New York clock semantics;
- `skill/ops-brief-policy/SKILL.md` requires one standalone control cycle at 2:45 AM/PM Eastern;
- legacy `docs/feature-ledger-2026-08-24.md`, category A row 1;
- PR #31 `project/FEATURES.yaml` candidate `MIRA-F009` independently restates `02:45`, `14:45`, `America/New_York`, exact count two.

**Acceptance / verification boundary:** MIRA 2.0 may call the schedule behavior complete only after scheduler readback proves the intended recurrence/TZID and at least one observed AM and PM firing produce canonical run evidence in the correct slot. Unit tests alone do not prove scheduler firing.

**Compatibility notes:** For a future general-user product, cadence/timezone may become user-configurable through audited profile settings. This record preserves the current user's required deployment behavior and the rule that named-timezone semantics, not fixed UTC math, are authoritative.

---

### `OPS-002` — Single canonical dispatcher and prohibited duplicate schedules

**Description:** Scheduled Ops work must use one canonical dispatcher/control-cycle definition rather than parallel legacy, retry, child, diagnostic, UTC-shifted, 3:00, noon/midnight, or device-local duplicate schedules. Scheduled diagnostic or cleanup work should be consolidated into an existing compatible MIRA cycle when safe instead of consuming independent task slots merely because a feature exists.

**Why it exists / user outcome:** Duplicate automations create duplicate briefs, stale output, contradictory mutations, wasted task slots, and debugging sessions where everyone insists the clock is correct while three different clocks are firing.

**Requirement status:** `required`; supersedes historical duplicate/shifted schedule states.

**Delivery/evidence:** `specified`. Repository policy strongly specifies uniqueness/prohibited variants, and historical evidence says old paused jobs existed, but **current provider-wide duplicate enumeration is not verified in MIRA 2.0**.

**Hard dependencies:** `OPS-001`; provider capability to enumerate/read back scheduled tasks; stable dispatcher identity.

**Enables:** deduplicated scheduled behavior, reliable incident diagnosis, future cleanup/reconciliation consolidation.

**Milestone:** scheduler/control-plane foundation.

**Legacy evidence:**
- legacy feature ledger category A row 2;
- `skill/ops-brief-policy/SKILL.md` prohibits separate active Ops/lifecycle/job-watch, retry, child, 3:00, UTC, Pacific and duplicate jobs;
- PR #31 `project/FEATURES.yaml` `MIRA-F009` repeats forbidden schedule variants;
- PR #31 `starter/scheduler-planner-contract.json` prohibits feature-specific scheduled tasks by default and prefers attaching compatible cleanup work to existing MIRA cycles.

**Acceptance / verification boundary:** Enumerate the provider scheduler, prove exactly one canonical enabled Ops dispatcher for the configured cycle, prove prohibited variants are absent/disabled, and read back the canonical task definition. This remains unverified until provider state is inspected.

**Compatibility notes:** This does **not** prohibit every future MIRA scheduled task. It prohibits unnecessary duplicate schedules for compatible work. A separate schedule may exist only when a bounded feature proves consolidation would be unsafe or impossible.

---

### `OPS-003` — Canonical runtime clock gate with DST-safe slot matching

**Description:** Scheduled MIRA entry uses the executable runtime's own offset-aware system clock, converts that instant through the IANA timezone `America/New_York`, and decides whether execution belongs to the intended 02:45/14:45 logical slot. It handles daylight-saving transitions using timezone rules, records dispatch delay, allows only bounded lateness, and may wait once for an execution handed off no more than 60 seconds early. A model-supplied, prompt-supplied, device, travel, session, or naive local timestamp is not production clock authority.

**Why it exists / user outcome:** A scheduled system should know what time it actually is. This requirement exists because prior failures demonstrated that merely printing an Eastern-looking timestamp is not evidence that execution occurred in the correct slot.

**Requirement status:** `required by failure evidence`.

**Delivery/evidence:** `test_verified` in the legacy executable and regression suite. **Actual MIRA 2.0 scheduler entry remains integration/live-unverified.**

**Hard dependencies:** trustworthy runtime system clock; IANA timezone database; `OPS-001` canonical slot definition.

**Enables:** scheduler-integrity circuit breaking, correct AM/PM derivation, trustworthy Run Log timestamps, travel-safe brief scheduling.

**Milestone:** scheduler/control-plane foundation.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py`: `canonical_slot_evidence`, DST gap/repeat handling, grace bounds and runtime-owned live slot evidence;
- `skill/ops-brief-policy/scripts/test_ops_policy_entry.py`: tests equivalent summer/winter instants across Eastern/Central/Mountain/Pacific/UTC, bounded early dispatch, bounded delay, naive-time rejection and canonical-slot contradiction;
- `skill/ops-brief-policy/references/brief-run.md`: scheduled slot-check must run without model-supplied `--now`;
- legacy feature ledger category A row 3.

**Acceptance / verification boundary:** Repository tests must pass for DST/offset/grace behavior; then an actual scheduler integration must demonstrate that scheduled entry invokes the live runtime clock path and records matching canonical evidence. Only the latter can raise this feature beyond `test_verified`.

**Compatibility notes:** Future user-configurable timezones must still use the same IANA/runtime-clock model. No deployment may replace this with fixed UTC offsets.

---

### `OPS-004` — Fresh standalone run delivery with deterministic Run ID

**Description:** Every scheduled brief execution starts as a fresh run from the saved dispatcher rather than reusing an old chat response. A scheduled run receives the deterministic identity `OPS-YYYY-MM-DD-AM` or `OPS-YYYY-MM-DD-PM`; the delivered brief begins with that identity and is generated only from current-run state/evidence. The same identity is used for idempotent Run Log updates so retries or completion updates do not create a second logical run.

**Why it exists / user outcome:** The user must be able to distinguish today's actual brief from stale conversational output and determine whether the scheduler entered at all versus failing later in the workflow.

**Requirement status:** `required by stale-response incident`.

**Delivery/evidence:** `test_verified` for deterministic Run ID generation and policy contract; **fresh provider-created standalone scheduled delivery and live Run Log evidence remain unverified in MIRA 2.0**.

**Hard dependencies:** `OPS-003` canonical scheduled timestamp/slot; canonical Run Log/state feature to be audited later in category A; scheduler/provider capable of fresh-run invocation.

**Enables:** idempotent run logging, scheduler incident diagnosis, notification self-identification, stale-response prevention.

**Milestone:** scheduler and Ops Brief delivery foundation.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py` deterministically creates `OPS-{date}-{slot}` Run IDs;
- `skill/ops-brief-policy/scripts/test_ops_policy.py` verifies `OPS-2026-08-15-AM` Run Log identity;
- `skill/ops-brief-policy/references/brief-run.md` requires current-run output and Run ID as the first line;
- `skill/ops-brief-policy/SKILL.md` requires fresh saved-prompt standalone execution;
- legacy feature ledger category A row 4.

**Acceptance / verification boundary:** Tests must verify deterministic identity and idempotent same-row logging semantics. Integration verification requires a scheduled provider run to start fresh, create/update the matching Run Log record, and deliver output beginning with the expected Run ID without reusing prior chat content.

**Compatibility notes:** Manual smoke runs use a separate `OPS-MANUAL-*` namespace and never count as proof of scheduled firing.

---

### `OPS-005` — Deterministic HOME/ROAD context with explicit overrides

**Description:** MIRA resolves the user's operational context deterministically from canonical settings rather than chat inference. The base recurring HOME/ROAD state is defined by configured weekly transitions. An active explicit mode override can temporarily supersede the recurring default, with inclusive start, exclusive expiry, stable override identity, conflict detection, and deterministic precedence. Other later context mechanisms, including active-trip forcing and generic context pairs, are separate audited features and must not silently redefine this record.

**Why it exists / user outcome:** Briefs and actionable tasks must reflect whether the user is operationally HOME or ROAD without guessing from conversation tone, location fragments, or yesterday's state.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for legacy deterministic policy logic. Historical private-deployment claims are not treated as current MIRA 2.0 live evidence.

**Hard dependencies:** canonical settings/state storage; explicit override records; timezone-aware deterministic time parsing. Interaction with active-trip precedence is a separate later category-A feature.

**Enables:** mode-specific task visibility, HOME-only weather, ROAD route/weather behavior, appointment/brief presentation rules, home-early handling.

**Milestone:** operational context foundation.

**Legacy evidence:**
- `skill/ops-brief-policy/scripts/ops_policy.py`: configured `normal_mode`, override preparation and `resolve_mode_at`;
- `skill/ops-brief-policy/scripts/test_ops_policy.py`: weekly-boundary/DST tests plus override start/expiry, latest-start precedence, conflict rejection, uniqueness and Home-early behavior;
- `skill/ops-brief-policy/scripts/test_ops_policy_entry.py`: explicit HOME override beats active trip and active trip interaction is separately exercised;
- `skill/ops-brief-policy/SKILL.md`: mode precedence/invariant;
- legacy feature ledger category A row 5.

**Acceptance / verification boundary:** Deterministic policy tests must pass for weekly boundaries, DST and override conflicts. Integration/live verification later requires canonical MIRA 2.0 state readback showing the configured transitions and an explicit override round trip without reliance on legacy production sheets.

**Compatibility notes:** This record intentionally does not absorb generic context pairs or active-trip forcing. Those are separate features so future generalization cannot erase the current HOME/ROAD semantics or pretend downstream dependencies are already complete.

---

### `CTX-001` — Configurable operating-context pairs

**Description:** MIRA may use a two-label operating-context model when environment materially changes available tasks, equipment, evidence, connectivity, notifications, routes, weather, or routines. Supported/recommended patterns include `HOME / ROAD`, `HOME / TRUCK`, `HOME / FIELD`, `HOME / CAMPUS`, `HOME / AWAY`, and user-defined labels. `HOME / OFFICE` is a valid configured pair even though the audited legacy recommendation heuristic does not contain a dedicated OFFICE rule; it is supported through explicit/custom labels. Context is mutable user state, not identity, employment status, or scheduling timezone.

**Why it exists / user outcome:** Different people need different useful boundaries. A truck driver, field technician, student, office worker, or household user should not inherit somebody else's hard-coded HOME/ROAD worldview.

**Requirement status:** `accepted direction`, with explicit user-defined labels and current HOME/ROAD deployment semantics preserved.

**Delivery/evidence:** `test_verified` in the audited legacy onboarding/context-router candidate for recommended pairs, bypass behavior, custom two-label validation, and explicit selection. **No MIRA 2.0 canonical-state integration is yet verified.**

**Hard dependencies:** mutable profile/context authority; user confirmation/selection state; downstream modules must consume context labels through a contract rather than hard-coded personal assumptions.

**Enables:** reusable mode-specific task/routine/equipment behavior across personal, family, work, school, and later institutional profiles.

**Milestone:** generalized user model / onboarding foundation.

**Legacy evidence:**
- legacy feature ledger category A row 6;
- legacy candidate `starter/PROFILE_AND_CONTEXT_MODES.md` defines dynamic context separately from life profile and lists HOME/ROAD, HOME/TRUCK, HOME/FIELD, HOME/CAMPUS, HOME/AWAY and custom labels;
- legacy candidate `starter/tools/onboarding_profile_router.py` validates explicit two-label custom modes and returns deterministic recommended/bypassed/selected states;
- `starter/tests/test_onboarding_profile_router.py` verifies HOME/ROAD with HOME/TRUCK alternate, HOME/FIELD, custom labels, bypass, and timezone independence.

**Acceptance / verification boundary:** The generalized feature is integration-verified only after a MIRA 2.0 sandbox profile can store/read back selected labels and at least one downstream module consumes them without changing the canonical schedule timezone. Recommendation support for a label is distinct from explicit custom-label support.

**Compatibility notes:** Existing `OPS-005` remains the audited current deployment's HOME/ROAD transition/override behavior. Generalization must adapt that behavior through configured labels rather than deleting its proven semantics.

---

### `CTX-002` — Evidence-gated context recommendation and explicit activation

**Description:** Job title and duties may inform a context recommendation, but MIRA must never silently activate a context split from keywords or assumptions. Onboarding asks whether a recurring away/alternate environment actually exists; explicit `no` bypasses work-away context, explicit `yes` permits a recommendation that still requires confirmation/rename, and unresolved travel/field evidence remains `needs_confirmation` or `unresolved`. Explicit user labels outrank recommendations.

**Why it exists / user outcome:** A person's job title is useful evidence, not permission for MIRA to invent their lifestyle. The user should get helpful suggestions without waking up to a system that decided a Broadway actor works on the road because a substring matched `road`.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` in the legacy candidate router. **MIRA 2.0 onboarding/UI and canonical readback remain unimplemented/unverified.**

**Hard dependencies:** profile/job/duties intake; `CTX-001`; explicit activation/confirmation state.

**Enables:** low-friction onboarding, safe profile recommendations, Boomer-friendly setup without hidden behavior changes.

**Milestone:** generalized onboarding foundation.

**Legacy evidence:**
- legacy feature ledger category A row 7;
- `starter/PROFILE_AND_CONTEXT_MODES.md` routing contract requires confirmation and prohibits title-only activation;
- `starter/tools/onboarding_profile_router.py` uses word-boundary role-family matching plus explicit `works_away_from_home` state;
- `starter/tests/test_onboarding_profile_router.py` verifies trucker recommendation without silent selection, explicit office-worker bypass, field-role `needs_confirmation`, custom-label precedence, and the Broadway false-match regression.

**Acceptance / verification boundary:** Deterministic router tests must pass, then the MIRA 2.0 onboarding flow must prove that a recommendation cannot become enabled canonical context without explicit user confirmation/readback.

**Compatibility notes:** Recommendation and activation are deliberately separate. This feature must not infer context from employer, profession, age, or device location alone.

---

### `TRIP-001` — Independent trip occurrence lifecycle

**Description:** MIRA tracks each real trip/dispatch occurrence separately from reusable route knowledge, operating context, and paid-work/mileage accounting. Trips have stable identities and lifecycle states such as Planned, Active, Arrived, and Cancelled. An active trip may force ROAD context when no higher-precedence explicit override exists, but changing context does not itself create a Trip and learning a Route does not create a Trip/Mileage occurrence.

**Why it exists / user outcome:** A user can be ROAD without a specific paid trip, can learn a route without having driven it today, and can complete a trip without corrupting route history or payroll state. These are related facts, not the same row wearing four hats.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for core legacy separation/precedence behavior; **MIRA 2.0 trip-state persistence and provider readback remain unverified.**

**Hard dependencies:** canonical trip authority; `OPS-005`/context precedence contract; stable Trip IDs; route linkage only when a route exists.

**Enables:** route/weather watches, location/ETA tracking, multi-leg work cycles, later mileage/pay occurrence linkage, arrival evidence and trip history.

**Milestone:** travel/operational-state foundation.

**Legacy evidence:**
- legacy feature ledger category A row 8;
- `skill/ops-brief-policy/references/state-maintenance.md` explicitly separates reusable Routes, Trip occurrences and Mileage Log occurrences and prohibits creating a Trip merely because a Route changed;
- `skill/ops-brief-policy/references/route-weather.md` preserves Planned/Active/Arrived/Cancelled trip history;
- `skill/ops-brief-policy/scripts/test_ops_policy_entry.py` verifies an active trip survives the weekly HOME boundary and forces ROAD, while an explicit HOME override still wins.

**Acceptance / verification boundary:** MIRA 2.0 must create/update/read back Trip lifecycle state independently of context and mileage, then prove precedence behavior without mutating protected legacy production data.

**Compatibility notes:** Paid mileage and work-cycle accounting are intentionally deferred to the next audit packet. `TRIP-001` may reference those records later but does not make them the same authority.

---

### `ROUTE-001` — Learned routes, directional runtime, location and ETA inference

**Description:** MIRA maintains reusable learned route knowledge separately from Trip occurrences. A route is identified by endpoint pair, supports directional route overviews and directional average runtime, can derive ETA for a trip from departure plus stored runtime when no stronger explicit ETA exists, records user-reported current location/time, and may compute bounded time-progress information for corridor reasoning. Explicit user/company route/runtime corrections outrank older learned values. Multi-leg work is represented as separate trip occurrences rather than assuming the first destination is the final return home.

**Why it exists / user outcome:** MIRA should learn how recurring travel actually works instead of repeatedly asking the same route questions or substituting naive map-distance math for the user's real operating history.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for route-average ETA and related trip/weather primitives; route storage/reversal and progress primitives are implemented/specifically documented. **Human-facing ahead/behind interpretation and MIRA 2.0 live authority integration are not yet independently verified.**

**Hard dependencies:** `TRIP-001`; stable Route IDs and endpoint normalization; trustworthy departure/current-location evidence; explicit precedence for user-supplied ETA/runtime.

**Enables:** trip ETA/status, route-weather corridor scoping, runtime learning, current-location freshness prompts, later ahead/behind estimates and paid-mile occurrence association.

**Milestone:** travel/route foundation.

**Legacy evidence:**
- legacy feature ledger category A row 9;
- `skill/ops-brief-policy/references/route-weather.md` defines one learned route per unordered endpoint pair, directional overview/runtime, reverse fallback and explicit-user precedence;
- `skill/ops-brief-policy/references/state-maintenance.md` separates learned terminal-pair Routes from occurrence history and rejects map/odometer substitutes for paid miles;
- `skill/ops-brief-policy/scripts/ops_policy.py` derives ETA from route average and computes bounded `progress_fraction` from departure/ETA;
- `skill/ops-brief-policy/scripts/test_ops_policy.py` verifies route-average ETA and its use as route-weather watch expiry.

**Acceptance / verification boundary:** Unit tests must cover endpoint matching, directional runtime/route behavior, explicit ETA precedence, current-location handling and progress bounds. Integration verification requires canonical MIRA 2.0 Route + Trip round trips. Ahead/behind claims must remain labeled inference unless compared against observed location/time or other supported evidence.

**Compatibility notes:** Company-paid mileage is a distinct later feature. Route geometry/runtime can be directional even where a future paid-mile policy is symmetric.

---

### `WEATHER-001` — Context-gated HOME and ROAD weather intelligence

**Description:** Weather behavior depends on the user's selected operating context and active travel state. HOME mode permits home-location weather when it materially affects a HOME decision. ROAD mode can activate bounded route/corridor weather and official road-condition checks tied to an active trip/watch. Route watches have explicit/derived expiry and become inactive at expiry; MIRA must distinguish observed official road conditions from forecasts and estimated corridor position.

**Why it exists / user outcome:** The user needs relevant weather, not a generic forecast dumped into every brief. At home, local conditions matter. On the road, a closure, wind restriction, ice, flooding, or severe-storm timing along the remaining route can matter far more than the weather at home.

**Requirement status:** `required`.

**Delivery/evidence:** `test_verified` for deterministic HOME/ROAD weather gates, route-watch eligibility and expiry in legacy policy. The external NWS/DOT/511 evidence workflow is `specified`; **live MIRA 2.0 external-weather integration is not verified.**

**Hard dependencies:** `OPS-005` or generalized `CTX-001` context resolution; `TRIP-001`; `ROUTE-001` for corridor reasoning when applicable; external authoritative weather/road sources for actual hazard conclusions.

**Enables:** concise home-weather decisions, severe-weather route warnings, corridor restriction checks, weather-watch expiration and failure-isolated external evidence.

**Milestone:** travel/brief evidence foundation.

**Legacy evidence:**
- legacy feature ledger category A row 10;
- `skill/ops-brief-policy/scripts/ops_policy.py` returns HOME weather and ROAD route-weather gates plus expiring route-watch state;
- `skill/ops-brief-policy/scripts/test_ops_policy.py` verifies HOME weather allowance, ROAD-only route-weather behavior, route-average watch expiry, exclusive expiry and inactive HOME route watches;
- `skill/ops-brief-policy/references/route-weather.md` specifies NWS plus official DOT/511 corridor checks, timing correlation, current-location preference, and observed-vs-forecast distinction;
- `skill/ops-brief-policy/references/brief-run.md` restricts HOME and ROAD weather evidence to the engine-opened gates.

**Acceptance / verification boundary:** Deterministic gating/expiry tests must pass. Integration verification later requires a MIRA 2.0 sandbox Trip/Route/context state to open the correct gate and an external evidence pass to return source-grounded results without contaminating the opposite context. Provider/source failure must degrade only the weather module.

**Compatibility notes:** Weather location/source choices must be user/deployment configuration. The public repository must not hard-code a private home address or personal route.

## Audit status

- `M2-G0-002A` audited legacy category-A behaviors 1-5 and assigned `OPS-001` through `OPS-005`.
- `M2-G0-002B` audited category-A behaviors 6-10 and assigned `CTX-001`, `CTX-002`, `TRIP-001`, `ROUTE-001`, and `WEATHER-001`.
- The complete historical feature inventory is **not yet imported**. Do not infer absence from this file.
- The next bounded audit begins with legacy category-A behavior 11: company-paid mileage and estimated gross pay on both Thursday briefs.
