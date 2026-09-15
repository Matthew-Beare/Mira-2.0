# MIRA 2.0 — Current Work

## Active packet

`ANDROID-CAPTURE-001`

## Customer status

Objective: Add Android camera/QR/barcode capture to the existing canonical asset/inventory system without creating a second inventory authority.
Progress: `FIN-CANON-AUDIT-001` is closed with exact full-history provider/canonical stable-ID equality. Android shared-state, asset identity, identifier lookup, location state, inventory query and movement foundations are already merged/test-verified.
Deliverable: A bounded Android capture slice that turns camera/QR/barcode input into a nonauthoritative observation, resolves canonical identifier/asset state, and requires an explicit movement command before changing observed location.
Expected delivery: UNKNOWN.
Blocker: none currently known.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15.

Acceptance evidence:
- Finance provider transaction coverage reported `full_history`, `ready`, and complete for every deterministic bounded query used; freshness remains UNKNOWN.
- Every connected transaction account has a provider-observed earliest date or an explicit no-row state.
- Exact stable-ID reconciliation found one remaining late-2025 Prime Visa gap containing 42 posted marketplace purchases. Only those proven-missing provider IDs were appended into unused canonical rows; older production rows were not overwritten or deleted and unresolved item purpose remained reviewable.
- Post-write exact set equality: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0.
- Duplicate canonical transaction IDs = 0; duplicate canonical Event IDs = 0.
- Review-surface parity: 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs; difference = 0.
- Sanitized durable proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md` at main commit `942ace58cb780524198670ae561605a4f399f496`.
- Provider freshness remains UNKNOWN; closure proves historical projection equality for the queried provider dataset, not current-to-the-second freshness.

## Active objective — ANDROID-CAPTURE-001

Implement the queued Android capture work item against the existing Android/shared-state and canonical asset graph. Do not create a parallel inventory model, local-only asset authority, or scan-driven implicit movement.

Feature/work alignment:
- `CLIENT-ANDROID-001` / `ANDROID-CLIENT-CORE-001`
- `ANDROID-CAPTURE-001`
- `ASSET-001`, `ASSET-002`, `ASSET-003`
- `IDENT-001` / completed `ASSET-IDENTIFIER-001`
- `INV-001`, `INV-002`
- `LOC-001` / completed `LOCATION-STATE-001`
- `MOVE-001` / completed `MOVEMENT-CORE-001`
- `EVID-001`
- shared `API-001` command/readback semantics

Base state:
- Packet selected from `main` after finance closure proof at base SHA `942ace58cb780524198670ae561605a4f399f496`.
- `ANDROID-CAPTURE-001` is already queued in BACKLOG; its stated rule is that camera/barcode/QR/NFC/BLE inputs are nonauthoritative observations and passive reads never silently move assets.
- This bounded slice starts with camera/QR/barcode only. NFC/BLE remain outside this packet unless required by a hard shared abstraction dependency discovered during implementation.
- Existing canonical inventory primitives are reused: immutable asset Entity UUID, namespaced identifiers, hierarchical locations, inventory query projection and event-first movement/readback.

## Acceptance gates — ANDROID-CAPTURE-001

1. Android capture accepts camera/QR/barcode observations through a bounded capture interface; raw capture does not itself become canonical truth.
2. Supported identifier payloads normalize through existing `IDENT-001` namespace/collision rules and can resolve an existing canonical asset exactly.
3. Unknown identifiers fail honestly into an unresolved observation/result state; no fabricated asset is silently created.
4. A passive scan performs zero movement writes.
5. Any move requires an explicit user/action command using existing `MOVE-001` event semantics and shared queued mutation boundary.
6. Replay/idempotency prevents duplicate movement effects.
7. Exact readback proves the canonical asset/location state after an explicit move and proves zero-write behavior for passive scans/replay.
8. Offline/reconnect behavior preserves existing encrypted/replay-safe Android queue semantics rather than creating a second queue.
9. Tests cover successful lookup, unknown identifier, malformed/unsupported payload, passive zero-write, explicit move, replay and conflict/error paths.
10. Packet-to-feature alignment and idea-capture audit pass before merge; no uncaptured parallel inventory semantics are introduced.

## Next bounded step

Inspect the existing Android client modules, identifier contracts, movement commands and tests on `main`; choose the narrowest reusable capture seam. Then create the packet branch from the recorded base, implement camera/QR/barcode observation parsing plus canonical identifier lookup first, and prove passive scan = zero canonical writes before adding explicit move UI/command wiring.

## Preserved work state

- Stale PR #166 remains open from earlier finance work; do not merge it blindly or use its historical narrative as recovery authority.
- Broader Android representative-device, notification/TTS, NFC/BLE and release-signing work remains separate unless a hard dependency is proven.
- Finance review rows remain human-review work but no longer block historical canonical coverage closure.

## Idea/backlog capture audit

No new product semantics were introduced by the finance closure or packet switch. Android capture maps to existing `ANDROID-CAPTURE-001`, `IDENT-001`, `INV-001/002`, `LOC-001`, `MOVE-001`, `ASSET-001/002/003`, and `EVID-001` scope.
