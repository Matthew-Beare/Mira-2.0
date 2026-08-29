# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android, Microsoft, Apple/iCloud, Cloud Run, Linux and SQL remain supported later lanes. The immediate product objective is to keep turning the audited feature corpus into functioning user-visible MIRA behavior without losing or rediscovering accepted scope.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`. Completed work remains in the corpus with evidence; it is never deleted merely to shorten an active list.

## Preserved checkpoint — `M2-M0-010`

The Personal starter/distribution branch `integration/m0-010-personal-starter-distribution` was created from `main` at `71ab2278a6a45925f6bb74f9d3628f859d25ab71` but contains no unique commits. It is displaced by the customer's explicit request to reconcile the complete product/feature corpus before further distribution implementation. Resume point: start deterministic Personal starter/distribution work from the then-current merged `main`; no M2-M0-010 implementation needs recovery.

Android remains paused at the exact live queued-writer Apps Script proof checkpoint already recorded in Git history.

## Active packet

### `M2-G0-011` — Product corpus reconciliation and progressive onboarding

- **Primary work:** `FEATURE-ALIGN-001`, `DISCOVERY-CORE-001`
- **Primary features:** `DEV-005`, `DEV-007`, `ONBOARD-003`, `ONBOARD-004`
- **Related invariants/features:** `ONBOARD-005`, `OPS-001`, `SERVICE-001`, `ROUTINE-001`, `WEARABLE-001`, `MEAL-001`, `GROCERY-001`, `RECEIPT-001`, `ASSET-001`, `INV-001`, `EDU-001`, `LOCAL-001`, `STUDIO-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/g0-011-product-corpus-reconciliation`
- **Base SHA:** `71ab2278a6a45925f6bb74f9d3628f859d25ab71`
- **Objective:** make the complete audited MIRA product corpus queryable as a durable lifecycle ledger, reconcile stale implementation status, and extend onboarding so Minimum Useful Setup naturally continues into optional progressive discovery without turning setup into a forty-question hostage situation.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- the canonical feature index already contains 118 stable semantic features covering briefs/tasks, appointments/mail, orders/receipts/finance, assets/fitment/knowledge, inventory/location/movement, groceries/recipes/meals, profiles/permissions, service composition, routines/fitness/accountability, education, travel/mileage, wearables, weather, Android, local/Home Assistant/Plex bridges, voice, backup/recovery, provider portability and enterprise deployment;
- `ONBOARD-003` already owns the four-question Minimum Useful Setup and currently only offers later continuation in prose;
- `ONBOARD-004` owns deeper capability/friction/context discovery but does not yet define the requested post-four choice or bounded one-question-per-day brief drip;
- F13 maps fitness/accountability to `ROUTINE-001` + task/service semantics rather than creating a second fitness authority;
- F22 / `WEARABLE-001` already preserves optional smartwatch/activity ingestion;
- `MEAL-001`, `GROCERY-001`, `RECEIPT-*`, `ASSET-*`, `INV-*`, `EDU-001`, `LOCAL-001`, and the other major life domains are already in the canonical corpus and must not be rediscovered as new features merely because implementation is pending.

### `BACKLOG.md`

Verified before implementation:

- completed forensic audits A-G remain durable, including bounded audits for receipts, assets, inventory, meals, roles, fitness/routines, education, travel, backup, knowledge, Android and provider foundations;
- implementation work is retained rather than removed after completion, but stale status metadata exists: `FIRSTBOOT-CORE-001`, `SERVICE-STATE-001`, and `ONBOARD-INSTRUCTIONS` have already merged evidence yet still require canonical backlog status reconciliation;
- `FEATURE-ALIGN-001` is the existing governance work for packet/feature drift automation;
- `DISCOVERY-CORE-001` is the existing deeper onboarding/discovery work and is the correct implementation home for progressive post-setup discovery rather than inventing a parallel onboarding subsystem.

### `ROADMAP.md`

Verified before implementation:

- useful no-app Personal MIRA remains ahead of Android expansion;
- feature-corpus reconciliation is a foundational multiplier because it prevents completed work being reselected and prevents accepted features disappearing while implementation proceeds;
- progressive onboarding should feed later verticals without blocking immediate use of MIRA.

### Direction result

**ALIGNED.** Reconciliation and progressive onboarding directly address the customer's stated failure mode: too much rediscovery, stale work status and no durable mechanism for continuously selecting the next unimplemented accepted feature.

## Historical corpus finding

A new history pass across available MIRA/LyfeOS conversations and the existing audit PRs confirms that much of the requested whole-life scope has already been normalized into Git. The work is not to create another feature list; it is to make the existing list operationally trustworthy and add newly clarified behavior.

Preserved major domains include:

- Ops Briefs, contexts, tasks, routines, reminders and accountability;
- appointments, Calendar projection, email triage and communication safety;
- orders, shipments, receipts, returns/refunds, spending, reimbursement and optional finance/subscriptions;
- assets, vehicles/equipment, identifiers, fitment, maintenance/warranties, manuals, technical specs and knowledge;
- inventory, intended/observed location, QR/barcode movement, par levels and optional passive sensing;
- groceries, pantry/freezer, recipes, meal planning and shopping intent;
- work/self-employment, retired/nonworking, student, caregiver, household, parent/dependent and permission scopes;
- travel/work trips/routes/mileage, education/study and offline preparation;
- optional health administration, fitness/routine accountability, wearable/activity ingestion and weather preferences;
- Android/mobile, voice, Home Assistant/Plex/local bridges, Google/Microsoft/Apple provider lanes, enterprise/managed deployment, backup/recovery and future SQL/private backends;
- MIRA Studio, bounded custom features and controlled sharing.

## Newly clarified onboarding behavior

The product contract for the next implementation must be:

1. The first four Minimum Useful Setup questions remain exactly the current canonical four.
2. Immediately after question four, MIRA asks a simple choice: **continue setup now** or **start using MIRA**.
3. Choosing continue enters progressive discovery immediately, one topic at a time, with the user able to stop at any point.
4. Choosing start using MIRA must not abandon discovery. For up to seven local calendar days, an eligible Ops Brief may include at most one short discovery prompt. No more than one discovery topic is emitted per local day, and the user can dismiss/disable the drip at any time.
5. The first progressive topic should explicitly offer fitness/activity/nutrition/weight-goal help. If accepted, the immediate branch asks what the user's goals are and what kind of help they want. This is preference/service discovery, not a new canonical `FITNESS-*` authority and not medical diagnosis.
6. Subsequent discovery topics cover high-value existing domains such as meal/grocery planning, household/routines, education/study, receipts/assets/inventory, travel/work tracking, and optional connected integrations such as wearables/local smart-home services.
7. Positive answers create explicit intent/preferences and follow existing service/capability gates. They never silently activate providers or claim integrations work.
8. Discovery remembers answered/declined/skipped topics so it does not repeatedly ask the same question. Silence never counts as an answer.
9. MIRA Studio remains available later for continued refinement beyond the initial seven-day drip.

## Lifecycle-ledger behavior required

The repository must expose one deterministic machine-readable product ledger derived from Git authorities, not a second editable database.

For every feature, expose at minimum:

- stable feature ID;
- title;
- requirement state;
- raw evidence state;
- dependencies.

For every backlog work item, expose at minimum:

- stable work ID;
- class;
- work description;
- dependencies;
- raw status;
- normalized lifecycle state such as `completed`, `active`, `queued`, `deferred`, `paused`, `provisional`, `split`, or `unknown`.

Completed work remains visible forever unless explicitly superseded/rejected. The ledger must make completed work easy to exclude from next-work selection without deleting its history.

## Acceptance criteria

1. Deterministic product-ledger generator combines `FEATURES.md` and `BACKLOG.md` without creating a second editable authority.
2. Duplicate work IDs fail validation.
3. Work-status normalization is deterministic and conservative; ambiguous status never becomes completed by inference.
4. CLI can validate the corpus and emit JSON suitable for later dashboard/database projection.
5. CI runs the corpus/lifecycle validation every PR.
6. Known stale completed backlog rows are reconciled against merged PR evidence rather than deleted.
7. `ONBOARD-003` completion orientation exposes the continue-now vs start-using-MIRA choice.
8. Provider-neutral progressive discovery persists answered/skipped topic state and resumes deterministically.
9. Brief-drip selection emits no more than one topic per supplied local date and stops after seven topic-days or explicit disablement.
10. Fitness/wellness discovery branches to goals when accepted while preserving explicit service/capability boundaries.
11. Tests cover continue-now, start-using-MIRA, daily dedupe, seven-day exhaustion, opt-out, fitness accept/decline/goal branch and restart/resume.
12. Code ownership/evidence remains valid.
13. End-of-session recheck confirms accepted receipts, meals, inventory, wearables, local integrations and other major domains remain present and ranked.

## Exact next action

1. Implement the deterministic product lifecycle ledger and CI check.
2. Reconcile the known stale completed backlog statuses from PRs #58-#60.
3. Extend provider-neutral onboarding with the post-four choice and progressive discovery ledger/drip behavior.
4. Update direct tests and ownership evidence.
5. Re-run FEATURES/BACKLOG/ROADMAP alignment and CI on the exact PR head.
6. Merge only when green, then resume the highest-value uncompleted no-app work from the lifecycle ledger rather than conversational memory.

## Recovery protocol

Read this file first. Continue on `integration/g0-011-product-corpus-reconciliation`. Do not resume the empty M2-M0-010 distribution branch or Android until this reconciliation packet closes. Git feature/work authorities remain canonical; conversation history is discovery evidence used to reconcile them, not a replacement authority.