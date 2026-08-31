# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it; normal product UI, brief titles, automation titles, and ordinary conversation say MIRA.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is now implementation/test/release verified and merged through PR #76; lifecycle evidence must be reconciled from its pre-merge `partial-test+requirement-refined` state.
- `CAL-007` generic source-linked Calendar projection is required direction and remains specified/unimplemented.
- `CAL-006` preferred-Calendar projection/provider readback builds on `CAL-005` and `RECOVERY-002`; provider-specific capability proof remains downstream of the provider-neutral core.
- `CAL-008` appointment evidence intake depends on both durable identity and Calendar projection, so projection is the next hard prerequisite before the user-visible appointment intake slice.

### `BACKLOG.md`

- `APPOINTMENT-IDENTITY-001` is merged through PR #76 and must be reconciled complete.
- `APPOINTMENT-INTAKE-001` is the intended user-visible vertical but depends on `CALENDAR-PROJECTION-001`.
- The existing `CALENDAR-PROJECTION-001` row is too broad for one bounded implementation packet because it combines provider-neutral projection semantics with Google, Microsoft/Outlook/M365 and Apple/iCloud provider capability/readback proof.
- Split the umbrella rather than silently growing one packet. `CALENDAR-PROJECTION-001A` is the provider-neutral synthetic projection core selected now; provider-specific adapter/readback proof remains downstream.

### `ROADMAP.md`

- M2-M0.5 prioritizes useful stock-ChatGPT + Personal Google verticals before Android.
- Appointment capture/reminder usefulness is dependency-blocked by safe source-linked Calendar projection semantics, so the provider-neutral projection core is the highest-ranked bounded prerequisite after appointment identity.

### Direction result

**ALIGNED.** Start the bounded provider-neutral Calendar projection core. Do not expand this packet into real Google/Microsoft/Apple Calendar mutation, appointment extraction, reminder delivery, outbound contact, medical interpretation, legacy migration, or Android.

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
- **PR:** none yet
- **Dependencies:** merged `CAL-005` identity semantics; structured-state adapter contract; recovery/failure-isolation semantics.
- **Blockers:** none known. `FEATURES.md`/`BACKLOG.md` lifecycle reconciliation is required before this packet can pass repository alignment gates.

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

- Packet selected from dependency-ranked accepted scope after verified merge of M2-M0-021.
- Branch created from verified `main` merge SHA `831a169918572174df13352c9aa993d955a3f5bb`.
- No legacy production Calendar data has been used or modified.

## Exact next action / resume point

1. Reconcile `CAL-005` / `APPOINTMENT-IDENTITY-001` completion and split `CALENDAR-PROJECTION-001` into bounded provider-neutral core `CALENDAR-PROJECTION-001A` in `FEATURES.md` / `BACKLOG.md`.
2. Implement `mira/calendar_projection.py` plus direct synthetic tests.
3. Register code ownership/direct verification and add `calendar_projection` to the clean Personal starter/validator contract without activating any provider.
4. Run repository gates, repair only packet/baseline blockers, then open a PR when the bounded implementation is green.
5. Require exact-head CI, protected merge, remote-main readback and post-merge main CI before completion.
6. Do not expand into real provider Calendar writes, appointment intake, reminders, contact, medical meaning, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-022-calendar-projection-core` still starts from verified main SHA `831a169918572174df13352c9aa993d955a3f5bb` and inspect any newer branch commits rather than reconstructing from chat. M2-M0-021 is merged and must not be reopened absent new integrity evidence. Protected legacy MIRA production state remains read-only and unavailable as a development fixture.
