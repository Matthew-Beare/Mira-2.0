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
- **Status:** forensic research complete and checkpointed by this commit; feature/backlog normalization next.

## Objective

Determine the stable provider-neutral Android/mobile client semantics required for MIRA's first native mobile surface, separate those semantics from legacy implementation choices, and convert verified gaps into bounded feature/backlog work without implementing the Android application in this packet.

## Canonical G10 findings

1. Android is a **client adapter**, never a canonical state/provider authority. It consumes the same `API-001` semantics as ChatGPT and other approved clients.
2. The stable product requirement is not “PWA-first” or one Java implementation. The stable requirement is one Android client surface that can present/capture locally, report verified device capabilities, deliver Android-native notifications/TTS, queue supported offline work, and synchronize through the shared API without duplicating business policy.
3. M2-M1 remains exactly: Android reads/mutates the same canonical reality state without becoming a second authority.
4. Native Android credentials must be least-privilege client/session credentials, revocable, scope-bound by server authorization, and stored using an Android/OS protected-secret mechanism when durable storage is required. Database, provider-authority and source-control credentials do not belong in the client.
5. Offline work is a client queue, not an authority. Canonical command/event IDs and idempotency survive reconnect; the service owns stale-version/conflict decisions and verified write/readback.
6. Device capability state is evidence-based. Package/code presence, OS permission prompts or hardware connection alone cannot mark notification/TTS/camera/NFC/BLE paths healthy; device-specific paths require observed capability evidence where appropriate.
7. Reminder delivery preserves one canonical reminder identity. Native scheduling/delivery must suppress replay, respect explicit speech opt-in/privacy detail, show visual notification independently, and report honest Android timing/audio-route limits rather than promising cloud control of device audio.
8. Native camera/barcode/QR, NFC and BLE/RFID inputs are observations/capture adapters. They emit canonical envelopes and never silently become asset/location identity or infer an asset move from one passive observation.
9. Release evidence is tiered: source exists -> build succeeds -> distributable/signing state verified -> integration with canonical API verified -> representative-device behavior observed. CI cannot prove physical-device behavior or production signing identity by implication.
10. Legacy implementation may share a PWA/WebView surface with native bridges, but MIRA 2.0 does not make that implementation choice a permanent semantic requirement.

## Legacy evidence classification

### Strong specification/test-supported boundary evidence

- `MIRA-Personal-Production/docs/runtime-platform-architecture.md` defines one versioned API for web/desktop/Android, client-only presentation/capture/TTS/capability/offline responsibilities, server-owned behavior, no client DB credentials and Android-first native mobile architecture.
- `starter/client-api-contract.json` requires versioned transport, server auth/authz/preflight/schema/idempotency/canonical write/readback/audit, cursor sync, offline idempotency and server conflict authority.
- `starter/hardware-capture-contract.json` makes hardware observations nonauthoritative and requires real-sample verification before capability health.
- `starter/tests/test_client_surfaces.py` and `test_cross_platform_clients.py` test the shared API/no-direct-database boundary, background-TTS distinction, hardware observation rules and presence of canonical Android build workflow.

### Legacy main candidate implementation evidence

- `starter/clients/android/` contains a real Gradle Android application with `MainActivity`, `ReminderScheduler`, `ReminderReceiver` and `SpeechService`.
- `SpeechService` implements foreground visual notification, local Android `TextToSpeech`, and local duplicate-speech suppression keyed by reminder ID.
- `ReminderScheduler` implements exact alarm when permitted and `setAndAllowWhileIdle` fallback otherwise; `MainActivity` exposes the limitation honestly.
- `AndroidManifest.xml` declares notification, foreground-media-playback and exact-alarm permissions and keeps receiver/service non-exported.
- Canonical legacy workflow `.github/workflows/android-client.yml` builds `:app:assembleDebug` and uploads `app-debug.apk`.
- Commit `00d9ea1ca45636fe9d1fb7c1e85527d9d4696b22` has a successful GitHub Actions Android Client build run (`32912057501`), so the debug Android project is **build/test-verified at that legacy revision**. The historical artifact is no longer retained by GitHub, so the APK itself is not current evidence available for inspection.

### PR #31 candidate evidence ceiling

- Legacy `MIRA-Personal-Production` PR #31 is open/unmerged at head `eb2eae9e5405c350d227064b951963f7fe1a41f8`; it changes 153 files and is salvage/reference only.
- Its Android workflow successfully completed at head (`Android Client` run `33026778687`), proving that candidate Android debug/release compilation path passes its own build job.
- The PR adds release APK/AAB build/signature-status machinery and a sane release-signing policy: permanent key outside Git, exact artifact signature verification, retained signing identity, representative-hardware testing required before ship.
- However the overall PR head is **not green**: other required checks at that same head fail, including `python-and-config`, `build-and-smoke`, and `secret-patterns`. Green-before-growth therefore forbids treating the mega-PR as releasable or mergeable evidence.
- Critically, PR #31 `MainActivity` adds direct Google OAuth/access-token handling and direct HTTPS calls to Google API hosts from the Android client. That violates the now-canonical G7 rule that Android must mutate/read canonical reality through `API-001` rather than becoming a provider-authority client. This direct-Google path is **architecturally rejected for MIRA 2.0** even though separate WebView/NFC/BLE/barcode/UI pieces may be salvageable.
- PR #31 also adds native NFC, BLE observation, ML Kit barcode scanning and a shared WebView/PWA surface. Those are candidate implementation pieces only until reconciled to canonical `API-001` capture/observation envelopes and verified in MIRA 2.0.

## Gaps that remain after audit

- No MIRA 2.0 Android client implementation exists.
- No MIRA 2.0 device enrollment/scoped-auth flow is implemented or integrated with `API-001`.
- No MIRA 2.0 Android protected credential-store implementation is proven.
- No canonical Android offline command/evidence queue + reconnect/conflict/readback implementation is proven.
- No MIRA 2.0 integration proof shows Android and stock ChatGPT reading/mutating the same canonical entity through one shared API path.
- No current signed MIRA 2.0 release artifact/signing identity exists.
- No MIRA 2.0 observed-device evidence proves notification timing, TTS routing/dedupe, reconnect, camera/barcode, NFC or BLE capabilities.
- The architecture must preserve the stock ChatGPT milestone's no-required-self-hosted-server rule; therefore `API-CORE-001`/deployment work must supply an ordinary-user-compatible shared API/service path rather than forcing Android to bypass it and call provider authorities directly.

## Acceptance criteria

1. Stable Android/mobile semantic boundary identified without making Android an authority. **Satisfied.**
2. Canonical state paths downstream of `API-001`, no direct DB/provider authority or duplicated business policy. **Satisfied as requirement; legacy PR direct-Google path explicitly rejected.**
3. Identity/enrollment/revocation/scoped credential boundary explicit. **Satisfied as requirement; implementation gap remains.**
4. Offline/reconnect/idempotency/conflict boundary explicit. **Satisfied as requirement; implementation gap remains.**
5. Notification/TTS identity, opt-in/privacy, dedupe and Android-limit semantics explicit. **Satisfied; legacy candidate partially implemented/build-verified.**
6. Hardware observations remain nonauthoritative canonical capture events. **Satisfied; legacy candidate partially implemented.**
7. Capability health requires evidence, not code presence. **Satisfied.**
8. Release evidence tiers separated. **Satisfied; legacy build proof exists, MIRA 2.0 release/device proof absent.**
9. PWA/WebView implementation choice not promoted to eternal product semantics. **Satisfied.**
10. Protected legacy production/provider state and executable MIRA 2.0 code untouched. **Satisfied.**
11. Stable feature/work IDs and dependency normalization. **Pending.**
12. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Add one stable semantic Android-client feature ID to `FEATURES.md` unless existing IDs prove sufficient; avoid duplicating reminder, capture or API domain semantics.
2. Add bounded implementation/release/integration work rows to `BACKLOG.md`, explicitly rejecting direct provider-authority client mutation and preserving `ANDROID-SYNC` as the M2-M1 vertical.
3. Update `CURRENT_WORK.md` with normalized IDs and packet-close evidence.
4. Compare branch against `main`; require only intended Git authority files.
5. Open bounded PR, verify exact changed files/head/mergeability, merge exact head and remote-readback `main`.
