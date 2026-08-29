# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and exact recovery state.

## Product direction

Default Personal MIRA is stock ChatGPT + Google Workspace, with no external infrastructure prerequisite. Android, Microsoft, Apple/iCloud, Cloud Run, Linux and SQL remain supported later lanes but do not block the first useful Google-only Personal product.

Every work session begins and ends by checking `FEATURES.md`, `BACKLOG.md`, and `ROADMAP.md`. CI runs `python -m mira.work_session_alignment check` so active work and feature references cannot drift silently.

## Completed no-app foundation this session

- `M2-M0-007` / `FIRSTBOOT-CORE-001` merged in PR #58 at `a60e8879e71b8f464eb1de1ea8cc15cbd309eccb`: four-question resumable Interview Ledger + CI work-session direction gate + isolated Google persistence/readback proof.
- `M2-M0-008` / `SERVICE-STATE-001` merged in PR #59 at `2fd34e1bd66bcb3a73c632e60457564f9e4a859c`: explicit intent/recommendation/readiness/activation state + isolated Google persistence/readback proof.

The Android packet remains paused at its exact live Apps Script queued-writer proof checkpoint in Git history.

## Active packet

### `M2-M0-009` — Stock-ChatGPT no-app operating protocol

- **Primary work:** `ONBOARD-INSTRUCTIONS`
- **Primary features:** `ONBOARD-001`, `ONBOARD-003`, `ONBOARD-006`
- **Related invariants/features:** `CORE-001`, `STORE-001`, `API-001`, `AUTH-001`, `SERVICE-001`, `CAL-006`, `RECOVERY-002`, `DATA-001`
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-009-no-app-protocol`
- **Base SHA:** `2fd34e1bd66bcb3a73c632e60457564f9e4a859c`
- **Objective:** ship a complete sanitized source-backed operating instruction/protocol with the Google Workspace starter so stock ChatGPT can execute first boot against canonical MIRROR state instead of requiring a Python process or Android app.

## Session-start alignment verification — 2026-08-29

### `FEATURES.md`

Verified before implementation:

- `ONBOARD-001` requires complete replacement instruction delivery rather than fragmentary patches.
- `ONBOARD-003` defines the exact four-question Minimum Useful Setup and completion orientation.
- `ONBOARD-006` requires ordinary browser-only Personal setup with no terminal fallback.
- `CORE-001` fixes the assistant/product name as MIRA.
- `STORE-001`, `AUTH-001`, and `API-001` require canonical identity, revision/idempotency, exact readback, and one-authority semantics.
- `SERVICE-001` requires appointment-help intent to remain separate from actual service activation.
- `CAL-006` prohibits pretending preferred Calendar sync is active before verified provider capability/readback.
- `DATA-001` prohibits using legacy production state as a test fixture.

### `BACKLOG.md`

Verified before implementation:

- `ONBOARD-INSTRUCTIONS` already exists as source-backed full instruction replacement work.
- full `SERVICE-COMPOSE-001` depends on broader runtime/source routing and is not the shortest path to a usable stock-ChatGPT first boot;
- `NONTECH-INSTALL-001` remains later installation/upgrade hardening;
- `OPS-BRIEF-VSLICE`, appointments, receipts/assets/inventory, and Android remain preserved work.

### `ROADMAP.md`

Verified before implementation:

- M2-M0.5 requires a useful no-app Personal product before Android resumes;
- the next work should promote the proven Google substrate into actual stock-ChatGPT behavior rather than adding unnecessary infrastructure;
- provider-specific details must remain adapter/protocol concerns rather than changing canonical product semantics.

### Direction result

**ALIGNED.** A complete stock-ChatGPT Workspace operating protocol is a shorter path to an actually usable no-app MIRA than entering the broader service-composition dependency tree now.

## Acceptance criteria

1. A complete sanitized no-app MIRA instruction/protocol ships inside the Workspace starter source bundle.
2. It identifies MIRA as fixed and never asks the user to rename it.
3. It requires canonical Workspace preflight/readback before mutation and never treats chat memory as mutable-state authority.
4. It implements the four-question first-boot/resume sequence exactly.
5. It preserves explicit appointment Calendar preference without claiming Calendar sync capability or activation.
6. It maps appointment-help intent into explicit requested service state, not active state.
7. It requires stable IDs, expected revision, deterministic request fingerprint/idempotency, canonical write, and exact readback for state mutation.
8. It states that stock-ChatGPT Personal mode is single-writer and must fail closed if queued-writer/shared mode is active.
9. It contains no provider IDs, secrets, personal state, or legacy production data.
10. Workspace bundle validation and direct tests require the protocol and its critical clauses.
11. Existing Apps Script bundle/runtime tests remain green.
12. Session-end FEATURES/BACKLOG/ROADMAP alignment is recorded before merge.

## Exact next action

Create the complete no-app instruction/protocol artifact, bind it into Workspace bundle validation/tests, prove it against the isolated synthetic Google no-app workbook, then merge only with latest-head CI green.
