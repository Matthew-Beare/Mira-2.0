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
- **Shared/high-contention surfaces:** none modified by this bounded slice beyond branch-local `CURRENT_WORK.md`. PR #134 currently owns People Discovery and edits `project/code_ownership.json`; PR #135 owns Sheets/code-ownership-fragment work. Both remain open/draft and unmerged at the final reconciliation checkpoint.
- **Current status:** implementation complete on branch; exact-head CI #508 passed on `69e031113bc5a795cfc69a5760381bc11674d862`; this checkpoint commit records that evidence and therefore requires one final exact-head CI before merge.

## Objective

Implement the smallest dependency-safe compute-fabric foundation: extend the existing provider-neutral runtime router so MIRA can distinguish local and hosted execution lanes, apply explicit `off` / `normal` / `aggressive` local-compute policy, require generic runtime capabilities, fail closed on unavailable/unhealthy/locked local workers, preserve existing privacy/approval/capability evidence rules, and rank eligible lanes deterministically.

This packet does not deploy workers, expose inference/Python/shell services, configure private hardware, add WOL/shutdown, implement queue persistence, invent thermal thresholds, execute self-hosted CI, or claim live worker/provider evidence.

## Acceptance state

- Whole 2026-09-08 product-owner directive captured durably: **complete in `docs/work-packets/M2-M1-021.md`**.
- Exact verified public-repo `main` base recorded: **complete**.
- Concurrency collision check against People Discovery PR #134 and Sheets PR #135: **complete and rechecked immediately before closeout**.
- Existing runtime-router/onboarding/roadmap/features/backlog architecture reviewed: **complete**.
- Local/hosted runtime-kind contract: **implemented**.
- `off` / `normal` / `aggressive` compute policy: **implemented**.
- Generic runtime capability matching: **implemented**.
- Health/availability/interactive-lock fail-closed behavior: **implemented**.
- Deterministic ranking with policy precedence: **implemented**.
- Architecture seam documentation: **implemented**.
- Deterministic compute-routing tests: **implemented in `tests/test_compute_routing.py`**.
- CI run #505 on `215fad9a52bdc9db2b8aaec59237057e4af2567b`: **failed at work-session alignment because this file used the wrong machine-parsed field label; corrected without changing product behavior**.
- CI run #506 on `b9abb845e570825c3174389f10914afbbb22c350`: **passed governance/code-ownership/Android gates and reached Python tests; failed because the malformed-mode test helper dereferenced `.value` before `RuntimePolicy` validation; corrected in the test**.
- CI run #508 on `69e031113bc5a795cfc69a5760381bc11674d862`: **PASS end-to-end: compile, feature registry, lifecycle, starter distribution, work-session alignment, code ownership, Android proof/provenance/retention, Python unit tests, and Workspace Apps Script tests all succeeded**.
- Final pre-merge `main` readback: **still `d4ede63db07de48504bbce2f0c5296c3a1614647`; no rebase/reconciliation changes required**.
- PR #134 / #135 readback: **both remain open draft and unmerged; this packet still does not overlap their implementation surfaces**.
- Final exact-head CI after this documentation-only checkpoint: **pending**.
- Current-main PR merge/readback: **pending final exact-head green**.
- Live worker/provider/device proof: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed from verified `main` `d4ede63db07de48504bbce2f0c5296c3a1614647`. `LOCAL-001` already defines the scoped local-service bridge, `PROVIDER-001` already defines evidence-based provider-neutral runtime routing, and `OBS-001` / `STUDIO-001` / `DEV-004` / `DIST-001` / `ONBOARD-004` preserve the downstream observability, Studio, sanitization and onboarding requirements. No second authority or parallel onboarding system is introduced.

### `BACKLOG.md`

Reviewed. `LOCAL-INTEGRATIONS` is an existing deferred work item. The product owner explicitly reprioritized local compute on 2026-09-08. This packet uses that registered work anchor rather than adding an unregistered ID while high-contention governance files are changing on other active branches.

### `ROADMAP.md`

Reviewed. Advanced/self-hosted runtime is optional and follows the ordinary Personal baseline. This packet only adds a reusable policy/capability execution-routing seam and does not make local infrastructure a Standard-path dependency.

### Collision/concurrency review

Final pre-merge readback confirms `main` remains the recorded base. People Discovery PR #134 and Sheets PR #135 remain open/draft and unmerged. M2-M1-021 does not touch their implementation paths or `project/code_ownership.json`, so no semantic reconciliation change is required before this packet's merge.

### Direction result

ALIGNED

## Exact next action / resume point

1. Verify one final exact-head CI on this documentation-only checkpoint commit.
2. If green, mark PR #136 ready and merge through the normal PR path using the exact expected head SHA.
3. Read back merged remote `main` and post-merge CI/status evidence.
4. Record the implementation evidence ceiling as test-verified/integration-verified routing foundation only. Do not claim a live compute fabric, worker, local model, power-control path, telemetry system, or private deployment binding from M2-M1-021.
5. Select the next child packet from `docs/work-packets/M2-M1-021.md` by dependency/integrity ranking rather than expanding this completed packet.

## Recovery protocol

Resume by reading current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-021.md`, PR #136, the branch head, and active PRs/branches for new overlap. Do not reconstruct the directive from chat memory when the packet document exists.
