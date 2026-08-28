# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies the exact completed packet and the exact next activation point.

## Completed packet

### `M2-G0-008D` — Policy/data API foundation audit — legacy G7, Android prerequisite

- **Repository:** `Matthew-Beare/Mira-2.0`
- **Merged PR:** #31
- **Merge SHA / main readback:** `b844afb9b9a4267e79c303a82f0a533cc48eab09`
- **Branch:** `audit/g0-008d-api-service-foundation`
- **Branch start SHA:** `fc95d1c89f4592ebc92cd649349c4f7f5d2fcce6`
- **Research checkpoint:** `3c8054c0c034f21489d90499986ef06a28a512d5`
- **Feature normalization:** `06c2fcc4a7059dc40a43df802786dc7712a2b4a0`
- **Backlog normalization:** `40ac6241b5c8a50978a907f4ea40d621e35995c5`
- **Packet-close head:** `ecfaa5d8ba971afc9dd842299ecf88fa27a8db15`
- **Server-side file scope verified:** exactly `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`.
- **Result:** canonical `API-001` is now the versioned authenticated MIRROR client/service boundary in front of `AUTH-001`/`STORE-001`; `API-CORE-001` is a security/data-integrity BLOCKER before safe remote/native mutation; `CORE-ROUNDTRIP` must use that shared API path. PR #31 legacy candidate evidence remains partial/salvage only and does not count as MIRA 2.0 implementation or live proof.

## Next packet to activate

- **Packet ID:** `M2-G0-008E`
- **Name:** Android/mobile client boundary audit — legacy G10
- **Class:** forensic audit / Android milestone prerequisite
- **Planned branch:** `audit/g0-008e-android-client-foundation`
- **Reason for priority:** G7 proved the shared service boundary that G10 consumes; Android is the first native mobile target and is on the current M2-M1 dependency path.

### Pre-activation evidence already located

Legacy canonical/reference source contains a real Android candidate, not only prose:
- `docs/runtime-platform-architecture.md` defines Android as a replaceable client using the versioned service/API, with presentation/local capture/TTS/device-capability reporting/secure token storage/offline queue responsibilities and no canonical reconciliation policy.
- `starter/clients/android/README.md` defines the native companion as intentionally thin, with bounded reminder, notification, TTS and NFC adapters; PWA remains the normal shared visual/capture surface in that legacy design.
- Candidate Java code exists for `MainActivity`, `ReminderScheduler`, `ReminderReceiver`, and `SpeechService`.
- The candidate demonstrates local Android TTS, foreground notification delivery, exact/fallback alarm behavior and local replay suppression for spoken reminder IDs, but it does not by itself prove API authentication/enrollment, scoped credentials, service synchronization, NFC bridge, durable offline command queue, signed release, or observed-device behavior.

## Exact next action

1. Create `audit/g0-008e-android-client-foundation` from this completion checkpoint.
2. On that branch, write the exact branch-start SHA and `M2-G0-008E` scope/acceptance into `CURRENT_WORK.md`.
3. Forensically inspect G10-relevant legacy client contracts, Android code, tests/CI/release evidence, and any PR candidate evidence.
4. Separate portable client semantics from legacy implementation choices such as PWA-first UI, Android AlarmManager details, or package naming.
5. Normalize stable Android/mobile client feature/work IDs only where evidence warrants them; do not implement the Android app in this audit packet.
6. Keep `API-001`/`AUTH-001`/`STORE-001` authoritative: Android remains a client and never gains direct database/provider authority.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify `main` and the planned/active branch head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. new customer ideas go to BACKLOG unless required for acceptance or explicitly reprioritized.
