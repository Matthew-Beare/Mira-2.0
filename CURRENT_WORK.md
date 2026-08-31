# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it; normal product UI, brief titles, automation titles, and ordinary conversation say MIRA.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is merged through PR #76 with implementation/test/release evidence; final feature-ledger evidence reconciliation remains part of the post-merge lifecycle checkpoint rather than a reason to reopen that completed packet.
- `CAL-007` generic source-linked Calendar projection is the primary feature for this packet.
- `CAL-006` preferred-Calendar provider capability/readback remains downstream of this provider-neutral core.
- `CAL-008` appointment evidence intake remains blocked on both durable identity and safe Calendar projection semantics.

### `BACKLOG.md`

- `APPOINTMENT-IDENTITY-001` is reconciled complete through PR #76.
- `CALENDAR-PROJECTION-001` is split rather than silently expanded.
- `CALENDAR-PROJECTION-001A` is the single active provider-neutral synthetic core in `M2-M0-022`.
- `CALENDAR-PROJECTION-001B` preserves real Google/Microsoft/Apple provider capability/write/readback proof as downstream work.
- `APPOINTMENT-INTAKE-001` remains the intended user-visible vertical after projection prerequisites are satisfied.

### `ROADMAP.md`

- M2-M0.5 prioritizes useful stock-ChatGPT + Personal Google verticals before Android.
- Appointment capture/reminder usefulness is dependency-blocked by safe source-linked Calendar projection semantics, so this bounded core remains aligned with the active milestone.

### Direction result

**ALIGNED.** Complete and merge the bounded provider-neutral Calendar projection core. Do not expand this packet into real Google/Microsoft/Apple Calendar mutation, appointment extraction, reminder delivery, outbound contact, medical interpretation, legacy migration, or Android.

## Completed predecessor

### `M2-M0-021` — Appointment identity reconciliation core

- **Work:** `APPOINTMENT-IDENTITY-001`
- **Feature:** `CAL-005`
- **PR:** #76. Draft PR #75 was closed only because the connected GitHub ready-for-review wrapper failed on an invalid GraphQL response field; the exact same branch continued as non-draft PR #76.
- **Final PR head:** `64ceba6e2827af857e41c17a7d7b3fcb5271df85`
- **Exact-head CI:** `33376525725` green
- **Merge SHA / verified main checkpoint:** `831a169918572174df13352c9aa993d955a3f5bb`
- **Post-merge main CI:** `33376572089` green
- **Evidence:** separate durable `appointment_provider` and `appointment` identity, exact deterministic reconciliation, immutable evidence fingerprints, field-authority precedence, explicit Needs Review ambiguity handling, user-confirmed correction precedence, Personal starter Resource-type wiring, and zero Calendar/reminder/contact side effects.
- **Evidence ceiling:** no claim of inbound appointment extraction, live Calendar provider writes/readback, reminder delivery, appointment-service activation, medical inference, migration, or Android behavior.

## Active packet

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Primary work:** `CALENDAR-PROJECTION-001A`
- **Primary features:** `CAL-007`
- **Related invariants/features:** `CAL-006`, `CAL-005`, `RECOVERY-002`, `STORE-001`, `PROFILE-013`, `SERVICE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-022-calendar-projection-core`
- **Base SHA:** `831a169918572174df13352c9aa993d955a3f5bb`
- **PR:** #77 open, non-draft
- **Last verified green candidate head before this checkpoint:** `0037dd89099fee00458c9acda1afec60411d0395`
- **Exact-head CI:** `33427126236` green on `0037dd89099fee00458c9acda1afec60411d0395`
- **Current head rule:** this file is itself part of the final governance checkpoint, so resolve the live PR head from GitHub immediately before merge and require green CI on that exact live head. Do not reuse the pre-checkpoint SHA as the merge target.
- **Dependencies:** merged `CAL-005` identity semantics; structured-state adapter contract; recovery/failure-isolation semantics.
- **Current blockers:** none known beyond exact-head CI/readback on this governance checkpoint commit.

### Objective

Implement the smallest provider-neutral source-linked Calendar projection slice that gives MIRA a stable canonical projection identity, deterministic desired-event normalization, replay-safe provider-adapter mutation semantics, explicit stale/conflict behavior, and exact provider-adapter readback verification using synthetic/in-memory evidence only. The core must make later Google/Microsoft/Apple adapters possible without pretending any real Calendar provider is already verified.

### Explicitly out of scope

- real Google Calendar, Microsoft/Outlook/M365 or Apple/iCloud writes/readback;
- provider account onboarding, OAuth/scope provisioning, or provider selection UI;
- inbound email/photo/OCR/text appointment extraction (`CAL-008`);
- reminder scheduling/delivery (`CAL-001` through `CAL-003`);
- outbound email/contact (`MAIL-002` remains intact);
- medical interpretation;
- legacy production Calendar use as a development fixture;
- Android/mobile work.

## Acceptance criteria

1. Canonical Calendar projection identity is distinct from the source Resource identity and from the provider-generated event identity.
2. A projection is deterministically keyed by source Resource + target provider lane + target Calendar reference so replay cannot create a second logical projection.
3. Desired timed-event material has deterministic normalization/fingerprinting with explicit title, start, end, IANA timezone and optional location/description; malformed or impossible timing fails closed.
4. Source revision is monotonic: stale source revisions are rejected and the same source revision cannot silently map to different desired event material.
5. The provider adapter contract requires stable projection-key semantics, write capability and exact event readback; unsupported capability fails before mutation.
6. Create/update is replay safe. Reusing one idempotency key for different material is a conflict; replay of identical material does not duplicate provider events or canonical Resources.
7. Provider write success is not canonical success until independent adapter readback exactly matches the desired normalized event material.
8. Readback mismatch, missing provider event, provider-version conflict, canonical revision conflict, or persisted payload inconsistency fails closed with an explicit typed error; no false completion state is written.
9. The canonical `calendar_projection` Resource records source identity/revision, provider lane/calendar/event identity, provider version, desired material fingerprint and verified readback fingerprint without making provider state authoritative.
10. Direct tests cover create, identical replay, update from a newer source revision, stale source rejection, same-revision/different-material conflict, adapter idempotency conflict, unsupported capability, readback drift, missing provider event, provider-version conflict, canonical replay and zero Event/out-of-scope side effects.
11. New production code is registered in code ownership/direct verification. The clean Personal starter permits `calendar_projection` as a Resource type but does not silently activate a Calendar provider.
12. Required CI is green on the exact final PR head before merge; merge uses expected-head protection; post-merge main CI must pass before completion is claimed.

## Completed evidence for this packet

- `mira/calendar_projection.py` implements provider-neutral projection identity, deterministic desired-event normalization/fingerprinting, capability checks, source-revision monotonicity, replay/idempotency conflict handling, provider-version conflict handling, and exact adapter readback verification.
- `tests/test_calendar_projection.py` directly covers create, identical replay, newer-source update, stale/same-revision conflict, adapter idempotency conflict, unsupported capability, readback drift, missing provider event, provider-version conflict, canonical replay and zero canonical Event side effects.
- `distribution/personal_google_starter.json`, `mira/personal_distribution.py`, and `tests/test_personal_distribution.py` now permit and verify the clean `calendar_projection` Resource type without activating a provider Calendar lane.
- `project/code_ownership.json` registers `mira/calendar_projection.py` with direct verification at `tests/test_calendar_projection.py` under `CAL-007` / `CALENDAR-PROJECTION-001A`.
- `BACKLOG.md` reconciles `APPOINTMENT-IDENTITY-001` complete and splits the Calendar projection umbrella into active provider-neutral `001A` plus downstream provider-specific `001B`.
- CI `33427126236` passed compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, the full Python unit suite, and Workspace Apps Script tests on candidate head `0037dd89099fee00458c9acda1afec60411d0395`.
- Protected legacy production Calendar state has not been used or modified.
- No claim is made that Google Calendar, Microsoft/Outlook/M365, Apple/iCloud, appointment intake, reminder delivery, provider onboarding/OAuth, or appointment-service activation is live.

## Exact next action / resume point

1. Require green CI on the live PR #77 governance-checkpoint head.
2. Update PR #77 description with exact verified evidence and the provider-neutral evidence ceiling; PR metadata changes must not alter the source head.
3. Re-read exact PR #77 head and mergeability and verify the successful CI belongs to that exact head.
4. Merge PR #77 using that exact live SHA as `expected_head_sha`.
5. Verify remote `main` points to the returned merge SHA and require post-merge `main` CI success.
6. Only after post-merge success, create the lifecycle checkpoint that marks `CAL-007` / `CALENDAR-PROJECTION-001A` merged/completed, reconciles the prior `CAL-005` feature evidence, and dynamically selects the next bounded packet.
7. Do not expand into real provider Calendar writes, appointment intake, reminders, contact, medical meaning, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-022-calendar-projection-core`, PR #77, and its remote head before any implementation or merge. If the branch head differs from the recorded last-green checkpoint, inspect the intervening commits and their CI rather than reconstructing from chat. `M2-M0-021` is complete and must not be reopened absent new integrity evidence. Protected legacy MIRA production state remains read-only and unavailable as a development fixture.
