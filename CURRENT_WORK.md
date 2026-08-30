# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work stays in the product corpus with evidence and is filtered from future selection rather than deleted. The current priority is repeated user-visible no-app verticals, not generic infrastructure growth.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-010` — Deterministic Personal Google starter distribution

Merged in PR #62 to `main` at `9bf241f694e9bd52c846416336e0704a31fe7d8c` after exact-head CI `33281585486` passed. `DIST-STARTER-001` and `STARTER-SANITIZE-001` are reconciled completed in `BACKLOG.md` with Git-source, CI and independent Google substrate evidence.

## Preserved checkpoints

- Android / `M2-M1-001` remains paused at the live isolated Google queued-writer proof point; synthetic command-boundary work remains intact.
- `DISCOVERY-CORE-001` remains partial: progressive discovery is test-verified, including repeat-without-silent-advance; broader evidence-aware history/friction discovery remains unfinished.
- `NONTECH-INSTALL-001` remains queued: full browser installation of bound Apps Script/provider authorization is not part of this vertical.

## Active packet

### `M2-M0-011` — First useful no-app Ops Brief + canonical tasks

- **Primary work:** `OPS-BRIEF-VSLICE`
- **Primary features:** `OPS-001`, `OPS-003`, `OPS-004`, `TASK-001`, `TASK-002`
- **Related invariants/features:** `RECOVERY-001`, `RECOVERY-002`, `ONBOARD-004`, `OPS-005`, `STORE-001`, `AUTH-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-011-no-app-ops-brief`
- **Base SHA:** `9bf241f694e9bd52c846416336e0704a31fe7d8c`
- **PR:** #63
- **Objective:** make stock-ChatGPT Personal MIRA produce one genuinely useful deterministic Ops Brief from canonical Google-backed task state without making Android, Cloud Run, generic runtime routing, orders, weather, email, Calendar or the full service-composition stack prerequisites.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `TASK-001` requires structured task hierarchy and one-action-per-item rendering;
- `TASK-002` requires evidence-grounded next actions and honest completion state;
- `OPS-003` owns canonical DST-safe slot matching;
- `OPS-004` owns deterministic Run ID/fresh-run semantics;
- `OPS-001` owns the twice-daily brief schedule;
- `RECOVERY-001` requires durable run identity/checkpoint behavior;
- `ONBOARD-004` permits at most one bounded discovery prompt per local day with no inference from silence;
- weather, appointments, orders, mail, mileage and other accepted brief inputs are not prerequisites for the first task-centered vertical.

### `BACKLOG.md`

Verified before implementation and refined during the packet:

- the original `OPS-BRIEF-VSLICE` row over-required broad `SERVICE-COMPOSE-001` / `SERVICE-DEPS-001` work;
- the bounded same-user task brief instead depends on `STORE-001`, `TASK-001`, `TASK-002`, `OPS-003`, `OPS-004`, and `RECOVERY-001`;
- generic service composition remains valid for richer later briefs but no longer blocks the first useful no-app vertical;
- PR #62 distribution work is now reconciled completed rather than left active/queued.

### `ROADMAP.md`

Verified before implementation:

- useful no-app Personal MIRA must precede Android focus;
- Ops Brief/tasks is explicitly allowed to become the first user-visible no-app vertical;
- progressive discovery may use an eligible brief slot but must not displace operational content;
- broad installer/runtime work must not expand this packet.

### Direction result

**ALIGNED.** The task-centered Ops Brief is the shortest high-value route from proven substrate/onboarding to visible Personal MIRA behavior.

## Implemented evidence

### Canonical task state

`mira/tasks.py` implements durable provider-neutral `task` resources over STORE-001 semantics:

- stable task ID and revision;
- explicit title and exactly one actionable `next_action`;
- `high` / `medium` / `low` priority;
- `open` / `completed` / `cancelled` state;
- optional due date, context and parent task;
- offset-aware `completed_at` only for completed tasks;
- create/read/update/complete/cancel/reopen/query behavior;
- completed/cancelled history is retained rather than deleted;
- editing completed/cancelled history requires explicit reopen;
- active ordering is deterministic by priority, dated-before-undated, due date and stable ID;
- null context is eligible everywhere; context-specific tasks only appear in the matching brief context.

### Deterministic Ops Brief composition

`mira/ops_brief.py` implements the first no-app brief vertical:

- canonical local AM slot `02:45` and PM slot `14:45`;
- IANA/ZoneInfo conversion for DST-safe clock matching;
- deterministic run IDs `ops-brief:<YYYY-MM-DD>:am|pm`;
- active canonical task selection and context filtering;
- priority/due ordering and one-action-per-line rendering;
- overdue/due-today/future-due markers;
- unavailable weather/orders/email/calendar/mileage sections are omitted, not fabricated;
- one immutable `ops_brief_run` checkpoint per slot;
- exact task IDs/revisions and SHA-256 source fingerprint stored with the rendered text;
- `status=composed`, `delivered=false` so composition is never misrepresented as scheduled delivery;
- same run ID replays the original checkpoint even if task state later changes; a later slot may reflect new canonical state.

### Progressive discovery integration

The first brief vertical now integrates the already-accepted optional discovery flow:

- no more than one discovery prompt appears on one local date across AM/PM runs;
- unanswered topic may repeat on a later local day;
- silence never counts as decline and never advances to another topic;
- seven automatic prompt-days maximum, after which drip pauses with unanswered state intact;
- if fitness is accepted but goals/details are still pending, the next eligible brief renders the goals follow-up rather than repeating the initial yes/no fitness question;
- operational task content always precedes optional setup content.

### Personal Google/no-app contract

The Personal starter/resource contract now includes `task` and `ops_brief_run` alongside existing authority/onboarding/service resources.

`workspace/apps_script/MIRA_NO_APP_INSTRUCTIONS.md` now defines:

- task authority binding and task state semantics;
- explicit completion/cancel/reopen rules;
- canonical brief slot/run rules;
- deterministic task rendering;
- immutable brief checkpoint semantics;
- progressive-discovery insertion rules;
- explicit distinction between composition and actual delivery.

`mira.personal_distribution` and `mira.workspace_bundle` validate these expanded release requirements.

### Ownership

`project/code_ownership.json` now includes:

- `canonical-tasks` for `mira/tasks.py` with `tests/test_tasks.py`;
- `personal-ops-brief` for `mira/ops_brief.py` with `tests/test_ops_brief.py`.

## Independent Google provider proof — 2026-08-29

A newly created isolated synthetic Google spreadsheet, never a legacy production artifact, was built with the expanded Personal starter metadata and exact STORE-001 tables.

Provider readback verified:

- one synthetic Personal Google authority;
- `authority_binding/binding-task` -> `task`;
- `authority_binding/binding-ops-brief-run` -> `ops_brief_run`;
- one canonical open high-priority home task with stable ID/revision/payload/request hash;
- one canonical AM brief run with deterministic run ID, exact task revision input, exact rendered text, source fingerprint, request hash and matching Idempotency result;
- brief persisted as `status=composed` and `delivered=false`;
- Metadata exactly advertises the expanded resource type set.

The synthetic spreadsheet was renamed after proof so it cannot be mistaken for an installable starter. Its provider resource identifier is not committed to public Git.

Durable evidence: `docs/NO_APP_OPS_BRIEF_PROVIDER_PROOF.md`.

This proof **does not** claim a scheduler or notification fired. It proves Google-backed canonical task state plus exact brief composition/checkpoint persistence.

## Test evidence

PR #63 CI run `33282906421` on implementation head `b6718261c2a1eecd6a8875b4630f6d993fa047c4` passed before this closeout-only CURRENT_WORK commit:

- compile — green;
- feature registry — green, 118 features;
- product lifecycle ledger — green, 143 work items with zero unknown states;
- lifecycle states at that head: 52 completed, 74 queued, 1 active, 2 partial, 1 paused, 1 provisional, 10 deferred, 2 split;
- Personal starter distribution/manifest — green;
- work-session alignment — green;
- code ownership — green, 16 components / 24 production artifacts;
- Python unit tests — **189/189 passed**;
- Workspace Apps Script tests — **15/15 passed**.

The direct test set includes the pending-fitness-goals follow-up behavior on a later brief day.

This closeout commit changes governance text only and must receive its own exact-head CI before merge.

## End-of-session alignment verification — 2026-08-29

### `FEATURES.md`

Rechecked after implementation:

- all 118 stable semantic features remain represented;
- task/brief implementation preserves `TASK-001`, `TASK-002`, `OPS-001`, `OPS-003`, `OPS-004`, `RECOVERY-001`, and `ONBOARD-004` semantics;
- receipts/purchases/spending remain preserved;
- assets/fitment/knowledge remain preserved;
- inventory/location/movement remain preserved;
- meals/groceries/recipes remain preserved;
- routines/fitness/accountability and wearables remain preserved;
- appointments/calendar/mail remain preserved;
- education, travel/mileage, local integrations, Android, Microsoft, Apple/iCloud, backup/recovery, voice, enterprise and MIRA Studio remain preserved;
- no parallel task, brief, fitness or provider authority was invented.

### `BACKLOG.md`

Rechecked after implementation:

- all 143 work items remain represented;
- PR #62 distribution items are completed with evidence, not deleted;
- `DISCOVERY-CORE-001` remains partial because broader history/friction discovery is unfinished;
- `OPS-BRIEF-VSLICE` is the only active item in this packet and has narrow real dependencies rather than generic runtime/service fan-out;
- Android command boundary remains partial and Cloud Run advanced proof remains paused;
- appointments, receipts/assets/inventory, meals/groceries and other user-visible domains remain unfinished/selectable for subsequent packets.

### `ROADMAP.md`

Rechecked after implementation:

- the useful no-app milestone requirement is now materially satisfied by a real canonical task/brief vertical, pending merge;
- broader scheduled delivery, installer hardening and richer brief sections remain separate work;
- the roadmap still requires continued user-visible vertical progress rather than immediately returning to Android or generic infrastructure.

### Direction result

**ALIGNED.** MIRA now has an end-to-end task-centered no-app product slice rather than another substrate-only proof.

## Acceptance result

1. Canonical Task service with explicit state/history/idempotency — PASS.
2. `task` and `ops_brief_run` Personal Google resource/authority contract — PASS.
3. Deterministic slot/run identity and task ordering/rendering — PASS.
4. Immutable composed/not-delivered canonical run checkpoint — PASS.
5. Progressive discovery one-day/repeat-without-advance/follow-up behavior — PASS.
6. Direct task/brief/discovery tests — PASS.
7. Stock-ChatGPT no-app operating contract — PASS.
8. Deterministic Personal starter/manifest after schema expansion — PASS.
9. Code ownership — PASS.
10. Implementation-head CI — PASS.
11. Isolated Google canonical task/run exact readback — PASS.
12. Whole-life feature/lifecycle preservation and PR #62 reconciliation — PASS.

## Exact next action

1. Run CI on this exact closeout head.
2. If green, merge PR #63 with exact expected head SHA and remotely verify `main`.
3. In the next packet, reconcile `OPS-BRIEF-VSLICE` to completed with PR #63 evidence.
4. Dependency-rank the next user-visible no-app vertical. Current candidates are appointment intake/calendar projection, receipts/purchases/assets, inventory/location/movement, meal/grocery planning, or verified scheduled brief delivery; select based on hard prerequisites, vertical value and how much already-tested semantic work can be reused.
5. Keep Android paused unless/until the no-app milestone has enough useful vertical coverage or the customer explicitly reprioritizes it.

## Recovery protocol

Read this file first. If PR #63 is still open, verify the exact head and exact-head CI before merge. If #63 is merged, verify `main`, then create the next bounded user-visible packet from current `main`. Do not broaden unfinished work from conversational memory; use the lifecycle/dependency/value result.