# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide at the same time under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-021` — Compute-fabric execution routing foundation

- **Primary work:** `LOCAL-INTEGRATIONS` (explicitly reprioritized by the product owner on 2026-09-08).
- **Primary features:** `LOCAL-001`, `PROVIDER-001`.
- **Related invariants/features:** `SOURCE-001`, `RECOVERY-002`, `OBS-001`, `STUDIO-001`, `DEV-004`, `DIST-001`, `ONBOARD-004`, `API-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-021-compute-fabric`.
- **Base SHA:** `d4ede63db07de48504bbce2f0c5296c3a1614647`.
- **Packet:** `docs/work-packets/M2-M1-021.md`.
- **Owned implementation surfaces:** `mira/runtime_router.py`, `tests/test_compute_routing.py`, `docs/architecture/COMPUTE_FABRIC.md`, packet doc, this branch's `CURRENT_WORK.md`.
- **Shared/high-contention surfaces:** none modified by this bounded slice beyond branch-local `CURRENT_WORK.md`. PR #134 currently edits `project/code_ownership.json`; PR #135 owns Sheets/code-ownership-fragment work, so this packet avoids both surfaces and must reconcile current `main` before merge.
- **Current status:** in progress; full compute-fabric/Studio directive is durably decomposed in the packet document, and the bounded execution-routing implementation is on this branch awaiting exact-head verification.

## Objective

Implement the smallest dependency-safe compute-fabric foundation: extend the existing provider-neutral runtime router so MIRA can distinguish local and hosted execution lanes, apply explicit `off` / `normal` / `aggressive` local-compute policy, require generic runtime capabilities, fail closed on unavailable/unhealthy/locked local workers, preserve existing privacy/approval/capability evidence rules, and rank eligible lanes deterministically.

This packet does not deploy workers, expose inference/Python/shell services, configure private hardware, add WOL/shutdown, implement queue persistence, invent thermal thresholds, execute self-hosted CI, or claim live worker/provider evidence.

## Acceptance state

- Whole 2026-09-08 product-owner directive captured durably: **complete in `docs/work-packets/M2-M1-021.md`**.
- Exact verified public-repo `main` base recorded: **complete**.
- Concurrency collision check against People Discovery PR #134 and Sheets PR #135: **complete**.
- Existing runtime-router/onboarding/roadmap/features/backlog architecture reviewed: **complete**.
- Local/hosted runtime-kind contract: **implemented on branch**.
- `off` / `normal` / `aggressive` compute policy: **implemented on branch**.
- Generic runtime capability matching: **implemented on branch**.
- Health/availability/interactive-lock fail-closed behavior: **implemented on branch**.
- Deterministic ranking with policy precedence: **implemented on branch**.
- Architecture seam documentation: **implemented on branch**.
- Deterministic tests: **implemented in `tests/test_compute_routing.py`; exact-head execution pending**.
- CI run #505 on head `215fad9a52bdc9db2b8aaec59237057e4af2567b`: **failed at work-session alignment before code ownership/tests because this file used the wrong machine-parsed label `Related features/invariants`; compile, feature registry, lifecycle and starter gates passed. Corrected here to canonical `Related invariants/features`.**
- Exact-head CI after metadata correction: **pending**.
- Current-main reconciliation / PR merge: **pending**.
- Live worker/provider/device proof: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified `main` `d4ede63db07de48504bbce2f0c5296c3a1614647`. `LOCAL-001` already defines the scoped local-service bridge, `PROVIDER-001` already defines evidence-based provider-neutral runtime routing, and `OBS-001` / `STUDIO-001` / `DEV-004` / `DIST-001` / `ONBOARD-004` preserve the downstream observability, Studio, sanitization and onboarding requirements. No second authority or parallel onboarding system is introduced.

### `BACKLOG.md`

Reviewed. `LOCAL-INTEGRATIONS` is an existing deferred work item. The product owner explicitly reprioritized local compute on 2026-09-08. This packet uses that registered work anchor rather than adding an unregistered ID while high-contention governance files are changing on other active branches.

### `ROADMAP.md`

Reviewed. Advanced/self-hosted runtime is optional and follows the ordinary Personal baseline. This packet only adds a reusable policy/capability execution-routing seam and does not make local infrastructure a Standard-path dependency.

### Collision/concurrency review

Reviewed active remote packet work. PR #134 owns People Discovery and currently changes `project/code_ownership.json`. PR #135 owns Sheets control surfaces plus code-ownership-fragment work. This packet avoids those implementation paths and must semantically reconcile current `main` before merge.

### Direction result

ALIGNED

## Exact next action / resume point

1. Verify exact-head CI after the alignment-label correction.
2. If any gate fails, fix only the bounded cause and rerun exact-head CI.
3. Re-read current `main` and active PRs, reconcile intervening compatible work, and preserve any newer governance/ownership mechanism.
4. Merge only through the normal PR path if exact-head CI is green and the branch remains non-destructive.
5. Read back merged `main` and record the exact implementation evidence ceiling. No live worker/provider claim is permitted from this packet.

## Recovery protocol

Resume by reading current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-021.md`, PR #136, the branch head, and active PRs/branches for new overlap. Do not reconstruct the directive from chat memory when the packet document exists.
