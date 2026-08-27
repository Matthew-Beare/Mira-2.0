# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and its exact resume point.

## Completed packet

### `M2-G0-006F` — Feature Audit Slice E6 — provider onboarding/bootstrap and category-E closure

- **Merged PR:** #19
- **Merge SHA:** `2adf361c86731d76819acc7b24b025c47bb3a730`
- **Audited features:** `PROVIDER-002`, `ONBOARD-007`, `PROVIDER-003`.
- **Result:** all 26 historical category-E rows are accounted for; browser/provider/source/runtime/orchestration boundaries are separated; Personal Google is a deterministic adapter rather than MIRA architecture.
- **Remote readback:** `FEATURES.md` on `main` contains all three E6 features and explicitly marks categories A-E complete.
- **Live Google production touched:** no.
- **Executable product behavior changed:** no.

## Active packet

- **Packet ID:** `M2-G0-007A`
- **Name:** Feature Audit Slice F1 — core life-service module boundaries
- **Class:** forensic audit / prerequisite
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Branch:** `audit/g0-007a-core-life-services`
- **Base merge SHA:** `2adf361c86731d76819acc7b24b025c47bb3a730`
- **Status:** active; branch creation and forensic evidence pass next.

## Exact category-F scope in this packet

Audit exactly the first five rows of legacy category F, **Life-service modules discussed or catalogued**:

1. Briefs/action digest — REQUIRED; executable + skill workflow.
2. Next-action planner — REQUIRED/ACCEPTED; skill workflow.
3. Email triage — REQUIRED; skill workflow.
4. Orders/shipments — REQUIRED; executable + skill workflow.
5. Receipt archive — REQUIRED; skill workflow + partial executables.

Do not expand this packet into personal finance, calendar/reminders, health organization, shopping, meals, household routines or later category-F rows. Do not reopen category A-C behavior semantics unless required to distinguish service-module composition from already-audited behavior features.

## Packet objective

Reconstruct what these first five category-F rows mean as MIRA service modules, map them to existing canonical behavior features without duplicate IDs, identify any missing service-layer contract needed for activation/dependency/failure-isolation/composition, record actual evidence levels and rank only genuine gaps.

Category F is a service-catalog/composition audit, not permission to duplicate earlier behavior features merely because the ledger lists them again under service names.

## Acceptance criteria

1. Account for all five F1 ledger rows with stable semantic mapping.
2. Reuse existing canonical feature IDs where the F row is only a service projection/composition of already-audited behavior; create a new stable feature only if the service layer has distinct behavior/authority not represented elsewhere.
3. Keep service activation (`SERVICE-001`) separate from behavior implementation, provider capability and recommendation.
4. Record each service’s required/optional behavior dependencies and failure-domain boundary.
5. Preserve optional/module failure isolation under `RECOVERY-002`; one unavailable service/provider path must not falsify or disable unrelated service state.
6. Preserve communication safety: email triage cannot imply outbound-send authority.
7. Preserve canonical commerce boundaries: orders/shipments and receipt archive are related services but must not merge fulfillment state, receipt/purchase identity or financial settlement authorities.
8. Record actual legacy implementation/test/workflow evidence and MIRA 2.0 verification gaps without promoting contract/skill prose to executable evidence.
9. Reconcile relevant PR #31 candidates only as evidence/salvage reference; never merge wholesale or inherit integration/live status.
10. Update only `FEATURES.md`, `BACKLOG.md`, and `CURRENT_WORK.md` unless a hard audit dependency requires another authority-file change.
11. Open a bounded PR, verify changed-file scope, merge and remotely read back before advancing to F2.
12. Touch no live Google production state and change no executable MIRA 2.0 product behavior.

## Exact next action

Create branch `audit/g0-007a-core-life-services` from this exact activation commit. Then inspect the legacy service/module catalog, behavior dependency database, installable MIRA skill/service activation router and tests for F row 1 **Briefs/action digest**. Determine whether F row 1 is fully represented by `OPS-*` + `SERVICE-001` or whether a distinct service-composition feature exists before proceeding to row 2.

## Next packet after F1

### `M2-G0-007B` — Feature Audit Slice F2

Begin with category-F row 6 **Personal finance organization** and continue only through the next bounded coherent service slice determined during F1 closure. Do not pre-expand F2 from memory.

## Recovery protocol

On any new conversation/session:
1. read this file first;
2. verify repository/branch/head when tools permit;
3. continue from the exact next action;
4. do not broaden scope from chat history;
5. capture new customer ideas in BACKLOG unless required for acceptance or explicitly reprioritized;
6. before the final packet line, state any customer action needed; if none is needed, use `Just tell me to continue.`;
7. the final visible line remains the packet recovery tag.
