# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point.

## Product deployment invariant

Default Personal MIRA is Google Workspace first and zero external infrastructure. Stock ChatGPT + Google Drive/Sheets/Docs must become meaningfully useful before Android or advanced infrastructure becomes the development focus. Android, Microsoft, and Apple/iCloud remain preserved extension/provider lanes.

## Work-session direction rule

Every development work session begins and ends with an explicit review of `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`. CI runs `python -m mira.work_session_alignment check` to mechanically verify active work/feature IDs and the recorded session-start authority review. Semantic priority remains the developer's responsibility.

## Preserved Android checkpoint

`M2-M1-001` remains paused by explicit customer reprioritization. Its exact resume point is the live isolated Google queued-writer Apps Script proof already recorded in Git history. Do not redesign or restart Android architecture when it resumes.

## Completed predecessor

### `M2-M0-007` — No-app first-boot Interview Ledger

Merged to `main` in PR #58 at `a60e8879e71b8f464eb1de1ea8cc15cbd309eccb` after latest-head CI `33279406547` passed.

Completed evidence:

- provider-neutral four-question `InterviewLedgerService` implemented and test-verified;
- fixed MIRA name is never asked;
- resume/order/re-answer behavior is deterministic;
- appointment Calendar preference remains separate from capability/projection/service activation;
- work-session FEATURES/BACKLOG/ROADMAP alignment gate is in CI;
- isolated Google Workspace persistence/readback compatibility for synthetic onboarding state verified without modifying the clean source template.

## Active packet

### `M2-M0-008` — Explicit service state foundation

- **Primary work:** `SERVICE-STATE-001`
- **Primary features:** `SERVICE-001`, `SERVICE-002`
- **Related invariants/features:** `ONBOARD-003`, `CAL-006`, `RECOVERY-002`, `STORE-001`, `API-001`, `PROVIDER-001`, `TASK-001`, `OPS-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-008-service-state`
- **Base SHA:** `a60e8879e71b8f464eb1de1ea8cc15cbd309eccb`
- **Pull request:** #59
- **Head before closeout checkpoint:** `c9d9f7fbe6bfd018f91795325c2b560f17c5027d`
- **Status:** implementation complete; direct service-state tests passed in the first CI run; one stale repository-alignment test was corrected; isolated Google persistence/readback verified; latest-head CI pending.
- **Objective:** provide one durable provider-neutral service-state model where user intent, recommendation, capability/readiness, and actual activation are separate truths, so onboarding can request help without silently enabling unsupported behavior.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `SERVICE-001` requires explicit finite service activation state separate from capability and recommendation.
- `SERVICE-002` requires activatable service bundles with dependency-derived readiness rather than merely assuming configured capability.
- `ONBOARD-003` may capture appointment-help preference but must not silently activate services.
- `CAL-006` requires preferred Calendar projection only through verified provider capability/readback.
- `PROVIDER-001` keeps provider capability routing evidence-based rather than assumed.
- `RECOVERY-002` requires failure isolation between modules/services.

### `BACKLOG.md`

Verified before implementation:

- `SERVICE-STATE-001` already exists as a no-app prerequisite.
- `SERVICE-COMPOSE-001` and `SERVICE-DEPS-001` through `SERVICE-DEPS-010` remain separate follow-on dependency/composition packets and were not dragged wholesale into this packet.
- `OPS-BRIEF-VSLICE` remains a candidate first no-app user-visible vertical once minimum service composition exists.
- appointments, receipts/assets/inventory, and Android remain preserved backlog work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 explicitly orders `FIRSTBOOT-CORE-001` then `SERVICE-STATE-001` / minimal service composition before the first no-app user-visible vertical;
- M2-M0.5 prohibits expanding this packet into the entire product;
- Android remains after a real no-app Personal vertical unless a hard dependency changes the order.

### Direction result

**ALIGNED.** `SERVICE-STATE-001` is the hard prerequisite between completed first boot and safely activating the first useful no-app service.

## Implemented behavior

`mira/service_state.py` implements the bounded provider-neutral state machine over the existing `StructuredStateAdapter`.

Durable truths are separate:

- activation state: `disabled`, `requested`, `active`, or `suspended`;
- capability state: `unknown`, `unavailable`, or `available`;
- recommendation state: `none` or `suggested`;
- explicit dependency blockers;
- suspension reason.

Behavior:

1. a new service begins disabled with unknown capability;
2. `request_enable()` records user intent but never activates;
3. `recommend()` records a suggestion without creating user intent or activation;
4. `activate()` requires explicit prior user intent plus verified available capability and zero blockers;
5. blocked or unknown readiness fails closed;
6. readiness loss while active moves the service to `suspended` and clears effective-active truth;
7. readiness recovery never silently reactivates a suspended service; explicit activation is required again;
8. disable preserves durable service identity/history rather than deleting the record;
9. exact repeated transitions are read-only replay rather than needless revision growth;
10. onboarding appointment intent maps to `appointments_calendar=requested` when help is wanted, with capability still unknown and effective activation false.

## Verification evidence

### Direct tests

`tests/test_service_state.py` covers:

- fresh disabled/unknown state;
- request without activation;
- recommendation without request/activation;
- activation requiring user intent;
- activation blocked by unknown capability or explicit dependency blockers;
- successful activation only when requested and ready;
- readiness loss suspension;
- readiness recovery without silent reactivation;
- explicit resume;
- disable with stable identity;
- read-only replay;
- onboarding appointment intent request mapping;
- onboarding decline remaining disabled.

The first PR #59 CI run showed all service-state tests passing. It failed only because `tests/test_work_session_alignment.py` still asserted the previous packet ID `M2-M0-007`; that stale test was corrected to validate the live repository packet generically instead of hard-coding a permanent packet ID.

### Google Workspace state proof

The same isolated synthetic no-app proof workbook used for first boot was extended; the clean source template remained untouched.

Provider readback verified:

- `service_state` added to the synthetic `resource_types_json` alongside `onboarding_ledger`;
- synthetic `appointments_calendar` service persisted at revision 2 after an onboarding-derived request;
- persisted activation state is `requested`;
- capability state is `unknown`;
- dependency blockers are empty;
- recommendation state is `none`;
- there is no effective activation claim;
- both synthetic upsert idempotency records and deterministic request hashes read back exactly;
- edited backend rows retain readable wrap/vertical formatting.

This is provider persistence/readback compatibility evidence, not a claim that Calendar provider capability has been verified or Calendar sync activated.

## Acceptance status

1. Provider-neutral `service_state` schema/state machine — **passed**.
2. Finite activation states explicit/validated — **passed**.
3. Capability/readiness/recommendation separate from activation — **passed**.
4. Request never activates — **passed**.
5. Activation fails closed unless ready — **passed**.
6. Readiness loss stops effective activation — **passed**.
7. Disable preserves durable identity — **passed**.
8. Expected revisions/idempotent structured-state persistence — **passed**.
9. Direct transition/onboarding mapping tests — **passed**.
10. Production ownership/evidence — **passed**.
11. Latest-head CI — **pending after stale test correction and this closeout commit**.
12. Session-end alignment review — **passed below**.

## Session-end alignment verification — 2026-08-29

### `FEATURES.md`

Re-read after implementation. `SERVICE-001` is directly implemented by this bounded state machine; `SERVICE-002` remains broader because dependency-derived bundle composition is intentionally not claimed complete. `ONBOARD-003`, `CAL-006`, `PROVIDER-001`, `RECOVERY-002`, `OPS-001`, and `TASK-001` remain structurally compatible. No Android, receipt, asset, inventory, appointment-provider, Microsoft, or Apple feature was removed or weakened.

### `BACKLOG.md`

Re-read after implementation. `SERVICE-STATE-001` has implementation/test/provider-state evidence on this branch. `SERVICE-COMPOSE-001` remains the next minimal composition prerequisite; the `SERVICE-DEPS-*` family remains later bounded repair work rather than being silently absorbed here. `OPS-BRIEF-VSLICE` remains the leading first user-visible no-app candidate once minimal composition can declare whether it is actually ready.

### `ROADMAP.md`

Re-read after implementation. This packet satisfies the second M2-M0.5 foundation step without expanding into a complete service engine. Direction remains toward the smallest stock-ChatGPT user-visible vertical, not Android or external infrastructure.

### Direction result

**ALIGNED.** The packet closes a real safety/integrity gap between onboarding intent and service execution while preserving all accepted downstream feature families.

## Exact next action

1. Verify latest-head PR #59 CI after this closeout commit.
2. Repair only if the latest head is red; do not bypass the failure.
3. Merge PR #59 only after latest-head CI is green and remotely verify `main`.
4. Start the smallest bounded `SERVICE-COMPOSE-001` slice needed to compute readiness for the first no-app vertical.
5. Drive immediately into the first stock-ChatGPT user-visible vertical, with Ops Brief/tasks as the current default candidate unless the session-start dependency/value check selects a shorter higher-value slice.
6. Do not resume Android merely because its live provider proof remains pending.

## Recovery protocol

Read this file first. If PR #59 is open, inspect the latest head and CI. If merged, verify main and create the next M2-M0.5 service-composition packet. Android remains paused at its exact Git-backed provider-proof checkpoint. Keep personal/provider identifiers and live production state out of public Git.
