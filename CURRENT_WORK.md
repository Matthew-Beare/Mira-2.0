# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-044` — Deterministic reconciliation and pre-reply gate

- **Primary work:** `FIN-EVIDENCE-RECONCILE-001`.
- **Primary features:** `RECOVERY-001`, `RECOVERY-002`, `OPS-004`, `FIN-001`.
- **Related invariants/features:** `AUTH-001`, `SOURCE-001`, `MAIL-001`, `ORDER-001`, `ORDER-002`, `ORDER-005`, `MILE-001`, `MILE-002`, `TASK-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-044-reconciliation-reply-gate`.
- **Base SHA:** `be73fd5eb987841be37fb050bc383dfd6f660606`.
- **Packet:** `docs/work-packets/M2-M1-044.md`.

## Closed/displaced work

`M2-M1-043` / PR #159 merged at exact `main` SHA `be73fd5eb987841be37fb050bc383dfd6f660606`. Exact-merge check runs on that SHA are green. The Studio compute-dispatch vertical is therefore no longer the active packet in this chat.

## Customer outcome

MIRA must not compose an operational or Financial Escape reply merely because it fetched some data. A run must first execute a deterministic sweep:

`DISCOVER -> RECONCILE -> MUTATE -> REBUILD -> VERIFY -> CHECKPOINT -> REPLY`

The sweep is reusable across Finance Escape, Trucking/Ops, mileage, orders/shipments, receipts/assets, calendar, jobs and later domains. Each module must finish with an explicit terminal disposition and evidence. Required mutations must have exact readback before the module can claim success. Unknown/blocked state remains explicit, and one failed module must not suppress healthy independent modules.

## Packet boundary

This packet implements the reusable deterministic run/reply gate and its proof tests. It does **not** implement every provider adapter or silently claim live scheduling/background execution. Finance, trucking/mileage and shipment/email handlers remain domain modules that must plug into this contract in bounded follow-on work.

### Owned implementation surfaces

- `ops/reconciliation_sweep.py` (new)
- `tests/test_reconciliation_sweep.py` (new)
- `docs/OPS_EVIDENCE_AUTHORITY_CONTRACT.md` (bounded contract extension)
- `docs/work-packets/M2-M1-044.md`
- this branch's `CURRENT_WORK.md`

### Shared/high-contention surfaces

No `FEATURES.md`, `BACKLOG.md`, `ROADMAP.md`, `PROJECT_INSTRUCTIONS.md`, Google production data, or live provider resources are authorized for mutation in the implementation slice. Existing `FIN-EVIDENCE-RECONCILE-001` is reused rather than duplicated.

### Collision review

- Open draft PR #135 (`M2-M1-020`) owns reusable Google Sheets control-surface implementation and older governance-file edits. This packet will not touch its Sheets renderer/control-surface code.
- Stale PR #115 is lifecycle-only and does not overlap the owned implementation surface.

## Acceptance criteria

1. A run has deterministic identity, timezone/slot/context and a declared module manifest.
2. Every declared module reaches one terminal disposition: `complete`, `needs_review`, `blocked`, or `not_applicable`.
3. A module cannot claim `complete` after mutations unless exact readback evidence is present for every required mutation.
4. Source freshness/coverage and counts of discovered/matched/updated/duplicate/unresolved evidence are checkpointed.
5. Required blocked modules remain visible as exact blockers; healthy independent modules remain usable.
6. The reply gate refuses unsupported claims such as `current`, `updated`, `reconciled`, or `done` for modules whose verification did not pass.
7. Successful replay of the same completed run is idempotent and does not rerun module side effects.
8. A checkpoint records enough state for the next run to resume from durable last-success cursors/markers supplied by domain modules.
9. The engine is provider-neutral and contains no private account IDs, spreadsheet IDs, email contents, routes or credentials.
10. Synthetic tests cover success, review-required, blocker isolation, missing readback, duplicate module IDs, replay and overclaim rejection.
11. Git exact-head CI must pass before merge; post-merge exact-SHA CI/readback is required before integration-verified closeout.

## Session-start alignment verification — 2026-09-13

### `FEATURES.md`

The packet advances existing recovery/run integrity (`RECOVERY-001`, `RECOVERY-002`, `OPS-004`) and the already accepted financial evidence-reconciliation direction (`FIN-001`, `MAIL-001`, `ORDER-*`, `MILE-*`). It does not create a second canonical finance model or duplicate provider infrastructure.

### `BACKLOG.md`

`FIN-EVIDENCE-RECONCILE-001` already requires repeatable reconciliation with stable source identity, replay dedupe, exception queues and exact readback. This packet extracts the reusable deterministic run/reply gate prerequisite so finance and non-finance operational modules can obey the same contract. `FIN-CANON-AUDIT-001` remains separate canonical-finance work and is not falsely marked complete here.

### `ROADMAP.md`

Direction remains ordinary-language MIRA backed by durable canonical state, explicit evidence/readback, failure isolation and no fabricated provider/live claims. The packet improves reliability of every recurring user-facing run without changing provider choice or Standard/Advanced deployment semantics.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- The customer-approved global reconciliation sweep is implemented as a reusable prerequisite inside existing recovery/run and `FIN-EVIDENCE-RECONCILE-001` semantics rather than creating a parallel finance system.
- Pig Phet shared-mileage backstop and deep daily shipment/email recheck remain domain policy/handler requirements, not duplicate global engines.
- No private production identifiers or account data are committed.
- No unrelated feature is admitted.

### Direction result

ALIGNED

## Exact next action / resume point

1. Implement `ops/reconciliation_sweep.py` with deterministic manifest, module-result validation, checkpoint serialization and pre-reply claim gate.
2. Add adversarial synthetic tests in `tests/test_reconciliation_sweep.py`.
3. Extend `docs/OPS_EVIDENCE_AUTHORITY_CONTRACT.md` with the global pre-reply sweep plus the already user-approved mileage-backstop and unresolved-shipment diligence rules.
4. Open a draft PR and use exact-head CI to discover repository-wide ownership/alignment issues.
5. Fix only packet-owned failures; then perform semantic closeout, merge/readback and post-merge CI.

## Evidence ceiling

Synthetic tests can prove deterministic orchestration, validation, replay and claim-gating semantics. They cannot prove Gmail was actually read, a bank/card provider is fresh, Pig Phet's live sheet was reconciled, a carrier was dereferenced, or a scheduled AM/PM run executed. Those require domain/live provider evidence in follow-on packets/runs.
