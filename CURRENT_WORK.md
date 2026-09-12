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

`M2-M1-038` / `STUDIO-INTAKE-001` remains preserved in draft PR #153 on branch `work/m2-m1-038-studio-intake`, head `f3d22a1b8451fd0092c926776a106715926c8f8f` at this packet's start.

PR #153 changed `CURRENT_WORK.md`, its packet doc, `mira/studio_intake.py`, `tests/test_studio_intake.py`, and adds one `studio-intake` component to `project/code_ownership.json`. After M2-GOV-002 merges, resume that exact branch/PR and semantically reconcile it onto newly verified `main`; preserve its implementation rather than reconstructing from chat.

## Intended repair

- Register a governance feature requiring continuous idea/backlog capture audit.
- Register dependency-ranked work implementing that governance feature.
- Strengthen Project Instructions so every materially new product idea is immediately reconciled against canonical `FEATURES.md` / `BACKLOG.md` and does not live only in chat.
- Require explicit `### Idea/backlog capture audit` evidence with exact marker `CAPTURE AUDIT COMPLETE` during session alignment/checkpoint/closeout.
- Make the existing deterministic work-session alignment gate reject missing or incomplete capture-audit evidence.
- Keep idea capture separate from packet scope: recording an idea never silently authorizes implementation.

## Acceptance criteria

1. `DEV-008` exists in `FEATURES.md`. **PENDING write/readback.**
2. `IDEA-CAPTURE-AUDIT-001` exists in `BACKLOG.md`. **PENDING write/readback.**
3. Project Instructions require durable idea/backlog capture and repeated audit without expanding packet scope. **IMPLEMENTED on branch; CI/readback pending.**
4. Work-session alignment fails closed without the audit section/marker. **PENDING implementation/test.**
5. Repository `CURRENT_WORK.md` satisfies the new audit contract. **IMPLEMENTED checkpoint; gate pending.**
6. Exact-head CI passes all existing and new gates. **PENDING.**
7. Current-main overlap is rechecked before merge and PR #153 is preserved. **PENDING.**
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

## Exact next action / resume point

1. Write/read back `DEV-008` in `FEATURES.md` and `IDEA-CAPTURE-AUDIT-001` plus strengthened triage/audit rule in `BACKLOG.md`.
2. Harden `mira/work_session_alignment.py` and direct tests for required capture-audit evidence.
3. Add an instruction-contract regression test.
4. Reconcile repository-integrity ownership metadata if required.
5. Run exact-head CI and repair failures without bypassing existing gates.
6. Re-read current `main` and PR #153 overlap immediately before merge; merge with expected-head protection only if compatible.
7. Verify exact post-merge `main` and CI/status evidence.
8. Resume `M2-M1-038` from PR #153 head and reconcile it onto the verified post-governance `main`.

## Evidence ceiling

The Git gate can require explicit durable audit evidence and reject packets that omit it. It cannot independently inspect every human conversation and prove that no idea was ever missed. MIRA remains responsible for performing the semantic audit against the conversation; this packet makes that responsibility explicit, repeatable, reviewable, and fail-closed at alignment/closeout.
