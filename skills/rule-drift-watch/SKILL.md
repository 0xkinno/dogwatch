---
name: rule-drift-watch
description: Run the Lookout once: Tavily search and extract on administration sites, gated by domain, keyword and verified quote.
---

# rule-drift-watch

## When to use
Run the Lookout once: Tavily search and extract on administration sites, gated by domain, keyword and verified quote.

## Inputs
None.

## Outputs
Review items, or DRIFT_UNAVAILABLE when Tavily cannot be reached.

## Entry point
```bash
python -m dogwatch.skills.rule_drift_watch --help
```

## Safety notes
Review items only. A rule pack changes only when a person releases a new version.

This skill is loaded by the Dogwatch Officer of the Watch and by any agent that reads SKILL.md folders.
