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
| `AUDIT-A` | PREREQUISITE | Feature Audit Slice A: brief/time/tasking/operational-state feature reconstruction. | G0-001 | **in progress**; A1-A2 complete, A3 next |
| `AUDIT-A1` | PREREQUISITE | Audit category-A behaviors 1-5: canonical schedule, duplicate prohibition, runtime clock gate, deterministic Run ID/fresh delivery, deterministic HOME/ROAD + overrides. | G0-001 | **complete in packet `M2-G0-002A`**; features `OPS-001`…`OPS-005` |
| `AUDIT-A2` | PREREQUISITE | Audit category-A behaviors 6-10: generic context pairs; job/duties context recommendation; active trip separation; multi-leg route/runtime/location/ETA inference; ROAD severe-weather vs HOME weather. | AUDIT-A1 | **complete in packet `M2-G0-002B`**; features `CTX-001`, `CTX-002`, `TRIP-001`, `ROUTE-001`, `WEATHER-001` |
| `AUDIT-A3` | PREREQUISITE | Audit category-A behaviors 11-15: company-paid mileage/gross; separate Miles & Pay tracker authority; task hierarchy; next-action completion evidence; phase-aware Run Log/recovery/circuit breaker. | AUDIT-A2 | **next packet `M2-G0-002C`** |
| `AUDIT-A4` | PREREQUISITE | Audit category-A behavior 16: optional-module failure isolation and finalize Slice A dependency/evidence consistency. | AUDIT-A3 | queued |
| `AUDIT-B` | PREREQUISITE | Feature Audit Slice B: calendar/reminders/mail/communication safety. | AUDIT-A | queued |
| `AUDIT-C` | PREREQUISITE | Feature Audit Slice C: orders/shipments/receipts/payments/spending. | AUDIT-B checkpoint | queued |
| `AUDIT-D` | PREREQUISITE | Feature Audit Slice D: assets/fitment/inventory/storage/identifiers/evidence. | AUDIT-C checkpoint | queued |
| `AUDIT-E` | PREREQUISITE | Feature Audit Slice E: profiles/onboarding/family/customization/accessibility. | AUDIT-D checkpoint | queued |
| `AUDIT-F` | PREREQUISITE | Feature Audit Slice F: providers/portability/distribution/enterprise. | AUDIT-E checkpoint | queued |
| `AUDIT-G` | PREREQUISITE | Feature Audit Slice G: ChatGPT/Android/web/desktop/CLI/device surfaces. | AUDIT-F checkpoint | queued |
| `AUDIT-LEGACY` | HARDENING | Reconcile PR #31 plus meaningful legacy branches/repos against stable MIRA 2.0 features. | audit slices A-G | queued; relevant evidence may be inspected earlier only when it materially changes the active feature record |
| `DEP-GRAPH` | PREREQUISITE | Build complete feature dependency/enables graph, dedupe/supersession map, and ranked engineering backlog. | completed forensic feature registry | queued |
| `DATA-SANDBOX` | PREREQUISITE | Create separate MIRA 2.0 Google/MIRROR sandbox with synthetic data and prove no legacy production modification. | G0 audit + canonical state contract | queued |
| `CORE-ROUNDTRIP` | VERTICAL | Prove stock ChatGPT can create/read/mutate/dedupe/read-back one canonical Google-backed MIRROR entity. | dependency graph + sandbox | provisional |
| `ANDROID-SYNC` | VERTICAL | Prove Android reads/mutates same canonical entity without second authority. | CORE-ROUNDTRIP | provisional |
| `OPS-BRIEF-VSLICE` | VERTICAL | Generate/deliver one real MIRA Ops Brief from canonical MIRA 2.0 state. | core + delivery prerequisites | provisional; depends on audited `OPS-*`, context/travel, task/run-log foundations |
| `BRAND-ASSETS` | ENHANCEMENT | Integrate approved MIRA symbol, wordmark, hero/banner, adaptive icon, monochrome mark, and generated platform derivatives. | branding source delivered to spec | queued; source spec exists |
| `ONBOARD-INSTRUCTIONS` | PREREQUISITE | Build boomer-safe onboarding that teaches users how to install full replacement ChatGPT Project Instructions and other required instruction blocks without CLI. | audited onboarding requirements + current ChatGPT UI verification | queued |
| `GOV-RESP-001` | ENHANCEMENT | Update the next full Project Instructions replacement so development replies include any required customer action or the exact fallback sentence `Just tell me to continue.` immediately before the final packet recovery line. Never ship this as a fragment-only instruction patch. | next legitimate full Project Instructions replacement | queued; current conversation behavior applies immediately |
| `LEGACY-MIGRATION` | LATER | Migrate selected legacy MIRA data only after stable MIRA 2.0 schema and vertical proof. | stable schema + backup/rollback/reconciliation | deferred |
| `DESKTOP-PARITY` | LATER | Windows/Linux/web/CLI feature parity and polished packaging. | working core vertical slices | deferred |
| `RFID` | LATER | RFID inventory capture and specialized handheld hardware. | stable asset/location/movement schemas | deferred |
| `LOCAL-INTEGRATIONS` | LATER | Home Assistant/Plex/Paperless/Node-RED/MQTT/local service integrations. | authority model + stable integration contracts | deferred |
| `ENTERPRISE` | LATER | Institutional/locked-down deployment path. | stock product core + provider abstraction | deferred |

## Dependency findings from `AUDIT-A1`

- `OPS-001` requires a named-timezone scheduler/provider plus `OPS-003` runtime slot integrity and `OPS-004` identifiable fresh delivery before live completion can be claimed.
- `OPS-002` cannot be live-verified from source code; it requires provider task enumeration/readback to prove there is exactly one canonical dispatcher and no prohibited duplicates.
- `OPS-003` is already test-verified in legacy code but needs later MIRA 2.0 integration/live scheduler evidence.
- `OPS-004` depends on the later Run Log/recovery feature still awaiting `AUDIT-A3`; its deterministic ID logic is test-verified but live standalone scheduler delivery is not.
- `OPS-005` remains separate from generic context pairs and active-trip forcing.

## Dependency findings from `AUDIT-A2`

- `CTX-001` generalizes operating labels but does not replace `OPS-005`; MIRA 2.0 needs an adapter from selected context labels to deterministic transition/override behavior.
- `CTX-002` is a prerequisite for safe generalized onboarding: job title/duties may recommend a context but explicit confirmation is required before activation.
- `TRIP-001` is an independent occurrence authority. Context, Route knowledge and later Mileage records may reference a Trip, but learning/changing one must not silently manufacture the others.
- `ROUTE-001` depends on `TRIP-001` for occurrence-specific ETA/status but remains reusable route knowledge. Route-average ETA is test-supported; human-facing ahead/behind interpretation needs explicit later verification.
- `WEATHER-001` depends on context plus Trip/Route state for ROAD corridor checks. Deterministic gating is test-verified; actual NWS/DOT/511 evidence retrieval remains an external integration boundary.
- PR #31 adds no narrower travel/context feature implementation that should supersede these audited records; its broad `MIRA-F009` Ops Brief candidate merely requires mode-specific filtering to remain contract-driven/tested.

## New-idea triage rule

Whenever the customer introduces a new idea:

1. capture it without forcing special syntax;
2. assign/link feature/work IDs;
3. identify hard dependencies and downstream capabilities it enables;
4. determine whether it blocks the active packet/milestone;
5. re-rank affected work dynamically;
6. keep current work unchanged unless required for acceptance or explicitly reprioritized.
