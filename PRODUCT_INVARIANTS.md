# MIRA 2.0 Product Invariants

Git is authoritative. These are cross-feature product rules, not implementation suggestions.

## Intent-first ordinary-user activation

MIRA is designed for ordinary users who should not need to understand provider APIs, developer consoles, scripts, resource IDs, OAuth scopes, terminals, repositories, or internal architecture.

For any optional MIRA capability or connected provider:

1. The MIRA-side decision is expressed in ordinary language, normally a simple yes/no such as **“Yes, use my calendar.”**
2. If the external provider requires authorization, MIRA may surface the provider's own unavoidable **Allow / Connect / Continue** consent UI.
3. After consent, MIRA performs every setup, discovery, binding, resource-selection, recovery, and verification step that the available provider/runtime can safely automate.
4. MIRA must not require a normal user to manually create hidden resources, copy provider IDs, edit OAuth scopes, open Apps Script/developer consoles, paste code, run terminal commands, or understand implementation mechanics when those steps can be performed by software.
5. If a provider/runtime cannot support a safe ordinary-user flow, that lane is not the default Personal path. Preserve the limitation as capability/evidence state and select a simpler supported lane where possible rather than exporting engineering work to the user.
6. Provider consent is not permission for unrelated behavior. MIRA still observes service activation state, least privilege, protected-data rules, action-specific confirmation requirements, and exact readback/evidence boundaries.
7. Advanced, institutional, self-hosted, diagnostic, and developer workflows may expose technical controls when appropriate, but those controls must not leak into the default Personal experience.

This invariant applies across Calendar, Gmail/mail, Drive/files, Contacts, receipts, finance, automations, devices, local integrations, and future provider-backed features.

## Single canonical MIRROR reality authority

MIRROR is MIRA's single durable structured reality authority. Product domains may use separate schemas, tables, indexes, projections, tabs, caches, adapters, provider views, and user-facing surfaces, but they must not become independent competing databases or sources of truth for the same reality state.

1. Finance, receipts, bills, subscriptions, allowances, earmarks, income, debts, assets, inventory, trips, tasks, appointments, orders, and future domains participate in one canonical MIRROR reality model through stable entities, facts/events, relationships, provenance, and authority rules.
2. A Google Sheet, dashboard, report, chart, source-budget tab, provider response, or other projection is a view/input surface unless the Canonical Authority Registry explicitly assigns that data class to the provider. Presentation separation is allowed; authority separation is not.
3. Domain-specific tables or services are implementation boundaries, not separate realities. They must join through stable canonical identities and relationships so MIRA can reason across domains without copying the same fact into unrelated stores.
4. External providers remain authoritative only for the data classes explicitly assigned to them. MIRROR records the normalized observation, provenance, freshness, confidence, and relationships needed for cross-domain reasoning without silently overwriting provider truth.
5. User-authored classifications, policies, earmarks, allowances, reconciliation decisions, and other MIRA-owned semantics belong in MIRROR and attach to the underlying canonical entities/events rather than living only in a dashboard or spreadsheet cell.
6. Derived summaries, budgets, forecasts, charts, telemetry, and command-center views must be reproducible from canonical MIRROR state plus explicit model assumptions. They must never become an independent editable authority that can drift from the underlying records.
7. Source-specific or scenario-specific evidence may be preserved separately for comparison, but it remains provenance-linked evidence inside the same MIRROR model. A separate tab or projection does not imply a separate database.
8. When legacy or provider constraints temporarily require parallel storage, the separation must be explicit, bounded, provenance-linked, and treated as migration/adapter debt. MIRA must not normalize that temporary state into a permanent second source of truth.
9. Any feature that would create a second independent canonical store for an existing MIRROR data class is rejected unless the product owner explicitly changes this invariant.

## Connection surface application

`PROVIDER-002` / `PROVIDER-ONBOARD-001` must apply the intent-first rule through an obvious ordinary-user connection surface rather than treating provider authorization as documentation work for the user.

1. Whenever the host/client supports product-owned controls, MIRA exposes a simple Connections/Integrations surface with service-level actions such as **Connect Google Calendar**, **Connect Google Drive**, and **Connect Gmail**. Equivalent Microsoft, Apple and future provider lanes use the same interaction model when supported.
2. Each connection must expose honest user-facing state such as **Connect**, **Connected**, **Reconnect**, **Needs attention**, **Unavailable**, and **Disconnect**. Capability evidence, authorization state and MIRA service activation remain separate internally even when the presentation is simple.
3. Selecting **Connect** starts the host/provider-native connection and authorization flow directly. After the provider returns control, MIRA performs capability discovery, binding and exact verification automatically. A successful OAuth screen alone is not treated as verified readiness.
4. Connection labels describe what the user recognizes, not implementation plumbing. For example, Google Drive is the user-facing connection for supported Drive/Docs/Sheets/Slides access rather than asking the user to understand separate internal adapters.
5. If stock ChatGPT or another host does not permit MIRA to render its own connection buttons, ordinary-language connection intent must route into the closest supported native app/plugin flow. When the host exposes plugin/app discovery or installation, MIRA should resolve the relevant supported integration and surface the native install/connect prompt directly from the conversation instead of instructing the user to hunt through settings. The user still completes any unavoidable provider consent or workspace-admin approval.
6. If the host cannot directly surface that install/connect flow, MIRA may require at most one concise unavoidable host action. It must not compensate for missing host UI by asking the user to manually create provider resources, copy IDs, edit scopes, run scripts, open developer consoles, or perform terminal setup.
7. Optional providers are connected independently and with least privilege. Enabling one service must not silently pre-authorize unrelated services.
8. Onboarding may recommend a connection because of a user-selected goal, but must not silently connect or activate it. Declining or postponing a connection does not block unrelated MIRA use.
9. Provider-neutral connection contracts must not hard-code Google-only assumptions. Microsoft, Apple/iCloud and future provider lanes must fit the same state/action contract even when a particular host currently lacks a native connector for that provider.
10. The future Android client must implement the same connection semantics through a native Connections surface and shared capability/service state. Android must not invent a second provider-activation model or require technical setup merely because it owns more of the UI.

## Calendar application

For the default Personal Google Calendar lane, the intended user flow is:

**User:** “Yes, use my calendar.”  
**MIRA:** resolves and surfaces the supported native ChatGPT/Google connection flow if connection is required, then the user completes unavoidable Google authorization.  
**Then:** MIRA discovers the usable Calendar capability, selects/binds the safe default according to policy, and performs its own verification. No MIRA menu hunting or manual Calendar creation is part of the normal product flow.

A dedicated MIRA-created secondary Calendar or stronger ETag-guarded Apps Script adapter may remain available as an optional organization/concurrency/hardening lane, but it is not a prerequisite for ordinary single-writer Personal activation unless provider evidence proves no safe simpler lane exists.
