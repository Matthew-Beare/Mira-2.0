# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Android, Microsoft, Apple/iCloud, Cloud Run, Linux and SQL remain supported later lanes. The immediate product objective is repeated user-visible no-app progress while the complete audited product corpus remains durable and queryable.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`. Completed work remains in the corpus with evidence and is filtered from next-work selection rather than deleted.

## Preserved displaced checkpoints

### `M2-M0-010` — Personal starter/distribution

Branch `integration/m0-010-personal-starter-distribution` was created from `main` at `71ab2278a6a45925f6bb74f9d3628f859d25ab71` but contains no unique commits. It was displaced by explicit customer reprioritization. Resume distribution from the then-current merged `main`; no implementation recovery is required.

### Android / `M2-M1-001`

Android remains paused at the previously recorded live isolated Google queued-writer proof checkpoint. Synthetic command-boundary implementation is preserved; do not redesign it when Android resumes.

## Active packet

### `M2-G0-011` — Product corpus reconciliation and progressive onboarding

- **Primary work:** `FEATURE-ALIGN-001`, `DISCOVERY-CORE-001`
- **Primary features:** `DEV-005`, `DEV-007`, `ONBOARD-003`, `ONBOARD-004`
- **Related invariants/features:** `ONBOARD-005`, `OPS-001`, `SERVICE-001`, `ROUTINE-001`, `WEARABLE-001`, `MEAL-001`, `GROCERY-001`, `RECEIPT-001`, `ASSET-001`, `INV-001`, `EDU-001`, `LOCAL-001`, `STUDIO-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/g0-011-product-corpus-reconciliation`
- **Base SHA:** `71ab2278a6a45925f6bb74f9d3628f859d25ab71`
- **PR:** #61
- **Objective:** make the complete audited MIRA product corpus queryable as a durable lifecycle ledger, reconcile stale implementation state, and extend onboarding so Minimum Useful Setup can continue into optional bounded progressive discovery without blocking ordinary MIRA use.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- 118 stable semantic features already cover briefs/tasks, appointments/mail, orders/receipts/finance, assets/fitment/knowledge, inventory/location/movement, groceries/recipes/meals, profiles/permissions, routines/fitness/accountability, education, travel/mileage, wearables, weather, Android, local/Home Assistant/Plex bridges, voice, backup/recovery, provider portability and enterprise deployment;
- `ONBOARD-003` owns the exact four-question Minimum Useful Setup;
- `ONBOARD-004` is the correct home for deeper progressive discovery;
- fitness/accountability remains composed from `ROUTINE-001` + task/service semantics rather than a duplicate fitness authority;
- optional smartwatch/activity ingestion remains `WEARABLE-001`;
- receipts, meals/groceries, assets, inventory, education, local integrations and other whole-life domains are already canonical and must not be repeatedly rediscovered as new features.

### `BACKLOG.md`

Verified before implementation:

- completed forensic audits A-G already preserve the broad historical feature corpus;
- stale completion text existed for first boot/service state/no-app instructions;
- `FEATURE-ALIGN-001` and `DISCOVERY-CORE-001` were existing work IDs and therefore no parallel governance/onboarding subsystem was needed.

### `ROADMAP.md`

Verified before implementation:

- useful no-app Personal MIRA remains ahead of Android expansion;
- lifecycle reconciliation is foundational because it prevents completed work being accidentally reselected;
- deeper onboarding must remain optional and must feed user-visible verticals rather than delay them.

### Direction result

**ALIGNED.** Reconciliation and progressive onboarding directly address the customer's stated failure mode: stale status, repeated rediscovery, and no durable way to select unfinished accepted scope.

## Implemented evidence

### Product lifecycle ledger

`mira/product_ledger.py` now derives one machine-readable product view from `FEATURES.md` + `BACKLOG.md`; it does not create a second editable authority.

Verified behavior:

- parses ranked and unranked canonical work tables;
- fails duplicate work IDs;
- retains raw feature evidence and work status;
- conservatively normalizes work to completed/active/queued/deferred/partial/paused/provisional/split/etc.;
- ambiguous prose is never promoted to completed;
- CLI supports validation, JSON projection, and unfinished-work selection;
- completed/deferred/paused/split/rejected work is excluded from selectable next-work without being deleted;
- CI runs product lifecycle validation before session alignment;
- session alignment now uses the same canonical backlog parser, fixing the old ranked-table blind spot.

Latest verified projection on PR #61 head before closeout:

- 118 features;
- 143 work items;
- 49 completed;
- 76 queued;
- 2 active;
- 1 partial;
- 1 paused;
- 2 provisional;
- 10 deferred;
- 2 split;
- zero unknown lifecycle states.

### Backlog reconciliation

Canonical backlog state now records rather than deletes completed work:

- `FIRSTBOOT-CORE-001` — complete, PR #58 + tests + isolated Google persistence/readback;
- `APPOINTMENT-ONBOARD-001` — complete, fourth-question preference behavior verified without fake provider activation;
- `SERVICE-STATE-001` — complete, PR #59 + tests + isolated Google persistence/readback;
- `ONBOARD-INSTRUCTIONS` — complete, PR #60 + bundled protocol + fresh-copy first-boot provider proof;
- `API-DEPLOYMENT-001B` — paused rather than unknown;
- `ANDROID-COMMAND-BOUNDARY-001` — partial rather than unknown because live Google worker proof is still pending;
- `DISCOVERY-CORE-001` — active/partial: the new progressive slice is implemented/tested while broader evidence-aware history/friction discovery remains unfinished.

### Progressive onboarding

Minimum Useful Setup remains exactly four questions. After question four MIRA now offers:

- **continue setup now**; or
- **start using MIRA**.

Provider-neutral `progressive-discovery` state then supports:

- one topic at a time;
- persistent accepted/declined/skipped/needs-details state;
- restart/resume without repeating completed topics;
- brief-drip mode with at most one new topic per supplied local date;
- silence never counts as an answer and never advances the queue;
- automatic brief discovery stops after seven topic-days or explicit disablement;
- first topic is optional fitness/activity/nutrition/weight-management help;
- a positive fitness answer immediately asks goals/help type;
- later topics cover meals/groceries, household/routines, education/study, receipts/assets/inventory, travel/work tracking and optional connected integrations such as wearables/local smart-home services;
- positive answers remain intent/preferences only and never silently activate providers/services.

The stock-ChatGPT no-app operating instructions and Workspace bundle validation were updated so the actual no-app product contract matches the tested Python behavior.

## Latest test evidence

PR #61 CI run `33281117715` on head `f34275137f5fbd6223127a0e4f26bfeac2bb6f55` passed before this closeout-only CURRENT_WORK commit:

- compile — green;
- feature registry — green;
- product lifecycle ledger — green;
- work-session alignment — green;
- code ownership — green;
- Python unit tests — **167/167 passed**;
- Workspace Apps Script tests — **15/15 passed**.

This closeout commit changes governance text only. It must receive its own latest-head CI before merge.

## End-of-session alignment verification — 2026-08-29

### `FEATURES.md`

Rechecked after implementation:

- all 118 feature IDs remain present;
- receipts/purchases/spending remain preserved;
- groceries/recipes/meal planning remain preserved;
- assets/fitment/knowledge remain preserved;
- inventory/location/movement/par remain preserved;
- routines/fitness/accountability remain preserved;
- education/study remain preserved;
- travel/work-trip/mileage remain preserved;
- `WEARABLE-001` remains preserved;
- `LOCAL-001` Home Assistant/Plex/private-service direction remains preserved;
- Android, Microsoft, Apple/iCloud, backup/recovery, voice, enterprise and MIRA Studio remain preserved;
- no new parallel fitness, meal, inventory, or onboarding authority was invented.

### `BACKLOG.md`

Rechecked after implementation:

- total work-item count remains 143, so reconciliation did not silently delete work;
- known stale completed work was corrected to completed with evidence;
- partial/paused work is now explicit rather than ambiguous;
- unfinished whole-life verticals remain queued/deferred and selectable by lifecycle/dependency/value ranking;
- `DISCOVERY-CORE-001` correctly remains partial because broader evidence-aware history/capability discovery is not finished.

### `ROADMAP.md`

Rechecked after implementation:

- no-app Personal usefulness remains ahead of Android;
- post-four progressive discovery is explicitly optional and bounded;
- deterministic starter/distribution and a meaningful user-visible no-app vertical remain the next milestone concerns;
- completed work remains durable and excluded from reselection by lifecycle state rather than deletion.

### Direction result

**ALIGNED.** The packet improved both product behavior and the mechanism used to keep future implementation pointed at unfinished accepted scope.

## Acceptance result

1. Product ledger over canonical FEATURES/BACKLOG — PASS.
2. Duplicate work-ID validation — PASS.
3. Conservative lifecycle normalization — PASS.
4. JSON/validation/next-work CLI — PASS.
5. CI lifecycle gate — PASS.
6. Stale completed backlog reconciliation — PASS.
7. Post-four continue/use-MIRA choice — PASS.
8. Durable progressive discovery — PASS.
9. One-topic-per-local-date / seven-topic-day limit — PASS.
10. Fitness goals branch with service/capability separation — PASS.
11. Direct progressive-discovery test matrix — PASS.
12. Code ownership/evidence — PASS.
13. End-of-session whole-life feature preservation check — PASS.

## Exact next action

1. Run CI on this exact closeout head.
2. If green, merge PR #61.
3. Remotely verify `main` contains the merge.
4. Mark `FEATURE-ALIGN-001` completed and the progressive portion of `DISCOVERY-CORE-001` test-verified while preserving its broader unfinished scope in the next checkpoint.
5. Select the next highest-value unfinished no-app work using the lifecycle ledger, with deterministic Personal starter/distribution and the first meaningful user-visible vertical as the current leading candidates.

## Recovery protocol

Read this file first. If PR #61 is still open, verify the exact head and CI before merge. If #61 is merged, verify `main`, then create the next bounded packet from current `main`. Do not resume the empty old M2-M0-010 branch or Android by habit; use the lifecycle/dependency/value result. Conversation history remains discovery evidence, not the mutable development authority.