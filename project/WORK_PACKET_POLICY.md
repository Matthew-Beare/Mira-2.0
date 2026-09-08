# MIRA Work-Packet Policy

## Ownership

The user is the customer/product owner. The assistant/developer owns feature decomposition, architecture, dependency ordering, backlog ranking, packet sizing, acceptance criteria, implementation sequencing, Git checkpoints, testing strategy, and CURRENT_WORK maintenance.

The customer may brainstorm freely and does not need project-management syntax.

## Concurrent repository model

Multiple MIRA development chats may work in parallel, but Git isolation is mandatory.

- Each chat/session owns exactly one active work packet at a time.
- Each packet has a unique packet ID and its own `work/...` branch.
- Multiple packet branches may be active repository-wide at the same time.
- `main` is the serialized integration branch and is never a shared scratch branch.
- A packet is a bounded outcome, preferably a vertical slice. If it cannot be reliably completed and verified in one working session, split it before implementation.
- Remote packet branches and open PRs are the repository-wide concurrency registry. Do not assume `CURRENT_WORK.md` on `main` exhaustively describes every in-flight branch.
- `CURRENT_WORK.md` on a packet branch describes that branch's one active packet and exact safe resume point. This preserves the mechanical one-active-packet-per-branch alignment gate while allowing many branches to progress concurrently.

## Collision prevention

Before implementation writes, every chat must:

1. read current remote `main` and verify its SHA;
2. read `CURRENT_WORK.md`, FEATURES, BACKLOG, and ROADMAP from the relevant base/current branch;
3. if resuming, verify the packet's remote branch head and packet document;
4. inspect active `work/...` branches and open PRs for overlapping implementation surfaces;
5. record owned implementation surfaces / expected touched paths in the packet document;
6. record any shared or high-contention surfaces and the integration plan before editing them.

Two packets must not intentionally modify the same implementation surface concurrently unless an explicit dependency or integration plan is recorded first.

Shared governance files such as `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PROJECT_INSTRUCTIONS.md` are high-contention surfaces. Keep changes minimal, additive where practical, and reconcile them against current `main` immediately before merge.

Never force-update another packet's branch or reuse it for unrelated work.

## Scope admission

A newly discussed idea joins the current chat's active work only when:

1. it is required for an existing acceptance criterion;
2. it exposes a hard dependency blocking the packet; or
3. the customer explicitly reprioritizes that chat's current work.

Otherwise capture it in FEATURES/BACKLOG and continue the current packet. Reprioritizing one chat does not globally suspend unrelated non-conflicting packet branches.

## Work-session direction gate

Every development work session must begin by reading and reconciling these four Git authorities before implementation continues:

1. `CURRENT_WORK.md` — this branch's one active packet and exact resume point;
2. `FEATURES.md` — accepted semantic feature set and dependencies;
3. `BACKLOG.md` — dependency-ranked implementation work, including displaced work;
4. `ROADMAP.md` — milestone and product-ordering intent.

Also inspect remote active packet branches/open PRs for collision risk before writes.

The session-start result must be recorded in `CURRENT_WORK.md` under a heading beginning `## Session-start alignment verification`. It must explicitly cover FEATURES, BACKLOG and ROADMAP and record a direction result of `ALIGNED` before implementation proceeds.

The repository CI gate `python -m mira.work_session_alignment check` verifies the active primary work exists in `BACKLOG.md`, all declared active feature/invariant IDs exist in `FEATURES.md`, and the required authority review is present. This mechanical check supplements product judgment; it does not replace it.

Before a work session ends or the active branch is handed off, repeat the semantic direction check. Record any drift, newly discovered dependency, reprioritization, collision risk, or exact resume point in `CURRENT_WORK.md`. A green test suite without this direction check is not a safe recovery checkpoint.

## Feature-set alignment gate

MIRA development must not optimize a local subsystem while drifting away from the intended product. `FEATURES.md` is the canonical semantic contract, with `ROADMAP.md` and `BACKLOG.md` providing milestone and ranked-work context.

Before a packet begins implementation, the assistant/developer must:

1. read the current related feature IDs in `FEATURES.md` and their dependencies;
2. read relevant roadmap/backlog mappings, including adjacent user-visible features that the packet could accidentally break or make impossible;
3. record in `CURRENT_WORK.md` a feature/session-alignment section containing:
   - primary feature/work IDs;
   - user-visible behavior this packet must enable;
   - existing product invariants/features it must preserve;
   - intentionally deferred related features;
4. compare proposed architecture against those requirements and reject designs that solve the packet by silently weakening or deleting accepted product behavior;
5. capture newly discovered customer requirements in `FEATURES.md`/`BACKLOG.md` without silently expanding the active packet.

Before merge/closeout, repeat the feature-alignment check. A packet may not be called complete merely because its code/tests pass if the implementation contradicts the canonical feature set, drops a required user-visible behavior, or makes an accepted downstream feature structurally impossible.

`DEV-005` provides the machine-readable feature registry. `DEV-007` and `mira.work_session_alignment` provide the mechanical packet/session grounding checks. Semantic product judgment remains mandatory because a parser cannot tell whether a locally clever design has made the actual product stupid.

## Explicit reprioritization

Before one chat switches packets:

1. checkpoint its current branch durably;
2. write the exact resume point to that branch's CURRENT_WORK and packet document;
3. confirm displaced and new work already exist in BACKLOG or add them there;
4. commit/push and remotely read back when Git access permits;
5. then switch the chat to a new or resumed packet branch.

Existing backlog items do not need duplicate rows merely because their priority changes. Other non-conflicting packet branches may continue.

## Packet record

Every packet records:

- packet ID/name;
- related feature/work IDs;
- objective;
- branch/base/current remote head where applicable;
- dependencies/blockers;
- owned implementation surfaces / expected touched paths;
- shared/high-contention surfaces and integration plan where applicable;
- feature alignment: user-visible behavior, preserved feature invariants, and explicitly deferred related features;
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

When the customer explicitly changes priority in one chat, that direction overrides older ordering for that chat after its displaced packet is safely checkpointed. This does not cancel unrelated parallel work unless a shared integrity/dependency issue requires it.

## Main integration discipline

Parallel implementation does not permit blind parallel merges.

Before any packet merges to `main`:

1. re-read current remote `main` and compare it with the packet base;
2. identify intervening merged packets and overlapping files/domains;
3. reconcile the packet with current `main` semantically, preserving compatible newer work;
4. never resolve a conflict by simply discarding another packet's valid newer changes;
5. rerun required tests and affected baseline gates after reconciliation;
6. update the packet document with reconciled head/evidence;
7. merge through a normal PR/non-force path;
8. read back remote `main`, merge SHA, and relevant CI/status evidence before claiming completion.

If safe reconciliation cannot be proven, leave both branches intact and stop the merge. A branch that was green on an old base is not automatically safe after another packet merges.

## Completion evidence

Track separately:

`desired → specified → implemented → test_verified → integration_verified → live_verified`

Do not upgrade evidence level without the corresponding proof.

## Green before growth

Do not add unrelated feature work to a packet whose required baseline gates are red. A red packet does not automatically freeze unrelated isolated branches unless it exposes a repository-wide integrity/security issue or shared hard dependency.

Newly discovered blockers may preempt affected work, but every interrupted packet must retain an exact resume point.

## Recovery

Assume any session can terminate unexpectedly.

- Commit/checkpoint frequently at meaningful boundaries.
- Never leave the only unfinished-work description in chat.
- On recovery, read current remote `main`, then the relevant packet branch's `CURRENT_WORK.md` and packet document before relying on conversational reconstruction.
- Verify the remote branch head.
- Inspect other active packet branches/PRs for newly overlapping work.
- Run the work-session direction check before continuing implementation.
- Record the first incomplete item, not merely a percentage.

## Legacy data

Legacy MIRA Google/Drive/brief/scheduler state is protected production. MIRA 2.0 uses a separate sandbox until an explicit migration packet authorizes a controlled migration with backup, rollback, reconciliation, bounded writes, and readback.

## Reply recovery tag

Every assistant response in MIRA development ends with exactly one final visible line:

`PACKET: <current-chat-packet-id>`

Use the packet owned by the current chat, not another branch's packet. Git remains authoritative; the tag is only a human recovery pointer.
