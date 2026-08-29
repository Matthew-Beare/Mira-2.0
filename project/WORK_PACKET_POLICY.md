# MIRA Work-Packet Policy

## Ownership

The user is the customer/product owner. The assistant/developer owns feature decomposition, architecture, dependency ordering, backlog ranking, packet sizing, acceptance criteria, implementation sequencing, Git checkpoints, testing strategy, and CURRENT_WORK maintenance.

The customer may brainstorm freely and does not need project-management syntax.

## One active packet

There should normally be exactly one active work packet. A packet is a bounded outcome, preferably a vertical slice. If it cannot be reliably completed and verified in one working session, split it before implementation.

## Scope admission

A newly discussed idea joins active work only when:

1. it is required for an existing acceptance criterion;
2. it exposes a hard dependency blocking the packet; or
3. the customer explicitly reprioritizes current work.

Otherwise capture it in FEATURES/BACKLOG and continue the active packet.

## Work-session direction gate

Every development work session must begin by reading and reconciling these four Git authorities before implementation continues:

1. `CURRENT_WORK.md` — one active packet and exact resume point;
2. `FEATURES.md` — accepted semantic feature set and dependencies;
3. `BACKLOG.md` — dependency-ranked implementation work, including displaced work;
4. `ROADMAP.md` — milestone and product-ordering intent.

The session-start result must be recorded in `CURRENT_WORK.md` under a heading beginning `## Session-start alignment verification`. It must explicitly cover FEATURES, BACKLOG and ROADMAP and record a direction result of `ALIGNED` before implementation proceeds.

The repository CI gate `python -m mira.work_session_alignment check` must verify that the active primary work exists in `BACKLOG.md`, all declared active feature/invariant IDs exist in `FEATURES.md`, and the required authority review is present. This mechanical check supplements product judgment; it does not replace it.

Before a work session ends or the active branch is handed off, repeat the semantic direction check. Record any drift, newly discovered dependency, reprioritization, or exact resume point in `CURRENT_WORK.md`. A green test suite without this direction check is not a safe recovery checkpoint.

## Feature-set alignment gate

MIRA development must not optimize a local subsystem while drifting away from the intended product. `FEATURES.md` is the canonical semantic contract, with `ROADMAP.md` and `BACKLOG.md` providing milestone and ranked-work context.

Before a packet begins implementation, the assistant/developer must:

1. read the current related feature IDs in `FEATURES.md` and their dependencies;
2. read relevant roadmap/backlog mappings, including adjacent user-visible features that the packet could accidentally break or make impossible;
3. record in `CURRENT_WORK.md` a **Feature alignment** or session-alignment section containing:
   - primary feature/work IDs;
   - user-visible behavior this packet must enable;
   - existing product invariants/features it must preserve;
   - intentionally deferred related features;
4. compare proposed architecture against those requirements and reject designs that solve the packet by silently weakening or deleting accepted product behavior;
5. capture newly discovered customer requirements in `FEATURES.md`/`BACKLOG.md` without silently expanding the active packet.

Before merge/closeout, repeat the feature-alignment check. A packet may not be called complete merely because its code/tests pass if the implementation contradicts the canonical feature set, drops a required user-visible behavior, or makes an accepted downstream feature structurally impossible.

`DEV-005` provides the machine-readable feature registry. `DEV-007` and `mira.work_session_alignment` provide the mechanical packet/session grounding checks. Semantic product judgment remains mandatory because a parser cannot tell whether a locally clever design has made the actual product stupid.

## Explicit reprioritization

Before switching:

1. checkpoint current work durably;
2. write the exact resume point to CURRENT_WORK;
3. confirm displaced and new work already exist in BACKLOG or add them there;
4. commit/push and remotely read back when Git access permits;
5. then switch scope.

Existing backlog items do not need duplicate rows merely because their priority changes; CURRENT_WORK records the active priority and exact resume point while BACKLOG remains non-FIFO.

## Packet record

Every packet records:

- packet ID/name;
- related feature/work IDs;
- objective;
- branch/base/head where applicable;
- dependencies/blockers;
- **feature alignment:** user-visible behavior, preserved feature invariants, and explicitly deferred related features;
- explicit acceptance criteria;
- completed evidence;
- exact next action/resume point.

## Dynamic priority

BACKLOG is not FIFO. Priority order:

1. integrity/privacy/security and active blockers;
2. hard prerequisites;
3. foundational multi-feature enablers;
4. user-visible vertical value;
5. release hardening/evidence;
6. enhancements;
7. later ideas.

When the customer explicitly changes priority, that direction overrides an older milestone ordering after the displaced packet is safely checkpointed. The roadmap/backlog must not be treated as an excuse to continue lower-value work the customer has just rejected.

## Completion evidence

Track separately:

`desired → specified → implemented → test_verified → integration_verified → live_verified`

Do not upgrade evidence level without the corresponding proof.

## Green before growth

Do not add unrelated feature work while required baseline gates are red. Newly discovered blockers may preempt current work, but the displaced packet must retain an exact resume point.

## Recovery

Assume any session can terminate unexpectedly.

- Commit/checkpoint frequently at meaningful boundaries.
- Never leave the only unfinished-work description in chat.
- On recovery, read `CURRENT_WORK.md` before relying on conversational reconstruction.
- Run the work-session direction check before continuing implementation.
- Record the first incomplete item, not merely a percentage.

## Legacy data

Legacy MIRA Google/Drive/brief/scheduler state is protected production. MIRA 2.0 uses a separate sandbox until an explicit migration packet authorizes a controlled migration with backup, rollback, reconciliation, bounded writes, and readback.

## Reply recovery tag

Every assistant response in MIRA development ends with exactly one final visible line:

`PACKET: <active-packet-id>`

Git remains authoritative; the tag is only a human recovery pointer.
