# Evidence

Every claim in this repository points to a file here. States used throughout: LIVE RUN, LOCAL BUILD, FIXTURE, NOT RUN.

## Data status

- Arjun Menon is a fictional persona. Everything shown about him is invented for the demonstration.
- Specimen certificates are rendered by this project and labelled SPECIMEN on the image.
- Synthetic seafarer profiles used in the proof campaign are labelled SYNTHETIC.
- No real identifier, certificate image or personal document is committed anywhere in this repository.

## Index

| Area | State | Location |
|---|---|---|
| Repository safeguards (authorship, copy gate) | LOCAL BUILD | `.githooks/`, `.github/workflows/`, `scripts/check_copy.py` |
| OpenShell prover on the declared policy and attack proposals | LIVE RUN | `evidence/prover/`, `PLATFORM_PROBE.md` |
| Encoding corpus (P3), counting conventions (P7), Navigator against the oracle (P6 engine side) | LOCAL BUILD | `eval/results/`, `PROOF.md` |
| Restart with a pending approval (P11) | FIXTURE | `eval/results/p11_restart.json`, local capture transport |
| Web checks at eight viewports | LOCAL BUILD | `web/tests/layout.spec.ts`, screenshots in `docs/img/` |
| Model probe, P6 against Nemotron, P8, P9, P10, P12 | LIVE RUN (Route: NVIDIA API Catalog, development) | `evidence/probe/`, `evidence/receipts/`, `eval/results/`, `evidence/unattended/` |
| OpenShell gateway, provider profile, Seal registration | LIVE RUN | `PLATFORM_PROBE.md`, `openshell/scripts/` |
| Tavily | LIVE RUN | `eval/results/p9_drift.json` |
| Nebius Token Factory | NOT RUN (no key) | `scripts/switch_to_tokenfactory.sh` |
| Telegram and Resend live flow, P11 live | LIVE RUN (offer synthetic, approval by the driver, both labelled) | `evidence/actions/live-flow.json` |
| India and Singapore rule packs | LIVE RUN (read through Tavily Extract) | `core/rulepacks/*/sources/` |
| OpenShell sandbox | LIVE RUN on a GitHub Actions ubuntu-24.04 runner (runs 41009598425, 41012951503, 41017826733; not the seafarer's machine) | `evidence/boundary/run1/`, `run2/`, `run3/` |
| P1 on the sandbox effective policy | LIVE RUN: two excesses found and fixed; re-proof unsupported by the prover | `evidence/boundary/run3/prover/` |
| P2 injection inbox (20 of 20 sandboxed posts denied), P4 fail closed (403 with the Seal stopped) | LIVE RUN, valid, run 41017826733 | `evidence/boundary/run3/results/` |
| P5 credential placeholder (the agent saw only a placeholder; 0 real keys at the canary) | LIVE RUN, runs 41012951503 and 41017826733 | `evidence/boundary/run2/results/`, `run3/results/` |
| Advisor flow | LIVE RUN, partial (run 2, CLI) | `evidence/boundary/run2/results/` |
