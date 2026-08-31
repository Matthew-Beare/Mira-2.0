# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace with no external infrastructure prerequisite. Repeated useful no-app verticals and integrity/recovery hardening remain ahead of Android. Normal user-facing branding is **MIRA**. `MIRROR` remains an internal database/reality-layer term only when a technical database-specific context requires it.

Ordinary-user setup follows `PRODUCT_INVARIANTS.md`: the MIRA-side choice is plain-language intent, normally a simple yes/no such as **“Yes, use my calendar.”** If a provider requires authorization, the provider's unavoidable Allow/Connect consent UI is the only provider-specific ceremony. MIRA performs every setup/discovery/binding/verification step that software can safely perform. Normal users are not expected to create hidden resources, copy provider IDs, edit OAuth scopes, open Apps Script/developer consoles, paste code, run a terminal, or understand implementation mechanics.

Every work session begins and ends by checking `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and applicable cross-feature product invariants.

## Session-start alignment verification — 2026-08-31

### `FEATURES.md`

- `CAL-005` appointment/provider identity is merged/test-verified through PR #76.
- `CAL-007` provider-neutral Calendar projection is merged/test-verified through PR #77 with synthetic provider readback only.
- `CAL-006` still requires one real preferred-Calendar lane before MIRA may claim Calendar sync is live.
- `CAL-008` remains the next user-visible appointment-intake vertical after a default Personal Calendar lane is usable.
- Existing `ONBOARD-006` / `PROVIDER-002` direction already requires browser-only nontechnical provider onboarding; `PRODUCT_INVARIANTS.md` now makes the plain-language-intent/no-developer-chores rule explicit across all features.

### `BACKLOG.md`

- `CALENDAR-PROJECTION-001A` is complete through PR #77.
- `CALENDAR-PROJECTION-GOOGLE-001` remains the single active provider-lane prerequisite in M2-M0-023, but the default-Personal interpretation is corrected below.
- The stronger Google ETag/Apps Script lane remains useful hardening for concurrent/shared-writer scenarios; it must not become ordinary-user setup merely because it offers stronger concurrency semantics.
- Microsoft/Outlook/M365 and Apple/iCloud proofs remain separate downstream work.

### `ROADMAP.md`

- M2-M0.5 prioritizes an ordinary-user stock-ChatGPT + Personal Google product before Android.
- The completed Personal Google Sheets baseline explicitly accepts a native same-user **single-writer** connector path without pretending it provides distributed compare-and-swap.
- Calendar should follow the same product principle: simple native Personal behavior first, stronger concurrent/shared-writer execution later.
- Browser-first means no terminal, copied Calendar IDs, manual API setup, hidden menu rituals, or protected production fixtures.

### Direction result

**ALIGNED WITH USER ACCEPTANCE CORRECTION.** The earlier design that made **MIRA → Enable Calendar** a required ordinary-user activation step was too technical. Keep the already-built Apps Script managed-Calendar/ETag adapter as optional stronger-provider evidence, but do not require it for default Personal activation. Continue M2-M0-023 by implementing and verifying the native stock-ChatGPT Google Calendar **single-writer** lane and by codifying intent-first activation.

## Completed predecessor

### `M2-M0-022` — Provider-neutral Calendar projection core

- **Work:** `CALENDAR-PROJECTION-001A`
- **Feature:** `CAL-007`
- **PR:** #77
- **Merge/main SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **Post-merge main CI:** `33427385919` green
- **Evidence ceiling:** provider-neutral/synthetic only; no real Calendar provider write/readback was claimed.

## Active packet

### `M2-M0-023` — Google Calendar Personal projection lane

- **Primary work:** `CALENDAR-PROJECTION-GOOGLE-001`
- **Primary features:** `CAL-006`, `CAL-007`
- **Related invariants/features:** `RECOVERY-002`, `PROFILE-013`, `SERVICE-001`, `PROVIDER-002`, `ONBOARD-006`, `CAL-008`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-023-google-calendar-projection`
- **Base SHA:** `fcc81f0e9d9510d05406acd9068d9ca4ee016806`
- **PR:** #78 open, non-draft, mergeable before this scope-correction commit
- **Last exact fully green head before scope correction:** `3b1054cede74101723ec422352669bec98b6d3c6`
- **CI on that head:** `33434223658` green
- **Current head rule:** re-read the live PR head after each source change and require exact-head CI before merge. Do not create content-identical source commits merely to record their own SHA.

### Objective

Provide the default Personal Google Calendar lane with the lowest-friction safe behavior supported by stock ChatGPT. The user expresses intent in normal conversation, for example **“Yes, use my calendar.”** If Google authorization is missing, MIRA surfaces Google's normal authorization/connection UI. After authorization, MIRA uses the connected Google Calendar capability directly, discovers the available calendar lane, binds the selected/default calendar according to policy, creates/updates only canonical MIRA-tracked projections, and performs exact provider readback.

The stock connector lane is explicitly **single-writer**. It must perform exact preflight read before an update, refuse to overwrite provider drift it did not create/verify, target the exact persisted provider event ID, and perform exact post-write readback. Because the current generic update surface exposes no atomic ETag/If-Match precondition, this lane must not be represented as safe for concurrent Android/multi-client mutation. The already-built Apps Script adapter retains the stronger atomic ETag path for later shared-writer/hardening use and isolated provider proof.

### User-facing activation invariant

For Calendar and future provider-backed features:

1. MIRA asks only for the user's actual intent/permission in ordinary language.
2. Provider-native consent UI is allowed when the provider itself requires it.
3. MIRA does the technical setup after consent.
4. A hidden MIRA/Sheet menu, manually created secondary Calendar, copied provider ID, API console, Apps Script editor, OAuth-scope editing, terminal or pasted code is **not** acceptable default Personal setup.
5. If a provider cannot support a safe simple lane, MIRA records the capability limitation and does not export engineering work to the user.

### Already implemented/test-verified evidence retained from this branch

- Provider versions are opaque tokens, allowing exact Google ETags rather than fake counters.
- `GoogleCalendarProjection.gs` implements a stronger Calendar REST adapter through bound Apps Script user OAuth.
- That stronger lane can create/recover one MIRA-owned secondary Calendar, recover lost create acknowledgement through an installation marker, use private projection/idempotency properties, exact independent GET readback, and exact prior ETag through `If-Match`.
- Its manifest uses `calendar.app.created` + `calendar.calendarlist.readonly` + `script.external_request` and release validation rejects broad Calendar scopes.
- No attendees, attendee notifications, Meet links, reminders, appointment extraction, Microsoft/Apple behavior, medical behavior, or legacy Calendar mutation are introduced.
- Deterministic Personal packaging includes the adapter and its tests.
- A private isolated Drive copy exists for later stronger-lane/provider-template evidence, but ordinary users are not required to open it or invoke a Calendar menu.
- The last pre-correction branch head `3b1054cede74101723ec422352669bec98b6d3c6` passed every repository gate in CI `33434223658`.

### New implementation required by acceptance feedback

- Define native stock-ChatGPT Google Calendar capability semantics for the Personal single-writer lane.
- Preserve stable canonical projection identity even when the native provider surface does not expose private extended-property/idempotency tokens directly.
- Persist provider calendar ID/event ID and verified provider material/version evidence in canonical MIRA state; provider event identity is not inferred from title/time searches after creation.
- Create only after explicit service/calendar intent and provider capability verification.
- On identical replay, read the exact persisted provider event and return unchanged; never create a second event merely because the provider has no idempotency parameter.
- Before update, read the exact persisted event and require it still matches MIRA's last verified provider state. Provider/manual drift fails closed to Needs Review/conflict instead of being overwritten.
- Update the exact provider event ID, then independently read it back and require exact normalized material before canonical success.
- Label the lane honestly as native/single-writer/non-atomic-update. Android/shared-writer Calendar mutation remains blocked until the stronger guarded provider lane is live-verified.
- Update no-app operating instructions and release validation so **plain-language intent + provider authorization** is the default user flow and the Sheet menu is not presented as required activation.

### Live-provider evidence boundary

The connected Google Calendar surface is already authorized enough to list calendars and exposes create/update/read operations, but its generic update action does not accept an atomic ETag/If-Match precondition. Existing Primary/Family calendars remain protected production state and are not development fixtures.

Therefore this packet can complete native-lane implementation/test/release evidence without forcing a manual user click. Live write proof still requires an isolated provider target or an explicitly approved bounded test target. If that live target is unavailable, record the exact live-verification ceiling rather than weakening the ordinary-user UX or writing synthetic test events into protected calendars.

## Acceptance criteria

1. `PRODUCT_INVARIANTS.md` intent-first activation rule is preserved across the current Calendar release surface.
2. Default Personal Calendar activation requires only plain-language user consent plus Google's own unavoidable authorization UI when needed.
3. No required normal-user step involves manual Calendar creation, Sheet-menu hunting, provider IDs, OAuth-scope editing, Apps Script/developer consoles, code pasting or terminal use.
4. Native Google Calendar lane is explicitly same-user/single-writer and never advertised as distributed-CAS/concurrent-writer safe.
5. Create targets the selected/default authorized Calendar, records the exact returned provider calendar/event identity, and requires exact independent readback before canonical success.
6. Identical logical replay uses the persisted exact provider event identity and cannot create a duplicate event.
7. Before native update, exact provider preflight must match the last verified canonical provider state; provider/manual drift fails closed rather than being overwritten.
8. Native update targets the exact persisted provider event and requires exact post-write readback. Lack of atomic ETag precondition remains visible evidence, not hidden.
9. The stronger Apps Script `If-Match` adapter remains available as optional/shared-writer hardening and is not required for ordinary Personal setup.
10. Primary/Family/legacy Calendars are not used as unapproved development fixtures.
11. Direct tests cover create, replay, preflight drift rejection, update/readback and capability/evidence labeling.
12. No-app instructions/release validation lock the intent-first flow and prevent reintroduction of mandatory developer-style Calendar setup.
13. Exact final PR-head CI, expected-head merge protection, remote-main readback and post-merge CI are required before packet completion.
14. Live-provider completion is claimed only at the evidence level actually proven; synthetic/CI success does not imply real provider write verification.

### Evidence state

- **Desired:** yes
- **Specified:** yes, corrected by explicit user acceptance feedback on 2026-08-31
- **Strong Apps Script lane implemented:** yes
- **Strong Apps Script lane test/release verified:** yes
- **Default native Personal lane implemented:** not yet
- **Default native Personal lane test-verified:** not yet
- **Live-verified:** no

## Exact next action / resume point

1. Implement the native stock-ChatGPT Google Calendar single-writer capability/projection contract and direct tests without mutating live provider state.
2. Update the complete no-app operating contract and release validator so the default user flow is ordinary-language intent → provider consent if required → MIRA-managed setup/readback, not a Sheet menu.
3. Re-rank `CALENDAR-PROJECTION-GOOGLE-UPDATE-001` as stronger concurrent/shared-writer hardening rather than a blocker for the default Personal lane.
4. Run exact-head CI and fix only packet-related failures.
5. Seek isolated live provider proof through available authorized tools without requiring technical user setup or touching protected Primary/Family state.
6. If live proof remains externally unavailable, preserve that evidence ceiling explicitly; do not make ordinary-user setup worse merely to manufacture a live checkbox.
7. Do not expand into Microsoft/Apple Calendar, appointment intake, reminders, outbound contact, medical meaning, migration or Android during this packet.

## Recovery protocol

Read this file and `PRODUCT_INVARIANTS.md` first. Confirm PR #78 and branch `integration/m0-023-google-calendar-projection`, inspect any commit newer than the recorded last-green head, and treat the intent-first ordinary-user correction as highest-authority acceptance feedback. M2-M0-022 remains complete. Protected personal/legacy Calendar state remains unavailable as a development fixture.
