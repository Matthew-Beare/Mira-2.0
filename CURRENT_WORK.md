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

The developer must record the result in this file. A session is not considered safely checkpointed merely because code tests pass. If the active packet is no longer the highest-value valid work under the customer priority, it must be checkpointed and reprioritized before unrelated implementation continues.

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
- **Current head:** update from branch readback after each checkpoint write
- **Objective:** make stock-ChatGPT MIRA have a real deterministic first boot instead of merely possessing a working Google-backed state substrate.

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

- `FIRSTBOOT-CORE-001` already exists and is queued as a prerequisite.
- `DISCOVERY-CORE-001`, `ONBOARD-SCHEDULE-001`, `SERVICE-STATE-001`, `NONTECH-INSTALL-001`, `MIRA-SKILL-001`, and broader service/provider work remain separate follow-on packets.
- Android work is already represented and therefore can be paused without losing scope.
- receipts, assets, inventory, appointments, Ops Brief, and the remaining accepted feature families remain preserved and are not being removed by this packet.

### `ROADMAP.md`

Verified before implementation:

- the product invariant says ordinary Google users must get useful MIRA before needing servers/Linux/SQL/Cloud Run/Git/paid model APIs;
- M2-M0 core Google state proof is already complete;
- onboarding hardening was previously listed after Android core proofs, but that ordering now conflicts with the customer's explicit priority to make the no-app product useful first;
- this packet intentionally supersedes that priority ordering while preserving Android's checkpoint.

### Direction result

**ALIGNED AFTER REPRIORITIZATION.** The shortest valid progress toward the customer-visible product is `FIRSTBOOT-CORE-001`, not further Android concurrency work.

## User-visible behavior this packet must enable

A fresh Personal MIRA session can:

1. identify that Minimum Useful Setup is incomplete;
2. ask the four canonical kickoff questions in order;
3. never ask the user to choose or rename MIRA;
4. persist each answer in a durable Interview Ledger with explicit question identity and completion state;
5. resume from the first unanswered question rather than restarting;
6. preserve an explicit appointment-help / preferred-Calendar preference without falsely activating or claiming unavailable provider integration;
7. after question four, mark Minimum Useful Setup complete and tell the user they can ask MIRA later to continue the interview for additional useful questions;
8. introduce MIRA Studio and optional sharing without silently enabling either;
9. expose deterministic state that can be stored through the existing provider-neutral structured-state contract and later projected into the Google Workspace starter.

## Explicitly deferred from this packet

This packet does **not** implement:

- full historical discovery/question banks (`DISCOVERY-CORE-001`);
- automatic service activation;
- Calendar provider writes/readback;
- Gmail ingestion;
- Ops Brief generation;
- receipt/asset/inventory verticals;
- Android UI/client behavior;
- MIRA Studio implementation itself;
- deterministic public installer/distribution promotion.

Those remain canonical backlog work.

## Acceptance criteria

1. New provider-neutral onboarding runtime exists with no Google-specific row coordinates or provider IDs.
2. Exactly four canonical kickoff question IDs and prompts are defined and deterministic.
3. MIRA's name is fixed and never appears as an onboarding question.
4. Ledger can start, answer, read, and resume deterministically.
5. Answers are trimmed/validated and material re-answer behavior is explicit rather than silently duplicated.
6. Appointment preference records interest plus requested Calendar lane separately from actual provider capability/activation.
7. Completion occurs only when all four canonical answers exist.
8. Completion orientation includes later interview continuation and MIRA Studio introduction without auto-activation.
9. State serializes to JSON-compatible payloads suitable for `STORE-001`.
10. Direct unit tests cover fresh start, ordered progression, resume, invalid input, fourth-question provider preference, completion, and no-name-question behavior.
11. Repository ownership/evidence manifest covers all new production code.
12. CI remains green.
13. End-of-session alignment rechecks `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md` and records any drift before merge/closeout.

## Exact next action

1. Add the automatic work-session/packet alignment checker and CI gate so future sessions cannot rely only on memory.
2. Implement `FIRSTBOOT-CORE-001` provider-neutral Interview Ledger runtime and direct tests.
3. Update production ownership evidence.
4. Run CI through the PR and repair failures.
5. Re-run feature/backlog/roadmap alignment before merge.
6. If green and aligned, merge this packet and then select the next highest-value no-app user-visible packet.

## Recovery protocol

Read this file first. Confirm the branch/head state. Do not resume Android merely because its live provider proof is unfinished; the customer explicitly reprioritized no-app usability. If `M2-M0-007` is unfinished, continue at the first incomplete acceptance criterion above. Keep all personal/provider identifiers and live production state out of public Git.
