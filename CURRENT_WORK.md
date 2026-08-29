# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Completed work stays in the product corpus with evidence and is filtered from future selection rather than deleted. The current priority is now user-visible no-app usefulness, not more generic infrastructure.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Completed predecessor

### `M2-M0-010` — Deterministic Personal Google starter distribution

Merged in PR #62 to `main` at `9bf241f694e9bd52c846416336e0704a31fe7d8c` after exact-head CI `33281585486` passed. The Personal Google spreadsheet substrate is now reproducible from Git via a sanitized blueprint and source-SHA-bound release manifest. An independently created blank Google Sheet was built from the blueprint and read back with exact clean Metadata/headers and zero mutable state rows. Bound Apps Script source-to-provider installation remains a separate installer/provider-capability gap and was not overclaimed.

`DIST-STARTER-001` and `STARTER-SANITIZE-001` are completed by PR #62 and must be reconciled to completed in `BACKLOG.md` in this packet.

## Preserved checkpoints

- Android / `M2-M1-001` remains paused at the live isolated Google queued-writer proof point. Synthetic command-boundary work remains intact.
- `DISCOVERY-CORE-001` remains partial: progressive discovery is merged/test-verified; broader evidence-aware history/friction discovery remains unfinished.
- `NONTECH-INSTALL-001` remains queued: full browser installation of bound Apps Script/provider authorization is not silently pulled into this vertical.

## Active packet

### `M2-M0-011` — First useful no-app Ops Brief + canonical tasks

- **Primary work:** `OPS-BRIEF-VSLICE`
- **Primary features:** `OPS-001`, `OPS-003`, `OPS-004`, `TASK-001`, `TASK-002`
- **Related invariants/features:** `RECOVERY-001`, `RECOVERY-002`, `ONBOARD-004`, `OPS-005`, `STORE-001`, `AUTH-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-011-no-app-ops-brief`
- **Base SHA:** `9bf241f694e9bd52c846416336e0704a31fe7d8c`
- **Objective:** make stock-ChatGPT Personal MIRA produce one genuinely useful deterministic Ops Brief from canonical Google-backed task state, while preserving the existing twice-daily slot/run semantics and optionally inserting the already-implemented progressive-discovery prompt without making Android, Cloud Run, generic runtime routing, orders, weather, email, or Calendar prerequisites for the first brief.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `TASK-001` requires structured task hierarchy and one-action-per-item rendering;
- `TASK-002` requires evidence-grounded next actions and honest completion state;
- `OPS-003` already owns canonical DST-safe slot matching semantics;
- `OPS-004` requires fresh standalone run delivery with deterministic Run ID;
- `OPS-001` owns the canonical twice-daily brief schedule and depends on OPS-003/OPS-004;
- `RECOVERY-001` requires durable run identity/checkpoint behavior;
- `ONBOARD-004` progressive discovery may contribute at most one bounded discovery prompt per local day and must never advance on silence;
- `OPS-005`, weather, appointments, orders, mail, mileage and other sections remain accepted future brief inputs but are not required to prove the first task-centered no-app vertical.

### `BACKLOG.md`

Verified before implementation:

- `OPS-BRIEF-VSLICE` is still provisional and currently points at broad `SERVICE-COMPOSE-001` / `SERVICE-DEPS-001` prerequisites;
- those broad service/runtime dependencies are excessive for a first same-user stock-ChatGPT task brief because a deterministic renderer can read canonical task/onboarding state directly through the existing `STORE-001`/Authority substrate;
- `SERVICE-COMPOSE-001` remains necessary for broader multi-service readiness/activation later, but must not delay the minimal task/brief vertical;
- no dedicated task-core work ID currently exists; this packet will keep `OPS-BRIEF-VSLICE` as the bounded work item rather than creating a parallel task project unless implementation proves a reusable prerequisite must be split.

### `ROADMAP.md`

Verified before implementation:

- the roadmap explicitly requires at least one meaningful user-visible no-app vertical before Android resumes;
- M2-M2 Ops Brief is the default candidate and may move into the no-app milestone when it is the shortest high-value slice;
- progressive discovery may use an eligible brief slot but must not displace operational content;
- broad installer/runtime work must not expand this packet.

### Direction result

**ALIGNED.** A canonical task-centered Ops Brief is the shortest currently identified route from proven substrate/onboarding to visible Personal MIRA value. Generic service composition is intentionally deferred from this first vertical unless a concrete acceptance dependency emerges.

## Dependency refinement decision

For this bounded vertical, the actual hard prerequisites are:

- canonical structured-state semantics (`STORE-001`);
- a valid Personal Authority binding for the new `task` and `ops_brief_run` data classes;
- deterministic task identity/state and one-action rendering (`TASK-001`, `TASK-002`);
- deterministic brief slot/run identity (`OPS-003`, `OPS-004`, `RECOVERY-001`);
- existing progressive discovery state only when a discovery prompt is eligible.

The following remain explicitly **not required** for the first task brief:

- generic AI runtime router/source lanes;
- Cloud Run;
- Android;
- full `SERVICE-COMPOSE-001` / `SERVICE-DEPS-001` fan-out;
- Gmail/Calendar provider bootstrap;
- weather, orders, shipments, mileage or finance sections;
- live scheduler firing. The packet proves deterministic slot/run composition and stock-ChatGPT rendering; actual scheduled automation delivery can layer on that contract without redefining brief content/state.

## Required user-visible behavior

1. MIRA can create/update/complete canonical tasks without deleting completed task history.
2. Each task has a stable ID, title, explicit next action, priority, state, optional due date, optional context and optional parent task.
3. Completion is explicit; omitted/silent evidence never marks a task complete.
4. A brief for a supplied authoritative IANA timezone/local datetime resolves a canonical AM/PM slot and deterministic Run ID.
5. Active tasks render in deterministic priority/due ordering with exactly one action per line.
6. Completed/cancelled tasks do not appear as active brief actions but remain queryable canonical state.
7. A brief can optionally include one progressive-discovery prompt when eligible; it never emits a second discovery topic for the same local date and silence never advances discovery.
8. Re-rendering the same run from unchanged canonical state is deterministic.
9. The first vertical is useful even if weather/orders/calendar/mail/mileage are unavailable; unavailable sections are omitted rather than fabricated.
10. No user must run Python, Git, Linux, SQL, Cloud Run or Android to use the no-app task/brief behavior.

## Acceptance criteria

1. Provider-neutral canonical Task service over `STORE-001` with validation, create/update/complete/reopen/read/query semantics and stable revisions/idempotency.
2. New `task` data class is added to the Personal Google starter schema and Authority bootstrap/readback path without creating a second authority.
3. Provider-neutral Ops Brief composer produces deterministic slot/run identity and deterministic task ordering/rendering.
4. `ops_brief_run` canonical resource records the rendered run/checkpoint without pretending delivery occurred.
5. Progressive-discovery integration obeys one-topic-per-local-day and silence rules.
6. Direct tests cover task creation, update, completion preservation, invalid transitions, due/priority ordering, deterministic rerender, AM/PM slot IDs, discovery insertion/dedupe and omission of unavailable sections.
7. Stock-ChatGPT no-app instructions are updated to use the task/brief contract and distinguish composition from actual scheduled delivery.
8. Personal starter blueprint/manifest remains deterministic after adding required resource types.
9. Code ownership covers new domain components.
10. CI is green on exact PR head.
11. Where connector capability permits, create canonical synthetic task/run state in an isolated Google starter and read it back exactly; never touch legacy production.
12. End-of-session feature/lifecycle reconciliation marks PR #62 distribution work completed and preserves all broader brief/domain features for future vertical expansion.

## Exact next action

1. Implement canonical task state and task service.
2. Implement deterministic Ops Brief composer/run checkpoint with progressive-discovery integration.
3. Extend Personal starter schema/Authority bootstrap/no-app instructions for `task` and `ops_brief_run`.
4. Add direct tests and ownership evidence.
5. Reconcile `BACKLOG.md` distribution completion and narrow `OPS-BRIEF-VSLICE` dependencies/status to this active packet.
6. Run CI and isolated Google provider proof.
7. Recheck FEATURES/BACKLOG/ROADMAP, merge when exact-head green, then select the next user-visible vertical.

## Recovery protocol

Read this file first. Continue on `integration/m0-011-no-app-ops-brief`. Do not broaden this packet into the full service router, scheduler platform, Android, or every historical Ops Brief section. The acceptance target is one real canonical task brief in stock ChatGPT.