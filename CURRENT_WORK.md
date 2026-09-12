# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-038` — Ordinary-language Studio intake

- **Primary work:** `STUDIO-INTAKE-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`.
- **Related invariants/features:** `DEV-005`, `DEV-007`, `DEV-008`, `DIST-001`, `SOURCE-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-038-studio-intake`.
- **Current reconciliation base:** `2cd46d95bb7aeb1b732753707ba61bf9667346f4` (`main` after M2-GOV-002).
- **Preserved pre-repair checkpoint:** `3f8d52b2904891b5b9677ec26d64978afb4e4afa` on `checkpoint/m2-m1-038-pre-financial-repair`.
- **Preserved pre-reconciliation implementation head:** `f3d22a1b8451fd0092c926776a106715926c8f8f`.
- **Packet:** `docs/work-packets/M2-M1-038.md`.
- **Pull request:** `#153`.
- **Current status:** ACTIVE. Deterministic Studio intake implementation and adversarial tests already exist on the preserved branch. This checkpoint reconciles that work onto the current verified `main` without force-rewriting history; exact-head CI on the reconciled merge state is still required.
- **Owned implementation surfaces:** `mira/studio_intake.py`, `tests/test_studio_intake.py`, packet doc, branch-local `CURRENT_WORK.md`, and one bounded `studio-intake` code-ownership registration.
- **Shared/high-contention surfaces:** `CURRENT_WORK.md` and `project/code_ownership.json`; no Google Workspace/Sheets, finance, Android, People Discovery, live provider/source/share adapter, final graphical Studio UX, or live user data is owned by this packet.

## Intervening packet closure evidence

The packet was interrupted by reliability/governance work and is resumed only after exact integration verification:

- `M2-M1-039` / PR #154 merged at `6551691c7836a9c70a8be080cd11bb2ee18536d2`; its Financial Escape repair remains fail-closed beyond verified provider/readback evidence.
- `M2-M1-040` / PR #155 merged at `e6e6135837278b094de6ceb495736010a650af52`; post-merge CI #612 passed. Mutable shipment facts now require live fact-specific authority when reachable and durable non-consumables use a fail-closed receipt-to-inventory completion contract.
- `M2-GOV-002` / PR #156 merged at `2cd46d95bb7aeb1b732753707ba61bf9667346f4`; exact post-merge CI #615 passed. `DEV-008` / `IDEA-CAPTURE-AUDIT-001` now require explicit durable idea/backlog capture audits and fail work-session alignment closed when the audit evidence is absent or incomplete.

The original Studio implementation head `f3d22a1b8451fd0092c926776a106715926c8f8f` is preserved as a parent of the reconciliation merge. No Studio implementation is reconstructed from chat.

## Objective

Implement the stock-ChatGPT/no-app Studio front door so the customer can describe a desired preference, workflow, or capability in ordinary language without supplying internal engineering identifiers.

The customer-facing input is the raw request plus any explicit constraints they actually stated. A host/model may propose a semantic interpretation of that request. Deterministic MIRA validates the interpretation against the exact canonical `FeatureRegistry`, derives transitive dependency scope, preserves explicit constraints separately from assistant/model assumptions, generates stable intake identity, surfaces material blockers/questions, and decides whether the result is ready for customer review.

This packet does not invoke a model, create an implementation packet/branch from intake, mutate source/provider state, publish/install/share/activate behavior, infer customer approval, or implement final graphical/browser Studio UX.

## Implemented behavior on preserved branch

- `StudioIntakeRequest` accepts only ordinary-language request text plus explicit customer constraints.
- `StudioSemanticInterpretation` carries validated change kind, desired outcome, feature scope, customer-constraint echo, model assumptions, unresolved questions, conflicts and authority claims.
- Selected feature IDs must exist in the exact canonical FeatureRegistry; unknown scope fails closed.
- Dependency scope is derived deterministically and transitively from canonical feature dependencies rather than trusted from model prose.
- Explicit customer constraints and assistant/model assumptions remain separate; mismatches or masquerading assumptions fail closed.
- Material unresolved questions create deterministic blockers and exactly one clarification next action; otherwise the draft becomes review-ready.
- Stable `intake-<sha256>` identity binds normalized request/interpretation evidence to the exact registry SHA.
- Intake cannot authorize implementation, source mutation, publication, installation, approval or activation.
- Direct tests cover feature, workflow and preference intake; dependencies; ambiguity; constraint/assumption separation; unknown scope; replay; registry revision binding; authority escalation; malformed/control-character input; and canonical internal evidence ordering.

## Acceptance state

1. Ordinary-language customer request contract: **IMPLEMENTED on preserved branch; reconciled-head CI pending.**
2. Host/model semantic interpretation validation: **IMPLEMENTED; reconciled-head CI pending.**
3. Exact feature-registry grounding and transitive dependency derivation: **IMPLEMENTED; reconciled-head CI pending.**
4. Explicit customer constraints vs assistant/model assumptions: **IMPLEMENTED; reconciled-head CI pending.**
5. Material clarification/blocker state and exactly one next action: **IMPLEMENTED; reconciled-head CI pending.**
6. Stable generated intake identity with no customer-supplied packet/work/change/Git/provider identifiers: **IMPLEMENTED; reconciled-head CI pending.**
7. Zero implementation/source/share/install/approval/activation authority from intake: **IMPLEMENTED; reconciled-head CI pending.**
8. Direct adversarial tests: **IMPLEMENTED; reconciled-head CI pending.**
9. Exact-head repository CI after current-main reconciliation: **PENDING.**
10. Live model/provider/source execution: **not claimed and out of scope.**

## Session-start alignment verification — 2026-09-12 resumed after reliability/governance interruptions

### `FEATURES.md`

`STUDIO-001` requires an integrated guided user-facing Studio over bounded preferences/workflows/features with source/dependency awareness and no silent activation. `DEV-004` supplies the bounded private feature-building direction, while `DEV-005` keeps canonical feature identity/dependency grounding authoritative. `DEV-007` requires packet/product alignment and `DEV-008` now requires explicit idea/backlog capture evidence. This packet closes the user-facing gap between ordinary-language intent and the already-merged lower-level Studio lifecycle without inventing another feature family.

### `BACKLOG.md`

`STUDIO-INTAKE-001` already exists as the selected next `MIRA-STUDIO-001` child, so the resumed Studio work reuses that stable work ID rather than creating a duplicate. `IDEA-CAPTURE-AUDIT-001` is integration-verified by M2-GOV-002 / PR #156 / main CI #615; its textual lifecycle status in BACKLOG is stale and must be reconciled at the next safe shared-governance write rather than ignored or used to create duplicate work.

### `ROADMAP.md`

The roadmap prioritizes bounded no-app Personal usefulness. Ordinary-language Studio intake advances that direction without requiring Android, a server, terminal work, hard-coded providers, local compute, or paid model APIs as product dependencies.

### Idea/backlog capture audit

CAPTURE AUDIT COMPLETE

- Material ideas reviewed: the ordinary-language Studio intake capability plus the customer's newly enforced continuous capture-audit requirement.
- Studio intake is already represented by `STUDIO-001`, `DEV-004`, and `STUDIO-INTAKE-001`; no duplicate Studio feature/work ID was created.
- Continuous capture auditing is already represented by `DEV-008` / `IDEA-CAPTURE-AUDIT-001` and is integration-verified on current `main`.
- No new material product idea was introduced by reconciling the preserved Studio implementation with current `main`.
- Packet-scope result: unchanged and bounded; capture/audit compliance does not authorize additional Studio implementation.

### Reuse and boundary review

- `mira.feature_registry` remains the authority for exact feature IDs and dependencies.
- `mira.studio` remains the downstream deterministic Studio lifecycle projection after a bounded change exists.
- `mira.studio_competition` and `mira.studio_activation` remain review/approval/execution authorities.
- `mira.feature_share` and `mira.feature_share_transport` remain sharing/import authorities.
- `mira.studio_intake` owns only ordinary-language intake validation, registry grounding, deterministic draft identity, constraint/assumption separation, blocker/question state and review readiness.
- Financial Escape, shipment tracking and receipt/inventory live surfaces remain out of scope for this packet even though their reliability repairs are now present on the reconciliation base.

### Direction result

ALIGNED

## Exact next action / resume point

1. Create a non-force two-parent reconciliation merge preserving `f3d22a1b8451fd0092c926776a106715926c8f8f` and current `main` `2cd46d95bb7aeb1b732753707ba61bf9667346f4`, with current-main governance plus the Studio implementation/test/ownership surfaces.
2. Read back PR #153 head/mergeability and require exact-head CI green, including the new DEV-008 capture-audit alignment gate.
3. If CI exposes only packet-owned defects, repair them without weakening gates; if current-main semantics conflict, preserve both histories and reconcile explicitly.
4. Before merge, repeat the idea/backlog capture audit and current-main/PR-overlap check.
5. Merge only with expected-head protection, then read back exact post-merge `main` and CI/status before claiming integration verification.
6. Reconcile stale lifecycle text in `BACKLOG.md` (`IDEA-CAPTURE-AUDIT-001` complete; `STUDIO-INTAKE-001` current/complete as evidence permits) on a safe shared-governance write rather than manufacturing duplicate IDs.

## Evidence ceiling

M2-M1-038 may prove deterministic registry-grounded intake/draft behavior only. It does not prove live model interpretation, generated implementation beyond this deterministic intake boundary, Git/source mutation from intake, provider I/O, customer approval, activation, sharing/provider publication, imported installation, or final graphical/browser Studio UX.

## Recovery protocol

Resume from branch `work/m2-m1-038-studio-intake`, preserved implementation head `f3d22a1b8451fd0092c926776a106715926c8f8f`, current reconciliation base `2cd46d95bb7aeb1b732753707ba61bf9667346f4`, this file and `docs/work-packets/M2-M1-038.md`. The original pre-repair checkpoint remains `3f8d52b2904891b5b9677ec26d64978afb4e4afa`. Git, not chat, is authoritative.
