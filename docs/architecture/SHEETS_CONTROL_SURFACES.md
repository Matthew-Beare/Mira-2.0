# Google Sheets operational control surfaces

Status: M2-M1-020 foundation architecture, backed by implemented provider-neutral contracts in `mira/sheets_control.py`.

## Authority boundary

MIRROR remains canonical reality state. Google Sheets is a human-facing operational surface for inspection, filtering, analysis, controlled correction, reconciliation, dashboards and temporary modelling.

A Sheet/range/view must declare exactly one role:

1. canonical read-only projection;
2. controlled editable projection;
3. derived analytical view;
4. temporary non-authoritative prototype;
5. reconciliation queue;
6. generated dashboard.

A controlled edit never writes canonical state merely because a cell changed. It is converted into a revision-bound write-back plan, executed later through the canonical authority path, and must be followed by exact canonical/provider readback. If MIRROR changed since the row was projected, the edit becomes a conflict for explicit reconciliation rather than silently overwriting newer truth.

Runtime spreadsheet IDs, Drive IDs, provider credentials and private row data are separate from public feature manifests.

## Google capabilities to exploit deliberately

The Sheets API `spreadsheets.batchUpdate` surface can create/update/delete native Tables and can manage data validation, developer metadata, filter views, named ranges, protected ranges, charts, conditional formatting and slicers. Batch updates are atomic, so a malformed subrequest fails the whole update. Use field masks for narrow updates.

Native Sheets Tables are useful for human-facing operational data because they provide column types, structured references, table views/filtering and group-by views. Tables should be preferred for structured console surfaces when they improve usability.

Table references are useful in formulas because they expand with table data. Google currently documents an important limitation: table references are not supported as selected ranges for conditional formatting, charts or pivot tables. Therefore a MIRA renderer should use native Tables for the human table while generating concrete GridRanges/named ranges for charts, pivots and conditional-formatting rules instead of pretending one symbolic reference works everywhere.

`developerMetadata` plus DataFilter-capable APIs are high-value infrastructure for tagging feature ID, projection ID, schema version, role and generated-object ownership without relying solely on tab names or coordinates. Metadata is provider-side lookup metadata, never canonical record identity.

Filter views are preferable to a single shared basic filter for operational boards because users can inspect different slices without stomping on one another's current view. Slicers are useful for dashboard dimensions such as market, employer, role family, application status, drawdown category, necessity, vehicle and inventory category when the underlying range is appropriate.

Protected ranges should cover technical identity/revision/readback/reconciliation columns. Human-visible business columns may remain editable only when the feature definition explicitly allows write-back.

Hyperlinks/deep links should connect operational rows to canonical evidence or legitimate provider resources where available: source job/profile pages, receipts, manuals, Drive files, Git commits/PRs and other evidence. The link itself is a projection convenience, not authority.

## API and Apps Script limits that materially affect MIRA

Verified against current Google documentation in September 2026:

- Google Sheets files support up to 10 million cells or 18,278 columns.
- Sheets API read quota: 300 requests/minute/project and 60 requests/minute/user/project.
- Sheets API write quota: 300 requests/minute/project and 60 requests/minute/user/project.
- Google recommends keeping API payloads around 2 MB or smaller for speed; one request can time out after 180 seconds.
- Batch requests count as one API request toward the quota and are atomic.
- Apps Script runtime is 6 minutes per execution; custom functions and simple triggers have a 30-second execution limit.
- Apps Script supports 20 triggers per user per script. Trigger total runtime is 90 minutes/day for consumer accounts and 6 hours/day for Google Workspace accounts.
- Script/API-originated edits do not fire `onEdit`. Therefore MIRA must not depend on `onEdit` to observe its own API writes or to guarantee reconciliation.
- Simple triggers cannot use services that require authorization and are bound-file limited. Installable triggers/time-driven triggers are more capable but still have quotas and do not fire from script/API edits.

Architecture consequences:

1. batch reads/writes and formatting/object creation instead of cell-at-a-time loops;
2. explicit refresh/write-back actions or installable/time-driven automation rather than trigger folklore;
3. idempotent chunking/checkpoints for work that could exceed Apps Script runtime;
4. exponential backoff for quota pressure;
5. formulas remain lightweight presentation/analysis aids, not the durable compute engine;
6. large transaction/event histories should be partitioned/rolled up or projected from a larger backend before the 10-million-cell ceiling becomes operationally relevant;
7. `IMPORTRANGE`, large `QUERY` chains and cross-sheet dependency webs are avoided for core integrity paths because they create performance and failure coupling;
8. BigQuery/Connected Sheets is a future analytical option when data scale genuinely warrants it, not a prerequisite for ordinary Personal MIRA.

## Formula policy

Good uses of formulas include lightweight human analysis and presentation: simple `QUERY`, `FILTER`, `SORT`, `UNIQUE`, lookups, array transforms, SPARKLINE and dashboard helper ranges where they remain understandable and cheap.

Do not implement durable identity, provenance, deduplication, canonical transaction classification, qualification matching, service-due logic, reconciliation, conflict policy or other domain rules primarily as spreadsheet formulas. Those belong in MIRA/MIRROR where they are testable and portable.

Gemini in Sheets may be useful as an optional user-side exploratory copilot on eligible Google plans, but it is plan-dependent and non-deterministic. MIRA feature correctness, installation and automation must not depend on Gemini in Sheets.

## Apps Script policy

Apps Script can add real value for custom menus, sidebars, buttons, feature initialization, explicit refresh/reconcile commands and bounded scheduled maintenance. Keep it thin:

- UI/control-plane glue, not duplicated domain logic;
- enqueue or invoke canonical operations rather than directly inventing truth;
- idempotent, resumable and quota-aware;
- no claim that a trigger ran until provider/runtime evidence proves it;
- no silent outreach or unrelated provider actions.

## Additional high-value Sheets ideas

1. **Developer-metadata anchors:** tag generated tabs/ranges/objects with feature/projection/schema identifiers so renames/reordering do not destroy MIRA's ability to recognize its own surface.
2. **Data Health console:** a reusable cross-feature view of stale, missing, conflicting, low-confidence and failed-reconciliation rows.
3. **Decision queues, not free-form write zones:** expose compact allowlisted human decisions such as classification corrections, application status, follow-up action or reconciliation choice while provider/canonical observations remain protected.
4. **Generated view packs:** declare useful filter views/slicers from feature configuration so installing a market or domain produces consistent operational views instead of hand-built one-offs.
5. **Technical-column quarantine:** hide/protect stable identity, MIRROR revision, read timestamp and reconciliation state while keeping them inspectable for diagnostics.
6. **Formula-light dashboards:** MIRA computes integrity-sensitive analytical fields; Sheets handles pivots/charts/slicers/conditional display. This keeps dashboards fast and logic testable.
7. **Evidence/deep-link columns:** one click from a row to the underlying source/evidence/provider resource when legitimate and available.
8. **Market-board factory:** Dallas/DFW, Austin and RTP differ by configuration. Future markets should be created by the same manifest/renderer path.
9. **Explicit prototype banner/metadata:** temporary modelling sheets should carry a conspicuous non-authoritative role and schema/version metadata so useful experiments cannot quietly become shadow MIRROR databases.
10. **Scale tripwires:** surface row/cell/formula/refresh-health telemetry before a Sheet gets near practical scale limits, then move heavy analytical history behind an appropriate backend while preserving the same human projection contract.

## Sources checked

- Google Sheets API, Update spreadsheets / `batchUpdate`: https://developers.google.com/workspace/sheets/api/guides/batchupdate
- Google Sheets API, Read and write cell values: https://developers.google.com/workspace/sheets/api/guides/values
- Google Sheets API, Usage limits: https://developers.google.com/workspace/sheets/api/limits
- Google Docs Editors Help, Use tables in Google Sheets: https://support.google.com/docs/answer/14239833
- Google Docs Editors Help, Use table references in Google Sheets: https://support.google.com/docs/answer/15637642
- Google Drive Help, Files you can store in Google Drive: https://support.google.com/drive/answer/37603
- Apps Script, Quotas for Google Services: https://developers.google.com/apps-script/guides/services/quotas
- Apps Script, Simple Triggers: https://developers.google.com/apps-script/guides/triggers
- Apps Script, Installable Triggers: https://developers.google.com/apps-script/guides/triggers/installable
