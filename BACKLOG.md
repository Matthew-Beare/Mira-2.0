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
| `AUDIT-A` | PREREQUISITE | Feature Audit Slice A: brief/time/tasking/operational-state feature reconstruction. | G0-001 | **in progress**; A1-A3 complete, A4 next |
| `AUDIT-A1` | PREREQUISITE | Audit category-A behaviors 1-5. | G0-001 | **complete in `M2-G0-002A`**; `OPS-001`…`OPS-005` |
| `AUDIT-A2` | PREREQUISITE | Audit category-A behaviors 6-10. | AUDIT-A1 | **complete in `M2-G0-002B`**; `CTX-001`, `CTX-002`, `TRIP-001`, `ROUTE-001`, `WEATHER-001` |
| `AUDIT-A3` | PREREQUISITE | Audit category-A behaviors 11-15: mileage/gross, Miles & Pay authority, task hierarchy, next-action evidence, Run Log/recovery/circuit breaker. | AUDIT-A2 | **complete in `M2-G0-002C`**; `MILE-001`, `MILE-002`, `TASK-001`, `TASK-002`, `RECOVERY-001` |
| `AUDIT-A4` | PREREQUISITE | Audit category-A behavior 16: optional-module failure isolation; then reconcile Slice-A dependencies/evidence and close category A. | AUDIT-A3 | **next packet `M2-G0-002D`** |
| `AUDIT-B` | PREREQUISITE | Feature Audit Slice B: calendar/reminders/mail/communication safety. | AUDIT-A | queued |
| `AUDIT-C` | PREREQUISITE | Feature Audit Slice C: orders/shipments/receipts/payments/spending. | AUDIT-B checkpoint | queued |
| `AUDIT-D` | PREREQUISITE | Feature Audit Slice D: assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C checkpoint | queued |
| `AUDIT-E` | PREREQUISITE | Feature Audit Slice E: profiles/onboarding/family/customization/accessibility. | AUDIT-D checkpoint | queued |
| `AUDIT-F` | PREREQUISITE | Feature Audit Slice F: providers/portability/distribution/enterprise. | AUDIT-E checkpoint | queued |
| `AUDIT-G` | PREREQUISITE | Feature Audit Slice G: ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F checkpoint | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audit slices A-G | queued; relevant evidence may be inspected earlier only when materially relevant to active records |
| `DEP-GRAPH` | PREREQUISITE | Build complete feature dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic feature registry | queued |
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | G0 audit + canonical state contract | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Prove stock ChatGPT can create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity. | dependency graph + sandbox | provisional |
| `ANDROID-SYNC` | VERTICAL | Prove Android reads/mutates same canonical entity without second authority. | CORE-ROUNDTRIP | provisional |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | core + delivery prerequisites | provisional; depends on audited schedule/context/task/recovery foundations |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA symbol, wordmark, hero/banner, adaptive icon, monochrome mark, and generated platform derivatives. | branding source delivered to spec | queued; source spec exists |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Build boomer-safe onboarding for full replacement ChatGPT instruction blocks without CLI. | audited onboarding requirements + current ChatGPT UI verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Next full Project Instructions replacement must require any customer action or exact fallback `Just tell me to continue.` immediately before final packet recovery line. | next legitimate full Project Instructions replacement | queued; current conversation behavior applies immediately |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy MIRA data only after stable MIRA 2.0 schema and vertical proof. | stable schema + backup/rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI feature parity and polished packaging. | working core vertical slices | deferred |
| `RFID` | LATER | RFID inventory capture and specialized handheld hardware. | stable asset/location/movement schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Home Assistant/Plex/Paperless/Node-RED/MQTT/local service integrations. | authority model + stable integration contracts | deferred |
| `ENTERPRISE` | LATER | Institutional/locked-down deployment path. | stock product core + provider abstraction | deferred |

## Dependency findings from `AUDIT-A1`

- `OPS-001` requires named-timezone scheduling plus `OPS-003` runtime slot integrity and `OPS-004` fresh identifiable delivery before live completion.
- `OPS-002` requires provider task enumeration/readback; source cannot prove unique live scheduling.
- `OPS-003` is test-verified in legacy code but needs MIRA 2.0 scheduler evidence.
- `OPS-004` depends on `RECOVERY-001` for durable same-run logging.
- `OPS-005` remains separate from generalized context and Trip forcing.

## Dependency findings from `AUDIT-A2`

- `CTX-001` generalizes operating labels but does not replace `OPS-005`; downstream context behavior needs an adapter from configured labels to deterministic state transitions.
- `CTX-002` requires explicit confirmation before recommended context activation.
- `TRIP-001` is an occurrence authority separate from context, Route knowledge and Mileage.
- `ROUTE-001` provides reusable route/runtime knowledge; human-facing ahead/behind still needs explicit verification.
- `WEATHER-001` has test-verified deterministic gating but external NWS/DOT/511 evidence remains an integration boundary.

## Dependency findings from `AUDIT-A3`

- `MILE-001` deterministic paid-mile/gross reporting depends on `MILE-002` authority, supported paid-mile evidence, verified rate and `OPS-001` Thursday brief semantics.
- `MILE-002` is the logical mileage/pay authority; the historical live Google tracker is migration/reference evidence, not MIRA 2.0 live verification. Initial Google storage may later be replaced without changing logical semantics.
- `TASK-001` is the canonical task structure and is a prerequisite for task-aware Android sync and useful Ops Brief rendering.
- `TASK-002` depends on `TASK-001` plus evidence/deadlines/prerequisites/context where relevant. It is not yet promoted to test-verified because the generic next-action/completion semantics need dedicated tests.
- `RECOVERY-001` is a hard reliability prerequisite for scheduled mutation workflows and connects directly back to `OPS-004`. Run Log field generation has tests; live scheduled Run Log entry remains unverified.
- The remaining optional-module failure isolation behavior is closely related to `RECOVERY-001` but stays in `AUDIT-A4` because it applies system-wide and must be checked against all Slice-A modules before category A closes.

## New-idea triage rule

Whenever the customer introduces a new idea:

1. capture it without forcing special syntax;
2. assign/link feature/work IDs;
3. identify hard dependencies and downstream capabilities it enables;
4. determine whether it blocks the active packet/milestone;
5. re-rank affected work dynamically;
6. keep current work unchanged unless required for acceptance or explicitly reprioritized.
