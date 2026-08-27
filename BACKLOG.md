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
| `AUDIT-A` | PREREQUISITE | Feature Audit Slice A: governance/core runtime + brief/time/operational state. | G0-001 | next |
| `AUDIT-B` | PREREQUISITE | Feature Audit Slice B: calendar/reminders/mail/communication safety. | AUDIT-A checkpoint | queued |
| `AUDIT-C` | PREREQUISITE | Feature Audit Slice C: orders/shipments/receipts/payments/spending. | AUDIT-B checkpoint | queued |
| `AUDIT-D` | PREREQUISITE | Feature Audit Slice D: assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C checkpoint | queued |
| `AUDIT-E` | PREREQUISITE | Feature Audit Slice E: profiles/onboarding/family/customization/accessibility. | AUDIT-D checkpoint | queued |
| `AUDIT-F` | PREREQUISITE | Feature Audit Slice F: providers/portability/distribution/enterprise. | AUDIT-E checkpoint | queued |
| `AUDIT-G` | PREREQUISITE | Feature Audit Slice G: ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F checkpoint | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audit slices A-G | queued |
| `DEP-GRAPH` | PREREQUISITE | Build complete feature dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic feature registry | queued |
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | G0 audit + canonical state contract | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Prove stock ChatGPT can create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity. | dependency graph + sandbox | provisional |
| `ANDROID-SYNC` | VERTICAL | Prove Android reads/mutates same canonical entity without second authority. | CORE-ROUNDTRIP | provisional |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | core + delivery prerequisites | provisional |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA symbol, wordmark, hero/banner, adaptive icon, monochrome mark, and generated platform derivatives. | branding source delivered to spec | queued; source spec exists |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Build boomer-safe onboarding that teaches users how to install full replacement ChatGPT Project Instructions and other required instruction blocks without CLI. | audited onboarding requirements + current ChatGPT UI verification | queued |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy MIRA data only after stable MIRA 2.0 schema and vertical proof. | stable schema + backup/rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI feature parity and polished packaging. | working core vertical slices | deferred |
| `RFID` | LATER | RFID inventory capture and specialized handheld hardware. | stable asset/location/movement schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Home Assistant/Plex/Paperless/Node-RED/MQTT/local service integrations. | authority model + stable integration contracts | deferred |
| `ENTERPRISE` | LATER | Institutional/locked-down deployment path. | stock product core + provider abstraction | deferred |

## New-idea triage rule

Whenever the customer introduces a new idea:

1. capture it without forcing special syntax;
2. assign/link feature/work IDs;
3. identify hard dependencies and downstream capabilities it enables;
4. determine whether it blocks the active packet/milestone;
5. re-rank affected work dynamically;
6. keep current work unchanged unless required for acceptance or explicitly reprioritized.
