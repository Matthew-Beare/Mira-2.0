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

## Calendar application

For the default Personal Google Calendar lane, the intended user flow is:

**User:** “Yes, use my calendar.”  
**MIRA:** surfaces Google's authorization UI if authorization is not already granted.  
**Then:** MIRA discovers the usable Calendar capability, selects/binds the safe default according to policy, and performs its own verification. No MIRA menu hunting or manual Calendar creation is part of the normal product flow.

A dedicated MIRA-created secondary Calendar or stronger ETag-guarded Apps Script adapter may remain available as an optional organization/concurrency/hardening lane, but it is not a prerequisite for ordinary single-writer Personal activation unless provider evidence proves no safe simpler lane exists.
