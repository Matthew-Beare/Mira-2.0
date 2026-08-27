# MIRA 2.0 BACKLOG

This backlog is **not FIFO**. Arrival order never determines implementation order. Priority is recomputed from blockers, dependencies, milestone value, architectural leverage, user-visible value, and verification needs.

## Priority classes

1. **BLOCKER** — data integrity, privacy, security, or active acceptance blocker.
2. **PREREQUISITE** — hard dependency for higher-value work.
3. **VERTICAL** — user-visible end-to-end slice for active milestone.
4. **HARDENING** — reliability, testing, migration, observability, recovery.
5. **ENHANCEMENT** — useful but not required for active proof.
6. **LATER** — valid direction intentionally outside current milestone.

## Open work

| Work ID | Class | Work | Dependencies | Status |
|---|---|---|---|---|
| `AUDIT-A` | PREREQUISITE | Brief/time/tasking/operational-state feature reconstruction. | G0-001 | **complete through `M2-G0-002D`** |
| `AUDIT-B` | PREREQUISITE | Calendar/reminders/mail/communication safety. | AUDIT-A | **in progress; B1 complete, B2 next** |
| `AUDIT-B1` | PREREQUISITE | Category-B rows 1-5: Saturday lookahead; day-before/morning-of; relative reminder; medication reminder safety; caregiver sharing. | AUDIT-A | **complete in `M2-G0-003A`**; `CAL-001`…`CAL-003`, `REMIND-001`, `REMIND-002` |
| `AUDIT-B2` | PREREQUISITE | Category-B rows 6-10: context-aware appointment windows, important mail triage, no auto-email, archive approval, career/job watch. | AUDIT-B1 | **next packet `M2-G0-003B`** |
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | queued |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C | queued |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant |
| `DEP-GRAPH` | PREREQUISITE | Build complete dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic registry | queued |
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

## Reminder-safety dependency findings from `AUDIT-B1`

- `CAL-001` Saturday weekly lookahead is now mode-independent in the repaired deterministic policy; this supersedes older ledger wording that tied it specifically to ROAD.
- `CAL-002` day-before/morning-of semantics have two surfaces: deterministic reminder planning and Ops Brief appointment visibility. Provider projection/readback remains a separate integration boundary.
- `CAL-003` defaults to a 60-minute relative reminder but preserves configurability and suppresses/deduplicates invalid or overlapping times.
- `REMIND-001` is safety-critical: reminder timing may only come from explicit owner, prescription-label, pharmacy or clinician evidence with explicit confirmed schedule; no dose/timing inference or missed-dose advice.
- `REMIND-002` is default-off and requires explicit sharing activation plus recipient identity. Unit tests prove the gate but not real recipient resolution/authorization; that remains integration evidence.
- PR #31 provides only broad Android notification/background expectations here. It does not supersede the dedicated deterministic reminder policy or prove Calendar/notification delivery.

## Slice-A dependency closure

- Scheduling: `OPS-001` depends on `OPS-003`/`OPS-004`; live uniqueness remains `OPS-002` provider-readback work.
- Recovery: `OPS-004` depends on `RECOVERY-001`; multi-module behavior uses `RECOVERY-002` for scoped failure domains.
- Context/travel/mileage remain separate authorities linked by stable identity.
- `TASK-002` remains specified pending dedicated generic completion/next-action tests.
- Legacy live-provider claims do not promote MIRA 2.0 evidence levels.

## New-idea triage rule

New customer ideas are captured without special syntax, assigned/linked to feature/work IDs, dependency-ranked, and do not expand active work unless required for acceptance or explicitly reprioritized.
