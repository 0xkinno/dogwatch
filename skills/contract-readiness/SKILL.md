---
name: contract-readiness
description: Check a contract window and return READY, NOT_READY or CANNOT_VERIFY.
---

# contract-readiness

## When to use
Check a contract window and return READY, NOT_READY or CANNOT_VERIFY.

## Inputs
A profile JSON, start and end dates, optional travel days.

## Outputs
The overall verdict and a one-line summary with the day count.

## Entry point
```bash
python -m dogwatch.skills.contract_readiness --help
```

## Safety notes
Pure code. A missing or unread fact can never produce READY.

This skill is loaded by the Dogwatch Officer of the Watch and by any agent that reads SKILL.md folders.
