# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may remain active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-GOV-002` — Continuous idea/backlog capture audit

- **Primary work:** `IDEA-CAPTURE-AUDIT-001`.
- **Primary features:** `DEV-008`.
- **Related invariants/features:** `DEV-001`, `DEV-002`, `DEV-003`, `DEV-005`, `DEV-007`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-gov-002-idea-backlog-audit`.
- **Base SHA:** `e6e6135837278b094de6ceb495736010a650af52`.
- **Packet:** `docs/work-packets/M2-GOV-002.md`.
- **Trigger:** the customer explicitly required MIRA to add new product ideas/features to the Git-backed backlog and continuously audit whether it is actually doing so, rather than relying on conversational memory.
- **Owned surfaces:** `FEATURES.md`, `BACKLOG.md`, `PROJECT_INSTRUCTIONS.md`, `mira/work_session_alignment.py`, `tests/test_work_session_alignment.py`, `tests/test_project_instructions_contract.py`, this packet's `CURRENT_WORK.md`, and the packet document. `project/code_ownership.json` is touched only if repository-integrity metadata requires it.
- **Shared/high-contention surfaces:** `FEATURES.md`, `BACKLOG.md`, `CURRENT_WORK.md`, `PROJECT_INSTRUCTIONS.md`, and potentially `project/code_ownership.json`.
- **Out of scope:** implementing brainstormed product features merely because they are captured, changing unrelated product priorities, modifying private production data, or rewriting Studio implementation.

## Prior packet closeout

`M2-M1-040` / PR #155 is closed at its bounded evidence ceiling:

- merge/readback `main`: `e6e6135837278b094de6ceb495736010a650af52`;
- exact post-merge CI run #612: completed / success;
- Trusted Runner Gate on the same merge SHA: completed / success;
- live enabled AM/PM brief prompts had already been updated and read back with mutable-live-fact authority and receipt-to-inventory commit rules;
- no claim is made that every future external carrier/provider call will succeed; unavailable live authority remains fail-closed as `UNVERIFIED`.

## Displaced work / durable resume point

`M2-M1-038` / `STUDIO-INTAKE-001` remains preserved in draft PR #153 on branch `work/m2-m1-038-studio-intake`, head `f3d22a1b8451fd0092c926776a106715926c8f8f` at this packet's start and at the pre-merge recheck.

PR #153 changed `CURRENT_WORK.md`, its packet doc, `mira/studio_intake.py`, `tests/test_studio_intake.py`, and adds one `studio-intake` component to `project/code_ownership.json`. After M2-GOV-002 merges, resume that exact branch/PR and semantically reconcile it onto newly verified `main`; preserve its implementation rather than reconstructing from chat.

## Implemented repair

- Registered `DEV-008` as the canonical continuous idea/backlog capture-audit feature.
- Registered dependency-ranked `IDEA-CAPTURE-AUDIT-001` under repository-growth hardening rather than treating backlog arrival order as priority.
- Strengthened Project Instructions so every materially new product idea is reconciled immediately against canonical `FEATURES.md` / `BACKLOG.md` and cannot live only in chat, code, a PR description, or `CURRENT_WORK.md`.
- Added the mandatory explicit `### Idea/backlog capture audit` checkpoint with exact marker `CAPTURE AUDIT COMPLETE` at session alignment, material checkpoints, packet switches and merge/closeout.
- Hardened the existing deterministic work-session alignment gate so missing or incomplete capture-audit evidence fails closed.
- Added direct regression coverage for valid capture evidence, missing capture heading, and incomplete capture marker, plus a Project Instructions contract test.
- Kept idea capture separate from packet scope: recording an idea never silently authorizes implementation.
- Deliberately left `project/code_ownership.json` unchanged after exact-head code-ownership CI passed, avoiding an unnecessary shared-manifest conflict with PR #153 while keeping the already-owned `mira/work_session_alignment.py` under the existing repository-integrity component.

## CI / integration evidence

- PR #156 opened from `work/m2-gov-002-idea-backlog-audit` against `main`.
- Pre-checkpoint implementation head `cf01674579cefe59c206e6193d36543fe2bd78b0` passed exact-head CI run #613.
- CI #613 passed compile, feature registry, product lifecycle ledger, Personal starter distribution, work-session alignment, code ownership, Android client/proof APK, APK provenance, Python unit tests and Workspace Apps Script tests.
- Immediately before this checkpoint, remote `main` remained `e6e6135837278b094de6ceb495736010a650af52`; no intervening merge was detected.
- PR #153 remained open/draft at head `f3d22a1b8451fd0092c926776a106715926c8f8f`; its known overlap is shared governance state plus an additive `studio-intake` ownership registration, not the Studio implementation files owned by this packet.
- This checkpoint changes the branch SHA, so final exact-head CI must pass again before merge. CI #613 is evidence for the implementation state, not permission to skip final-head validation.

## Acceptance criteria

1. `DEV-008` exists in `FEATURES.md`. **PASS — written and read back.**
2. `IDEA-CAPTURE-AUDIT-001` exists in `BACKLOG.md`. **PASS — written and read back.**
3. Project Instructions require durable idea/backlog capture and repeated audit without expanding packet scope. **PASS — implemented and contract-tested in CI #613.**
4. Work-session alignment fails closed without the audit section/marker. **PASS — direct regression tests and CI #613.**
5. Repository `CURRENT_WORK.md` satisfies the new audit contract. **PASS — work-session alignment gate passed in CI #613; this checkpoint preserves the required audit evidence.**
6. Exact-head CI passes all existing and new gates. **PRE-CHECKPOINT PASS #613; final checkpoint head CI pending.**
7. Current-main overlap is rechecked before merge and PR #153 is preserved. **PASS at pre-merge checkpoint; repeat immediately before merge.**
8. Post-merge `main` and CI/status are read back before closure. **PENDING.**
9. Resume `M2-M1-038` from PR #153 after governance closure. **PENDING.**

## Session-start alignment verification — 2026-09-12

### `FEATURES.md`

The customer request is a governance capability, not a new user-runtime domain. Existing `DEV-001`/`DEV-002`/`DEV-003`/`DEV-005`/`DEV-007` establish Git authority, resumable packets, ranked backlog, machine-readable lifecycle, and packet alignment, but none explicitly requires continuous capture-audit evidence for materially new ideas. This packet therefore adds bounded governance feature `DEV-008` rather than pretending `DEV-007` already covers the exact failure mode.

### `BACKLOG.md`

The existing New-idea triage rule says new ideas are captured and must not expand the active packet, but there is no explicit work item/gate requiring repeated proof that the capture actually occurred. `IDEA-CAPTURE-AUDIT-001` is therefore a bounded HARDENING child of existing repository-integrity work, not a new product vertical.

### `ROADMAP.md`

This does not change MIRA's product priority or active milestone. It hardens the Git-authoritative development control plane so user ideas cannot disappear into chat or silently bypass dependency ranking, while preserving the rule that capture alone does not expand the active packet.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- New material idea reviewed: continuously ensure that new product ideas/features are added to canonical backlog and audit whether that capture actually happened.
- Canonical disposition: new governance feature `DEV-008` plus work item `IDEA-CAPTURE-AUDIT-001` in this bounded governance packet.
- Reused related IDs: `DEV-001`, `DEV-002`, `DEV-003`, `DEV-005`, `DEV-007`.
- Packet-scope result: capture/audit hardening only; no brainstormed product feature implementation is admitted by this packet.

### Direction result

ALIGNED

## Pre-merge checkpoint — 2026-09-12

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Material ideas introduced since session-start audit: none beyond the already-captured continuous capture/audit requirement.
- Canonical disposition remains `DEV-008` / `IDEA-CAPTURE-AUDIT-001`; no duplicate feature/work IDs created.
- Implementation-discovered behavior was limited to the deterministic alignment enforcement already inside this work item.
- PR #153 Studio intake remains displaced rather than absorbed into this packet.
- Packet-scope result: unchanged and bounded.

## Exact next action / resume point

1. Require exact-head CI green on this pre-merge checkpoint SHA.
2. Re-read remote `main` and PR #153 head/overlap immediately before merge.
3. Mark PR #156 ready and merge only with expected-head protection when final CI is green and `main` remains compatible.
4. Read back exact post-merge `main`, merge SHA and CI/Trusted Runner status; do not call the packet closed on merge alone.
5. Resume `M2-M1-038` from PR #153 head, reconcile it semantically onto verified post-governance `main`, add the newly required capture-audit evidence to its `CURRENT_WORK.md`, and rerun exact-head CI.

## Evidence ceiling

The Git gate can require explicit durable audit evidence and reject packets that omit it. It cannot independently inspect every human conversation and prove that no idea was ever missed. MIRA remains responsible for performing the semantic audit against the conversation; this packet makes that responsibility explicit, repeatable, reviewable, and fail-closed at alignment/closeout.
