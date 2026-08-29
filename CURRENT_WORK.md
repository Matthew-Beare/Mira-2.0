# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point.

## Product deployment invariant

Default Personal MIRA remains **Google Workspace first and zero external infrastructure**.

The ordinary no-app Personal lane must be usable with **stock ChatGPT plus the user's Google Drive, Google Sheets and Google Docs**. It must not require Cloud Run, Linux, SQL, a self-hosted server, a tunnel, a separately billed OpenAI API runtime, or another external service merely to begin using MIRA.

A bound Google Apps Script is **not required for the stock-ChatGPT-only Personal lane**. It is an optional Google-native implementation tool for initialization/automation, and the queued-writer script becomes relevant only when a second concurrent writer such as Android is enabled. Even then it remains inside the user's Google Workspace rather than creating a Cloud Run/Linux/SQL prerequisite.

Provider-neutral `API-001`, `AUTH-001` and `STORE-001` remain canonical. No client becomes an independent authority and no dual writable masters are permitted.

## Customer priority clarifications — 2026-08-29

These are accepted product constraints and must be preserved by every later packet:

1. **Google Workspace is the first usable Personal product lane.** The product must not postpone meaningful no-app usefulness until Android exists.
2. **Android is an extension, not a prerequisite for ordinary no-app MIRA.** Android may add camera, notifications, offline behavior and shared-state mutation without retroactively making the Google-only lane depend on Android infrastructure.
3. **Apple/iCloud must be supported, but it is not a current implementation focus and must not block the Google-first Personal baseline or the current Android proof.** Microsoft/Outlook/M365 is likewise a provider lane rather than a reason to delay the first Google vertical. Provider-neutral contracts are designed once; provider adapters are proved independently when selected.
4. **Feature inventory is not conversational memory.** `FEATURES.md` is the canonical semantic inventory and `BACKLOG.md` is the dependency-ranked work inventory. Every packet must read both before implementation and before merge under `DEV-007`.
5. **Receipts, assets and inventory remain accepted product scope.** They are not to be dropped merely because the current packet is Android/concurrency work.

## Completed predecessor

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- Complete and remotely verified.
- PR #50 merge `e412405a475d1423edaac821d7a99481e4a6eb4b`; CI `33243206658` green.
- PR #51 merge `641a7ce412bd0de46500c229910e52cb35a90bcc`; CI `33243533206` green.
- PR #52 merge `07d79c3a72cc906e93316e213e282919a1fcc4ff`; CI `33243840207` green.
- Closeout PR #53 merge `983444bf697a58a42c4482859d4fe7f0c17fb454`; CI `33274016785` green.
- Proven Personal path: clean Workspace copy → Authority/binding bootstrap → stock ChatGPT native Google create/read/replay/mutate/readback with exact provider verification.
- Native read-then-write Sheets mutation is single-writer only; it is not distributed compare-and-swap.
- This proves the no-external-infrastructure substrate. It does **not** mean the complete user-facing MIRA feature set is already implemented.

## Feature/governance refinement merge

The requirement/governance capture that this file previously listed as pending has already merged.

- Main merge: `618fefa1f15ddfd91a96d7197e3186e19b988457`
- Merge title: `Merge M2-M1-001 feature contract refinements`
- Captured fixed-name onboarding, appointment photo/email intake, preferred Calendar onboarding, MIRA Studio and packet-to-feature-set alignment requirements.
- CI `33275466247` green according to the merge commit.

The previous `CURRENT_WORK.md` checkpoint was stale because it still told the next session to merge work that was already merged. This checkpoint corrects that recovery defect.

## Active packet

### `M2-M1-001` — Concurrent canonical command boundary

- **Primary work:** `ANDROID-COMMAND-BOUNDARY-001`, first prerequisite slice of `ANDROID-CLIENT-CORE-001`
- **Related features:** `CLIENT-ANDROID-001`, `API-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Main baseline before this checkpoint branch:** `618fefa1f15ddfd91a96d7197e3186e19b988457`
- **Current checkpoint branch:** `integration/m1-001-checkpoint-priority-clarify`
- **Checkpoint branch base:** `618fefa1f15ddfd91a96d7197e3186e19b988457`
- **Current head:** update after provider readback of this checkpoint commit
- **Provider-neutral sequencer:** PR #54 merge `d21869d091cbcfce609d47665ef8872123f2be43`; CI `33274374052` green.
- **Workspace queued-writer worker:** PR #55 merge `1908629fc887b025a8ac821d7a99481e4a6eb4b`; CI `33274804921` green.
- **Architecture:** `docs/M1_CONCURRENT_COMMAND_BOUNDARY.md`
- **Status:** synthetic concurrency and Workspace worker behavior are implemented/test-verified and merged. Live isolated Google Apps Script worker proof remains pending.

## Feature alignment

### Primary behavior this packet must enable

Android and stock ChatGPT must be able to participate in one canonical MIRROR reality without independent writers racing Google Sheets. The packet must establish one replay-safe mutation sequencer before Android becomes a canonical writer.

### Product invariants this packet must preserve

- `CORE-001`: product/assistant identity remains MIRA.
- `API-001` / `AUTH-001` / `STORE-001`: Android is a client, not a second authority or alternate product model.
- `DATA-001`: no legacy production artifact is a test fixture.
- `ONBOARD-006` and `API-DEPLOYMENT-001A`: ordinary Personal use remains browser-first/zero-external-infrastructure; Android must not retroactively force every user into Cloud Run/Linux/SQL or paid API operation.
- The stock-ChatGPT-only Personal lane remains valid without the queued-writer script being active.
- `CAL-008` / `CAL-006`: the Android design must leave a clean path for appointment evidence capture and preferred-Calendar projection.
- Apple/iCloud remains a required supported Calendar/provider lane, but Apple adapter implementation is later work and is **not** an acceptance blocker for the Google-first Personal lane or `M2-M1-001`.
- `STUDIO-001`: Android/shared architecture must remain compatible with later user-generated bounded features/workflows and their declared dependencies.
- `ONBOARD-003`: Android work must not replace or invalidate the four-question first-boot Interview Ledger contract.
- `DEV-007`: passing concurrency tests does not permit a design that makes accepted downstream features impossible.

### Explicitly deferred related features

This packet does **not** implement Android UI, appointment photo/email parsing, Calendar provider adapters, reminder delivery, onboarding runtime, MIRA Studio, family sharing, Gmail/Calendar service fan-out, receipt intake, inventory UX, asset lifecycle UI, or Cloud Run live deployment. Those requirements are preserved in `FEATURES.md`/`BACKLOG.md` and must be re-read by the packet that implements them.

## Preserved feature inventory checkpoint

The following accepted areas are present in canonical `FEATURES.md` and must not be lost during architecture work:

### Receipts / purchases

- `RECEIPT-001` — multi-source canonical receipt intake and evidence dedupe.
- `RECEIPT-002` — searchable expandable purchase history and connected receipt graph.
- `RECEIPT-003` — configurable receipt taxonomy and line classification.
- `ORDER-001` through `ORDER-005` — order/carrier/lifecycle/cancellation/replacement/stale-shipment behavior.
- `PAYMENT-001`, `SPEND-001`, `REIMB-001` — settlement, spending and reimbursement relationships.

### Assets / fitment / evidence

- `ASSET-001` — immutable physical asset identity and idempotent acquisition.
- `ASSET-002` — provenance-linked acquisition/reference/lifecycle evidence.
- `ASSET-003` — bidirectional receipt/asset/identifier graph queries.
- `FITMENT-001` — assignment/installation/fitment relationships.
- `IDENT-001`, `EVID-001`, `SPEC-001`, `KNOW-001`, `KNOW-002` — identifiers, evidence, specifications and retained knowledge.

### Inventory / location / movement

- `INV-001` — inventory participation reuses canonical Entity UUID identity.
- `LOC-001` — hierarchical locations with intended placement separate from observed/last-moved state.
- `MOVE-001` — QR/barcode-driven replay-safe inventory movement semantics.
- `INV-002` — queryable household/loft/shop inventory projection.
- `PAR-001` / `PAR-002` — target quantity and optional passive sensing.
- `GROCERY-001`, `RECIPE-001`, `MEAL-001` — pantry/freezer, recipes and meal planning integrated with the same canonical inventory/purchase graph.

`BACKLOG.md` already contains corresponding implementation work including inventory movement/query/location, receipt taxonomy/spend/reimbursement, asset service/fitment, shopping, grocery and related service dependency work. These features remain queued/preserved even though they are not inside the current concurrency packet.

## Selected command architecture

For the ordinary Personal Android lane, use a **durable Google Workspace command inbox plus one serialized Apps Script worker** rather than allowing ChatGPT and Android to mutate canonical Sheets independently.

Command flow:

`ChatGPT/Android command → Commands inbox → one ScriptLock worker → API-001 semantics → Authority → STORE-001 → exact readback → durable command result`

This queue is a requirement of the **multi-writer Android extension**, not the stock-ChatGPT-only baseline.

The worker is asynchronous. Google documents that API writes do not fire installable edit triggers, so the inbox is polled by a time-driven trigger. The current implementation uses a one-minute trigger cadence. Cloud Run remains an advanced synchronous profile if later accepted behavior requires consistently lower latency.

## Completed M2-M1 synthetic evidence

### Provider-neutral sequencer — merged

`mira/command_sequencer.py` + `tests/test_command_sequencer.py` prove:

- duplicate command identity rejected;
- concurrent stale revision-0 commands serialize so only one can commit;
- crash after canonical mutation but before queue acknowledgement retries through canonical idempotency without a second revision;
- expected revisions progress 0 → 1 → 2 under serialized execution;
- same-user authorization failure is terminal with no provider mutation.

PR #54 passed full CI and merged at `d21869d091cbcfce609d47665ef8872123f2be43`.

### Google Workspace queued-writer worker — merged

`workspace/apps_script/CommandWorker.gs` implements a dedicated `Commands` inbox, `mutation_mode=queued_writer`, one time-driven trigger, ScriptLock serialization, bounded processing, Authority-owner checks, idempotency, stale-revision conflicts, canonical Resource write/readback and crash/retry recovery.

`mira/workspace_native.py` fails closed on direct native mutation when `mutation_mode=queued_writer`, closing the second-writer side door.

Executable fake-Apps-Script tests cover trigger activation, ScriptLock behavior, canonical create/readback, stale conflict, crash/retry recovery, mode failure and Authority-owner enforcement. PR #55 CI `33274804921` passed and merged at `1908629fc887b025a8ac821d7a99481e4a6eb4b`.

## Live proof blocker

The connected Google Drive/Sheets tooling available in this development environment can manipulate spreadsheet content but cannot create/update a bound Google Apps Script project. No installable Apps Script plugin/action is currently available.

The remaining provider step for the Android multi-writer boundary is to seed one isolated MIRA 2.0 synthetic/release spreadsheet with the Git-backed bound Apps Script, run `miraEnableQueuedWriter()`, then verify the live Commands tab/trigger/mutation/readback/retry behavior.

This blocker does **not** invalidate the already-proven stock-ChatGPT Google Workspace lane and must not be described as a dependency for ordinary no-app Personal MIRA.

## No-app usability status

There are two different meanings of “usable,” and they must not be conflated:

1. **Canonical no-app substrate:** already live-verified. Stock ChatGPT can use a clean copied Google Workspace starter and create/read/replay/mutate/read back canonical Google-backed state without external infrastructure.
2. **Meaningfully useful no-app MIRA product:** not complete. First-boot Interview Ledger, full service composition, deterministic public distribution/upgrade hardening, and user-visible verticals such as Ops Brief, appointments, receipts/assets/inventory still need implementation/integration packets.

The project therefore should not claim that MIRA is ready for ordinary users merely because `CORE-ROUNDTRIP` passed. The foundation is real; the user-facing product is still being assembled on top of it.

## Android distance to first functional app

The project is past the architecture-foundation stage but not yet at an Android APK/UI stage.

Remaining critical slices before the first genuinely functional Android shared-state proof:

1. live isolated Google queued-writer/trigger proof;
2. Android project/client skeleton + same-user enrollment/authentication and OS-protected credentials;
3. Android command submission/read path against the shared boundary;
4. replay-safe offline queue + reconnect/cursor/conflict handling;
5. Android mutates the exact canonical M2-M0 entity and stock ChatGPT reads it back;
6. representative-device proof.

Notifications/TTS, camera appointment capture, polished UI, signing/release and broader services come after that first shared-state proof unless dependency/value evidence changes the ranking.

## Acceptance status

1. No direct multi-writer Sheets mutation — test-verified/merged; live pending.
2. One canonical mutation sequencer — test-verified/merged; live pending.
3. Existing API/Authority/STORE semantics — preserved/test-verified.
4. Same-user authentication boundary — specified/synthetic checked; live Android path pending.
5. Replay safety — test-verified/merged.
6. Stale conflict safety — test-verified/merged.
7. Restart/retry safety — test-verified/merged.
8. No dual writable masters — direct native planner guard test-verified/merged.
9. Provider portability — preserved in command/API model.
10. Synthetic first — passed.
11. Legacy preservation — passed so far.
12. Bounded scope — maintained.
13. Stock-ChatGPT zero-external-infrastructure lane remains valid — live-verified in M2-M0.
14. Apple/iCloud support preserved without becoming a current blocker — requirement clarified; adapter implementation later.
15. Receipts/assets/inventory scope preserved — canonical feature/backlog inventory verified.
16. **Live isolated Google worker/trigger evidence for concurrent Android mutation — pending.**

## Exact next action

1. Commit and merge this checkpoint correction so `CURRENT_WORK.md` no longer points at the already-merged feature-contract PR and explicitly preserves the Google-first/no-external-infrastructure and Apple-not-current-focus constraints.
2. Resume `M2-M1-001` live proof from the merged head.
3. Seed one isolated synthetic/release MIRA 2.0 spreadsheet with the Git-backed bound Apps Script through an approved provider/operator path; never use a legacy production spreadsheet.
4. Enable queued-writer mode and independently verify the Commands tab, exactly one worker trigger, mutation mode, synthetic command result, canonical Resource/Idempotency readback and at least one stale/retry behavior.
5. If live proof passes, close `ANDROID-COMMAND-BOUNDARY-001` and create the next bounded `ANDROID-CLIENT-CORE-001` packet.
6. If the provider proof remains tool-blocked, retain this exact checkpoint and dependency-rank the next **no-app Google user-visible vertical** rather than inventing external infrastructure solely to unblock Android.

## Recovery protocol

Read this file first. Verify `main` contains `618fefa1f15ddfd91a96d7197e3186e19b988457` or a descendant and then verify the checkpoint correction PR from `integration/m1-001-checkpoint-priority-clarify` is merged or still open. Do not re-open the already merged feature-contract capture work. Continue `M2-M1-001` live provider proof if the Workspace script operator path is available; otherwise preserve the exact blocked step and select the highest-value Google-only user-visible vertical from canonical `FEATURES.md`/`BACKLOG.md` without making Android or external infrastructure a prerequisite for ordinary Personal MIRA.

Keep provider IDs, secrets, personal data and live row contents out of public Git.
