# MIRA 2.0 — Current Work

## Active packet

### `M2-M1-011` — Android passive identifier capture and explicit movement

- **Primary work:** `ANDROID-CAPTURE-001`
- **Primary features:** `CLIENT-ANDROID-001`, `IDENT-001`, `INV-001`, `MOVE-001`
- **Related invariants/features:** `API-001`, `ASSET-001`, `ASSET-002`, `ASSET-003`, `INV-002`, `LOC-001`, `EVID-001`, `RECOVERY-002`

## Customer status

Objective: Add Android camera/QR/barcode capture to the existing canonical asset/inventory system without creating a second inventory authority.
Progress: Finance historical projection is closed. PR #167 implements the first passive-capture core: verified read-only change query plus strict QR/UPC/EAN identifier parsing and canonical asset resolution. The first CI failure was obsolete Android SDK setup and is fixed; the next failure exposed this stale CURRENT_WORK alignment format and is being corrected here.
Deliverable: Bounded Android capture that treats raw camera/QR/barcode input as nonauthoritative, resolves existing canonical identifiers/assets, performs zero writes for passive scans, and requires an explicit replay-safe movement command plus exact readback before observed location changes.
Expected delivery: UNKNOWN.
Blocker: none currently known.

## Recovery authority

This file is the authoritative execution checkpoint. Chat context is disposable. Re-read repository instructions, remote `main`, open PRs and CI before implementation or merge.

## Closed packet — FIN-CANON-AUDIT-001

Closed 2026-09-15. Exact full-history identity proof at closure: 2,091 provider stable transaction IDs = 2,091 canonical stable transaction IDs; provider-minus-canonical = 0; canonical-minus-provider = 0; duplicate canonical transaction IDs = 0; duplicate Event IDs = 0. Review-surface parity was 660 canonical `NEEDS REVIEW` Event IDs = 660 Spending Review `NEEDS REVIEW` Event IDs. Sanitized proof is `docs/FINANCE_EVIDENCE_COVERAGE_PROOF.md`. Provider freshness remained UNKNOWN and closure did not claim current-to-the-second freshness.

## Active objective — ANDROID-CAPTURE-001

Implement the queued Android capture work item against the existing Android/shared-state and canonical asset graph. Do not create a parallel inventory model, local-only asset authority, or scan-driven implicit movement.

Current branch: `feature/android-capture-001`
Current PR: #167
Recorded packet base: `942ace58cb780524198670ae561605a4f399f496`
Latest packet branch head before this checkpoint: `c9910280975d234b19ca5ad1479d01b3a83735e0`

Implemented in the current PR:
- `VerifiedChangeQuery`: bounded provider-neutral read-only fold over verified canonical Changes; it never reconciles or submits commands.
- `IdentifierCaptureResolver`: strict decoded QR/UPC-A/EAN-8/EAN-13 identifier parsing and lookup against canonical `IDENT-001` snapshots.
- Honest unresolved, ambiguous, malformed, transport, protocol and integrity states; unknown scans never create assets.
- Serial-level duplicate resolution fails closed.
- Direct JVM tests for passive query/capture behavior and Android ownership registration.
- CI Android SDK bootstrap no longer requests the removed legacy `tools` package.

Not yet accepted/integrated:
- PR #167 is not merged and CI is not green yet.
- Camera/Google Code Scanner app-edge wiring is not implemented yet.
- Explicit movement command/replay/readback is not implemented yet.
- Representative-device proof is not complete.

## Acceptance gates — ANDROID-CAPTURE-001

1. Android capture accepts camera/QR/barcode observations through a bounded capture interface; raw capture does not itself become canonical truth.
2. Supported identifier payloads normalize through existing `IDENT-001` namespace/collision rules and resolve an existing canonical asset exactly.
3. Unknown identifiers fail honestly into an unresolved result; no fabricated asset is silently created.
4. A passive scan performs zero movement writes.
5. Any move requires an explicit user/action command using existing `MOVE-001` event semantics and the shared queued mutation boundary.
6. Replay/idempotency prevents duplicate movement effects.
7. Exact readback proves canonical asset/location after an explicit move and zero-write behavior for passive scans/replay.
8. Offline/reconnect preserves the existing encrypted/replay-safe Android queue; no second queue is introduced.
9. Tests cover lookup, unknown identifier, malformed/unsupported payload, passive zero-write, explicit move, replay and conflict/error paths.
10. Packet-to-feature alignment and idea-capture audit pass before merge; no uncaptured parallel inventory semantics are introduced.

## Next bounded step

1. Rerun PR #167 CI after this alignment checkpoint and repair only actual failing gates.
2. Once the passive core compiles/tests cleanly, add the camera edge using the existing Android app boundary while keeping decoding separate from canonical semantics.
3. Inspect the existing queued API/Workspace command contract for a reusable `MOVE-001` append-event path. Extend the shared boundary only if no existing explicit movement command exists; do not fake movement as an ordinary passive scan/upsert.
4. Prove explicit movement replay/conflict/exact readback, then checkpoint acceptance evidence before merge.

## Preserved work state

- Stale PR #166 remains open from earlier finance work; do not merge it blindly or use its historical narrative as recovery authority.
- Existing Android client, Authority/store, identifier, inventory/location and movement modules remain canonical dependencies; this packet extends them rather than replacing them.
- NFC/BLE and broader native notification/release work remain outside this bounded packet unless a hard shared abstraction dependency is proven.
- Legacy/production state must never be used as test fixtures.

## Session-start alignment verification — 2026-09-15

### `FEATURES.md`

Reviewed. Active scope maps to existing Android client, identifier, inventory, movement, API, asset, location, evidence and recovery features. No new semantic feature is required for the passive capture core.

### `BACKLOG.md`

Reviewed. `ANDROID-CAPTURE-001` is the selected canonical work item. Camera/barcode/QR are the current bounded slice; NFC/BLE remain deferred within the same backlog item.

### `ROADMAP.md`

Reviewed. The work preserves the Personal Google/shared-state direction and reuses the existing Android/API/Authority boundaries rather than adding a server or second state authority.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

No materially new product capability was introduced by the current implementation or CI repair. Google Code Scanner is an implementation choice for the already-captured camera/barcode/QR surface, not a new product feature. Explicit movement remains existing `MOVE-001` semantics and must not be silently expanded by passive capture.

### Direction result

ALIGNED
