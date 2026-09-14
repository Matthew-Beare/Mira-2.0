# MIRA 2.0 CURRENT WORK

Git is authoritative. This checkpoint is reconciled to remote `main` before further work selection.

## Current objective

Continue `FIN-CANON-AUDIT-001` by reconciling the historical provider transaction gap into the existing canonical MIRROR finance graph using stable provider identity, preserved provenance, idempotent replay, and exact readback. Historical source data must not be discarded or hidden behind an artificial MIRA 2.0 start date.

## Reconciled repository state — 2026-09-14

- `M2-M1-046` / finance evidence coverage is merged to remote `main`.
- Verified remote `main` before this checkpoint: `8ed16f9e2b3e2672ff7149488ba0a7d28a4a0222`.
- Post-merge Trusted Runner Gate for that exact head completed successfully.
- The previous CURRENT_WORK checkpoint was stale: it still described M2-M1-046 as active and its merge/CI acceptance gate as pending. That stale state is superseded here.
- Connected Finances transaction coverage reports `full_history`, `ready`, and complete bounded-query coverage; freshness remains `unknown`.
- Direct oldest-row probe proves accessible connected transaction history reaches at least **2024-08-09**, materially earlier than the current canonical finance projection. This is source-coverage evidence only, not yet proof that every historical row has been projected into MIRROR.

## Customer priority / sequencing

1. Close or durably bound the historical finance projection gap first. Because the connected source demonstrably exposes older history, an artificial product start boundary is not acceptable.
2. Preserve source evidence/provenance and stable provider transaction identity. Reconciliation may add canonical entities/relations/events but must not duplicate economic effects or overwrite older production data.
3. Explicitly represent any genuine unavailable source gaps if discovered.
4. After historical finance coverage is closed or bounded by actual source unavailability, move to the user-visible Android inventory/scanning vertical using existing `INV-001`, `INV-002`, `MOVE-001`, `IDENT-001`, `ASSET-001`, `ASSET-002`, `ASSET-003` and the existing Android client architecture. Do not create a parallel inventory model.

## Acceptance gates for the historical finance continuation

1. Inventory the actual connected historical range per relevant account/source rather than assuming a date boundary.
2. Compare provider stable transaction identities against canonical MIRROR finance event/source identities.
3. Project every supported missing historical provider event exactly once, preserving source provenance and current category/interpretation rules without converting evidence authorities into money authorities.
4. Preserve ambiguous/unresolved semantic classification as reviewable state rather than guessing.
5. Exact readback proves no duplicate event IDs, evidence IDs, entity IDs or relation IDs and no broken relation endpoints.
6. Exact readback proves the historical provider identity set is either represented in canonical MIRROR or explicitly accounted for by a documented source-unavailability/exclusion reason.
7. Public Git stores only sanitized coverage/proof, never private balances, account/provider IDs, transaction IDs, receipt contents, addresses or secrets.
8. Repository CI must pass at exact head and again after merge before the objective is called complete.

## Environment ceiling / resume point

This runtime can read connected Finances and GitHub directly, but no canonical MIRROR/Google Sheets mutation connector is currently loaded in this run. Therefore the next executable step is to use the available canonical-state connector when present to compare the provider historical identity set against MIRROR and perform idempotent backfill with exact readback. Do not infer completion merely from provider full-history coverage.

## Canonical six-line status

Objective: Reconcile all accessible historical finance transactions into the existing canonical MIRROR finance graph without duplicate economic effects.
Progress: M2-M1-046 merge/CI was verified, stale CURRENT_WORK was reconciled, and connected history was directly proven to reach at least 2024-08-09.
Last 24h: Finance evidence coverage was merged and post-merge CI passed while preserving the explicit historical projection blocker.
Deliverable: Exact historical provider-to-MIRROR coverage proof plus idempotent backfill of every supported missing transaction.
Expected delivery: UNKNOWN.
Blocker: Canonical MIRROR mutation/readback connector is not loaded in this runtime; continue immediately when that connected state surface is available.
