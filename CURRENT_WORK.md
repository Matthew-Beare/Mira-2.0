# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active/recovery packet and exact recovery state.

## Product direction

Default Personal MIRA remains stock ChatGPT + Google Workspace first. Android extends the same canonical reality and must not become a second authority. Google authorization/network details live behind a replaceable provider module; provider-neutral client state, reconnect orchestration and row-transport semantics remain in `:core`.

M2-M1-001 through M2-M1-007 and M2-GOV-012 are complete at their recorded bounded evidence ceilings. The broader Android client remains partial because the canonical Android read/mutation/stock-ChatGPT cross-readback vertical and representative-device evidence are unfinished.

## Prior-packet / remote-main verification — 2026-09-04

- Repository: `Matthew-Beare/Mira-2.0`.
- PR #106 merged the first M2-M1-007 product-behavior implementation at `f6d38ee9398bc473425f33b6fe97fb5fb0ae4b35`; post-merge CI `33826483012` succeeded on that exact SHA.
- Duplicate PR #105 is closed unmerged and preserved only as salvage/history. It must never be merged as a second Google provider stack.
- PR #107 reconciled the duplicate implementations and merged with expected-head protection at `f6b05eee9b70a97e7786c181723b164f5c2c4b7a`.
- Remote `main` independently read back the same PR #107 merge SHA.
- Post-merge CI `33835441292` succeeded on exact merge SHA `f6b05eee9b70a97e7786c181723b164f5c2c4b7a`.
- Canonical lifecycle reconciliation then advanced through final lifecycle head `635f19666b86a4d9be180234d0c3e197ed2aa088`; CI `33835898677` succeeded on that exact head.

## Session-start alignment verification — 2026-09-04 M2-M1-007 final closeout

### `FEATURES.md`

- `CLIENT-ANDROID-001` now records `specified+implemented+test_verified+partial` rather than stale unmerged/legacy-only evidence.
- The feature remains partial because `ANDROID-SYNC`, conflict UX and representative-device proof remain unfinished.
- `PROVIDER-002` ordinary-user connection semantics and `PROVIDER-003` deterministic Personal Google verification remain preserved without making Google a universal client dependency.

### `BACKLOG.md`

- `ANDROID-CLIENT-CORE-001` now correctly records partial through M2-M1-007: enrollment/session trust, protected credentials, encrypted offline state, reconnect coordination, Workspace transport, and Android Google authorization/Workspace binding are merged/test-verified.
- Live Android Google authorization/provider-device evidence, the bounded canonical Android↔ChatGPT shared-state vertical, conflict UI and representative-device proof remain unfinished.
- `ANDROID-SYNC` is the dependency-correct next milestone work, not another provider-binding implementation.

### `ROADMAP.md`

- M2-M1-001 through M2-M1-007 are recorded complete at their bounded evidence ceilings.
- The next ordered proof is Android read of canonical Personal state, followed by Android mutation, stock-ChatGPT readback from the same authority, and representative-device proof.
- No live Android provider/device evidence is fabricated by CI or repository completion.

### `PRODUCT_INVARIANTS.md`

- Ordinary-user provider connection remains intent-first and least-privilege.
- Provider consent is not readiness; exact MIRA post-consent verification remains required.
- Users are never asked to copy spreadsheet IDs, OAuth scopes/tokens, open developer consoles, run scripts, or use a terminal for the normal Personal connection path.
- Google provider details remain outside provider-neutral `:core`, one canonical authority is preserved, and legacy MIRA production state remains protected.

### Direction result

**ALIGNED.** M2-M1-007 is complete at implementation/test/integration repository evidence. The Android umbrella remains partial and the next dependency-correct milestone work is the bounded `ANDROID-SYNC` shared-state proof. No additional Google provider implementation or repeat of M2-M1-001 through M2-M1-007 is justified.

## Active packet

### `M2-M1-007` — Android Google authorization and Workspace binding

- **Primary work:** `ANDROID-CLIENT-CORE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `PROVIDER-002`, `PROVIDER-003`
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `API-001`, `RECOVERY-002`, `DATA-001`, `SOURCE-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Final implementation/reconciliation PR:** #107
- **Final verified PR head:** `17c8d488b6f3de10e82cbc1ca6de7242f25204e6`
- **Final verified PR-head CI:** `33829923602` — success
- **Merge SHA:** `f6b05eee9b70a97e7786c181723b164f5c2c4b7a`
- **Verified post-merge CI:** `33835441292` — success
- **Lifecycle reconciliation head before this closeout commit:** `635f19666b86a4d9be180234d0c3e197ed2aa088`
- **Verified lifecycle CI:** `33835898677` — success
- **Status:** complete at bounded implementation/test/integration evidence ceiling; this final closeout commit requires exact-head CI and remote-main readback for durable closure

## Objective result

**COMPLETE AT THE BOUNDED PACKET EVIDENCE CEILING.**

M2-M1-007 supplies one hardened Android Google Workspace provider seam beneath the already-verified provider-neutral Android core:

1. Google Identity Services authorization with the exact least-privilege `drive.file` scope and Google-owned single-Sheet Picker flow.
2. Provider revocation support and fail-closed grant parsing.
3. Automatic verification of selected Drive file identity, Google-Sheet type, Trash/editability state and clean MIRA starter Metadata.
4. Honest `direct_single_writer` versus verified `queued_writer` readiness; provider consent alone never equals shared-write readiness.
5. Exact Commands/Changes protocol-header verification before queued transport readiness.
6. Fresh-token revalidation of a token-free binding without forcing the user to select the same Sheet again.
7. A bounded Sheets/Drive REST bridge that permits only required MIRA reads and exact one-row Commands append semantics.
8. Google SDK/network/provider-identity ownership isolated in `:google-workspace`; provider-neutral `:core` remains free of Google Play Services and provider-only INTERNET permission.
9. Access-token material remains opaque/provider-local; raw token/provider identity is excluded from string/log surfaces.
10. Multi-module Android ownership and CI directly verify every production Android artifact.

## Duplicate-implementation resolution

- PR #106 provided the stronger initial product behavior but placed Google-specific implementation inside `:core`.
- Concurrent PR #105 provided stronger provider-module separation/privacy/governance but was never merged.
- PR #105 was closed and retained only as salvage evidence.
- PR #107 kept the stronger product behavior from #106 while importing the stronger architecture/privacy/HTTP/governance constraints from #105.
- Exactly one Google provider production stack remains. There is no second Android Google authority/connection path.

## Completed evidence

- M2-M1-001 through M2-M1-006 remain durably closed and were not rerun.
- PR #107 final head `17c8d488b6f3de10e82cbc1ca6de7242f25204e6` passed exact-head CI `33829923602`.
- PR #107 merged with expected-head protection at `f6b05eee9b70a97e7786c181723b164f5c2c4b7a`.
- Remote main independently read back the exact merge SHA.
- Post-merge CI `33835441292` succeeded on that exact merge SHA, including compile, feature registry, lifecycle ledger, Personal starter distribution, work-session alignment, multi-module Android ownership, both Android modules, Python and Workspace Apps Script tests.
- `FEATURES.md` lifecycle evidence was reconciled in main commit `16169ef48bb7f46bdaced3ea8ed6ed2190c1a6dc`.
- `ROADMAP.md` M2-M1 ordering/status was reconciled in main commit `152d22e178abda7ce380c238aed820ac9cefade5`.
- `BACKLOG.md` Android core/lifecycle findings were reconciled in main commit `635f19666b86a4d9be180234d0c3e197ed2aa088`.
- Lifecycle CI `33835898677` succeeded on exact lifecycle head `635f19666b86a4d9be180234d0c3e197ed2aa088`.
- No Work mode was used.
- No live Google provider mutation, historical M2-M1-001 proof-resource mutation, legacy MIRA production fixture, personal spreadsheet ID, token, email, credential or other private provider state was used or committed.

## Acceptance criteria result

1. Exactly one Google provider implementation — **satisfied and merged**.
2. Provider-neutral `:core` with no Google SDK/provider-only INTERNET requirement — **satisfied and merged**.
3. Dedicated `:google-workspace` owns GIS authorization/revoke, Picker parsing, verification/readiness/revalidation and bounded REST — **satisfied and merged**.
4. Strong file identity/clean-starter/direct-vs-queued/revalidation/revocation behavior preserved — **satisfied**.
5. Token/provider identity privacy hardening — **satisfied**.
6. REST bounded/fail-closed/no hidden append retry — **satisfied**.
7. Multi-module ownership and CI — **satisfied and green**.
8. Zero Work/live-provider/legacy-state development scope — **satisfied**.
9. Exact PR-head CI, expected-head merge, remote-main readback and post-merge CI — **satisfied**.
10. Canonical FEATURES/BACKLOG/ROADMAP lifecycle reconciliation and exact lifecycle CI — **satisfied**.
11. Final CURRENT_WORK closeout exact-head CI plus matching remote-main readback — **pending only**.

## Explicitly deferred

- Live Android Google authorization/provider-device proof.
- `ANDROID-SYNC`: Android canonical read, mutation, and stock-ChatGPT cross-readback from the same authority.
- Conflict-resolution UI.
- Broad Android Connections UI polish/presentation.
- Representative physical-device proof and Android release signing/distribution.
- Gmail, Calendar, Contacts, Microsoft, Apple/iCloud, Airtable, finance and other provider adapters.
- Context-aware integration recommendation implementation under `PROVIDER-004`.

## Session-end alignment verification — 2026-09-04 M2-M1-007 final closeout

### `FEATURES.md`

`CLIENT-ANDROID-001` is correctly partial with merged implementation/test evidence. M2-M1-007 completion does not imply Android shared-state or device completion.

### `BACKLOG.md`

`ANDROID-CLIENT-CORE-001` is correctly partial through M2-M1-007. `ANDROID-SYNC` remains the next shared-state vertical; no completed packet is returned to the active queue.

### `ROADMAP.md`

M2-M1-001 through M2-M1-007 are now recorded complete at their evidence ceilings, while canonical Android read/mutation/cross-readback and device proof remain the next ordered work.

### `PRODUCT_INVARIANTS.md`

Least privilege, provider-owned unavoidable UI only, automatic verification, no copied IDs/technical setup, provider-neutral core, one-authority semantics and legacy-data protection remain preserved.

### Direction result

**ALIGNED.** The packet closes the Android Google provider-binding prerequisite without falsely completing `CLIENT-ANDROID-001` or `ANDROID-CLIENT-CORE-001`. Dependency-ranked next work begins with the bounded `ANDROID-SYNC` evidence gap.

## Exact next action / resume point

1. Require CI on this final `main` closeout commit and verify success on the exact pushed head.
2. Independently read back remote `main` at that same closeout head.
3. Once both are green/matching, treat M2-M1-007 as durably closed and never rerun it.
4. Before opening the next packet, re-read `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PRODUCT_INVARIANTS.md` from authoritative main.
5. Open exactly one dependency-correct bounded M2-M1 continuation, expected `M2-M1-008`, derived from `ANDROID-SYNC`. Prefer the smallest meaningful shared-state slice, likely canonical Android read first; include mutation/cross-readback only if it remains a bounded independently verifiable vertical after fresh dependency review.
6. Do not absorb conflict UI, broad Connections UI, notification/TTS, capture, release/signing or unrelated providers unless a hard dependency is discovered.
7. Do not use Work mode until deterministic source/tests are green and a narrowly scoped live provider/browser/device acceptance proof genuinely remains.

## Recovery protocol

Read this file first and verify the final closeout commit against remote `main` plus exact-head CI. If both match and are green, M2-M1-007 is durably closed. PR #105 is closed history/salvage only; PR #106 and PR #107 are completed history. Do not create another Google provider stack and do not rerun M2-M1-001 through M2-M1-007. Select the next packet from canonical Git state, not chat memory.
