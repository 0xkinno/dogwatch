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
| OpenShell sandbox, Telegram first message, email | NOT RUN | `PLATFORM_PROBE.md` |
| P1 on the sandbox effective policy, P2, P4, P5 | NOT RUN (kernel below Landlock ABI 3) | `PROOF.md` |
