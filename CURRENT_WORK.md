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
- **Status:** activated; forensic evidence collection in progress.

## Objective

Determine the stable provider-neutral Android/mobile client semantics required for MIRA's first native mobile surface, separate those semantics from legacy implementation choices, and convert verified gaps into bounded feature/backlog work without implementing the Android application in this packet.

## Exact scope

1. Audit legacy G10 Android/mobile intent and actual candidate client code/contracts.
2. Reconcile Android responsibilities with `API-001`, `AUTH-001`, `STORE-001`, `PROFILE-013`, `RECOVERY-002`, notification/reminder contracts and client capability routing.
3. Establish trust boundaries for client identity/enrollment, scoped credentials, protected local storage, server authorization and revocation.
4. Audit synchronization/offline semantics: bounded read models, queued idempotent commands/events/evidence, reconnect/replay, server conflict authority and no local second master.
5. Audit Android-native capability boundaries: notifications, user-approved TTS/audio routing, background work, camera/barcode/QR, NFC/hardware observations and evidence capture where actually supported by evidence.
6. Audit release/evidence requirements: build artifact, signing boundary, compatibility, device capability readback and observed-device verification.
7. Preserve one shared business-policy path: Android may present/capture/deliver locally but never owns canonical reconciliation/business rules or direct provider/database authority.

Do **not** expand this packet into executable Android implementation, API runtime implementation, Google/provider provisioning, production signing/secrets, live device enrollment, public-network deployment, iOS, desktop parity, or protected legacy production mutation.

## Evidence already located

- Legacy `docs/runtime-platform-architecture.md` says clients are replaceable adapters and Android must use the versioned API; clients own presentation, local capture/decoding, local notification/TTS, device capability reporting, secure token storage and offline queueing where supported, while server/control-plane owns behavior.
- Legacy `starter/clients/README.md` says Android uses the shared PWA for visual/capture UI where practical and native code for mobile-browser gaps; all clients use the same API and never receive direct database/provider credentials.
- Legacy `starter/clients/android/README.md` defines four first native adapters: reminder receiver, visual notification, opt-in Android TTS, and NFC observation bridge; it explicitly requires canonical reminder UUID/idempotency and observed-device release proof.
- Candidate Android source exists for `MainActivity`, `ReminderScheduler`, `ReminderReceiver`, and `SpeechService`.
- Candidate `SpeechService` provides a foreground notification, Android local TTS and local `reminderId` replay suppression using app preferences/in-flight state.
- Candidate `ReminderScheduler` uses exact alarms when Android allows them and a non-exact fallback otherwise; `MainActivity` honestly exposes the timing capability limitation.
- The located candidate code is not yet evidence of API auth/enrollment, scoped credential storage, service sync, NFC bridge, durable offline command/evidence queue, production signing, compatibility enforcement or observed-device success.

## Preliminary acceptance criteria

1. Stable Android/mobile semantic feature boundary is identified without turning Android into a data authority.
2. Every canonical read/mutation/sync path is explicitly downstream of `API-001`; no direct DB/provider credentials or business-policy duplication.
3. Device/client identity, enrollment, revocation and least-privilege credential storage boundaries are explicit; possession of an app/device token alone never broadens resource/action scope.
4. Offline/reconnect behavior preserves canonical IDs and idempotency, cannot create a second writable master, and defers authoritative conflict resolution to the service.
5. Notification/TTS behavior preserves one canonical reminder identity, explicit speech opt-in/privacy detail, replay suppression and honest platform timing/audio-route limits.
6. Native capture/hardware observations use canonical envelopes and cannot silently infer asset/location truth from one scan/read.
7. Capability health is evidence-based and device-specific where required; code/package presence is not capability proof.
8. Release evidence separates source existence, build success, signed distributable, integration verification and observed-device verification.
9. Legacy PWA-first/native-thin architecture is treated as implementation evidence, not silently promoted to an eternal product requirement unless G10 evidence requires it.
10. Protected legacy production data, provider state and executable MIRA 2.0 code remain untouched.
11. Packet normalization remains bounded to Git authority files unless forensic evidence proves another authority file must change.

## Exact next action

1. Inspect the legacy Android manifest/build/release configuration and shared client/API/hardware contracts.
2. Inspect Android-related tests/CI and candidate PR history for build/device evidence.
3. Identify what is specification-only, candidate implemented, test-verified, integration-verified and live/device-verified.
4. Decide stable semantic feature ID(s) and exact implementation blockers only after evidence classification.
5. Checkpoint forensic findings before normalization.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
