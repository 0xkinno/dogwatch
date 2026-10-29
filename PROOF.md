# PROOF.md

Every set is pre-registered: the case files and `eval/cases/prereg.json` are committed and their SHA-256 recorded here before the run. Case files are never edited after their run. Misses stay in the denominator and are listed by id.

## Pre-registration

| Item | SHA-256 | Registered |
|---|---|---|
| `eval/cases/prereg.json` | 5d80256515ad2b45e2bb06566c63be1455957ab154731ef4e07ee0e73abc2fa9 | 2026-10-28, before any evaluation run |

The prereg file lists the SHA-256 of each case file. Results are added below by `scripts/facts.py` and the run scripts.

## Results so far

Numbers below are generated from `eval/results/` through `docs/FACTS.json`; `scripts/check_facts.py` fails CI if they drift. The sets are built by this project, so they are internal measurements, labelled as such, and the headline proof is the prover and the unmodified-agent comparisons listed as NOT RUN until they run.

### P3 Encoding corpus (LOCAL BUILD, synthetic values)

- Cases: <!--fact:p3.attacks-->200<!--/fact--> attack bodies across 20 transforms, <!--fact:p3.legit-->200<!--/fact--> legitimate bodies. Each case by id is in `eval/results/p3_seal_corpus.json`.
- Literal-only guard: let through <!--fact:p3.literal.missed-->158<!--/fact--> of 200 attacks, blocked <!--fact:p3.literal.false_blocks-->0<!--/fact--> legitimate bodies.
- The Seal, first version: let through <!--fact:p3.seal_v1.missed-->8<!--/fact--> of 200. Every miss was a base64 token shorter than the 12 character minimum the build notes specified (`eval/results/p3_seal_corpus_v1.json`, ids A001, A005, A006, A010, A123, A124, A128, A129).
- The Seal, second version (minimum lowered to 8 characters after seeing the misses): let through <!--fact:p3.seal.missed-->0<!--/fact-->, blocked <!--fact:p3.seal.false_blocks-->0<!--/fact--> legitimate bodies. The v2 number was reached by fixing the misses the first run showed, on the same cases, so it is a regression check and not an independent score. A fresh corpus is the next test.
- Limits: short values under 5 characters are ignored by design; values split across two separate HTTP requests are not detected by a per-request guard.

### P6 Navigator against the oracle (LOCAL BUILD, synthetic profiles)

- <!--fact:p6.profiles-->60<!--/fact--> profiles, expected verdicts written by an independent oracle before the run. The Navigator matched <!--fact:p6.engine.correct-->60<!--/fact-->; false-safe <!--fact:p6.engine.false_safe-->0<!--/fact-->.
- This is a self-built set and is not the headline. The comparison with Nemotron on the same profiles is NOT RUN until a Token Factory key is available.

### P7 Counting conventions (LOCAL BUILD, synthetic histories)

- <!--fact:p7.histories-->60<!--/fact--> histories near the revalidation thresholds; <!--fact:p7.flips-->7<!--/fact--> flip between counting conventions.
- Sourced rules that state a counting convention: <!--fact:p7.rules_stating_convention-->0<!--/fact-->. The convention is not stated in the sources read, so near-boundary cases return ASK_ADMINISTRATION.

### P11 Restart (FIXTURE transport)

- After a kill with one approved packet pending and a restart: <!--fact:p11.sends-->1<!--/fact--> send, <!--fact:p11.duplicates-->0<!--/fact--> duplicates. The mail transport is a local capture, so this proves the state machine and the idempotency key, not a mail provider.

## NOT RUN yet

P1 prover (needs OpenShell), P2 injection inbox, P4 fail closed, P5 credential placeholder, P6 against Nemotron, P8 reading, P9 drift, P10 unattended, P12 cost. Each needs a key or the OpenShell stack and is tracked in `TASK.md`.
