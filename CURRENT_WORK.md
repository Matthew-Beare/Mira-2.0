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
- **Status:** activated; graph audit and ranking next.

## Objective

Produce the final acyclic dependency/enables model and ranked engineering backlog from the completed feature audit. Remove circular/over-broad dependencies, separate first-proof prerequisites from later release/onboarding/hardening work, define the shortest safe M2-M0 -> M2-M1 path, and choose exactly one first implementation packet.

## Scope

1. Audit all current implementation work dependencies for direct cycles and milestone overreach.
2. Normalize the first synthetic storage/API proof separately from full Personal Google bootstrap/nontechnical installation.
3. Preserve privacy/security blockers where truly required, but do not make family/enterprise/later features universal core prerequisites.
4. Rank work by data integrity/security -> hard milestone prerequisites -> architectural leverage -> vertical value -> hardening -> later.
5. Define explicit M2-M0 stock ChatGPT core proof and M2-M1 Android proof dependency chains.
6. Select one bounded first implementation packet small enough to complete/test/checkpoint reliably.

No executable MIRA 2.0 product code is implemented in this packet.

## Known graph defects entering packet

1. `DEP-GRAPH` depends on `FEATURE-REGISTRY-001`, an implementation task, creating a process-order contradiction because G0-010 must close before implementation begins.
2. `STORE-ADAPTER-001` depends on `DATA-SANDBOX`, while `DATA-SANDBOX` depends on `STORE-ADAPTER-001`, creating a direct dependency cycle.
3. `DATA-SANDBOX` depends on full `GOOGLE-BOOTSTRAP-001`, which itself depends on installer/skill/provider/source/service infrastructure broader than necessary for the first synthetic state proof.
4. `CORE-ROUNDTRIP` currently couples the first canonical state proof to full Google bootstrap/onboarding instead of a minimal synthetic provider adapter/resource.
5. `API-CORE-001` includes `PROFILE-013` globally even though cross-person sharing authorization is not required for a same-user minimal core entity roundtrip; exact API authorization is required, but full cross-person sharing enforcement can remain a blocker for shared-person features rather than M2-M0 itself.

## Preliminary normalization direction

- G0-010 can derive/rank dependencies directly from canonical `FEATURES.md`/`BACKLOG.md`; `FEATURE-REGISTRY-001` becomes the **first implementation governance gate** rather than a prerequisite for completing the graph audit.
- Introduce a bounded **synthetic storage harness** work packet rather than requiring the full Google bootstrap before adapter/API tests.
- `STORE-ADAPTER-001` should depend on storage contracts + recovery boundaries, not on an already-created provider sandbox.
- `DATA-SANDBOX` should depend on working Authority Registry + adapters and create the actual isolated Google/MIRROR integration namespace later.
- A **synthetic core roundtrip** should precede Google-backed integration proof so API correctness can be tested without provider complexity.
- M2-M0 remains Google-backed stock ChatGPT as the integration milestone, but internal implementation packets can and should prove storage/API semantics on synthetic adapters first.
- `PERMISSION-SCOPE-001` remains a BLOCKER for cross-person/shared/minor/caregiver features, but not for same-person M2-M0 state unless the API command exercises shared resources.

## Acceptance criteria

1. No dependency cycles remain in the ranked critical path.
2. G0-010 no longer depends on implementation work.
3. Synthetic unit/integration harness separated from live/sandbox provider integration.
4. M2-M0 shortest safe chain is explicit.
5. M2-M1 shortest safe chain is explicit and strictly downstream of shared API/core proof.
6. Cross-person privacy blockers remain enforced only where relevant rather than globally over-blocking same-user core.
7. Full onboarding/distribution/enterprise/local/later work does not block first core proof.
8. First implementation packet selected and bounded with objective/acceptance/resume point.
9. BACKLOG priority order reflects the normalized graph rather than historical insertion order.
10. No executable product code/provider state changes in G0-010.
11. Bounded PR/merge/readback, then immediate activation of selected implementation packet.

## Exact next action

1. Read current `BACKLOG.md` implementation rows and identify cycles/over-broad edges.
2. Define normalized dependency waves and first-proof work IDs.
3. Update `BACKLOG.md` and `ROADMAP.md`/`FEATURES.md` only if semantic milestone/dependency wording must change.
4. Checkpoint the chosen first implementation packet before PR close.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture unrelated ideas in BACKLOG unless required for acceptance or explicitly reprioritized.
