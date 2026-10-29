---
name: sea-service-ledger
description: Add a discharge-book entry and recompute sea-service totals under every counting convention.
---

# sea-service-ledger

## When to use
Add a discharge-book entry and recompute sea-service totals under every counting convention.

## Inputs
A ledger JSON, an optional new entry, a window.

## Outputs
Totals under days inclusive, days exclusive, calendar months, 360 day and 365 day conventions.

## Entry point
```bash
python -m dogwatch.skills.sea_service_ledger --help
```

## Safety notes
Overlapping entries count once. Where conventions disagree the answer is ASK_ADMINISTRATION.

This skill is loaded by the Dogwatch Officer of the Watch and by any agent that reads SKILL.md folders.
