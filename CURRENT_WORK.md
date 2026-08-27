# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-004C` — Feature Audit Slice C3 — optional subscriptions/full-finance direction and category-C closure

- **Merged PR:** #9
- **Merge SHA:** `4377674edac8eca5c5ac1f9272c1157701564d9d`
- **Audited features:** `SUB-001`, `FIN-001`
- **Result:** category C is complete; optional/deferred finance directions remain at their actual evidence levels.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-005A`
- **Name:** Feature Audit Slice D1 — asset identity and evidence foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Objective:** Audit the first five asset/evidence capabilities as stable feature records, preserving identity, fitment, provenance, bidirectional query and identifier boundaries without entering inventory-location/movement scope.

## Audit rows in this packet

1. Stable asset identity and item-to-vehicle/equipment fitment.
2. Asset purchase evidence, manuals, warranties, maintenance and verified specifications.
3. Bidirectional receipt/order ↔ asset/vehicle/tool queries.
4. Namespaced UPC/GTIN, merchant SKU, manufacturer part/model, serial, IMEI and MAC identities.
5. Product/serial/barcode photo and Gmail evidence enrichment.

Do not expand this packet to manual discovery/Drive retention as a product workflow, location hierarchy, QR movement, grocery/par sensing, or category-D rows 6-16.

## Acceptance criteria

1. Each scoped behavior receives a stable semantic feature ID and complete evidence-bound feature record.
2. Asset/entity identity is immutable and fitment/assignment relationships remain explicit rather than encoded by changing asset identity.
3. Purchase/evidence/manual/warranty/maintenance/specification relationships are provenance-backed and do not imply all specification verification is complete; the dedicated technical-specification row remains for D2.
4. Bidirectional receipt/asset/identifier query behavior is recorded separately from UI/provider projection.
5. Identifier namespaces, normalization, check-digit/format validation and unique serial-level collision rules are preserved at their audited evidence level.
6. Photo/OCR/mail evidence enriches existing entity/Receipt identity and cannot silently overwrite verified identifiers or create duplicates.
7. Relevant executable/tests/policy and materially relevant PR #31 evidence are inspected without importing private user inventory.
8. `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` are the only intended changed files.
9. A small PR is scope-verified, merged, and remotely read back.
10. `CURRENT_WORK.md` advances to `M2-G0-005B` with exact D2 resume point.
11. No live Google production state and no executable product behavior is changed.

## Exact next action

Create branch `audit/g0-005a-asset-identity-evidence` from current `main`. Inspect category-D row 1: **Stable asset identity and item-to-vehicle/equipment fitment**, including immutable entity/relationship identity, exact source identity, assignment/fitment evidence and idempotent replay. Assign its stable feature ID before moving to row 2.

## Next packet boundary

If D1 completes, `M2-G0-005B` audits category-D rows 6-10: manual discovery/retention, technical-spec provenance, shopping intent separation, immutable inventory IDs, and hierarchical intended/last-moved locations.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
