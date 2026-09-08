# MIRA 2.0 CURRENT WORK

Git is authoritative. This branch records exactly one active packet. Multiple other packet branches may be active repository-wide at the same time under `docs/CONCURRENT_WORK_POLICY.md`.

## Active packet

### `M2-M1-019` — People Discovery vertical slice

- **Primary work:** `PEOPLE-DISCOVERY-001`.
- **Primary features:** `CAREER-001`.
- **Related invariants/features:** `AUTH-001`, `STORE-001`, `RECOVERY-002`, `MAIL-002`, `DATA-001`.
- **Repository:** `Matthew-Beare/Mira-2.0`.
- **Branch:** `work/m2-m1-019-people-discovery`.
- **Base SHA:** `738ebf082cd3921a0ba807604acabfa756f40c1d`.
- **Packet:** `docs/work-packets/M2-M1-019.md`.
- **Owned implementation surfaces:** new People Discovery provider/domain/tracker modules and tests; packet-specific synthetic fixtures/docs.
- **Shared/high-contention surfaces:** `FEATURES.md`, `BACKLOG.md`, `project/code_ownership.json`, branch-local `CURRENT_WORK.md`; reconcile against current `main` immediately before merge.
- **Current status:** implementation active. Provider/Google integration reconnaissance is in progress; no live third-party people data has been written and no outreach action exists.

## Objective

Deploy a repeatable People Discovery system that finds useful professional contacts at active target employers, with Austin and Research Triangle/Raleigh-Durham as the initial markets and WGU plus networking/cloud/infrastructure relevance strongly prioritized. Normalize, deduplicate, score and retain provenance for candidates; maintain a Google Sheets user-facing tracker; support manual interaction tracking; and prohibit automated outreach.

## Hard boundaries

- No automated email, LinkedIn connection request/message, comment, post, or other contact action.
- No unauthorized LinkedIn scraping, login automation, or browser scraping.
- LinkedIn URLs may be stored when returned by legitimate providers/public sources.
- One logical MIRROR authority. The Google tracker is a projection/bounded input surface, not a second conflicting truth store.
- Public Git contains synthetic examples only. Third-party person data, provider credentials, live spreadsheet IDs and private job-search state stay out of the public repository.
- Uncertain identity matches fail closed rather than silently merging people.

## Provider decision state

Official current documentation has been inspected for People Data Labs and Apollo.

- People Data Labs Person Search is the leading first adapter because arbitrary Person Schema filtering supports the key WGU-first query dimensions: current employer, education/school, title, location, skills, work history and LinkedIn URL. Certifications are searchable/returnable when the relevant premium resume field bundle is available.
- PDL currently offers 100 free Person Search records/month at 10 requests/minute, enough for a bounded live proof without requiring a paid plan.
- Apollo remains a useful replaceable secondary adapter. Its current documented People Search endpoint supports employer/domain/title/location/seniority/keywords but does not expose a direct education/school filter, making it less precise for Tier-1 WGU discovery.
- No relevant Apollo/PDL ChatGPT plugin is currently surfaced by Plugin Directory search, so an external provider credential is likely required for the live provider adapter unless a later native integration is discovered.

## Concurrent-work collision check

- `M2-M1-018` is active on `work/m2-m1-018-finance-truth-command-center`; it owns private finance/workbook truth. This packet does not edit finance modules or private finance artifacts.
- `M2-M1-016` and `M2-M1-017` are completed predecessor/recovery branches and are not reused.
- Android `M2-M1-012` remains held and untouched.
- Before every merge, inspect then-current `main` and active packet PRs/branches for newly overlapping surfaces.

## Acceptance state

- Unique packet/branch isolated from other chats: **satisfied**.
- Existing Sheets/canonical-state architecture inspected: **in progress; Google structured-state and native Workspace paths confirmed reusable**.
- Provider abstraction selected: **specified; implementation pending**.
- Real provider operational: **pending credential/preflight/live proof**.
- Candidate normalization: **pending implementation**.
- Entity resolution/dedupe: **pending implementation**.
- Relevance scoring: **pending implementation**.
- Provenance retention: **pending implementation**.
- Google tracker projection with COMPANIES/PEOPLE/INTERACTIONS/JOBS: **pending implementation/live write**.
- Repeat discovery update proof: **pending**.
- Exact tracker readback: **pending**.
- Manual interaction-state write/readback: **pending**.
- Automated outreach absence: **required; implementation/test pending**.
- Relevant tests/baseline gates: **pending**.
- Remote Git/CI completion proof: **pending**.

## Exact next action / resume point

1. Finish repository/provider reconnaissance for existing Google Workspace runtime, structured-state conventions, target-company/job-search state and code-ownership requirements.
2. Implement provider-neutral people candidate/provenance/scoring/entity-resolution core using synthetic tests.
3. Implement an injected-credential People Data Labs provider adapter with bounded, credit-aware WGU/role/employer/location searches; no contact/outreach endpoints.
4. Implement canonical People Discovery records and Google tracker projection/readback using existing MIRA Google/Sheets patterns rather than a duplicate persistence stack.
5. Reconcile `PEOPLE-DISCOVERY-001` and any refined stable career feature semantics into `BACKLOG.md` / `FEATURES.md` before CI/merge.
6. Run local/CI tests, then perform provider credential/capability preflight.
7. If the only remaining boundary is a PDL API key/account, request exactly that single user action after all independent implementation is complete.
8. Execute real discovery, real Sheet write/readback, rerun-update proof and manual-interaction proof before claiming deployment.

## Session-start alignment verification — 2026-09-07

### `FEATURES.md`

Reviewed. Existing `CAREER-001` covers qualified job-watch semantics but does not fully encode People Discovery; the packet will add a stable refinement before merge. The design preserves `AUTH-001`, `STORE-001`, `RECOVERY-002`, `MAIL-002`, and `DATA-001`, especially one-authority semantics, exact readback, failure isolation, outbound-contact control and protected production data.

### `BACKLOG.md`

Reviewed. No existing work item covers this requested People Discovery vertical. `PEOPLE-DISCOVERY-001` is the new bounded work ID and must be added to the canonical backlog before merge. This branch does not hijack finance, Android, or unrelated backlog work.

### `ROADMAP.md`

Reviewed. People Discovery is a user-visible career vertical built on existing Personal Google/Sheets foundations. It does not change the Personal Google architecture, require Android, or authorize automated outreach.

### Direction result

ALIGNED

## Recovery protocol

Resume by reading current remote `main`, this branch's `CURRENT_WORK.md`, `docs/work-packets/M2-M1-019.md`, and this branch's remote head. Then inspect active packet branches/PRs for new overlap before writes. Do not recover private people/provider state from public Git.
