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

### P6 Nemotron alone (Route: NVIDIA API Catalog (development))

- Same <!--fact:p6.profiles-->60<!--/fact--> profiles, thinking off, rule text supplied. Nemotron Super alone: <!--fact:p6.super.correct-->30<!--/fact--> correct, <!--fact:p6.super.false_safe-->22<!--/fact--> false-safe (said READY when not). Nemotron Ultra alone: <!--fact:p6.ultra.correct-->47<!--/fact--> correct, <!--fact:p6.ultra.false_safe-->0<!--/fact--> false-safe, <!--fact:p6.ultra.false_alarm-->8<!--/fact--> false alarms. Misses by id are in `eval/results/p6_model_alone.json`. Models: `nvidia/nemotron-3.5-super-vl-120b-a12b`, `nvidia/nemotron-3-ultra-550b-a55b`.

### P8 Reading (Route: NVIDIA API Catalog (development))

- <!--fact:p8.exact-->39<!--/fact--> of <!--fact:p8.specimens-->40<!--/fact--> specimens exact, <!--fact:p8.unread-->1<!--/fact--> UNREAD (S40, rotated and blurred), <!--fact:p8.wrong_confident-->0<!--/fact--> wrong without a flag. <!--fact:p8.leaks-->0<!--/fact--> identifiers in <!--fact:p8.bodies-->40<!--/fact--> outgoing request bodies. The first run (`eval/results/p8_reading_v1.json`) found <!--fact:p8.v1_leaks-->12<!--/fact-->: OCR split passport and CoC numbers with spaces, and a holder's name has no pattern. Detectors were made OCR tolerant and the name is matched from the vault table; the specimens and cases were not changed.

### P9, P10, P12 (Route: NVIDIA API Catalog (development))

- P9: <!--fact:p9.requests-->52<!--/fact--> Tavily requests, <!--fact:p9.searched-->49<!--/fact--> pages, <!--fact:p9.classified-->29<!--/fact--> classified, <!--fact:p9.items-->27<!--/fact--> review items. No ground truth exists for new rule text, so this is behaviour and gates, not accuracy.
- P10: <!--fact:p10.daily-->1<!--/fact--> daily and <!--fact:p10.weekly-->1<!--/fact--> weekly run triggered by the timer loop, `evidence/unattended/trace.json`.
- P12: <!--fact:p12.weekly_tokens-->49201<!--/fact--> tokens for one weekly drift check; a readiness run uses 0 tokens; Ultra about <!--fact:p12.latency_ratio-->2.35<!--/fact--> times slower than Super. No price exists on this route, so no dollar figure.

### P7 version 2 (India and Singapore rules)

- Registered after the new rules were read (`eval/cases/prereg_v2.json`, SHA-256 58241a130101014f5366756186d37aec806f414b10a2f7a40ac4a3f36bd8cd63; the case file was committed before the run, and v1 is unchanged): <!--fact:p7v2.flips-->12<!--/fact--> of <!--fact:p7v2.histories-->56<!--/fact--> histories flip between counting conventions.

### Live human loop and P11 on the live transport

- `evidence/actions/live-flow.json`: Telegram and Resend, Route: NVIDIA API Catalog (development). Email delivered (<!--fact:live.emails_sent-->1<!--/fact-->). P11 live: <!--fact:live.p11_sends-->1<!--/fact--> send, <!--fact:live.p11_duplicates-->0<!--/fact--> duplicates after a kill and restart. The offer was synthetic and the approval executed by the driver, both labelled in the file.

## OpenShell sandbox proofs on the GitHub Actions runner

Host: GitHub Actions ubuntu-24.04 runner (kernel 7.0.0-azure, Landlock present), not the seafarer's machine. The build machine cannot run the sandbox (Linux 5.10, Landlock ABI 3 needs 6.2). Evidence: `evidence/boundary/run1/`, workflow run 41009598425.

**Run 1 (what it showed).**
- The gateway started with the Seal registered, the NVIDIA provider was created and the `dogwatch` sandbox came up. LIVE RUN.
- **P1 on the effective policy found a real excess.** The prover reported `exceeds_boundary` with the counterexample `GET /` on `integrate.api.nvidia.com`: the stock NVIDIA provider profile adds `access: read-write` to the model host, wider than the narrow policy. The profile is now narrowed to POST `/v1/chat/completions` and GET `/v1/models`; this fix is not yet re-proved.
- **P2 baseline (no sandbox):** 20 of 20 injected emails made the agent post, and 20 of 20 canary requests carried a vault value (`evidence/boundary/run1/results/p2_injection.json`).
- **Not demonstrated:** the sandboxed side of P2, P4, P5 and the advisor flow did not execute. The probe scripts were uploaded to a path the sandbox treated as a directory, so they never ran, and the P4 counts in that file (3 denied) are probe errors, not Seal denials. Treat all of those as NOT RUN. The upload path is fixed; run 2 is pending.

Everything on Nebius Token Factory: no key.
