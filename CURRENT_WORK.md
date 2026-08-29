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
- `SERVICE-COMPOSE-001` and `SERVICE-DEPS-001` through `SERVICE-DEPS-010` remain separate follow-on dependency/composition packets and must not be dragged wholesale into this bounded state-machine packet.
- `OPS-BRIEF-VSLICE` remains a candidate first no-app user-visible vertical once the minimum service-state/composition prerequisites exist.
- appointments, receipts/assets/inventory, and Android remain preserved backlog work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 explicitly orders `FIRSTBOOT-CORE-001` then `SERVICE-STATE-001` / minimal service composition before the first no-app user-visible vertical;
- M2-M0.5 prohibits expanding this packet into the entire product;
- Android remains after a real no-app Personal vertical unless a hard dependency changes the order.

### Direction result

**ALIGNED.** `SERVICE-STATE-001` is the current hard prerequisite between completed first boot and safely activating the first useful no-app service.

## Required behavior

This packet must provide a durable service-state contract where:

1. user request/intent does not equal active;
2. recommendation does not equal user request or active;
3. provider/capability evidence does not equal user consent;
4. actual activation requires explicit user intent plus readiness;
5. readiness can be blocked by explicit dependency reasons;
6. loss of readiness while active fails closed rather than continuing to claim an active service;
7. deactivation is always possible without deleting the durable service record;
8. every transition is revision-safe/idempotent through `STORE-001`;
9. the model is provider-neutral and contains no Google row coordinates/provider IDs;
10. onboarding appointment intent can map to a `requested` service state while provider capability and activation remain unverified/off.

## Explicitly deferred

This packet does not implement:

- full service catalog/composition dependency graph;
- Google Calendar write/readback;
- Gmail ingestion;
- actual Ops Brief generation/delivery;
- receipt/asset/inventory services;
- Android service UI;
- cross-person permissions;
- provider-specific credential onboarding.

## Acceptance criteria

1. Provider-neutral `service_state` resource schema/state machine exists.
2. Finite activation states are explicit and validated.
3. Capability/readiness/recommendation are separate fields from activation.
4. Requesting a service never activates it.
5. Activation fails closed unless readiness conditions are satisfied.
6. Capability/readiness loss while active stops effective activation truth.
7. Disable/deactivate preserves state/history identity.
8. Structured-state persistence uses expected revisions/idempotency and exact readback.
9. Direct tests cover fresh state, request, recommend, blocked activation, successful activation, readiness loss, deactivate, replay/conflict semantics, and onboarding appointment intent mapping.
10. Production ownership/evidence is updated.
11. CI is green on latest head.
12. End-of-session FEATURES/BACKLOG/ROADMAP alignment is recorded before merge.

## Exact next action

Implement the bounded service-state model and tests; do not broaden into full service composition. Then prove the state format against the isolated no-app Google proof workbook, close the packet, and move directly toward the smallest first user-visible no-app vertical.
