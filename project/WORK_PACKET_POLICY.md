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

## Explicit reprioritization

Before switching:

1. checkpoint current work durably;
2. write the exact resume point to CURRENT_WORK;
3. record displaced/new work in BACKLOG;
4. commit/push and remotely read back when Git access permits;
5. then switch scope.

## Packet record

Every packet records:

- packet ID/name;
- related feature/work IDs;
- objective;
- branch/base/head where applicable;
- dependencies/blockers;
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
- Record the first incomplete item, not merely a percentage.

## Legacy data

Legacy MIRA Google/Drive/brief/scheduler state is protected production. MIRA 2.0 uses a separate sandbox until an explicit migration packet authorizes a controlled migration with backup, rollback, reconciliation, bounded writes, and readback.

## Reply recovery tag

Every assistant response in MIRA development ends with exactly one final visible line:

`PACKET: <active-packet-id>`

Git remains authoritative; the tag is only a human recovery pointer.
