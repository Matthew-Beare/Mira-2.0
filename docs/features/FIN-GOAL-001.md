# FIN-GOAL-001 — Financial Goal Command Center

Status: specified, planning only.

This is the sanitized public specification for a private-profile-first MIRA capability. Public Git contains only generic product behavior, schemas, tests, synthetic examples, and non-private configuration patterns. Concrete household financial values belong only in private MIRROR/provider state.

## Non-negotiable design rule

The private Financial Escape profile is the reference implementation. Generalization for other users is allowed only when it preserves every reference-profile behavior. If a generic abstraction weakens the private profile, redesign or omit the abstraction.

## Capability set

- Configurable financial goals and policy, including debt payoff, reserve building, savings milestones, and career/work transitions.
- Independent and coupled household income units, including all-or-nothing work arrangements.
- Provenance-bound historical observations with freshness and confidence.
- Plan-versus-actual trajectory, rate-of-change, forecast history, ahead/behind metrics, and forecast confidence.
- Configurable productive-work metrics where relevant.
- Protected-reserve semantics separate from free/uncommitted cash.
- Contribution tracking that keeps debt reduction, savings, and retirement/investment contributions distinct.
- Scenario comparison and transition/offer analysis.
- One primary command-center dashboard as a projection of MIRROR, never a competing authority.
- Configurable near-goal daily countdown mode.

## Reserved feature IDs

- FIN-GOAL-001
- FIN-HISTORY-001
- FIN-TRAJECTORY-001
- FIN-DASH-001
- FIN-SCENARIO-001
- FIN-COUNTDOWN-001
- FIN-PRIVATE-REF-001

## Proposed work IDs

- FIN-GOAL-MODEL-001
- FIN-SNAPSHOT-001
- FIN-TRAJECTORY-ENGINE-001
- FIN-WORK-INCOME-001
- FIN-SCENARIO-ENGINE-001
- FIN-DASHBOARD-001
- FIN-PRIVATE-PROFILE-001
- FIN-COUNTDOWN-MODE-001
- FIN-PROVIDER-INTEGRATION-001
- FIN-LIVE-VERIFY-001

## Private reference contract

The private profile must be able to express its exact coupled-income rules, protected reserves, staged budgets, payoff ordering, contribution policy, productive-work accounting, leave-period handling, ahead/behind conversions, forecast movement, rolling performance, separate completion/escape/preferred-exit/opportunity concepts, and replacement-household-income transition analysis without exposing private values in Git.

## Generic user model

Other users may choose goals such as credit-card payoff, selected debt-stack payoff, vehicle/student-loan/mortgage payoff, emergency-reserve building, a project or relocation fund, or a work/career transition. Each goal supplies its own target state, priority order, protected resources, time horizon, contribution policy, and decision rules.

## Authority and data quality

MIRROR remains the durable structured source of truth. The dashboard/spreadsheet is a human-readable view. Historical observations needed for trends are persisted with timestamp, source, freshness, and confidence. Stale provider data must not be represented as a fresh daily change. Payment amount and actual principal reduction are separate facts.

## Acceptance boundary

A future implementation is not acceptable unless:

1. public Git contains no private financial state;
2. synthetic fixtures cover multiple goal types, including a coupled-income transition case;
3. the private reference profile binds from private MIRROR/provider state without exposing values in code;
4. generic configurability does not weaken any private reference-profile rule;
5. dashboards remain projections rather than mutable-state authority;
6. protected resources remain protected unless the selected policy explicitly changes them;
7. trend/forecast outputs preserve source freshness and confidence.

## Backlog placement

This is a later financial vertical and does not interrupt active packet M2-M1-012. Before implementation, reconcile these reserved IDs into canonical FEATURES.md and BACKLOG.md under DEV-007 and split the work into bounded packets.

Tracking issue: #121.