# MIRA concurrent work policy

Git is authoritative. Multiple MIRA development chats may work in parallel, but concurrency is allowed only through isolated work packets and serialized integration into `main`.

## Core model

- Multiple packets may be active repository-wide at the same time.
- A single chat/session owns exactly one implementation packet at a time.
- Every active packet uses its own unique packet ID and branch.
- `main` is the integration branch and is never treated as a scratch workspace.
- Work on one packet must not silently broaden into another packet just because another chat is working nearby.

## Required packet metadata

Every packet must record:

- packet ID and name;
- related feature/work IDs;
- objective and bounded scope;
- branch;
- base SHA and current remote head SHA;
- dependencies and blockers;
- owned implementation surfaces / expected touched paths;
- shared or high-contention files, if any;
- explicit acceptance criteria;
- completed evidence;
- exact next action / resume point.

The packet document and the remote branch head are authoritative for that packet's exact resume state. `CURRENT_WORK.md` is the repository-wide coordination index and must point to the active packet documents/branches rather than pretending only one packet can exist.

## Starting or resuming work

Before writing:

1. Read `PROJECT_INSTRUCTIONS.md` and `CURRENT_WORK.md` from current remote `main`.
2. Verify the current remote `main` SHA.
3. If resuming a packet, verify that packet's remote branch head and read its packet document before making changes.
4. Inspect the repository-wide active-packet index for overlapping work surfaces.
5. Start new work from current verified `main` unless a documented dependency requires another base.
6. Create a unique branch for the packet before implementation writes.

## Collision prevention

- Two packets must not intentionally modify the same implementation surface concurrently unless an explicit integration plan is recorded first.
- Shared governance files such as `CURRENT_WORK.md`, `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, and `PROJECT_INSTRUCTIONS.md` are high-contention surfaces. Keep changes minimal, additive where practical, and reconcile them against current `main` immediately before merge.
- If another packet already owns a code path or schema that the current packet needs to change, either make the current packet depend on that work, split the ownership boundary, or checkpoint and coordinate before editing it.
- Do not force-push over another packet's branch or move another packet's branch ref merely to avoid a merge conflict.
- Do not reuse another packet's branch for unrelated work.

## Integration discipline

`main` integration is serialized even when implementation is parallel.

Before merge:

1. Re-read current remote `main`.
2. Detect whether another packet merged after this packet's base SHA.
3. Reconcile the packet with current `main` rather than assuming the old base is still valid.
4. Resolve conflicts deliberately, preserving newer compatible work from both packets.
5. Rerun the packet's required tests and any affected baseline gates after reconciliation.
6. Update the packet document with the reconciled head and evidence.
7. Merge through a pull request or other normal non-force integration path.
8. Read back remote `main`, verify the merge SHA, and verify relevant CI/status evidence before claiming completion.

A green branch on an old base is not sufficient evidence that it is safe to merge after another packet changes overlapping code.

## Reprioritization

A user may reprioritize one chat without globally suspending unrelated packets in other chats.

When a chat switches packets:

1. checkpoint its current packet branch;
2. record the exact resume point in that packet document;
3. update repository-wide coordination state when practical;
4. then start or resume the newly selected packet on its own branch.

Other non-conflicting packets may continue.

## Merge conflicts and stale branches

A merge conflict is a coordination signal, not permission to discard somebody else's work.

- Prefer semantic reconciliation over choosing one whole file version when both branches contain valid changes.
- If safe reconciliation cannot be proven from available evidence, stop the merge and leave both branches intact.
- Never overwrite a newer `main` or another active branch with an older snapshot.

## Recovery

Any chat should be able to recover by reading:

1. current remote `main`;
2. `CURRENT_WORK.md`;
3. the packet's own document;
4. the packet's remote branch head and open PR, if any.

Conversation history is helpful context but is never a substitute for those Git records.
