# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: users state intent in ordinary language, provider-native authorization is the only unavoidable provider ceremony, and MIRA performs technical setup when software can safely do it. Provider capability/readback evidence, service activation, source evidence, and canonical state remain separate truths.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity reconciliation remains the canonical identity authority and now includes a regression-fixed same-start correction path.
- `CAL-008` remains broader than the completed provider-neutral core: actual source-to-extraction integration is still required before the full appointment-intake feature may be called end-to-end complete.
- `CAL-006`/`CAL-007` provide projection semantics, but real provider Calendar event write/readback remains a separate live-evidence boundary.
- `MAIL-002` continues to prohibit outbound provider contact without explicit per-message approval.

### `BACKLOG.md`

- `APPOINTMENT-INTAKE-001` must be reconciled as an umbrella/partial user-visible vertical rather than falsely marked complete merely because its provider-neutral core is merged.
- `CALENDAR-PROJECTION-GOOGLE-001` is merged/test-verified at the native implementation layer but remains partial at live provider-write evidence.
- Gmail fetching, user-text/image extraction integration, reminders, Microsoft/Apple Calendar, outbound contact, and Android remain separate unfinished work.

### `ROADMAP.md`

- M2-M0.5 prioritizes repeated useful no-app Personal vertical progress before Android.
- The merged intake core is prerequisite plumbing for an actual no-app appointment flow, not the whole user experience.
- The next implementation packet must be selected from unfinished accepted work after this closure checkpoint is durable.

### Direction result

**ALIGNED FOR PACKET CLOSURE.** `M2-M0-024` delivered and merged the bounded provider-neutral appointment intake/reconciliation core at the evidence level actually proved. This closure checkpoint records merge/main evidence and preserves the remaining user-visible intake work instead of overstating feature completion.

## Completed predecessor

### `M2-M0-023` — Google Calendar Personal projection lane

- **Work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Features:** `CAL-006`, `CAL-007`
- **PR:** #78
- **Merge/main SHA:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **Post-merge main CI:** `33438237335` green
- **Evidence ceiling:** native Personal Calendar implementation/release contract test-verified; live event write/readback not verified because no isolated writable Calendar was available and protected Primary/Family state was not used as a fixture.

## Active packet

### `M2-M0-024` — Appointment evidence intake/reconciliation core — closure checkpoint

- **Primary work:** `APPOINTMENT-INTAKE-001`
- **Primary features:** `CAL-008`
- **Related invariants/features:** `CAL-005`, `RECOVERY-002`, `CAL-006`, `CAL-007`, `SERVICE-001`, `MAIL-002`, `PROFILE-013`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Implementation branch:** `integration/m0-024-appointment-intake`
- **Closure branch:** `governance/m0-024-closure`
- **Base SHA:** `b1d7a4f20ebad3503a3c518ec568c47498e85d42`
- **PR:** #79 merged
- **Final PR head:** `461b4ae30991a26a276030b50283b87b3e3c7cb9`
- **Final exact-head CI:** `33457428093` green
- **Merge/main SHA:** `d3ef80e1d9de8ddd610db4dbe2eea8ffd4f489c3`
- **Post-merge main CI:** `33457482126` green
- **Remote main readback:** `mira/appointment_intake.py` present at merge `main`.

### Completed objective

The bounded provider-neutral core now accepts authorized evidence references from the `email`, `image`, and `text` source classes plus structured extracted facts; validates provenance, immutable material fingerprint, offset-aware observation time, authority and confidence; fails closed on weak or ambiguous identity; reconciles provider then appointment through canonical `CAL-005`; preserves exact optional end/timezone material needed for later projection; and gates synthetic Calendar handoff behind explicit active service/capability state.

### Durable implementation evidence

- `mira/appointment_intake.py` implements the provider-neutral intake/reconciliation service.
- Deterministic confidence thresholds: 0.90 identity/timing, 0.80 optional descriptive metadata.
- User-confirmed evidence remains highest authority through canonical reconciliation.
- Exact evidence replay is zero-revision-growth; conflicting material for one source identity fails closed.
- Provider ambiguity blocks appointment mutation; appointment ambiguity becomes Needs Review.
- Canonical appointments optionally persist exact `end_at` and IANA `timezone`; legacy payloads lacking those fields remain readable.
- Calendar projection is downstream and non-destructive to canonical appointment truth.
- Existing `CAL-005` self-collision defect was fixed so a canonical appointment correction at the same start time excludes itself by `appointment_id` rather than comparing against `provider_id`.
- Direct regression `test_user_confirmed_same_start_correction_does_not_collide_with_itself` locks the integrity repair.
- Implementation CI `33457016348`: 366 Python + 30 Workspace Apps Script tests green and every repository gate passed.
- Final lifecycle head CI `33457428093`: green.
- Expected-head merge protection used successfully.
- Post-merge `main` CI `33457482126`: green.

### Acceptance criteria status

1. Email/image/text source class contract + provenance/fingerprint/time: **met/test-verified**.
2. Structured extraction result contract with confidence/authority: **met/test-verified**.
3. Deterministic essential identity before mutation: **met/test-verified**.
4. Explicit confidence thresholds and omission of weak optional facts: **met/test-verified**.
5. Provider-first ambiguity gate: **met/test-verified**.
6. Appointment ambiguity gate: **met/test-verified**.
7. Replay/conflicting-source behavior: **met/test-verified**.
8. User-confirmed precedence: **met/test-verified**, including same-start self-collision repair.
9. Canonical/Needs Review/projection state separation: **met/test-verified**.
10. Active-service-only synthetic projection handoff: **met/test-verified**.
11. Projection failure preserves canonical truth: **met/test-verified**.
12. No attendees/Meet/reminders/medical/outbound-contact expansion: **met**.
13. Direct source/replay/confidence/ambiguity/correction/service/projection coverage: **met**.
14. Ownership/repository alignment gates: **met**.
15. Final exact-head CI, expected-head merge, remote-main readback and post-merge CI: **met**.

### Evidence state

- **Desired:** yes
- **Specified:** yes
- **Implemented:** yes
- **Test-verified:** yes
- **Integration-verified:** provider-neutral canonical identity + service-state + synthetic Calendar projection composition only
- **Live-verified:** no

### Explicit evidence ceiling / unfinished umbrella work

`APPOINTMENT-INTAKE-001` is not end-to-end complete. The following remain outside the proved packet:

- source-to-extraction orchestration for ordinary user text and user-supplied images;
- Gmail search/fetch and mailbox evidence intake;
- OCR/model/provider extraction infrastructure where needed;
- real Google/Microsoft/Apple Calendar event mutation/readback;
- reminder delivery;
- outbound provider contact;
- medical interpretation;
- Android capture/client behavior.

Protected Primary/Family/legacy Calendar state remains unavailable as a development fixture.

## Exact next action / resume point

1. Reconcile `BACKLOG.md` so the merged provider-neutral core is durable evidence while `APPOINTMENT-INTAKE-001` remains partial/split until actual source-to-extraction user flow exists.
2. Run closure-branch CI and merge the closure checkpoint to `main` with expected-head protection.
3. Verify closure `main` readback/CI.
4. Re-rank unfinished accepted work against `ROADMAP.md`; prefer the shortest high-value no-app vertical that consumes the merged intake core without inventing provider capability.
5. Create exactly one next implementation packet and update `CURRENT_WORK.md` before code changes.
6. Do not resume Android or expand into unrelated feature families merely because this packet is closed.

## Recovery protocol

Read this file first, then `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md`. `M2-M0-024` implementation is merged and post-merge green at `d3ef80e1d9de8ddd610db4dbe2eea8ffd4f489c3` / CI `33457482126`. The only remaining action in this packet is durable lifecycle closure and next-work selection. Do not reconstruct unfinished source-integration work from chat memory; Git backlog decomposition is authoritative once the closure checkpoint merges.
