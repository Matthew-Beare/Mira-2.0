# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-038` — Ordinary-language Studio intake

- **Primary work:** `STUDIO-INTAKE-001`.
- **Primary features:** `STUDIO-001`, `DEV-004`.
- **Related invariants/features:** `DEV-005`, `DEV-007`, `DIST-001`, `SOURCE-001`, `RECOVERY-002`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-038-studio-intake`.
- **Base SHA:** `57f9cfab2976be1d93ccae41d07b497354511552`.
- **Packet:** `docs/work-packets/M2-M1-038.md`.
- **Current status:** PAUSED by explicit customer reprioritization on 2026-09-11 for Financial Escape freshness/reliability repair. No intake implementation has begun; packet-owned runtime files remain uncreated.
- **Owned implementation surfaces:** new `mira/studio_intake.py`, new `tests/test_studio_intake.py`, packet doc, branch-local `CURRENT_WORK.md`, and only the narrow code-ownership registration required for the new module.
- **Shared/high-contention surfaces:** no Google Workspace/Sheets, finance, Android, People Discovery, live provider/source/share adapter, `FEATURES.md`, final graphical Studio UX, or live user data is owned by this packet.

## Prior packet closeout

`M2-M1-037` merged through PR #152 at exact merge SHA `57f9cfab2976be1d93ccae41d07b497354511552`. Post-merge CI #597 / run `34563161435` passed end-to-end, including feature registry, product lifecycle ledger, work-session alignment, code ownership, Android proof build/provenance, Python tests and Workspace Apps Script tests. The backlog now records `SKILL-BUILDER-001` and `FEATURE-SHARE-001` complete at their bounded provider-neutral evidence ceilings, `MIRA-STUDIO-001` partial, and `STUDIO-INTAKE-001` as the next selected child.

## Objective

Implement the stock-ChatGPT/no-app Studio front door so the customer can describe a desired preference, workflow, or capability in ordinary language without supplying internal engineering identifiers.

The customer-facing input is the raw request plus any explicit constraints they actually stated. A host/model may propose a semantic interpretation of that request. Deterministic MIRA code validates the interpretation against the exact canonical `FeatureRegistry`, derives dependency scope, preserves explicit constraints separately from assistant/model assumptions, generates stable intake identity, surfaces material blockers/questions, and decides whether the result is ready for customer review.

This packet does not invoke a model, create an implementation packet/branch, mutate source/provider state, publish/install/share/activate behavior, infer customer approval, or implement final graphical/browser Studio UX.

## Acceptance state

- M2-M1-037 merge `57f9cfab2976be1d93ccae41d07b497354511552`: **integration-verified by post-merge CI #597**.
- Ordinary-language customer request contract: **pending implementation**.
- Host/model semantic interpretation validation: **pending implementation**.
- Exact feature-registry grounding and deterministic dependency derivation: **pending implementation**.
- Explicit customer constraints vs assistant/model assumptions: **pending implementation**.
- Material clarification/blocker state and exactly one next action: **pending implementation**.
- Stable generated intake identity with no customer-supplied packet/work/change/Git/provider identifiers: **pending implementation**.
- Zero implementation/source/share/install/activation authority from intake: **pending implementation**.
- Direct adversarial tests: **pending**.
- Exact-head repository CI: **pending**.
- Live model/provider/source execution: **not claimed and out of scope**.

## Session-start alignment verification — 2026-09-11

### `FEATURES.md`

`STUDIO-001` requires an integrated guided user-facing Studio over bounded preferences/workflows/features with source/dependency awareness and no silent activation. `DEV-004` supplies the bounded private feature-building direction, while `DEV-005` makes the canonical feature registry available for exact scope/dependency grounding. This packet closes the user-facing gap between ordinary-language intent and the already-merged lower-level Studio lifecycle.

### `BACKLOG.md`

`STUDIO-INTAKE-001` is the selected next `MIRA-STUDIO-001` child after M2-M1-037 reconciliation. Skill Builder and Feature Share are already complete at their bounded evidence ceilings, so this packet must compose/reuse them rather than reopen those foundations.

### `ROADMAP.md`

The roadmap prioritizes bounded no-app Personal usefulness. Ordinary-language Studio intake advances that direction without requiring Android, a server, terminal work, hard-coded providers, local compute, or paid model APIs as product dependencies.

### Reuse and boundary review

- `mira.feature_registry` remains the authority for exact feature IDs and feature dependencies.
- `mira.studio` remains the downstream deterministic Studio lifecycle projection after a bounded change exists.
- `mira.studio_competition` and `mira.studio_activation` remain review/approval/execution authorities.
- `mira.feature_share` and `mira.feature_share_transport` remain sharing/import authorities.
- `mira.studio_intake` will own only ordinary-language intake validation, registry grounding, deterministic draft identity, constraint/assumption separation, blocker/question state and review readiness.

### Direction result

ALIGNED

## Displacement checkpoint — 2026-09-11

Customer explicitly reprioritized Financial Escape reliability/freshness before continuing Studio. This packet is intentionally paused without implementation changes. The replacement repair packet is `M2-M1-039`. Resume this packet only after that repair is closed or the customer reprioritizes again.

## Exact next action / resume point

1. Implement `mira/studio_intake.py` with raw request + semantic interpretation contracts, registry grounding, dependency derivation, stable generated draft identity, constraints/assumptions separation, clarification/blocker state and zero execution authority.
2. Add direct adversarial `tests/test_studio_intake.py` for preference/workflow/feature, ambiguity, dependencies, unknown features, replay, malformed input and authority escalation.
3. Register exactly one bounded code-ownership component if required.
4. Run exact-head repository CI and repair only packet-owned failures.
5. Close/merge only from green evidence and verify exact post-merge CI.

## Evidence ceiling

M2-M1-038 may prove deterministic registry-grounded intake/draft behavior only. It does not prove live model interpretation, generated implementation, Git/source mutation, provider I/O, customer approval, activation, sharing/provider publication, imported installation, or final graphical/browser Studio UX.

## Recovery protocol

Resume from remote `main` merge `57f9cfab2976be1d93ccae41d07b497354511552`, branch `work/m2-m1-038-studio-intake`, this file and `docs/work-packets/M2-M1-038.md`. Git, not chat, is authoritative.
