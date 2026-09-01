# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. Provider capability/readback evidence, service activation, source evidence, and canonical state remain separate truths.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` canonical provider/appointment identity is merged/test-verified.
- `CAL-008` requires multi-source appointment evidence intake with provenance, confidence, ambiguity handling, dedupe and canonical reconciliation; this packet implements the direct stock-ChatGPT text/image seam without pretending Gmail or Calendar-provider proof exists.
- `CAL-006`/`CAL-007` projection remains capability-gated; successful appointment capture does not imply a Calendar event exists.
- `SERVICE-001` keeps explicit user intent/readiness/activation separate from source evidence.
- `MAIL-002` remains a hard outbound-contact boundary; direct appointment capture sends no mail.

### `BACKLOG.md`

- `APPOINTMENT-INTAKE-CORE-001` is complete through `M2-M0-024` / PR #79.
- `APPOINTMENT-INTAKE-NOAPP-001` is the active direct text/image slice. Its implementation, release contract, and isolated Google Workspace persistence/readback are now verified; actual live stock-ChatGPT model extraction/vision remains a separate evidence ceiling.
- `APPOINTMENT-INTAKE-GMAIL-001` remains separate downstream work because Gmail source capability/readback must not be smuggled into this packet.
- `APPOINTMENT-INTAKE-001` remains a split/partial umbrella until remaining source lanes/evidence are verified.

### `ROADMAP.md`

- M2-M0.5 prioritizes repeated useful no-app Personal vertical progress before Android.
- The direct appointment seam now composes existing canonical identity/intake and native Workspace foundations rather than introducing another authority.
- Live Calendar projection, Gmail source integration and model/vision quality remain independently evidenced capabilities.

### Direction result

**ALIGNED.** Complete `M2-M0-025` at the evidence level actually demonstrated: implementation/test verified plus isolated Google Workspace provider readback for appointment bindings/provider/appointment state. Do not claim live stock-ChatGPT extraction/vision or Calendar mutation from this evidence.

## Completed predecessor

### `M2-M0-024` — Appointment evidence intake/reconciliation core

- **Work:** `APPOINTMENT-INTAKE-CORE-001` (split from umbrella `APPOINTMENT-INTAKE-001`)
- **Feature:** `CAL-008`
- **PR #79 merge/main SHA:** `d3ef80e1d9de8ddd610db4dbe2eea8ffd4f489c3`
- **PR #79 final exact-head CI:** `33457428093` green
- **PR #79 post-merge main CI:** `33457482126` green
- **Closure PR #80 merge/main SHA:** `e400593af676ecbdf3c08d2eda2b8ab2eab0b87a`
- **Closure post-merge main CI:** `33457864873` green
- **Durable evidence:** provider-neutral intake/reconciliation, confidence/provenance gates, legacy-compatible end/timezone persistence, synthetic service-gated Calendar handoff, and CAL-005 same-start self-collision repair.
- **Evidence ceiling:** no source-to-extraction orchestration, Gmail fetching, live Calendar mutation, reminder delivery, outbound provider contact, medical interpretation, or Android behavior was claimed.

## Active packet

### `M2-M0-025` — Direct no-app appointment text/image flow

- **Primary work:** `APPOINTMENT-INTAKE-NOAPP-001`
- **Primary features:** `CAL-008`
- **Related invariants/features:** `CAL-005`, `CAL-006`, `CAL-007`, `SERVICE-001`, `RECOVERY-002`, `ONBOARD-006`, `PROVIDER-002`, `MAIL-002`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-025-appointment-noapp`
- **Base SHA:** `e400593af676ecbdf3c08d2eda2b8ab2eab0b87a`
- **PR:** #81 open
- **Green release-contract implementation head before lifecycle checkpoint:** `ba84b4883dced7ce032590a879a25183b49b2c69`
- **CI on that head:** `33459111450` green
- **Verification count:** 376 Python tests + 30 Workspace Apps Script tests passed; compile, feature registry, product lifecycle ledger, Personal distribution, work-session alignment and code ownership all green.
- **Dependencies:** merged `APPOINTMENT-INTAKE-CORE-001`, `CHATGPT-API-CLIENT-001`, `API-DEPLOYMENT-001A`, `SERVICE-STATE-001`
- **Blockers:** no implementation blocker. Live stock-ChatGPT text/image extraction/vision and live Calendar event projection remain unverified external evidence layers and must not be inferred from Workspace proof.

### Objective

Make direct appointment capture useful in stock ChatGPT without requiring Gmail or a custom app. When a user supplies appointment details as text or uploads an appointment image, MIRA has a deterministic runtime/release contract that converts structured model extraction into provenance-bound canonical provider/appointment reconciliation, asks only for materially blocking ambiguity, and persists/read backs the resulting canonical state through the native Personal Google Workspace path. Calendar projection remains optional downstream behavior only when the appointment service and provider lane are actually active/verified.

The stock ChatGPT model remains the semantic extractor for direct user text/image. Repository code owns deterministic provenance, confidence/identity gates, canonical mutation/readback planning, replay/correction semantics and the complete no-app operating contract. Unit/provider tests do not pretend to measure model vision quality.

### Implemented and test-verified behavior

- `mira/appointment_noapp.py` implements the direct no-app planning boundary without provider I/O inside the module.
- Accepted direct source classes are exactly `text` and `image`.
- Direct text uses SHA-256 of the exact UTF-8 user material with basis `exact_text_sha256` and does not copy the raw message wholesale into canonical payloads.
- Image evidence uses `raw_file_sha256` only when a real raw-file digest is supplied; otherwise it uses explicitly labelled `normalized_extraction_sha256_v1` over deterministic structured extraction material. The fallback is never represented as an image-byte hash.
- Stable source identity includes the fingerprint basis; conflicting material for one stable source fails closed to Needs Review.
- A backward-compatible Personal enrichment planner validates the existing verified Google Sheets authority and adds only missing exact bindings for `appointment_provider`, `appointment`, and `calendar_projection`. Historical entity bootstrap is not rewritten. Duplicate/conflicting routing fails closed.
- Fresh provider/appointment Resource readback is loaded into a planning snapshot and the real `AppointmentIdentityService` + `AppointmentIntakeService` execute the canonical CAL-005/CAL-008 rules. No second identity engine was created.
- Only actual canonical provider/appointment changes become native `WorkspaceUpsertPlan` mutations; planned native records must exactly equal the canonical reconciliation result.
- Native Workspace revision, idempotency, atomic Resource+Idempotency request material and exact readback semantics are reused unchanged.
- Exact replay is zero-write; user-confirmed correction precedence is preserved.
- Low-confidence/missing essential identity yields one concise materially blocking clarification; optional weak metadata remains omitted.
- Calendar handoff remains service/capability-gated and was tested only with synthetic projection infrastructure.
- Complete `MIRA_NO_APP_INSTRUCTIONS.md` and Workspace release guards now include direct appointment text/image provenance, binding enrichment, clarification, canonical write/readback and Calendar-downstream rules. Normal user-facing language is MIRA.
- No Gmail fetching, OCR/model service, reminder scheduling, outbound provider contact, medical inference, Microsoft/Apple Calendar, Android or paid OpenAI API dependency was introduced.

### Fresh isolated Google Workspace provider evidence

A fresh copy of a clean **synthetic** MIRA 2.0 proof spreadsheet was used. Its provider identifier is intentionally not stored in public Git. Legacy/personal production state and protected Calendars were not used.

Provider proof established:

1. mutable `Resources`, `Events`, and `Idempotency` state began empty apart from headers;
2. the proof copy was upgraded only within the isolated synthetic namespace to the current appointment-capable Resource-type metadata;
3. one synthetic `google-sheets-personal` authority was written with matching native Idempotency material and independently read back exactly;
4. the three appointment-related authority bindings were written as one bounded batch and independently read back exactly;
5. synthetic direct-text evidence using `exact_text_sha256` produced one deterministic provider and one deterministic appointment at revision 1;
6. provider + appointment Resource and Idempotency rows were written through the native Workspace material contract and independently read back with exact stable identities, revisions, payloads, request hashes and resource references;
7. no Calendar event was created and no source-provider or protected production state was mutated.

This proves the native Google Workspace binding/persistence/readback integration for direct appointment canonical material. It does **not** prove live stock-ChatGPT text interpretation, image vision/extraction quality, a complete connector-orchestration invocation of the new Python module, or live Calendar event projection.

### Acceptance criteria status

1. Deterministic direct `text`/`image` evidence contract: **met/test-verified**.
2. Source class/ref/time/authority/confidence/fingerprint basis without raw source copies: **met/test-verified**.
3. Exact-text hash and no fake image raw hash: **met/test-verified**.
4. Explicit derived image fingerprint fallback and source-conflict failure: **met/test-verified**.
5. Concise materially blocking clarification; optional weak metadata omitted: **met/test-verified**.
6. Provider then appointment reconciliation through merged core with correction precedence: **met/test-verified**.
7. Identical direct evidence replay zero canonical revision/write: **met/test-verified**.
8. Deterministic native Workspace mutation/readback plan: **met/test-verified**.
9. Exact native Resource identity/revision/idempotency/readback; no model-local authority: **met/test-verified and isolated-Google readback verified**.
10. Calendar only when effectively active/verified: **met in code/tests; synthetic projection only, no live Calendar write claimed**.
11. No protected Primary/Family Calendar or legacy production fixture: **met**.
12. No Gmail/outbound/reminder/medical/Microsoft/Apple/Android/paid-API expansion: **met**.
13. Complete no-app operating/release contract updated: **met/test-verified**.
14. Direct provenance/replay/conflict/correction/binding/readback/Calendar-gating tests: **met**.
15. Production ownership/release/work-session gates: **met on `ba84b488...`**.
16. Final exact-head CI, expected-head merge, remote-main readback and post-merge CI: **pending lifecycle checkpoint head**.
17. Evidence honesty: **met**; Workspace provider readback is verified, live stock-ChatGPT model/vision and Calendar projection are explicitly unverified.

### Evidence state

- **Desired:** yes
- **Specified:** yes
- **Implemented:** yes
- **Test-verified:** yes, head `ba84b4883dced7ce032590a879a25183b49b2c69`, CI `33459111450`, 376 Python + 30 Apps Script tests
- **Integration-verified:** yes for isolated native Google Workspace appointment authority-binding, provider Resource, appointment Resource, Idempotency and exact readback material; synthetic-only source facts
- **Live-verified:** no for actual stock-ChatGPT text/image extraction/vision or live Calendar projection

### Lifecycle interpretation

`M2-M0-025` can merge at implementation/test + bounded Workspace integration evidence once final exact-head CI is green. `APPOINTMENT-INTAKE-NOAPP-001` must remain **partial at the live source/model evidence layer** after merge unless a real stock-ChatGPT direct text/image extraction run is separately demonstrated. `APPOINTMENT-INTAKE-001` remains split/partial because Gmail and other source/provider evidence are separate child work.

## Exact next action / resume point

1. Reconcile `BACKLOG.md` and PR #81 with the exact test/provider evidence above without committing any proof-spreadsheet/provider identifier.
2. Require one final exact-head CI after lifecycle documentation changes.
3. Fix only packet-local failures if any final gate regresses.
4. Merge PR #81 only with `expected_head_sha` when final exact-head CI is green.
5. Verify remote `main` contains the new runtime/release contract and verify post-merge `main` CI.
6. Create a bounded closure checkpoint if required so Git records the actual merge SHA/post-merge CI before selecting new implementation scope.
7. Do not expand this packet into Gmail fetching, OCR/model infrastructure, live Calendar mutation, reminders, outbound contact, medical meaning, Microsoft/Apple Calendar or Android.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Confirm PR #81 and branch `integration/m0-025-appointment-noapp`. The implementation/release contract is green at `ba84b4883dced7ce032590a879a25183b49b2c69` / CI `33459111450`, and bounded isolated Google Workspace provider readback has succeeded without protected production state. Continue only from the exact next action above and preserve the live-evidence ceiling.
