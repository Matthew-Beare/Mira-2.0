# MIRA 2.0 BACKLOG

This backlog is **not FIFO**. Arrival order never determines implementation order. Priority is recomputed from blockers, dependencies, milestone value, architectural leverage, user-visible value, and verification needs.

## Priority classes

1. **BLOCKER** — data integrity, privacy, security, or active acceptance blocker.
2. **PREREQUISITE** — hard dependency for higher-value work.
3. **VERTICAL** — user-visible end-to-end slice for active milestone.
4. **HARDENING** — reliability, testing, migration, observability, recovery.
5. **ENHANCEMENT** — useful but not required for active proof.
6. **LATER** — valid direction intentionally outside current milestone.

## Audit work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `AUDIT-A` | PREREQUISITE | Brief/time/tasking/operational-state reconstruction. | G0-001 | **complete through `M2-G0-002D`** |
| `AUDIT-B` | PREREQUISITE | Calendar/reminders/mail/communication safety. | AUDIT-A | **complete through `M2-G0-003B`** |
| `AUDIT-B1` | PREREQUISITE | B rows 1-5: appointment/reminder safety. | AUDIT-A | complete; `CAL-001`…`CAL-003`, `REMIND-001`, `REMIND-002` |
| `AUDIT-B2` | PREREQUISITE | B rows 6-10: appointment presentation, mail triage, outbound approval, archive approval, job watch. | AUDIT-B1 | **complete in `M2-G0-003B`**; `CAL-004`, `MAIL-001`…`MAIL-003`, `CAREER-001` |
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | **next; split C1/C2/C3** |
| `AUDIT-C1` | PREREQUISITE | C rows 1-5: mail/carrier evidence correlation; ordered→shipped→delivered lifecycle; cancellation/replacement/return/refund/no-settlement states; replacement without duplicate spend; active-undelivered + five-business-day no-progress behavior. | AUDIT-B | **next packet `M2-G0-004A`** |
| `AUDIT-C2` | PREREQUISITE | C rows 6-10: receipt intake; searchable receipt/purchase history; email-grounded monthly spending; receipt taxonomy; expected charge/refund/reimbursement reconciliation. | AUDIT-C1 | queued |
| `AUDIT-C3` | PREREQUISITE | C rows 11-12: optional subscription/free-trial tracking; credit-card/complete financial ingestion direction; then category-C consistency closure. | AUDIT-C2 | queued |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C | queued |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |

## Post-audit / implementation work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | G0 audit + canonical state contract | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Stock ChatGPT create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity. | dependency graph + sandbox | provisional |
| `ANDROID-SYNC` | VERTICAL | Android reads/mutates same canonical entity without second authority. | CORE-ROUNDTRIP | provisional |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | core + delivery prerequisites | provisional |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA source artwork and generated platform derivatives. | branding source delivered | queued |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Boomer-safe onboarding for full replacement ChatGPT instructions without CLI. | audited onboarding + current UI verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Next full Project Instructions replacement must require customer action or exact fallback `Just tell me to continue.` before final packet line. | next legitimate full replacement | queued; conversation behavior applies now |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy data after stable schema/vertical proof. | stable schema + rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI parity and packaging. | core verticals | deferred |
| `RFID` | LATER | RFID inventory capture/specialized hardware. | stable inventory schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Home Assistant/Plex/Paperless/Node-RED/MQTT integrations. | stable authority/integration contracts | deferred |
| `ENTERPRISE` | LATER | Institutional/locked-down deployment. | stock core + provider abstraction | deferred |

## Category-B dependency findings

- `CAL-001` Saturday weekly lookahead uses repaired mode-independent slot semantics; older ROAD-only wording is superseded.
- `CAL-002`/`CAL-003` deterministic reminder timing is separate from provider Calendar projection and actual notification delivery.
- `CAL-004` prohibits fabricated acknowledgement/confirmation claims and isolates malformed/unavailable appointment evidence.
- `REMIND-001` requires explicit supported medication schedule evidence and forbids dose/timing inference or missed-dose advice.
- `REMIND-002` requires explicit sharing consent and real recipient resolution; a nonblank unit-test string is not integration proof.
- `MAIL-001` triage is evidence intake only. It does not authorize archival or external contact.
- `MAIL-002` is a provider-independent per-action outbound-contact approval gate; replacing Gmail with another provider must not weaken it.
- `MAIL-003` treats silence as no archive permission and repeats unresolved review state.
- `CAREER-001` is optional per user, relies on canonical qualifications/settings, and must remain inside an existing compatible control cycle rather than creating duplicate scheduling.
- No category-B feature is promoted to MIRA 2.0 integration/live verification from legacy provider behavior.

## Category-A dependency closure

- Scheduling: `OPS-001` depends on `OPS-003`/`OPS-004`; live uniqueness remains `OPS-002` provider-readback work.
- Recovery: `OPS-004` depends on `RECOVERY-001`; multi-module behavior uses `RECOVERY-002` for scoped failure domains.
- Context/travel/mileage remain separate authorities linked by stable identity.
- `TASK-002` remains specified pending dedicated generic completion/next-action tests.
- Legacy live-provider claims do not promote MIRA 2.0 evidence levels.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
