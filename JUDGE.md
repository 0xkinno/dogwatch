# JUDGE.md

Demo video (2:52): https://youtu.be/GOJ-oNZSZw4

No login and no key are needed for any path below. Live app: https://dogwatch-eight.vercel.app (API: https://dogwatch-api.vercel.app/api/status, a substitute host). Every result says whether it is LIVE, DEMO (the same code path run in the browser) or RECORDED.

## 60 seconds

1. Open the live app and press Check on the contract card. The medical certificate lapses on day 42 of 181, with the rule quote and the arithmetic.
2. On `/judge`, run the offer flow. It runs triage, the Navigator and the plan writer.
3. Open `/proof`. Misses are listed first, case by case.

## 3 minutes

1. `/boundary`: the four allowed destinations, the prover results with counterexamples, the Seal decisions.
2. `/outbox`: a draft with placeholders and its digest. The real values are filled in only on the seafarer's machine after approval.
3. `/watch`: the document matrix, the sea-service ledger under each counting convention, and the model routing table.

## 10 minutes

1. Read `PLATFORM_PROBE.md` and `SDK_SURFACE.md` for what is live and what is not.
2. Clone and run the tests without any key:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
(cd core && python -m pytest -q)
(cd radio && python -m pytest -q)
(cd seal && python -m pytest -q)
python eval/run_seal_corpus.py
python eval/run_conventions.py
python scripts/check_facts.py
```

3. Reproduce a number: `docs/FACTS.json` is written by `scripts/facts.py` from `eval/results/`, and `scripts/check_facts.py` fails if the README or the UI disagrees.

## Which route ran the models

Every live model result ran on the NVIDIA API Catalog (development route); Nebius Token Factory is the submission target and its key was not available. Each result says which route produced it. `bash scripts/switch_to_tokenfactory.sh` re-runs the evidence on Token Factory.

## What to look for

- The Navigator never calls a model. Every verdict carries rule ids, source quotes, URLs, the pack hash and the arithmetic.
- A rule that could not be sourced does not exist: the Nigeria pack ships no rules, India has 2 and Singapore 4 (each quote verified against a snapshot read through Tavily Extract), and the engine answers Ask administration where no sourced rule exists, for example India's renewal window.
- Both versions of the Seal run are published, including the 8 attacks the first version missed.
