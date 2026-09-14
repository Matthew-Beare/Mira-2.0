# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet.

## Active packet

### `M2-M1-047` — Canonical finance historical boundary closure

- **Primary work:** `FIN-CANON-AUDIT-001`.
- **Primary features:** `FIN-001`, `RECOVERY-001`, `RECOVERY-002`.
- **Related invariants/features:** `MAIL-001`, `ORDER-001`, `RECEIPT-001`, `ASSET-001`, `ASSET-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-047-finance-history-boundary`.
- **Base SHA:** `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`.
- **Packet:** `docs/work-packets/M2-M1-047.md`.

## Predecessor closure

`M2-M1-046` / PR #163 is merged at exact `main` SHA `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`. Remote `main` was read back at that SHA and push CI #657 completed successfully. Current indexed evidence coverage, replay/dedup integrity, deterministic exception disposition and bounded live receipt/event linkage are therefore integration-verified at the repository/live-readback ceilings recorded by that packet.

## Why this packet is next

`FIN-CANON-AUDIT-001` has one explicit remaining blocker: the connected financial provider exposes history predating the lower bound of the current canonical FinOps projection, while the live control surface still labels that gap `OPEN HISTORICAL BACKFILL`.

That contradiction must be resolved before MIRA can claim the canonical finance audit is complete. The correct next step is to measure the provider history and either backfill it through stable provider identity or encode an intentional durable historical boundary. Starting recurring/background reconciliation first would merely preserve an undefined truncation forever, a classic human achievement in turning a small data problem into archaeology.

## Customer outcome

Financial Escape must have an explicit, evidence-backed historical boundary. Provider money history and canonical projection coverage may differ only when a durable policy says so. Any backfill must preserve:

- one economic effect per canonical event lineage;
- stable provider transaction identity;
- transfer/payment/refund/income semantics;
- existing user overrides, evidence and asset relationships;
- exact readback and zero duplicate/broken-graph invariants;
- no private provider data in public Git.

## Collision review

- Draft PR #135 / `M2-M1-020` owns reusable Google Sheets control-surface implementation; this packet will not duplicate its renderer/control-surface code.
- Draft PR #160 remains Studio/local-worker work and does not displace this final canonical-finance blocker without explicit customer reprioritization.
- No broad schema rebuild or destructive migration is authorized. Historical work is additive/reconciliatory over existing identity.

## Acceptance state

1. Verify predecessor merge and exact post-merge CI. **PASS — `main` `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`, CI #657 green.**
2. Re-read linked-account coverage/freshness before historical conclusions. **PENDING.**
3. Quantify provider history before the canonical projection lower bound. **PENDING.**
4. Compare every bounded pre-projection provider source identity against existing canonical transaction/event identity before write. **PENDING.**
5. Separate true missing history from replay, transfer/payment, income and other non-spend semantics. **PENDING.**
6. Execute the smallest safe backfill or encode an explicit durable boundary with exact readback. **PENDING.**
7. Re-run duplicate event/evidence/entity/relation and broken-endpoint invariants. **PENDING.**
8. Update the live historical-boundary disposition and determine whether `FIN-CANON-AUDIT-001` is closable. **PENDING.**
9. Public Git contains sanitized evidence only. **PASS so far.**

## Session-start alignment verification — 2026-09-13

### `FEATURES.md`

This packet advances existing canonical finance and recovery/integrity semantics. It does not create another finance authority, another evidence graph or a new historical-storage feature.

### `BACKLOG.md`

`FIN-CANON-AUDIT-001` remains the active blocker. The pre-projection provider-history gap is an existing acceptance defect inside that work ID, not a new feature or parallel backlog item.

### `ROADMAP.md`

Direction remains ordinary-language MIRA backed by canonical state, stable identity, provider-specific authority, explicit provenance/readback and fail-closed uncertainty. Historical scope must be explicit before recurring automation can be trusted.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- The only newly active work is the already-recorded pre-projection history blocker from `FIN-CANON-AUDIT-001`.
- No recurring scheduler/runtime work is admitted early.
- No private historical values or identifiers are committed.
- No unrelated feature is admitted.

### Direction result

ALIGNED

## Exact next action / resume point

1. Re-read linked-account coverage/freshness.
2. Query provider transactions strictly before the current canonical lower bound.
3. Compare returned source identities to FinOps Ledger and canonical transaction entities before mutation.
4. Classify true missing history versus replay/non-spend semantics.
5. Perform only the smallest safe backfill or explicit boundary update, read it back exactly, and rerun finance/graph invariants.

## Evidence ceiling

`M2-M1-046` is integration-verified at post-merge CI and live Workspace readback ceilings. This packet has not yet refreshed provider history, so no new claim about the size or content of the pre-projection gap is accepted until the provider is queried here.
