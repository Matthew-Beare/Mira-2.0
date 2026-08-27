# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Active packet

- **Packet ID:** `M2-G0-005B`
- **Name:** Feature Audit Slice D2 — knowledge/spec/shopping/location foundations
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-005b-knowledge-spec-location`
- **Base main SHA:** `f41bb7f340e3d708e8ceff1f5178da3e209cf658`
- **Feature audit commit:** `abf0d204c1c1a7cb564030969ea47d3db50e7872`
- **Backlog checkpoint commit:** `02746b48acb4d2c9b2918021224afccf214e6a94`
- **Status:** acceptance work complete; PR/merge/readback pending.

## Completed acceptance evidence

1. Assigned five stable semantic features for category-D rows 6-10:
   - `KNOW-001` Canonical manual/reference knowledge identity and retained-document lifecycle;
   - `SPEC-001` Provenance-locked technical specifications with exact applicability;
   - `SHOP-001` Active shopping intent distinct from durable purchase history;
   - `INV-001` Inventory participation reuses canonical Entity UUID identity;
   - `LOC-001` Hierarchical locations with intended placement separate from observed/last-moved state.
2. Added dedicated `KNOW-*`, `SPEC-*`, `SHOP-*` and `LOC-*` feature-ID families so those authorities are not hidden under overloaded asset/inventory labels.
3. Recorded manuals/references as immutable Knowledge UUID objects with source identity, revision/edition, retained-file identity and honest queued/blocked/unavailable states.
4. Verified deterministic Knowledge validation for retained Drive identity/revision requirements, queued-without-retention behavior, unknown Knowledge relationship rejection and lookup-state progression.
5. Kept actual MIRA 2.0 Drive file/index writes below integration verification; added `KNOWLEDGE-INTEGRATION-001` for sandbox provider readback.
6. Recorded `SPEC-001` safety-critical verification boundary: exact subject Entity UUID/applicability, OEM/manufacturer/authoritative-regulatory source tier, source URL or retained Knowledge UUID, page/section locator and revision/version.
7. Verified deterministic specification tests reject owner-memory source tier, missing source locator, missing authoritative source link and silent mutation of an already verified value.
8. Added `SPEC-INTEGRATION-001` because provider/document readback remains unverified even though the specification validator core is test-verified.
9. Recorded `SHOP-001` as active mutable procurement intent only; durable purchases remain under `RECEIPT-*`/`ORDER-*`, and shopping state cannot become a second spend/purchase ledger.
10. Kept `SHOP-001` below `test_verified` because no dedicated deterministic shopping reconciliation suite was located; added `SHOP-CORE-001` for exact/ambiguous match, owner-confirmed fulfillment, cancellation, replacement, partial fulfillment, replay and deletion/readback behavior.
11. Recorded `INV-001` as a projection/state participation rule that reuses `ASSET-001` canonical Entity UUIDs instead of inventing a second inventory primary identity. Friendly IDs, QR labels, shelf labels and serial/vendor identifiers remain aliases/identifiers.
12. Inspected PR #31 `inventory_hierarchy.py` as unmerged salvage/reference evidence only. It contains nested location paths, container-location linkage and cycle/self-location protections but does not earn MIRA 2.0 implementation credit.
13. Recorded `LOC-001` intended/canonical placement separately from current/last-observed or moved-to state. Neither fact silently rewrites the other.
14. Added `LOCATION-STATE-001` for stable Location UUID hierarchy, cycle/container behavior and explicit intended-versus-observed movement semantics.
15. Touched no live Google production state and changed no executable product behavior.

## Key audit findings

- Manuals/reference documents are canonical Knowledge objects, not attributes stuffed onto an asset row.
- A verified technical specification is a provenance-locked fact for an exact subject/configuration, not merely extracted text.
- Shopping intent, purchase history and inventory ownership are three different state domains.
- Inventory does not need another physical-item identity system; the canonical Entity UUID survives every inventory projection.
- “Where this belongs” and “where it was last observed/moved” are different facts. PR #31 implements useful hierarchy primitives but not that complete semantic contract.

## Blockers

None inside the forensic packet. `SHOP-CORE-001`, `LOCATION-STATE-001`, `KNOWLEDGE-INTEGRATION-001`, and `SPEC-INTEGRATION-001` are separately ranked implementation/integration work.

## Exact next action

Open a pull request from `audit/g0-005b-knowledge-spec-location` to `main`, verify changed-file scope is limited to `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md`, merge it, remotely read back the merged D2 state, then activate `M2-G0-005C` on current `main` and create its audit branch.

## Next packet after merge

### `M2-G0-005C` — Feature Audit Slice D3 — inventory movement, query, par and grocery foundations

Audit exactly category-D rows 11-15:

1. QR/barcode scan-in and scan-out.
2. Queryable household/loft/shop inventory.
3. Consumable/grocery par levels and under-level notification.
4. Optional scale-based par sensing.
5. Grocery list/pantry/freezer flows.

Do not expand this packet to recipes/meal planning/category-D row 16, profiles/onboarding, Android implementation, RFID hardware, Home Assistant implementation or product coding.

The exact first unaudited behavior is **QR/barcode scan-in and scan-out**.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
