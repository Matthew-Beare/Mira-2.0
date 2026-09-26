# M2-M0-032 — Personal Google bootstrap

## Objective

Advance `GOOGLE-BOOTSTRAP-001` with a bounded, provider-neutral planning and verification slice for explicitly selected Personal Google Workspace services.

## Scope

- deterministic selected-service blueprint construction;
- exact Google provider/service identity checks;
- fresh SOURCE-001 capability verification for each selected service;
- fail-closed handling of missing, stale, declared-only, or mismatched evidence;
- no silent service activation.

Out of scope: provider authorization/consent execution, live provider mutation, resource creation, OAuth implementation, browser installation UX, and `NONTECH-INSTALL-001`.

## Branch and base

- Branch: `work/m2-m0-032-google-bootstrap`
- Base: `3ecf6c058aa02032090020c9e8dc2790bb7ad4f9`
- Related features: `PROVIDER-003`, `ONBOARD-007`, `PROVIDER-002`, `SOURCE-001`
- Work item: `GOOGLE-BOOTSTRAP-001`

## Owned surfaces

- `mira/google_bootstrap.py`
- `tests/test_google_bootstrap.py`

## Shared/high-contention surfaces

- `CURRENT_WORK.md`
- `BACKLOG.md`
- `project/code_ownership.json`

## Acceptance criteria

1. Selected services produce a deterministic, deduplicated Google bootstrap plan.
2. Unsupported service identifiers fail closed.
3. Every selected service requires fresh verified capability evidence for its exact required gates.
4. Missing evidence fails closed without inferring capability from authorization, declared scopes, code existence, or another Google service.
5. Provider/service identity mismatch is rejected.
6. Planning and verification perform no provider mutation and no MIRA service activation.
7. Exact-head CI and repository ownership/session gates pass before merge.

## Evidence so far

- `mira/google_bootstrap.py` implements deterministic planning and verification for Calendar, Gmail, and Sheets.
- `tests/test_google_bootstrap.py` covers deterministic dedupe, unsupported services, verified readiness, missing evidence, declared-only evidence, and provider identity mismatch.
- `project/code_ownership.json` registers the new implementation surface.
- No live provider state has been mutated or claimed.

### Idea/backlog capture audit

No new material feature was introduced. This packet implements the existing `GOOGLE-BOOTSTRAP-001` / `PROVIDER-003` direction. `CAPTURE AUDIT COMPLETE`.

## Exact next action

Update `CURRENT_WORK.md` to this packet, open the PR, then require exact-head CI. Fix only failures attributable to this bounded slice; do not widen into OAuth, provider mutation, or ordinary-user installation.
