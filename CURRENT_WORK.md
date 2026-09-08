# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active/recovery packet. Other MIRA packets may progress independently on isolated branches under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-019` — People Discovery vertical slice

- **Primary work:** `PEOPLE-DISCOVERY-001`.
- **Primary features:** `CAREER-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `MAIL-002`, `DATA-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-019-people-discovery`.
- **Base SHA:** `738ebf082cd3921a0ba807604acabfa756f40c1d`.
- **Packet:** `docs/work-packets/M2-M1-019.md`.
- **Owned implementation surfaces:** People Discovery domain/provider/tracker/Sheets-projection modules and tests; packet-specific synthetic fixtures/docs.
- **Shared/high-contention surfaces:** `FEATURES.md`, `BACKLOG.md`, `project/code_ownership.json`, branch-local `CURRENT_WORK.md`; reconcile against then-current `main` immediately before merge.
- **Current status:** durable implementation checkpoint, temporarily displaced by the customer-prioritized reusable Sheets operational-control foundation packet. Candidate normalization/identity/scoring/provenance, canonical relationship interaction/reply tracking, bounded search-only People Data Labs adapter, Google tracker projection, synthetic tests, canonical backlog registration and code ownership are implemented. Exact-head CI reaches Python tests but has one scoring failure described below. No live third-party people data has been written and no outbound-contact action exists.

## Objective

Deploy a first-class MIRA job-seeking feature that repeatedly discovers useful professional contacts at active target employers, with configurable market/employer/role priorities; normalize, deduplicate, score and retain provenance; maintain a Google Sheets human-facing tracker; track manual outreach and incoming replies/follow-ups; and never perform automated outreach.

The feature must remain publicly sanitizable. Public Git contains implementation, schemas, tests and synthetic fixtures only. Private third-party people data, provider credentials, live spreadsheet identifiers, actual message contents and personal job-search state remain outside the repository.

Do not name or frame this feature as "2-hour job search", `2HJS`, or similar shorthand. It is MIRA Career / People Discovery functionality.

## Relationship and messaging semantics

Canonical interaction history records channel, direction, kind, timestamp, outcome, optional private summary/source reference, reply linkage and follow-up due date. Relationship state is derived from history rather than maintained as an independent truth column. MIRA must be able to answer whether a person has been contacted, which channel was used, the last interaction, whether they replied, whether the user is awaiting a reply or owes a follow-up, and which company/job the interaction concerned.

Implemented branch module: `mira/people_tracker.py`.

The tracker exposes no `send`, `send_message`, `send_email`, `connect`, `post`, or `comment` operation. Human-performed outreach may be recorded after it happens; incoming replies may be recorded or later observed through an authorized provider path.

## Hard boundaries

- No automated email, LinkedIn connection request/message, comment, post, or other contact action.
- No unauthorized LinkedIn scraping, login automation, or browser scraping.
- LinkedIn URLs may be stored when returned by legitimate providers/public sources.
- One logical MIRROR authority. Google Sheets is a projection/bounded controlled-input surface, not a second conflicting truth store.
- Public Git contains synthetic examples only; private people/message/provider/workbook state stays private.
- Uncertain identity matches fail closed rather than silently merging people.
- The feature must be sanitizable and publicly publishable without leaking customer/provider data.

## Provider decision state

- People Data Labs Person Search remains the leading first adapter for the live proof because it supports employer, education/school, title, location, skills, work-history and profile dimensions needed by the current discovery strategy.
- A bounded injected-credential PDL search adapter is implemented with explicit per-run request/record caps, a WGU-first query phase and broader target-employer fallback phase. It exposes search only.
- Apollo remains an optional replaceable secondary adapter and is not required before independent implementation can continue.
- The user does not need to connect both providers.
- If a provider credential remains the only external boundary after implementation/CI, request the smallest single action required for the first live proof.

## Acceptance state

- Unique packet/branch isolated from other MIRA work: **satisfied**.
- Existing Sheets/canonical-state architecture inspected: **satisfied; reusable structured-state and Google Sheets gateway confirmed**.
- Provider-neutral candidate model/normalization: **implemented**.
- Conservative entity resolution/dedupe: **implemented**.
- Relevance scoring with configurable employer/role/technical/WGU weighting: **implemented; one current-role relevance defect remains**.
- Provenance retention: **implemented**.
- Canonical manual interaction history and derived reply/follow-up state: **implemented**.
- No outbound-send API in relationship tracker/provider: **implemented with synthetic tests**.
- Google tracker schema/projection for `COMPANIES` / `PEOPLE` / `INTERACTIONS` / `JOBS`: **implemented with stable-ID upsert, duplicate-ID fail-closed behavior, zero-write identical replay and exact post-write readback tests; live Sheet proof pending**.
- Bounded People Data Labs provider adapter: **implemented; credential/live proof pending**.
- Canonical backlog registration + production code ownership: **implemented on branch**.
- Real provider operational: **pending credential/preflight/live proof**.
- Exact live tracker readback and manual interaction-state live proof: **pending**.
- Public sanitization audit: **pending final branch audit**.
- Exact-head CI: **failing one Python test on head `ac8f06b21160c9d25f6dabbfb3e65d575cb00dfe`; all earlier CI gates pass through code ownership/Android build**.

## Exact CI defect / resume point

Exact-head CI run `34183687209` reaches the Python test suite and reports 491/492 passing. The only failure is:

`PeopleDiscoveryCoreTests.test_unrelated_executive_is_penalized_not_promoted_by_company_alone`

The synthetic candidate is currently `Chief Marketing Officer` with marketing-only current skills but a historical `Network Technician` role. `_technical_strength()` currently treats any historical technical title as current technical relevance, preventing the expected `weak technical relevance` penalty.

**Exact repair:** change current technical-relevance scoring so current-role/current-skill evidence determines the `technical_relevance` factor/penalty; historical technical roles remain available for experience/progression/context but do not by themselves promote an unrelated current executive role. Re-run direct People Discovery tests, then exact-head CI.

## Exact next action / resume point

1. Apply the current-vs-historical technical-relevance scoring repair above; do not weaken the test.
2. Re-run direct People Discovery tests and exact-head CI.
3. Complete canonical People Discovery persistence and live Google tracker writer/readback using the shared Sheets projection/reconciliation foundation once available rather than duplicating it locally.
4. Keep PR #134 draft until implementation tests, provider boundary and live tracker proof are earned.
5. Perform provider capability/credential preflight only after independent implementation is green.
6. If the only remaining boundary is a PDL API key/account, request exactly that single user action; Apollo remains optional.
7. Execute real discovery, real Sheet write/readback, rerun-update proof and manual interaction/reply proof before claiming deployment.
8. Reconcile shared `FEATURES.md`/`BACKLOG.md`/ownership changes against then-current `main` immediately before merge.

## Customer-prioritized displaced work

The customer supplied a broader MIRA modular-life-operations / Google Sheets control-surface directive and explicitly requested that it be added to the MIRA stack, including reusable Job Search/market boards, People Discovery integration, Finance Operations, Vehicle Operations, Inventory Operations, MIRA Operations visibility, safe Sheets prototyping, Studio/public sanitization, automation and an optional local NVIDIA 49B coding-worker lane. That work belongs in a separate bounded foundation/intake packet so it does not silently expand `M2-M1-019`.

## Session-start alignment verification — 2026-09-07

### `FEATURES.md`

Reviewed. Existing `CAREER-001` is the current canonical career feature anchor. `M2-M1-019` extends the user-visible career capability with People Discovery, relationship tracking and a no-automated-outreach boundary while preserving `AUTH-001`, `STORE-001`, `RECOVERY-002`, `MAIL-002` and `DATA-001`.

### `BACKLOG.md`

Reviewed. `PEOPLE-DISCOVERY-001` is now registered on this branch as the bounded work ID for the vertical.

### `ROADMAP.md`

Reviewed. People Discovery is a user-visible Personal MIRA career vertical built on the existing Google/Sheets and canonical-state foundations. It does not change the Personal Google architecture, require Android, authorize automated outreach or weaken public-repository privacy rules.

### Direction result

ALIGNED

## Recovery protocol

Resume by reading current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-019.md`, PR #134 and this branch's remote head. Inspect active packet branches/PRs for overlap before shared-file writes. Do not reconstruct private people/provider/message state from public Git or chat memory.
