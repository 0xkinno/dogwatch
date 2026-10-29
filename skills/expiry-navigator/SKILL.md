---
name: expiry-navigator
description: Compute validity and windows for every document in a profile.
---

# expiry-navigator

## When to use
Compute validity and windows for every document in a profile.

## Inputs
A profile JSON and a contract window.

## Outputs
A state per document: VALID_THROUGH, LAPSES_DURING, EXPIRED_BEFORE_START, UNREAD, MISSING.

## Entry point
```bash
python -m dogwatch.skills.expiry_navigator --help
```

## Safety notes
Pure code. No model is called.

This skill is loaded by the Dogwatch Officer of the Watch and by any agent that reads SKILL.md folders.
