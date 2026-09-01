# Stock ChatGPT native connection execution evidence

Packet: `M2-M0-029`  
Work: `HOST-CONNECT-EXEC-001`  
Date: 2026-09-01

## Bounded live proof

A live stock-ChatGPT host session received ordinary service intent for Google Calendar. Current Plugin Management discovery resolved the supported **Google Calendar** integration by service name and description rather than relying on a repository-persisted plugin identifier.

The host then surfaced its native install/connect action. The human user completed the host/provider connection ceremony through that native UI. MIRA did not manually walk the user through ChatGPT settings, request copied provider IDs or OAuth scopes, require a developer console, run provider scripts, or use a terminal.

This proves the stock-ChatGPT host execution seam can translate ordinary service intent into the current native connection surface when the host provides a matching supported integration.

## Evidence ceiling

This proof establishes **live host discovery and native connection-surface execution** for the tested Google Calendar lane. The resulting provider/account authorization event was user-driven through the host UI.

This document intentionally does **not** record or claim:

- account identifiers, tokens, private provider state, or granted-scope details;
- live Calendar resource discovery or binding;
- Calendar read or write capability verification;
- Calendar event mutation or readback;
- MIRROR canonical-state mutation;
- automatic MIRA service activation;
- equivalence for Gmail, Drive, Microsoft, Apple/iCloud, or future providers.

`Connected` remains a stronger state than “the user completed a host authorization flow.” MIRA must separately obtain fresh operation-specific capability/resource/readback evidence before presenting verified readiness for a service.

## Product consequence

For supported stock-ChatGPT integrations, ordinary-language connection intent must prefer current host discovery and the native install/connect control. Manual settings navigation is fallback-only when the host cannot surface the action directly, and technical provider setup is not an acceptable default Personal substitute.

The future Android client must preserve the same provider-neutral state model while presenting product-owned native connection controls.
