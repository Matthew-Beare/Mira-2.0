# Financial Escape chart audit — 2026-09-07

## Scope

This is a privacy-sanitized audit of the private live MIRA Financial Escape workbook's chart/projection layer. It records chart requirements, preservation, source-of-truth wiring, and corrective work without recording private transaction values, vendors, account identifiers, provider identifiers, or workbook identifiers.

The audit does not create a second finance authority. MIRROR remains one logical reality model. Workbook charts, support tables, dashboards, and review surfaces are projections or human-input views over canonical finance/event state.

## Durable requirement sources

The audit compared:

1. the historical `M2-M1-013` acceptance requirement for separate trend visuals, including mileage-versus-required, debt-versus-target, retirement contributions, normalized-spend-versus-budget, and forecast comparison;
2. retained pre-UI-cleanup workbook backups for embedded-chart preservation;
3. the current private live workbook's embedded chart metadata and exported chart types;
4. live formula readback for category/vendor and spending-telemetry chart support ranges.

Conversation-only recollections are not treated as stronger authority than Git-backed acceptance criteria plus retained live/backed-up artifacts.

## Findings

### Preserved visual history

The UI cleanup preserved the prior visual set rather than deleting it:

- the prior forecast/graph surface retained its five historical forecast charts;
- the prior monthly-pie surface retained all eighteen month-by-category and month-by-vendor pie charts for the represented months;
- the household-income bar chart remained present on its projection source.

The old monthly-pie surface was renamed during UI cleanup; its embedded chart identities and titles were preserved.

### Corrective defect found

Historical acceptance explicitly required a retirement-contributions trend, but the current visible forecast surface did not contain that chart. The live workbook was corrected by restoring a retirement-contributions line chart sourced from a dynamic filtered projection of retirement-contribution records. The forecast surface now carries six line charts, preserving the original five plus the restored requirement.

### Classification charts are canonical and live

Monthly category pies are sourced from the canonical FinOps event ledger's **effective category**, not from a stale copied category. Human review writes category overrides through the review surface; the ledger resolves the effective category; chart support queries aggregate that effective category; the pie charts consume those query results.

Therefore `Unknown` is intentionally visible while evidence/review is unresolved and automatically decreases or disappears as those same event records are classified. Historical rows are not guessed merely to make a chart look complete.

### Spending telemetry visual layer added

The live spending-insights surface now includes chart projections for:

- latest-month spend by category;
- latest-month spend by necessity;
- latest-month spend by allowance;
- latest-month review completion;
- monthly spend by necessity;
- monthly spend by allowance;
- known-versus-unknown category share by month;
- top allowance-bending vendors.

The monthly categorical support tables seed zero-value members where necessary so a temporarily absent class (for example, an allowance class with no current transactions) does not cause the chart schema to lose that series.

## Verification

Live metadata readback after correction reports **33 embedded charts** across the workbook:

- 6 forecast line charts;
- 18 monthly spend pie charts;
- 8 spending-insight charts;
- 1 household-income bar chart.

A fresh workbook export was inspected to verify that the embedded chart objects have the expected line, pie, and bar/column chart types. Formula readback confirmed that the monthly category and vendor projections reference canonical effective fields in the FinOps ledger and that the new spending-insight support queries are live formulas rather than pasted snapshots.

## Ongoing invariant

Any future finance chart that depends on transaction classification must read canonical effective fields from the one MIRROR finance model. Human review surfaces may edit overrides, and dashboards/charts may project the results, but neither may become a second transaction database or independent authority.

`Unknown` is a legitimate review state, not a cosmetic error. It must remain measurable until resolved by evidence or explicit human classification.
