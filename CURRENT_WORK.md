# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-008D` — Policy/data API foundation audit — legacy G7

- **Merged PR:** #31
- **Merge SHA / main readback:** `b844afb9b9a4267e79c303a82f0a533cc48eab09`
- **Post-merge completion checkpoint / this branch start SHA:** `312907f24a624a1860cf48863cee26655ad326ab`
- **Result:** `API-001` is canonical; `API-CORE-001` blocks unsafe remote/native mutation; `CORE-ROUNDTRIP` must use the shared API path.

## Active packet

- **Packet ID:** `M2-G0-008E`
- **Name:** Android/mobile client boundary audit — legacy G10
- **Class:** forensic audit / Android milestone prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-008e-android-client-foundation`
- **Branch start SHA:** `312907f24a624a1860cf48863cee26655ad326ab`
- **Activation commit:** `63ac793ff856b8ef69029eb80e99c77821abe841`
- **Research checkpoint:** `d884661b697d50fa961ab849f75c2fbe2ece94d8`
- **Feature normalization:** `a34649776be61117cbd6816dec8b6a42d8481edd`
- **Backlog normalization:** `4adcaadfab62975ce8edb487415ac8962a69c35b`
- **Status:** audit and dependency normalization complete; PR/server-side verification and merge remain.

## Objective

Determine the stable provider-neutral Android/mobile client semantics required for MIRA's first native mobile surface, separate them from legacy implementation choices, and convert verified gaps into bounded feature/backlog work without implementing the Android application in this packet.

## Canonical G10 result

1. G10 normalizes to stable semantic feature **`CLIENT-ANDROID-001` — Android native client adapter using the shared API, protected client credentials, offline replay-safe sync and evidence-based device capabilities**.
2. Android is a replaceable client adapter over `API-001`, never a canonical data/provider/source authority.
3. The stable requirement is not PWA-first, WebView-first or one Java implementation. Presentation technology may change while shared-API authority, protected credentials, offline replay safety, native capability boundaries and evidence requirements remain invariant.
4. Native client/session credentials must be scoped, revocable and stored with Android/OS protected-secret facilities when durable storage is required. Database/provider/source credentials do not belong in the client.
5. Offline queue/cache state is nonauthoritative. Canonical command/event IDs and idempotency survive reconnect; the service owns stale-version/conflict resolution and verified write/readback.
6. Native notification/TTS delivery preserves one canonical reminder identity, suppresses replay, keeps visual delivery independent of speech, requires explicit speech/privacy policy and reports honest Android timing/audio-route limits.
7. Camera/barcode/QR, NFC and BLE/RFID are nonauthoritative observation/capture adapters. Hardware reads never become canonical identity and one passive read never silently moves an asset.
8. Device capability health requires observed evidence where physical/platform behavior matters; package/code/permission presence is not proof.
9. Release evidence is tiered: source -> build -> distributable/signing state -> canonical API integration -> representative-device verification.
10. M2-M1 remains: Android reads and mutates the same canonical entity as stock ChatGPT through the same `API-001` path without becoming a second authority.

## Legacy / PR #31 evidence ceiling

- Legacy `docs/runtime-platform-architecture.md`, `starter/client-api-contract.json`, `starter/hardware-capture-contract.json`, `test_client_surfaces.py` and `test_cross_platform_clients.py` strongly specify the shared-API/no-direct-database client boundary and nonauthoritative hardware semantics.
- Legacy main contains a real Android Gradle application with `MainActivity`, `ReminderScheduler`, `ReminderReceiver` and `SpeechService`.
- Legacy main partially implements Android local TTS, foreground visual notification, reminder-ID replay suppression and exact-alarm/fallback timing behavior.
- Legacy commit `00d9ea1ca45636fe9d1fb7c1e85527d9d4696b22` has a successful canonical Android Client CI run (`32912057501`), so the legacy debug Android project is build-verified at that revision. The historical APK artifact is no longer retained for current inspection.
- Legacy `MIRA-Personal-Production` PR #31 remains open/unmerged mega-PR candidate evidence at head `eb2eae9e5405c350d227064b951963f7fe1a41f8`.
- PR #31's Android build job succeeded at that head and adds candidate release APK/AAB/signature workflow, WebView/PWA bridge, ML Kit barcode scanning, NFC and BLE capture.
- The overall PR #31 head is not green; other required checks fail, so it is not releasable/mergeable evidence.
- PR #31 `MainActivity` directly obtains Google access tokens and calls Google APIs from Android. That path is **architecturally rejected for MIRA 2.0** because it bypasses `API-001` and turns the client into a provider-authority mutation surface. Separate native UI/capture pieces may be salvaged only after reconciliation to canonical API envelopes.
- No MIRA 2.0 Android implementation, API integration, protected credential store, offline queue, signed release identity or representative-device proof is claimed.

## Normalized Git evidence

- `FEATURES.md` now contains `CLIENT-ANDROID-001`, the G10 mapping and G10 integrity findings.
- `BACKLOG.md` now contains completed `AUDIT-G10` and bounded implementation rows:
  - `ANDROID-CLIENT-CORE-001` — API-only client core, enrollment/scoped credentials, protected storage, offline sync/replay/conflict handling;
  - `ANDROID-NATIVE-DELIVERY-001` — native notification/TTS delivery hardening;
  - `ANDROID-CAPTURE-001` — camera/barcode/QR/NFC/BLE/RFID nonauthoritative capture adapters;
  - `ANDROID-RELEASE-001` — reproducible build/signing/update/device evidence.
- `ANDROID-SYNC` now explicitly depends on `CORE-ROUNDTRIP` + `ANDROID-CLIENT-CORE-001` and forbids direct provider mutation.
- No executable MIRA 2.0 code, provider state, protected legacy data or files outside `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are intended to change in this packet.

## Acceptance criteria

1. Stable Android/mobile semantic boundary. **Satisfied: `CLIENT-ANDROID-001`.**
2. All canonical reads/mutations downstream of `API-001`; no direct provider/database authority or duplicated business policy. **Satisfied; legacy direct-Google path explicitly rejected.**
3. Identity/enrollment/revocation/scoped protected credential boundary explicit. **Satisfied as requirement; implementation gap recorded.**
4. Offline/reconnect/idempotency/conflict boundary explicit. **Satisfied as requirement; implementation gap recorded.**
5. Notification/TTS identity, privacy, replay and Android-limit semantics explicit. **Satisfied; legacy candidate partial/build-verified.**
6. Hardware observations remain nonauthoritative canonical capture events. **Satisfied; legacy candidate partial.**
7. Capability health requires evidence, not code presence. **Satisfied.**
8. Release evidence tiers separated. **Satisfied; MIRA 2.0 signing/device proof absent and explicit.**
9. PWA/WebView implementation choice not promoted to permanent semantics. **Satisfied.**
10. Protected legacy production/provider state and executable MIRA 2.0 code untouched. **Satisfied by intended scope; final diff verification pending.**
11. Stable feature/work IDs and dependency normalization. **Satisfied.**
12. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Compare `audit/g0-008e-android-client-foundation` against `main`; require exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md` changed.
2. Open bounded PR for `M2-G0-008E`.
3. Verify server-side changed-file scope, mergeability and exact current head SHA.
4. Merge using the exact verified head SHA.
5. Remotely read back `main` and record the merge SHA/packet completion before activating the next dependency-ranked audit packet.
6. Choose the next packet from remaining F21-F23 / G rows by dependency priority rather than numeric order; do not start implementation before forensic/dependency closeout permits it.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
