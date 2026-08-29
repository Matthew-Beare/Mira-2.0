# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point.

## Product deployment invariant

Default Personal MIRA is **Google Workspace first and zero external infrastructure**.

The ordinary no-app Personal lane must be usable with **stock ChatGPT plus the user's Google Drive, Google Sheets and Google Docs**. It must not require Cloud Run, Linux, SQL, a self-hosted server, a tunnel, a separately billed OpenAI API runtime, or Android merely to become useful.

Android, Microsoft and Apple/iCloud remain supported extension/provider lanes. They must not redefine or delay the first usable Google-only Personal product.

## Mandatory work-session alignment gate

Every MIRA development work session must begin and end with a direction check against all four Git authorities:

1. `CURRENT_WORK.md` — exact active packet and resume point;
2. `FEATURES.md` — accepted semantic feature set and dependencies;
3. `BACKLOG.md` — dependency-ranked implementation work and preserved displaced work;
4. `ROADMAP.md` — milestone/product ordering.

The developer must record the result in this file. CI runs `python -m mira.work_session_alignment check` to reject an active packet whose primary work is absent from `BACKLOG.md`, whose declared features/invariants are absent from `FEATURES.md`, or whose session-start authority review is missing. Semantic direction judgment remains the developer's responsibility because a parser cannot determine product value.

## Customer priority override — 2026-08-29

The customer explicitly directed development to stop spending the active session on Android plumbing while the ordinary no-app Personal product is not yet meaningfully usable.

Priority is therefore:

1. produce a usable stock-ChatGPT + Google Workspace MIRA first;
2. verify each work session against the canonical feature/backlog/roadmap set;
3. resume Android from its exact preserved checkpoint after the no-app product has a real user-facing vertical or if a hard dependency requires Android work sooner.

This is a priority change, not deletion of Android scope.

## Displaced packet checkpoint

### `M2-M1-001` — Concurrent canonical command boundary

**Status:** paused by explicit customer reprioritization; implementation/evidence preserved.

Completed evidence:

- provider-neutral sequencer merged in PR #54 at `d21869d091cbcfce609d47665ef8872123f2be43`; CI green;
- Google Workspace queued-writer worker merged in PR #55 at `1908629fc887b025a8acb2d6fd5321ca191ad0e7`; CI green;
- synthetic conflict/replay/crash-recovery behavior test-verified;
- direct stock-ChatGPT mutation is guarded when queued-writer mode activates.

**Exact Android resume point:** seed one isolated synthetic/release MIRA 2.0 spreadsheet with the Git-backed bound Apps Script, run `miraEnableQueuedWriter()`, and verify the live Commands tab, exactly one worker trigger, mutation mode, canonical result/readback, and at least one stale/retry case. Do not restart the architecture design from scratch.

Relevant preserved work remains `ANDROID-COMMAND-BOUNDARY-001`, `ANDROID-CLIENT-CORE-001`, and `ANDROID-SYNC` in `BACKLOG.md`.

## Active packet

### `M2-M0-007` — No-app first-boot Interview Ledger

- **Primary work:** `FIRSTBOOT-CORE-001`
- **Primary features:** `ONBOARD-003`, `ONBOARD-002`, `CORE-001`
- **Related invariants/features:** `SERVICE-001`, `CAL-006`, `STUDIO-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`, `ONBOARD-006`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-007-no-app-firstboot`
- **Base SHA:** `a5f0f3596a53ddb2ea13ece97b4426aa9dd6d5c2`
- **Head before closeout checkpoint:** `577a400ab71df338b37bc912d99dfc4c209ad841`
- **Pull request:** #58
- **Status:** implementation complete; direct tests green; isolated Google Workspace persistence/readback compatibility verified; merge pending latest-head CI.
- **Objective:** give stock-ChatGPT Personal MIRA a deterministic first-boot state machine instead of merely possessing a working Google-backed storage substrate.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `ONBOARD-003` requires exactly four Minimum Useful Setup questions, a durable resumable Interview Ledger, fixed MIRA name, later user-invoked interview continuation, and introduction of MIRA Studio.
- `ONBOARD-002` requires sanitized generic starter behavior with no inherited personal production state.
- `CORE-001` fixes the assistant/product identity as MIRA and prohibits asking the user to rename it during onboarding.
- `CAL-006` preserves preferred Calendar provider selection as a preference/projection contract; selecting a provider must not falsely claim that provider capability is active.
- `SERVICE-001` requires activation state to remain explicit rather than inferred from an onboarding answer.
- `ONBOARD-006` preserves browser-only ordinary Personal use with no terminal fallback.

### `BACKLOG.md`

Verified before implementation:

- `FIRSTBOOT-CORE-001` exists as the bounded prerequisite owning this work.
- `DISCOVERY-CORE-001`, `ONBOARD-SCHEDULE-001`, `SERVICE-STATE-001`, `NONTECH-INSTALL-001`, `MIRA-SKILL-001`, and broader service/provider work remain separate follow-on packets.
- Android work is already represented and therefore can be paused without losing scope.
- receipts, assets, inventory, appointments, Ops Brief, and the remaining accepted feature families remain preserved and are not removed by this packet.

### `ROADMAP.md`

Verified before implementation:

- the product invariant requires useful Google-only Personal MIRA before advanced infrastructure;
- M2-M0 core Google state proof was already complete;
- old Android-before-onboarding ordering conflicted with the customer's explicit priority and was corrected in this packet;
- M2-M0.5 now explicitly owns usable no-app product progress before Android resumes.

### Direction result

**ALIGNED AFTER REPRIORITIZATION.** `FIRSTBOOT-CORE-001` was the shortest valid progress toward a user-facing no-app MIRA.

## Implemented behavior

`mira/onboarding.py` now provides a provider-neutral `InterviewLedgerService` over the existing `StructuredStateAdapter` contract.

The canonical Minimum Useful Setup is exactly:

1. `timezone` — validated authoritative IANA timezone;
2. `life_pattern` — broad work/study/household/caregiving/travel pattern;
3. `goals` — remembering/organizing/deciding/planning/follow-through goals;
4. `appointment_help` — explicit appointment-help intent plus requested Calendar lane.

MIRA's fixed name is not an onboarding question.

The ledger:

- creates deterministic empty first-boot state;
- persists each answer with optimistic revision semantics;
- resumes at the first unanswered question;
- rejects out-of-order answers;
- treats an exact repeated answer as a read-only replay;
- requires explicit replacement for a materially changed prior answer;
- validates timezones with IANA `ZoneInfo`;
- normalizes Google, Microsoft/Outlook/M365, Apple/iCloud, other and manual Calendar preference lanes;
- records `calendar_capability_verified=false`, `calendar_projection_active=false`, and `appointment_service_activated=false` when a Calendar lane is merely requested;
- marks Minimum Useful Setup complete only after all four answers;
- returns the required orientation that later interview continuation is available and MIRA Studio/sharing are optional rather than silently enabled.

## Verification evidence

### Direct executable tests

`tests/test_onboarding.py` covers:

- fresh start;
- exactly four canonical questions and no assistant-name question;
- ordered progression and resume;
- out-of-order rejection;
- invalid timezone rejection;
- exact-answer replay without revision growth;
- explicit material replacement;
- appointment preference without fake provider/service activation;
- declining appointment help;
- completion only after all four answers;
- completion orientation;
- trimmed JSON-compatible text state.

### Work-session alignment enforcement

`mira/work_session_alignment.py`, `tests/test_work_session_alignment.py`, the work-packet policy, and CI now enforce the mechanical portion of the customer's per-session direction requirement.

The gate confirms active primary work exists in `BACKLOG.md`, declared active features/invariants exist in `FEATURES.md`, and the session-start review explicitly covers FEATURES/BACKLOG/ROADMAP with an ALIGNED result.

### Google Workspace state compatibility proof

An isolated synthetic copy of the clean MIRA Personal Starter was created. The source template was not modified.

On the isolated copy only:

- `onboarding_ledger` was added to `resource_types_json` while preserving `STORE-001` and `single_writer` metadata;
- a fully synthetic Minimum Useful Setup history was materialized using the exact `GoogleSheetsStructuredStateAdapter` persisted row/idempotency format;
- the final canonical resource read back as `onboarding_ledger/minimum-useful-setup`, revision 5, status `complete`;
- all five synthetic upsert idempotency records read back with deterministic request hashes;
- the appointment answer requested the Google Calendar lane while capability verification, Calendar projection, and appointment-service activation all remained false;
- written backend rows were checked for readable wrap/vertical formatting;
- no personal production data, provider identifier, or legacy MIRA artifact was written into public Git.

This is **provider persistence/readback compatibility evidence**, not a claim that stock ChatGPT has already executed the conversational Interview Ledger end-to-end against Google. That user-facing orchestration remains follow-on integration work.

## Acceptance status

1. Provider-neutral onboarding runtime — **passed**.
2. Exactly four canonical kickoff question IDs/prompts — **passed**.
3. Fixed MIRA name, never asked — **passed**.
4. Start/answer/read/resume semantics — **passed**.
5. Validation and explicit re-answer behavior — **passed**.
6. Calendar preference separated from capability/activation — **passed**.
7. Completion only after four answers — **passed**.
8. Completion orientation / Studio introduction / optional sharing — **passed**.
9. JSON-compatible STORE-001 state — **passed**.
10. Direct unit-test coverage — **passed**.
11. Production ownership/evidence manifest — **passed**.
12. CI at PR head `577a400ab71df338b37bc912d99dfc4c209ad841` — **passed**, workflow run `33279242714`; latest closeout head still requires CI readback before merge.
13. Session-end alignment review — **passed below**.

## Session-end alignment verification — 2026-08-29

### `FEATURES.md`

Re-read against the implemented behavior. `ONBOARD-003`, `ONBOARD-002`, `CORE-001`, `CAL-006`, `SERVICE-001`, `STUDIO-001`, and `ONBOARD-006` remain compatible with this implementation. No accepted receipt, asset, inventory, appointment, brief, Android, Microsoft, or Apple feature was deleted or weakened.

### `BACKLOG.md`

Re-read after implementation. `FIRSTBOOT-CORE-001` is now implemented/test-verified by this branch and has Google state-format/readback evidence; the canonical row status still needs closeout bookkeeping after merge. The next no-app work should be selected from existing M2-M0.5 prerequisites/verticals rather than inventing Android or external infrastructure work.

### `ROADMAP.md`

Re-read after the roadmap correction. The branch now explicitly prioritizes useful no-app Personal MIRA, then companion/provider expansion, while preserving the exact Android resume point.

### Direction result

**ALIGNED.** The packet delivered real no-app product behavior plus provider-state compatibility and strengthened future direction control. It did not silently expand into service activation, Calendar writes, Ops Brief, receipts/assets/inventory, or Android.

## Exact next action

1. Wait for CI on this closeout checkpoint commit and repair only if the latest head is red.
2. Merge PR #58 only after latest-head CI is green.
3. Remotely verify `main` contains the merge and read back `CURRENT_WORK.md`.
4. Create the next bounded M2-M0.5 no-app packet from the merged head.
5. Current dependency/value default: implement the smallest `SERVICE-STATE-001` / service-composition foundation necessary to let onboarding preferences become explicit readiness/activation state, then drive directly toward the first stock-ChatGPT user-visible vertical. Do not resume Android merely because its provider proof is pending.

## Recovery protocol

Read this file first. If PR #58 is still open, check the latest branch head and CI before merge. If merged, verify `main` and start the next M2-M0.5 no-app packet. Android remains paused at the exact live Apps Script proof step recorded above. Keep personal/provider identifiers and live production state out of public Git.
