# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. Provider capability/readback evidence, service activation, source evidence, and canonical state remain separate truths.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` canonical provider/appointment identity is merged/test-verified.
- `CAL-008` requires actual multi-source appointment intake, not merely a provider-neutral extraction-result data structure.
- `CAL-006`/`CAL-007` projection remains capability-gated; no live Calendar write may be inferred from successful intake.
- `SERVICE-001` keeps explicit user intent/readiness/activation separate from source evidence.
- `MAIL-002` remains irrelevant to direct user text/image intake unless outbound provider contact is later requested; this packet sends no mail.

### `BACKLOG.md`

- `APPOINTMENT-INTAKE-CORE-001` is complete through `M2-M0-024` / PR #79.
- `APPOINTMENT-INTAKE-NOAPP-001` is the highest-value next appointment slice: direct user text or user-supplied image -> bounded extraction contract -> canonical Google-backed reconciliation/readback, with Calendar projection attempted only when verified active capability exists.
- `APPOINTMENT-INTAKE-GMAIL-001` is separate downstream work because Gmail source capability/readback should not be smuggled into this packet.
- `APPOINTMENT-INTAKE-001` remains a split/partial umbrella until direct no-app and later source lanes are verified.

### `ROADMAP.md`

- M2-M0.5 explicitly prioritizes repeated useful no-app Personal vertical progress before Android.
- The provider-neutral intake core is now merged; the next useful slice should let a normal stock-ChatGPT user give MIRA appointment information directly without terminal/server/provider-development ceremony.
- Packet scope must remain bounded; Gmail, reminder delivery, Microsoft/Apple Calendar and Android are not prerequisites for direct text/image capture.

### Direction result

**ALIGNED.** `APPOINTMENT-INTAKE-NOAPP-001` is selected because it consumes already-green identity/intake/Workspace foundations, unlocks direct ordinary-user value, and has fewer infrastructure dependencies than the Gmail lane. No-app text/image capture is now the one active implementation packet.

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
- **Dependencies:** merged `APPOINTMENT-INTAKE-CORE-001`, `CHATGPT-API-CLIENT-001`, `API-DEPLOYMENT-001A`, `SERVICE-STATE-001`
- **Blockers:** none known at packet start; provider/live evidence may be capability-limited and must be reported honestly rather than worked around with protected production state.

### Objective

Make direct appointment capture useful in stock ChatGPT without requiring Gmail or a custom app. When a user supplies appointment details as text or uploads an appointment image, MIRA should produce the bounded intake-core extraction material, preserve honest source provenance, ask only when missing/ambiguous facts materially block canonical identity, reconcile provider + appointment state through the existing core, and persist/read back the result through the native Personal Google Workspace path. Calendar projection is optional downstream behavior only when the appointment service and provider lane are actually active/verified.

The stock ChatGPT model is the semantic extractor for direct user text/image. Repository code owns the deterministic contract, validation, canonical mutation/readback protocol, replay/correction semantics, release instructions, and evidence truth. Tests must not pretend unit fixtures prove model vision quality or live provider writes.

### Source-provenance rule

1. Never fabricate a provider/raw-material hash that the runtime does not expose.
2. For direct text, exact user message material may be deterministically fingerprinted for replay/dedupe without storing the raw message in canonical structured state.
3. For image evidence, retain the strongest stable attachment/file source reference exposed by the runtime. If an immutable raw-file fingerprint is available, preserve it. If not, explicitly label any deterministic extraction fingerprint as derived from normalized extraction material rather than pretending it hashes original image bytes.
4. One stable source identity paired with materially conflicting extraction must fail closed to Needs Review/reconciliation rather than silently mutate source history.
5. Canonical appointment/provider truth stores normalized facts and provenance references, not raw chat text or image bytes.

### Acceptance criteria

1. Define a deterministic no-app direct-evidence contract for `text` and `image` that maps stock-ChatGPT extraction into `APPOINTMENT-INTAKE-CORE-001` without Gmail/provider-fetch dependencies.
2. Preserve source class, stable source reference, observation time, extraction authority/confidence, and fingerprint basis. Raw text/image bodies are not copied into canonical structured state.
3. Direct text may hash exact user-provided material locally for fingerprinting; image handling must never claim a raw-file hash unless that hash is actually exposed/verified.
4. If image raw fingerprint is unavailable, use an explicitly derived normalized-extraction fingerprint plus stable attachment reference; changing extracted material for the same source must fail closed rather than silently overwrite evidence.
5. Low-confidence or missing provider/occurrence identity returns a concise Needs Review question containing only materially blocking ambiguity; optional weak metadata is omitted.
6. Successful no-app intake reconciles provider then appointment through the merged core and preserves user-confirmed correction precedence.
7. Identical direct evidence replay performs zero additional canonical revision/write.
8. Provide a deterministic native Workspace mutation/readback plan for the canonical provider/appointment resources so stock ChatGPT can persist them through the existing same-user Google path without Apps Script/terminal/API-key ceremony.
9. Native Google persistence uses exact resource identity/revision/idempotency/readback semantics; no model-local state may become a second authority.
10. Calendar projection is attempted only when explicit service state is effectively active and a verified Calendar capability/target exists; otherwise intake succeeds with projection status honestly skipped/unavailable.
11. No protected Primary/Family Calendar or legacy MIRA production artifact is used as a development fixture.
12. No Gmail fetching, outbound provider contact, reminder scheduling, medical inference, Microsoft/Apple implementation, Android work, or paid OpenAI API dependency is introduced.
13. Update the complete no-app operating/release contract so direct appointment text/image behavior is executable by stock ChatGPT and cannot regress into technical user setup.
14. Direct tests cover text fingerprint/replay, image raw-fingerprint path, image derived-fingerprint fallback, conflicting extraction for one source, low-confidence clarification, canonical create/replay/correction, Workspace mutation/readback plan, inactive Calendar suppression, and capability-gated synthetic projection handoff.
15. Production ownership/release/work-session gates must cover any new production module or instruction contract.
16. Exact final PR-head CI, expected-head merge protection, remote-main readback and post-merge CI are required before packet completion.
17. Live-provider/source completion is claimed only at the level actually demonstrated; synthetic/CI evidence does not imply live ChatGPT image extraction or Calendar-provider verification.

### Evidence state

- **Desired:** yes
- **Specified:** yes in `CAL-008` / `APPOINTMENT-INTAKE-NOAPP-001`
- **Implemented:** no
- **Test-verified:** no
- **Integration-verified:** no
- **Live-verified:** no

## Exact next action / resume point

1. Inspect `MIRA_NO_APP_INSTRUCTIONS.md`, the Personal distribution/release validator, `workspace_native.py`, and the merged appointment-intake core before choosing the smallest implementation seam.
2. Implement provenance-honest direct text/image normalization + deterministic Workspace mutation/readback planning without adding Gmail/provider fetching.
3. Add direct tests and code-ownership/release validation.
4. Run exact-branch/PR CI; fix only packet-related failures.
5. Seek bounded synthetic/live Google-backed provider evidence through isolated MIRA 2.0 state only; never use protected legacy production or personal Calendar state as a fixture.
6. Reconcile lifecycle evidence before merge and do not overclaim model/provider capability.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. Confirm branch `integration/m0-025-appointment-noapp` starts from closure merge `e400593af676ecbdf3c08d2eda2b8ab2eab0b87a`, whose main CI `33457864873` is green. `M2-M0-024` is closed. Continue only `APPOINTMENT-INTAKE-NOAPP-001`; Gmail and other provider/source work remain outside this packet.
