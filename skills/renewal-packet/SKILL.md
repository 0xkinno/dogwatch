---
name: renewal-packet
description: Draft the renewal packet with placeholders and send it to the Radio Officer for approval.
---

# renewal-packet

## When to use
Draft the renewal packet with placeholders and send it to the Radio Officer for approval.

## Inputs
A profile JSON, a contract window, the manning agent address.

## Outputs
A draft with a digest posted to the Radio Officer. Nothing is sent until the seafarer approves that digest.

## Entry point
```bash
python -m dogwatch.skills.renewal_packet --help
```

## Safety notes
Only placeholders leave the sandbox. The Radio Officer refuses a draft that contains a vault value.

This skill is loaded by the Dogwatch Officer of the Watch and by any agent that reads SKILL.md folders.
