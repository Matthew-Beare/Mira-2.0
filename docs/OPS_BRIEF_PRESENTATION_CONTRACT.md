# MIRA Ops Brief presentation contract

Status: product-level user-facing projection contract.

This contract governs ordinary AM/PM brief presentation. It does not create a new data authority, provider integration, scheduler, notification path, or economic event.

## Executive-glance default

- Optimize for fast phone reading.
- Use short sections, whitespace, and bullets where they improve scanning.
- Show conclusions, exceptions, required actions, and material changes.
- Omit routine no-change statements and empty sections unless absence is itself operationally important.
- Keep provider mechanics, reconciliation plumbing, stable IDs, and successful routine checks behind the scenes unless a failure changes confidence or requires user action.

## Shipment/order presentation

- Never render tracking numbers or order numbers in an ordinary brief.
- Keep those identifiers internal for reconciliation and live-authority lookup.
- When a specific item/part name adequately identifies a shipment, render the item/part only.
- When only a generic item is known, render `item • vendor` when the vendor materially helps identify it.
- Omit carrier/vendor when it adds no useful distinction.
- Shipment ETA/progress/delivery state may be rendered only to the verification ceiling supported by the live mutable-state authority. Vendor/order mail alone is evidence, not automatic current carrier truth.

## Finance presentation

- Do not render a line merely to say that no financial activity occurred.
- Spend-control status uses the configured monthly budget with elapsed-month pacing unless that control explicitly specifies a different hard cap: approximately 25% by end week 1, 50% by end week 2, 75% by end week 3, and 100% by month-end.
- Distinguish `WATCH`/ahead-of-pace from actually exceeding the full monthly budget.
- Receipt/order evidence that is not matched to a posted provider transaction does not become posted spend.

## Charts

Use a chart only when it materially improves comprehension. Prefer at most one chart in an ordinary brief; detailed telemetry belongs on canonical dashboard/analysis surfaces.

## Failure behavior

One unavailable module must not suppress independent healthy modules. If a mutable fact cannot be verified to the required authority ceiling, omit it when nonessential or state the verification limit compactly when the uncertainty itself matters.
