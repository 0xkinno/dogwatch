# THESIS.md

## One sentence

Dogwatch is an always-on, private assistant that keeps a seafarer's certificates under his control and has every renewal ready before a lapse costs him a contract.

## Five-line pitch

```
NAME:       Dogwatch (the short evening watch: someone keeps watch while you rest)
MOMENT:     Arjun, Second Officer on a product tanker, has 20 minutes of ship internet a day. A manning
            agent offers his next six month contract; one certificate lapses mid-contract and he would
            find out at the agency desk, not at sea.
ACTION:     Dogwatch reads his certificates on his own machine, computes every expiry and sea-service
            window in code, drafts the renewal packet, and sends it from Telegram with one approval.
DISCOVERY:  An assistant does not need to see your documents to help with them. OpenShell lets the
            assistant work with placeholders: the cloud model never sees a certificate number, a
            passport number or an API key, and a gateway outside the agent enforces it.
PROOF:      Injected manning-agency emails, encoded exfiltration attempts and a permissive model, run
            with and without the sandbox; an SMT-proven policy boundary; the rule engine against
            Nemotron alone on pre-registered cases; misses published.
```

## Hook (first spoken words)

"Arjun is on the four-to-eight watch in the Arabian Sea. His ship has twenty minutes of internet a day. A manning agent just offered him six months of work starting in February. His medical certificate expires in March. He will not find that out until he is standing at the agency desk, and the job will go to someone else. Dogwatch finds it tonight, on his own laptop, without his documents ever leaving it."

## X without Y

A personal assistant that handles your identity documents without ever seeing them.

## The guarantee

Arjun never learns about a lapsed certificate from a manning agent, and nothing that identifies him leaves his machine unless he approved that exact packet.

Internal claim: no value from the vault reaches any network destination except inside an approved packet whose digest the seafarer signed, and no validity verdict is produced by a model.

## The crew

| Member | Where | Job |
|---|---|---|
| Bosun | inside the sandbox | OCR, placeholders, structuring with a verbatim quote per field |
| Navigator | inside the sandbox | every verdict, in code, no model |
| Officer of the Watch | inside the sandbox | the always-on loop, triage, plan writing around locked values |
| Lookout | inside the sandbox | weekly rule-drift watch |
| Radio Officer | host side | Telegram, approval tokens, rehydration, email, calendar |
| The Seal | OpenShell middleware | denies any outbound request carrying a vault value |
| The Master | the seafarer | photographs stamps, approves packets and new access |

## What a model may and may not do

May: classify a message, structure placeholder text into fields with quotes, write prose around locked value tokens, read a regulator page and quote it.
May not: decide validity, compute a date or count, write a digit the seafarer will act on, see a raw identifier, change a rule pack.

## Interruption budget

At most two questions to Arjun per day. A lapse on an offered contract, and any approval request, always go through. Enforced in code in `watch/budget.py`.
