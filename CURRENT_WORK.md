# MIRA 2.0 CURRENT WORK

Git is authoritative. This file identifies exactly one active packet and the exact recovery point for displaced work.

## Product deployment invariant

Default Personal MIRA is **Google Workspace first, zero infrastructure**. An ordinary user starts with Google Drive/Docs/Sheets and browser-managed Google authorization. Linux, SQL, Cloud Run, containers, tunnels and local services are advanced upgrade paths, not prerequisites.

Canonical deployment ladder:

1. **Personal Google Workspace baseline:** Sheets is the first structured MIRROR authority; stock ChatGPT uses its authenticated Google Drive/Sheets connection for same-user reads/writes; copied/bound Apps Script provides embedded Google-side initialization, validation and automation where useful. No terminal/server is required.
2. **Advanced managed/self-hosted profiles:** Cloud Run, Linux VM, containers, SQL, local services or other backends when needed.
3. **Migration preserves semantics:** `API-001`, `AUTH-001` and `STORE-001` remain provider-neutral; backend changes are controlled Authority/adapter cutovers, never silent rewrites or dual writable masters.

## Preserved displaced packet

### `M2-M0-005` — Cloud Run credential + live Google deployment proof

- **Related work:** `API-DEPLOYMENT-001B`.
- **Disposition:** paused/deprioritized, not failed/deleted.
- **Readiness PR:** #48 merged at `acb37af4aa378e8128d8591406859fe954af3474`; CI `33217543700` green.
- **Cloud Shell operator PR:** #49 merged at `3332081054d691eca646c1d7bb274d22096f1c62`; CI `33218561781` green.
- **Pre-pivot checkpoint:** `c392b9b829fab989be8856c9272294c9907e409e`.
- **Resume point if selected later:** execute the merged Cloud Run operator against an authenticated Google Cloud project and collect live provider/restart evidence.

No live Cloud Run evidence is claimed. All Cloud Run code remains preserved as an advanced profile.

## Active packet

### `M2-M0-006` — Google Workspace zero-infrastructure first run

- **Primary related work:** `API-DEPLOYMENT-001A`
- **Adjacent M2-M0 client proof:** `CHATGPT-API-CLIENT-001`
- **Class:** hard M2-M0 prerequisite / ordinary-user vertical deployment slice
- **Repository:** `Matthew-Beare/Mira-2.0`
- **Workspace implementation branch:** `integration/m0-006-google-workspace-first-run`
- **Branch start:** `fa0ff6741cc0294dd82d128428ea9a03c2a86a2e`
- **Read-only first-run PR:** #50
- **PR final head:** `cf5a7c870f2de549e1f4a0d212afa8fc86954f09`
- **PR CI:** `33243206658`; Python compile, feature registry, code ownership, Python tests and executable Apps Script tests all succeeded.
- **PR merge/main readback:** `e412405a475d1423edaac821d7a99481e4a6eb4b`
- **Status:** read-only embedded Apps Script slice is merged/test-verified. Current sub-slice is proving stock ChatGPT's native authenticated Google Drive/Sheets path against the isolated synthetic MIRROR state before enabling any broader first-run mutation workflow.

## Objective

Prove the default Personal MIRA path without infrastructure administration. A copyable Google Workspace starter uses Sheets as the first structured MIRROR authority. Stock ChatGPT accesses that state through the user's authenticated Google Drive/Sheets connection. Bound Apps Script remains an embedded Google-side automation/validation layer rather than an anonymously exposed API gateway.

The intended first-use experience trends toward **copy starter → connect/authorize Google → initialize MIRA → use MIRA in ChatGPT**, not Cloud Console, SSH, Docker, Linux, SQL or terminal commands.

## Acceptance criteria

1. **No infrastructure prerequisite.** No self-hosted server, Cloud Run project, Linux/SQL administration, Cloudflare/WireGuard tunnel, terminal, or paid OpenAI API usage is required for the Personal baseline.
2. **Copyable Workspace packaging.** Starter data/scripts contain no personal provider IDs or secrets in public source.
3. **Same MIRA semantics.** Google-specific transport/storage must preserve the canonical `API-001`, `AUTH-001`, `STORE-001` envelope/authority/revision/idempotency/readback model rather than create a second product model.
4. **Canonical authority.** All mutable structured state routes through persisted Authority semantics; no model/client silently becomes a second authority.
5. **Scoped authentication.** Stock ChatGPT uses the official same-user Google connection/authorization boundary. No bearer token is hidden in Sheet cells, URL parameters, prompt text or public Git.
6. **Google-backed roundtrip.** A synthetic entity can be created, exactly read back, mutated, replay-checked and provider-readback verified through the Workspace path.
7. **Browser-first.** Baseline setup remains browser-only.
8. **Legacy preservation.** Only isolated MIRA 2.0 synthetic/starter state is touched; legacy production Google artifacts remain protected.
9. **Portability.** Later migration through `AUTHORITY-MIGRATION-001` to Linux/SQL/Cloud Run must not require product-model rewrite or dual writable masters.
10. **Cloud Run does not block M2-M0.** `API-DEPLOYMENT-001B` remains advanced hardening.

## Completed evidence

### Workspace embedded runtime slice — merged

PR #50 introduced and test-verified:

- `workspace/apps_script/Code.gs`
  - `MIRA → Initialize this copy` browser action;
  - runtime-only copied spreadsheet binding via Script Properties;
  - web runtime reopens only the initialized copy;
  - `/v1/health`, `/v1/schema`, read-only `/v1/query`;
  - persisted `authority_binding` → `authority` resolution before canonical reads;
  - stable validation/error categories;
  - `/v1/commands` explicitly fails closed.
- `workspace/apps_script/appsscript.json` — bounded V8/current-Sheet manifest.
- `mira/workspace_bundle.py` — public-bundle/privacy validator.
- executable Node fake-Apps-Script tests plus Python bundle tests.
- CI run `33243206658` fully green.
- merge/main readback `e412405a475d1423edaac821d7a99481e4a6eb4b`.

### Client/auth architecture finding

Current OpenAI Google Drive app/actions expose authenticated Google Drive and Google Sheets read/write capabilities. Therefore the ordinary-user stock-ChatGPT path does **not** need to authenticate through an Apps Script public web endpoint. The user's Google connection is the client authorization boundary for the Personal baseline.

This also avoids a real Apps Script incompatibility: `doGet/doPost` event data does not expose arbitrary inbound HTTP headers, while standard GPT Action API-key authentication is header-based. Do not work around this by placing secrets in URL/query/body/visible Sheet data.

Apps Script remains useful for browser initialization, Google-side validation/automation and future non-ChatGPT execution surfaces; it is not required to be the first stock-ChatGPT transport.

## Current bounded sub-slice

**Native Google Drive/Sheets canonical roundtrip proof.**

Use the connected Google Drive/Sheets capability against only the isolated synthetic MIRROR spreadsheet. The proof must:

1. ground the exact synthetic spreadsheet by search + metadata;
2. read bounded `Metadata`, `Resources` and `Idempotency` state before any write;
3. verify the persisted canonical `authority_binding`/`authority` state;
4. choose a new synthetic entity ID only after proving it does not already exist;
5. perform one coherent Google Sheets mutation using the existing resource/idempotency row model;
6. exact-read the provider state back;
7. re-run the same logical request as an idempotency preflight and prove no duplicate mutation is required;
8. perform a revision-checked second mutation and exact readback;
9. record only non-sensitive evidence in Git; never commit spreadsheet IDs or private row contents.

This remains a **single-writer Personal proof**. Do not claim distributed compare-and-swap or safe multi-client Android concurrency from native connector operations. Multi-client synchronization may require a stronger execution boundary later.

## Scope control

Do not fan out into Gmail, Calendar, scheduler, Ops Briefs, family sharing, Android, enterprise distribution, Linux/SQL migration implementation or general UI polish. Do not resume Cloud Run. Do not touch legacy production artifacts.

## Exact next action

1. Execute the native Google Drive/Sheets synthetic roundtrip above.
2. If the official Google action path cannot preserve required MIRA integrity semantics, fail closed and record the exact missing capability instead of weakening idempotency/authority rules.
3. If it passes, update `BACKLOG.md`/`CURRENT_WORK.md` so `CHATGPT-API-CLIENT-001` reflects the native Google Workspace client path and record the provider proof without IDs/private data.
4. Then implement only the remaining first-run packaging/automation needed to make the successful path copyable for a new user.

## Recovery protocol

Read this file first. Verify `main` contains PR #50 merge `e412405a475d1423edaac821d7a99481e4a6eb4b` or a descendant. Continue only `M2-M0-006`. Preserve Cloud Run at `c392b9b829fab989be8856c9272294c9907e409e`; do not claim live Cloud Run evidence. Keep all provider IDs, secrets, personal data and live row contents out of public Git.
