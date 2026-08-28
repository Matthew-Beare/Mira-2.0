# MIRA 2.0 CURRENT WORK

Git is authoritative. This file records the completed G0 closeout and exact implementation successor.

## Completed packet

### `M2-G0-010` — Final dependency graph and implementation ranking closeout

- **Repository:** `Matthew-Beare/Mira-2.0`
- **Merged PR:** #36
- **Merge SHA / main readback:** `a7d3e947ac71803c3c19777668c0ea79d844463f`
- **Branch:** `audit/g0-010-dependency-closeout`
- **Branch start SHA:** `e03e4fa0a6ad323442d4ec33c7c5c30afb54b5c8`
- **Feature graph normalization:** `64622bab93f2c4c6a90d16d0703ff2daa1effc85`
- **Roadmap normalization:** `a166bf77dfcaeb5992405d6579e19c1751cfbd6f`
- **Ranked backlog:** `e6332c46defef8e1a771ccb1cbc5ef9d3e6e930c`
- **Packet-close head:** `5d663563f6dd9f9df743e34b470998718beec273`
- **Server-side file scope verified:** exactly `BACKLOG.md`, `CURRENT_WORK.md`, `FEATURES.md`, `ROADMAP.md`.
- **Result:** G0 forensic reconstruction, legacy reconciliation and dependency closeout are complete. The M2-M0/M2-M1 critical path is acyclic and the first bounded implementation packet is selected.

## Selected successor

### `M2-G1-001A` — Synthetic structured-state adapter core

- **Work ID:** `STORE-ADAPTER-001A`
- **Class:** implementation / foundational prerequisite
- **Planned branch:** `impl/g1-001a-structured-state-adapter`
- **Objective:** implement the provider-neutral structured-state contract and deterministic in-memory synthetic adapter used by later Authority Registry and API work.

### Acceptance criteria

1. Bounded interface for health/schema, exact read, bounded query, idempotent upsert and append-event behavior.
2. Stable caller-supplied canonical IDs; replay never invents competing identities.
3. Monotonic revisions and exact material readback after mutation.
4. Same idempotency key + same material request returns the prior result without another mutation.
5. Same idempotency key + different material request fails closed.
6. Stale expected revision fails explicitly and leaves state unchanged.
7. Invalid/unknown resource or envelope fails explicitly rather than permissively writing arbitrary state.
8. Deterministic tests cover create/read/query/update/replay/conflict/append-event/readback.
9. No Google/provider/network/evidence-store work, credentials or legacy production state.
10. Bounded production ownership and tests; one coherent PR.

## Exact next action

1. Create `impl/g1-001a-structured-state-adapter` from this exact main checkpoint.
2. Activate `M2-G1-001A` in `CURRENT_WORK.md` on that branch with the exact branch-start SHA.
3. Inspect current repository layout and choose the smallest coherent production/test paths.
4. Implement `STORE-ADAPTER-001A` only.
5. Run/verify applicable tests and baseline gates, update BACKLOG/CURRENT_WORK evidence, then bounded PR/merge/readback.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
