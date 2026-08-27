# MIRA 2.0 BACKLOG

This backlog is **not FIFO**. Arrival order never determines implementation order by itself. Priority is recomputed from blockers, dependency position, active milestone value, architectural leverage, user-visible value, and verification needs.

New customer ideas are captured here by default and do not expand `CURRENT_WORK.md` unless required for active acceptance or the customer explicitly reprioritizes.

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
| `AUDIT-A` | PREREQUISITE | Feature Audit Slice A: brief/time/tasking/operational-state feature reconstruction. | G0-001 | **complete through `M2-G0-002D`** |
| `AUDIT-A1` | PREREQUISITE | Category-A behaviors 1-5. | G0-001 | complete; `OPS-001`…`OPS-005` |
| `AUDIT-A2` | PREREQUISITE | Category-A behaviors 6-10. | AUDIT-A1 | complete; `CTX-001`, `CTX-002`, `TRIP-001`, `ROUTE-001`, `WEATHER-001` |
| `AUDIT-A3` | PREREQUISITE | Category-A behaviors 11-15. | AUDIT-A2 | complete; `MILE-001`, `MILE-002`, `TASK-001`, `TASK-002`, `RECOVERY-001` |
| `AUDIT-A4` | PREREQUISITE | Category-A behavior 16 plus Slice-A consistency pass. | AUDIT-A3 | **complete in `M2-G0-002D`**; `RECOVERY-002` |
| `AUDIT-B` | PREREQUISITE | Feature Audit Slice B: calendar/reminders/mail/communication safety. | AUDIT-A | **next; split into bounded B1/B2 packets** |
| `AUDIT-B1` | PREREQUISITE | Audit category-B rows 1-5: Saturday lookahead, day-before/morning-of reminders, one-hour-before reminders, evidence-gated medication reminders, caregiver-sharing safety boundary. | AUDIT-A | **next packet `M2-G0-003A`** |
| `AUDIT-B2` | PREREQUISITE | Audit category-B rows 6-10: context-aware appointment windows, important mail triage, no auto-email, archive approval, career/job watch. | AUDIT-B1 | queued |
| `AUDIT-C` | PREREQUISITE | Orders/shipments/receipts/payments/spending. | AUDIT-B | queued |
| `AUDIT-D` | PREREQUISITE | Assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C | queued |
| `AUDIT-E` | PREREQUISITE | Profiles/onboarding/family/customization/accessibility. | AUDIT-D | queued |
| `AUDIT-F` | PREREQUISITE | Providers/portability/distribution/enterprise. | AUDIT-E | queued |
| `AUDIT-G` | PREREQUISITE | ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audits A-G | queued; inspect earlier only when materially relevant to active records |
| `DEP-GRAPH` | PREREQUISITE | Build complete feature dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic feature registry | queued |
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | G0 audit + canonical state contract | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Prove stock ChatGPT can create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity. | dependency graph + sandbox | provisional |
| `ANDROID-SYNC` | VERTICAL | Prove Android reads/mutates same canonical entity without second authority. | CORE-ROUNDTRIP | provisional |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | core + delivery prerequisites | provisional; depends on audited schedule/context/task/recovery foundations |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA source artwork and generated platform derivatives. | branding source delivered to spec | queued |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Build boomer-safe onboarding for full replacement ChatGPT instruction blocks without CLI. | audited onboarding requirements + current ChatGPT UI verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Next full Project Instructions replacement must require any customer action or exact fallback `Just tell me to continue.` immediately before final packet recovery line. | next legitimate full Project Instructions replacement | queued; current conversation behavior applies immediately |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy data only after stable MIRA 2.0 schema and vertical proof. | stable schema + backup/rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI parity and packaging. | working core vertical slices | deferred |
| `RFID` | LATER | RFID inventory capture and specialized hardware. | stable asset/location/movement schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Home Assistant/Plex/Paperless/Node-RED/MQTT/local integrations. | authority model + stable contracts | deferred |
| `ENTERPRISE` | LATER | Institutional/locked-down deployment path. | stock product core + provider abstraction | deferred |

## Slice-A dependency closure

- Scheduling: `OPS-001` → requires `OPS-003` runtime integrity and `OPS-004` fresh run identity; unique provider state remains `OPS-002` live-readback work.
- Recovery: `OPS-004` → `RECOVERY-001`; multi-module scheduled behavior additionally relies on `RECOVERY-002` for scoped failure domains.
- Context: `OPS-005` preserves current deterministic HOME/ROAD semantics; `CTX-001` generalizes labels and `CTX-002` gates recommendation/activation.
- Travel: `TRIP-001`, `ROUTE-001`, and `MILE-*` are distinct authorities linked by stable identity rather than implicit record creation.
- Weather: `WEATHER-001` depends on context/Trip/Route and on `RECOVERY-002` when external evidence fails inside a broader run.
- Mileage: `MILE-001` depends on `MILE-002`, supported paid-mile evidence, verified rate, and Thursday brief semantics. Legacy live Google rows are not MIRA 2.0 verification.
- Tasks: `TASK-001` is test-verified legacy structure; `TASK-002` remains specified pending dedicated generic next-action/completion tests.
- Evidence ceiling: no category-A capability is marked MIRA 2.0 `integration_verified` or `live_verified` solely from legacy provider claims.

## New-idea triage rule

Whenever the customer introduces a new idea:

1. capture it without forcing special syntax;
2. assign/link feature/work IDs;
3. identify hard dependencies and downstream capabilities it enables;
4. determine whether it blocks the active packet/milestone;
5. re-rank affected work dynamically;
6. keep current work unchanged unless required for acceptance or explicitly reprioritized.
