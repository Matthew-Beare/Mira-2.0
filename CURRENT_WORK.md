# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active provider-integration packet and its resume point.

## Completed packet before this branch

### `M2-G1-006` — Production component ownership and anti-bloat gate

- **Merged PR:** #43
- **Merge SHA / main readback:** `1a8a3279ca3be55dac3371dab33155b996c0946b`
- **Post-merge completion checkpoint / this branch start SHA:** `a0ab0541ec5317b2f73d473ef89be804856acc5c`
- **Remote CI:** run `33211598736`; compile + feature registry + code ownership + full suite succeeded.
- **Result:** repository growth gates are green before provider/client fan-out.

## Active packet

### `M2-M0-001` — Isolated Google/MIRROR data sandbox

- **Work ID:** `DATA-SANDBOX`
- **Class:** provider integration prerequisite / protected-data boundary
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `integration/m0-001-google-sandbox`
- **Branch start SHA:** `a0ab0541ec5317b2f73d473ef89be804856acc5c`
- **Status:** activated; provider discovery/read-before-write next.

## Objective

Create and verify a separate Google Drive namespace for MIRA 2.0 synthetic integration work without touching, repurposing, migrating, or using any legacy MIRA production artifact as a fixture.

## Provider privacy boundary

Live Google Drive IDs, URLs, account identifiers, permissions and private content must not be written to this public repository. Git records only sanitized facts such as whether search/readback/create checks passed and what generic resource roles exist.

## Acceptance criteria

1. Search Drive before writing and prove whether an exact `MIRA 2.0 Sandbox` folder already exists.
2. Create at most one root-level `MIRA 2.0 Sandbox` folder; never rename/reuse a legacy MIRA/LyfeOS folder.
3. Create a dedicated `Structured State` child folder only inside the verified sandbox parent.
4. Use no personal operational data; provider resources contain generic names only and synthetic data only.
5. Read back folder metadata and parent relationships from Google after writes.
6. Verify the sandbox folder is distinct from any legacy artifacts encountered by search; do not modify those artifacts.
7. Provider resource IDs/URLs and account identifiers are not committed to public Git.
8. Record only sanitized verification evidence and exact next adapter requirements in Git.
9. No Google Sheet/state schema is created yet; that belongs to `GOOGLE-STORE-ADAPTER-001`.
10. No Gmail/Calendar/scheduler/Android/deployment changes.

## Exact next action

1. Search connected Google Drive for exact `MIRA 2.0 Sandbox` folder before any provider write.
2. If absent, create it at Drive root; if exactly one exists, reuse only that explicit MIRA 2.0 sandbox.
3. Search/list its direct children before creating `Structured State`.
4. Create the child only if absent and read back both folder metadata/parent relationship.
5. Record sanitized evidence in this file, PR/merge/read back main.
6. Activate `GOOGLE-STORE-ADAPTER-001` next.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from exact next action;
4. never place live provider IDs/private data in public Git;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
