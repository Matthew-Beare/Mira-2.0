# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it; normal product UI, brief titles, automation titles, and ordinary conversation say MIRA.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is merged and test-verified through PR #76.
- `CAL-007` provider-neutral Calendar projection semantics are merged and test-verified through PR #77 with synthetic readback only.
- `CAL-006` still requires preferred-Calendar provider capability plus exact real-provider write/readback evidence before MIRA may claim Calendar sync is live.
- `CAL-008` remains the intended user-visible appointment-intake vertical and should not begin until one default Personal provider lane is actually proven.

### `BACKLOG.md`

- `CALENDAR-PROJECTION-001A` is merged through PR #77 and must be reconciled complete.
- `CALENDAR-PROJECTION-001B` is still too broad for one packet because it bundles Google, Microsoft/Outlook/M365 and Apple/iCloud provider proof.
- The default Personal MIRA path is Google Workspace, so the next bounded prerequisite is a Google Calendar adapter/readback proof. Microsoft and Apple remain separate downstream provider packets rather than being dragged into this one.
- `APPOINTMENT-INTAKE-001` remains queued behind the proven provider projection lane.

### `ROADMAP.md`

- M2-M0.5 prioritizes useful stock-ChatGPT + Personal Google verticals before Android.
- A real but isolated Google Calendar projection proof is the shortest hard dependency between the merged provider-neutral core and a usable appointment-intake vertical.

### Direction result

**ALIGNED.** Start one Google Calendar provider adapter/readback packet. Do not expand into Microsoft/Apple Calendar, appointment extraction, reminders, outbound contact, medical interpretation, legacy migration, or Android.

## Completed predecessor

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Work:** `CALENDAR-PROJECTION-001A`
- **Feature:** `CAL-007`
- **PR:** #77
- **Final PR head:** `ec6fe091bfa68cabce5450e9974ff5337ae55800`
- **Exact-head CI:** `33427269214` green
- **Merge SHA / verified main checkpoint:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **Post-merge main CI:** `33427385919` green
- **Evidence:** stable source-linked `calendar_projection` identity, deterministic event normalization/fingerprinting, replay-safe synthetic provider mutation, explicit stale/idempotency/provider-version conflicts, exact synthetic readback, Personal starter Resource-type wiring, code ownership and full repository-gate coverage.
- **Evidence ceiling:** synthetic/in-memory provider only. No Google/Microsoft/Apple Calendar provider write/readback, OAuth/provider activation, appointment extraction, reminder delivery, outbound contact, medical inference, migration, or Android behavior was claimed.

## Active packet

### `M2-M0-023` — Google Calendar projection adapter/readback

- **Primary work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Primary features:** `CAL-006`, `CAL-007`
- **Related invariants/features:** `RECOVERY-002`, `PROFILE-013`, `SERVICE-001`, `PROVIDER-002`, `CAL-008`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-023-google-calendar-projection`
- **Base SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **PR:** none yet
- **Dependencies:** merged provider-neutral Calendar projection core; authenticated Google Calendar capability; isolated synthetic development Calendar/event namespace.
- **Blockers:** before implementation, `BACKLOG.md` must split the provider-specific umbrella and register this work ID. Live proof must use an isolated synthetic Calendar/test event and must not mutate protected personal/legacy Calendar state.

### Objective

Implement and prove the smallest Google Calendar adapter that satisfies the merged provider-neutral Calendar projection contract: capability inspection, deterministic create/update semantics, stable provider event identity/version handling, exact provider readback, replay safety and fail-closed mismatch behavior. Then run one isolated synthetic Google Calendar provider proof without treating a provider write response alone as success.

### Explicitly out of scope

- Microsoft/Outlook/M365 Calendar adapter/proof;
- Apple/iCloud Calendar adapter/proof;
- appointment email/photo/text extraction (`CAL-008`);
- reminder scheduling/delivery (`CAL-001` through `CAL-003`);
- outbound provider contact or scheduling negotiation;
- diagnosis, treatment, medication or other medical interpretation;
- legacy production Calendar migration or use as a test fixture;
- Android/mobile work;
- broad Google Workspace bootstrap beyond what is required to prove this one Calendar adapter.

## Acceptance criteria

1. A Google Calendar adapter implements the existing provider-neutral projection contract without changing canonical `calendar_projection` identity semantics.
2. Capability preflight proves the selected Google Calendar target is readable/writable before mutation; insufficient capability fails closed.
3. Create writes one timed event with exact normalized title/start/end/IANA timezone and optional location/description, retaining the resulting Google event identity and provider version material needed for later guarded updates.
4. Update targets the exact previously projected Google event and uses provider-version/concurrency evidence so stale provider state cannot be silently overwritten.
5. Identical logical replay performs no duplicate Calendar event creation and preserves the one canonical projection/event relationship.
6. Reuse of one logical idempotency key for different material fails closed before a conflicting provider mutation.
7. Provider write acknowledgement is insufficient: exact independent Google Calendar readback must match the normalized desired event before canonical projection success is recorded.
8. Missing event, readback drift, permission failure, stale provider version, wrong target Calendar or ambiguous provider identity produces an explicit typed failure and no false canonical completion.
9. Direct adapter tests use fakes/synthetic fixtures and cover create, replay, update, stale version, capability failure, missing event, readback mismatch and provider error translation.
10. Live provider proof uses a clearly isolated synthetic Google Calendar/test event namespace, records no provider identifiers/secrets/private state in public Git, and verifies cleanup or bounded retained-test-state policy explicitly.
11. Protected legacy/personal Calendar data is neither modified nor used as a development fixture.
12. Code ownership/direct verification and release/no-app contract are updated only as required for the Google adapter; the change must not claim Microsoft/Apple support.
13. Required CI is green on the exact final PR head before merge; merge uses expected-head protection; remote `main` readback and post-merge main CI must pass before completion is claimed.

## Completed evidence for this packet

- Predecessor M2-M0-022 is merged at `fcc81f0e9d9510d05406acd9068d9ca4ee016806` with post-merge CI `33427385919` green.
- Branch `integration/m0-023-google-calendar-projection` was created from that exact verified main SHA.
- No Calendar provider mutation has been performed for this packet yet.

## Exact next action / resume point

1. Split `CALENDAR-PROJECTION-001B` in `BACKLOG.md`: register `CALENDAR-PROJECTION-GOOGLE-001` as the single active M2-M0-023 work item and preserve Microsoft/Apple provider proof as queued downstream work.
2. Inspect the merged `mira/calendar_projection.py` adapter contract and current Google Calendar connector capabilities before designing provider-specific code.
3. Implement the bounded Google adapter plus direct fake-provider tests; register code ownership/release evidence without broadening provider claims.
4. Run repository gates and repair only packet/baseline blockers.
5. Use the connected Google Calendar authority only for an isolated synthetic provider proof after code/tests are green; perform exact provider readback and protect all existing personal/legacy Calendar state.
6. Open/update the PR, require exact-head CI, merge with expected-head protection, verify remote main and post-merge CI, then reconcile lifecycle and select the next packet.
7. Do not expand into Microsoft/Apple Calendar, appointment intake, reminders, contact, medical meaning, migration, or Android.

## Recovery protocol

Read this file first. Confirm branch `integration/m0-023-google-calendar-projection` and its remote head before implementation. If the branch head differs from this checkpoint, inspect intervening commits rather than reconstructing from chat. M2-M0-022 is complete and must not be reopened absent new integrity evidence. Protected legacy MIRA production state remains read-only and unavailable as a development fixture.
