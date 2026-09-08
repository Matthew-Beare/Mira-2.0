# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Other MIRA packet branches may progress independently under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-020` — Google Sheets operational control-surface foundation

- **Primary work:** `SHEETS-CONTROL-001`.
- **Primary features:** `SHEETS-001`, `STUDIO-001`.
- **Related invariants/features:** `MIRROR-001`, `AUTH-001`, `STORE-001`, `RECOVERY-002`, `DATA-001`, `DIST-001`, `DIST-002`, `DEV-004`, `DEV-005`, `OBS-001`, `CAREER-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-020-sheets-control-surface`.
- **Base SHA:** `d4ede63db07de48504bbce2f0c5296c3a1614647`.
- **Base tree:** `96fade8b7f89a15f369cea3bf821f3c83d724b8b`, identical in content to pre-cleanup `main` tree `738ebf082cd3921a0ba807604acabfa756f40c1d`.
- **Packet:** `docs/work-packets/M2-M1-020.md`.
- **Owned implementation surfaces:** new reusable Sheets control-surface/projection/reconciliation modules and tests; packet docs; generic synthetic feature definitions.
- **Shared/high-contention surfaces:** `FEATURES.md`, `BACKLOG.md`, `project/code_ownership.json`, branch-local `CURRENT_WORK.md`; reconcile against then-current `main` before merge.
- **Current status:** active feature intake + foundation implementation. No legacy/private Google resource is authorized as a development fixture.

## Objective

Implement a reusable Google Sheets-first operational control-surface layer that exposes MIRROR-backed domains for filtering, review, correction, reconciliation, dashboards and prototyping without turning Sheets into a second authority. Use that shared layer as the foundation for modular Job Search/market boards, People Discovery integration, Finance Operations telemetry, Vehicle Operations, Inventory Operations, MIRA Operations visibility and safe prototype-to-MIRROR promotion. Keep the features Studio/package/sanitization ready.

## Customer-approved downstream feature family

The uploaded directive is accepted product direction and is being normalized into existing MIRA semantics rather than copied as ten isolated spreadsheet systems:

1. reusable Job Search core;
2. reusable People Discovery integrated with jobs/employers/interactions and no automated outreach;
3. Dallas/DFW configured market board;
4. Austin configured market board;
5. RTP/Raleigh-Durham configured market board;
6. Finance Operations transaction telemetry including mandatory `drawdown category` and `necessary vs unnecessary` classifications;
7. Vehicle Operations over canonical assets/parts/specs/receipts/service evidence;
8. Inventory Operations over canonical asset/inventory/location/par/reorder state;
9. MIRA Operations read-only dashboard over Git/MIRROR/provider/automation evidence;
10. visibly non-authoritative Sheets modelling/prototyping workflow with explicit promotion/reconciliation/retirement;
11. reusable automation, Studio lifecycle and sanitization/export support across the above;
12. optional local coding-worker lane to reduce expensive-model iteration cost while preserving Git/CI/review authority.

Education/course/certification/study-progress/skills-gap tracking remains explicitly out of scope for this feature family. Existing discovered-person fields such as a credential or school affiliation may remain evidence on a person record where legitimately returned; that does not create an education-tracking subsystem.

## Local coding-worker direction

Use existing `PROVIDER-001`, `LOCAL-001`, Git governance and bounded packet semantics rather than inventing a separate development authority. First model target for evaluation is NVIDIA `Llama-3.3-Nemotron-Super-49B-v1.5` or a suitable lower-precision derivative, served through a replaceable local OpenAI-compatible endpoint when hardware/runtime evidence supports it.

The local worker may perform bounded repo analysis, code drafts, tests, refactors, boilerplate and documentation on an isolated branch/worktree. It must not independently merge/push to protected integration refs, approve its own work, mutate live providers, access undeclared secrets, weaken public-repository privacy, or claim live verification. MIRA/ChatGPT review + repository tests/CI remain the acceptance boundary.

## Sheets control-surface contract to implement

Every Sheet/range/view must declare exactly one role:

- canonical read-only projection;
- controlled editable projection;
- derived analytical view;
- temporary non-authoritative prototype;
- reconciliation queue;
- generated dashboard.

Controlled editable projections must declare canonical owner, stable row identity, allowed editable fields, validation/controlled vocabularies, source revision/read timestamp, write-back command/path, conflict detection, provenance, reconciliation state, retry/failure behavior and exact post-write readback. MIRA never silently overwrites a conflicting human edit.

Sheets formulas/visual features may provide sorting, filtering, dashboards, pivots, charts, slicers, conditional formatting and lightweight derived analysis, but durable identity, provenance, dedupe, canonical classification and domain business rules stay in MIRA/MIRROR.

## Acceptance state

- `M2-M1-019` People Discovery displaced with exact recovery checkpoint: **satisfied at remote `60f09dc96e1324a7832511b1374f5aa673bdd1ec`**.
- New isolated packet branch from verified `main`: **satisfied**.
- Packet document: **created**.
- Uploaded feature family captured in branch-local durable recovery state: **satisfied**.
- Existing feature/domain dedupe audit: **in progress**.
- Canonical `FEATURES.md` / `BACKLOG.md` registration: **pending**.
- Current Google Sheets/API/Apps Script capability and limit audit: **in progress**.
- Reusable Sheets projection/reconciliation implementation: **pending**.
- Direct synthetic tests: **pending**.
- Code ownership registration: **pending implementation files**.
- Exact-head CI: **pending**.
- Live Google proof: **not yet attempted; no private resource needed for synthetic foundation**.

## Additional high-value Sheets ideas

Maintain this section as implementation discovers useful ideas. Initial candidates to evaluate rather than blindly adopt:

- action/reconciliation queues that expose only allowlisted human decisions while keeping raw canonical state read-only;
- source hyperlinks/deep links from human rows back to canonical evidence, Git PRs, receipts/manuals, professional profiles or provider resources;
- per-feature generated filter views/slicers from declarative configuration instead of hand-maintained copies;
- compact `Data Health` views showing stale, missing, conflicting and low-confidence rows across domains;
- feature-owned protected technical tabs/ranges with user-facing console tabs separated from transport metadata;
- formula-light dashboards fed by MIRA-computed analytical columns so expensive or integrity-sensitive logic is testable outside Sheets;
- reusable market-board factory that changes geography/employers/thresholds through configuration rather than formulas/code forks.

## Exact next action / resume point

1. Reconcile requested capabilities against existing stable features and register only genuinely missing feature IDs/work IDs.
2. Inspect current official Google Sheets/API/Apps Script capabilities and quotas that materially constrain this design.
3. Inspect existing `google_sheets_store.py`, Workspace/native client, distribution/Studio foundations and code-ownership conventions.
4. Implement the smallest provider-neutral Sheets control-surface definition/reconciliation core and deterministic tests.
5. Demonstrate two synthetic domain projections through the same contract.
6. Register downstream packets and the optional local coding-worker work item.
7. Run feature registry, lifecycle, alignment, code ownership and Python tests; fix exact-head failures.
8. Update this file with completed evidence, limitations, additional high-value Sheets ideas and exact next packet.

## Session-start alignment verification — 2026-09-08

### `FEATURES.md`

Reviewed. Existing `STUDIO-001`, `DEV-004`, `DIST-001`/`DIST-002`, `STORE-001`, `AUTH-001`, `OBS-001`, `CAREER-001`, finance, asset and inventory features cover substantial portions of the uploaded direction. This packet will extend rather than duplicate those semantics. A new shared Sheets control-surface feature is justified because multiple accepted domains require the same human projection/edit/reconciliation contract.

### `BACKLOG.md`

Reviewed. Existing work contains Sheets storage/Workspace foundations and multiple domain implementations, but no reusable cross-domain operational Sheets control-surface/reconciliation work item and no local coding-worker acceleration lane. Those are being registered here together with downstream domain-specific projection/configuration packets.

### `ROADMAP.md`

Reviewed. A Sheets-first human control surface preserves the existing Personal Google direction and provider-neutral MIRROR authority. The local coding worker is development acceleration only and does not change ordinary-user deployment requirements.

### Direction result

ALIGNED

## Recovery protocol

Resume by reading current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-020.md`, remote branch head and active PR/packet branches for shared-file overlap. Git is authoritative; private Sheets/provider data never belongs in public Git.
