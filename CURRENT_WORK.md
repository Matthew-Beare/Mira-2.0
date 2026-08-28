# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet before this branch

### `M2-G0-009` — Legacy branch/PR reconciliation

- **Merged PR:** #35
- **Merge SHA / main readback:** `8155c8fa40d4d6e0f9f65d8594061fba598c5784`
- **Post-merge completion checkpoint / this branch start SHA:** `e03e4fa0a6ad323442d4ec33c7c5c30afb54b5c8`
- **Result:** legacy reconciliation complete; PR #31 selective salvage only, PR #34 superseded, generated mirrors noncanonical, independent productization code bounded to current work IDs.

## Active packet

- **Packet ID:** `M2-G0-010`
- **Name:** Final dependency graph and implementation ranking closeout
- **Class:** governance/dependency closeout — final G0 packet
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-010-dependency-closeout`
- **Branch start SHA:** `e03e4fa0a6ad323442d4ec33c7c5c30afb54b5c8`
- **Activation commit:** `30a02a196b8ad1f40bc3d5d3e7418097c86e7465`
- **Feature graph normalization:** `64622bab93f2c4c6a90d16d0703ff2daa1effc85`
- **Roadmap normalization:** `a166bf77dfcaeb5992405d6579e19c1751cfbd6f`
- **Ranked backlog / first-packet selection:** `e6332c46defef8e1a771ccb1cbc5ef9d3e6e930c`
- **Status:** acceptance complete; diff gate, bounded PR, merge and main readback remain.

## Canonical dependency result

The M2-M0/M2-M1 critical path is acyclic and no longer over-blocked by unrelated family, provider-routing, onboarding, enterprise or later infrastructure work.

### Defects repaired

- `DEP-GRAPH` no longer depends on implementation task `FEATURE-REGISTRY-001`.
- `STORE-ADAPTER-001` / `DATA-SANDBOX` direct cycle is removed.
- Full `GOOGLE-BOOTSTRAP-001` is no longer required before the first Google-backed integration proof.
- Same-user `API-CORE-001` no longer waits on cross-person `PROFILE-013`/`PERMISSION-SCOPE-001`; cross-person commands remain fail-closed until that work lands.
- Android client core no longer waits on unrelated AI/provider runtime routing.
- Feature-level cycles in schedule/clock, identifier/evidence, grocery/par and Person/permission semantics were removed by defining one-way foundations rather than mutual prerequisites.

### Shortest safe implementation waves

1. `STORE-ADAPTER-001A` — structured-state contract + deterministic in-memory adapter.
2. `AUTHORITY-REGISTRY-001` — one canonical mutable authority per data class.
3. `API-CORE-001` — authenticated/authorized shared service with mandatory idempotency/version/conflict/readback semantics.
4. `CORE-SYNTHETIC-ROUNDTRIP` — complete synthetic API proof without external provider state.
5. `FEATURE-REGISTRY-001` + `CODE-OWNERSHIP-001` — early repository growth gates before broad implementation fan-out.
6. `DATA-SANDBOX` + `GOOGLE-STORE-ADAPTER-001` — isolated synthetic Google-backed authority path.
7. `API-DEPLOYMENT-001` + `CHATGPT-API-CLIENT-001` — managed HTTPS shared service and stock ChatGPT client path; no required self-hosted server.
8. `CORE-ROUNDTRIP` — M2-M0 stock ChatGPT Google-backed canonical entity proof.
9. `ANDROID-CLIENT-CORE-001` — protected shared-API Android client with offline replay/reconnect semantics.
10. `ANDROID-SYNC` — M2-M1 Android and stock ChatGPT read/write the same canonical entity.
11. Native Android delivery/capture/release hardening follows the shared-state proof.

## First implementation packet selected

### `M2-G1-001A` — Synthetic structured-state adapter core

**Work ID:** `STORE-ADAPTER-001A`

**Objective:** implement the provider-neutral structured-state contract and deterministic in-memory synthetic adapter that all canonical mutable-state tests can use without Google, network access or legacy production state.

**Acceptance criteria:**
1. Define a bounded structured-state adapter interface for health/schema, exact read, bounded query, idempotent upsert and append-event behavior.
2. Use stable caller-supplied canonical IDs; adapter does not invent competing identities during replay.
3. Maintain monotonic revision/version state and expose exact material readback after mutation.
4. Replaying the same idempotency key + same request returns the prior material result without a second mutation.
5. Reusing an idempotency key for materially different input fails closed.
6. Stale expected revision/conflicting mutation fails explicitly and leaves canonical state unchanged.
7. Unknown entity/resource types and invalid envelopes fail explicitly rather than permissively writing arbitrary state.
8. Deterministic synthetic tests prove create/read/query/update/replay/conflict/append-event/readback semantics.
9. No provider/network/evidence-store implementation, credentials, protected state or legacy production data is touched.
10. New production artifacts have bounded ownership and tests; packet remains small enough for one coherent PR.

## G0-010 acceptance

1. No dependency cycles remain in the M2-M0/M2-M1 critical path. **Satisfied.**
2. G0-010 has no implementation prerequisite. **Satisfied.**
3. Synthetic state proof is separate from provider integration. **Satisfied.**
4. M2-M0 shortest safe chain is explicit. **Satisfied.**
5. M2-M1 shortest safe chain is explicit and downstream of shared API/core proof. **Satisfied.**
6. Cross-person privacy blockers remain enforced only where relevant. **Satisfied.**
7. Full onboarding/distribution/enterprise/local/later work does not block first core proof. **Satisfied.**
8. First implementation packet is explicitly bounded. **Satisfied.**
9. `BACKLOG.md` is dependency-ranked rather than insertion-ranked. **Satisfied.**
10. No executable product code/provider state changed in G0-010. **Satisfied.**
11. Bounded PR/merge/readback. **Pending.**

## Exact next action

1. Compare this branch to `main`; expected changed files are exactly `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, `CURRENT_WORK.md`.
2. Open/verify/merge the bounded G0-010 PR at the exact head and read back `main`.
3. Commit a main completion checkpoint naming `M2-G1-001A` as successor.
4. Create the implementation branch from that exact checkpoint.
5. Activate `M2-G1-001A` in `CURRENT_WORK.md` before writing product code.
6. Implement `STORE-ADAPTER-001A` only; adjacent provider/API/evidence work remains queued.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
