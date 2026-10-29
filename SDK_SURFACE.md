# SDK_SURFACE.md

Every sponsor feature, where it is used, its version, and whether it is live, recorded, designed, or not used. Versions: OpenShell release 0.1.6 installed on the build machine (docs read from the repository HEAD of 2026-10-28). Line numbers are in this repository.

| Feature | Where | State | Note |
|---|---|---|---|
| OpenShell policy prover (`openshell-prover check`) | `openshell/scripts/prove.sh`, `evidence/prover/` | LIVE RUN, release 0.1.6 | Declared policy checked; the sandbox effective export is NOT RUN |
| OpenShell policy schema (filesystem, process, network_policies, L7 rules) | `openshell/policy/dogwatch.yaml`, `boundary.yaml` | LIVE RUN (prover) | Not applied to a running sandbox |
| OpenShell gateway | `openshell/scripts/wsl-start.sh`, `seal-up.sh` | LIVE RUN | Started by hand; the systemd unit needs a user systemd session |
| Provider profile, stock NVIDIA | `openshell/profiles/nvidia-build.yaml` | LIVE RUN | lint, import, `provider create` succeeded; attached to the dev route |
| Provider profile, Nebius Token Factory | `openshell/profiles/nebius-token-factory.yaml` | WRITTEN, unattached | `switch_to_tokenfactory.sh` imports and attaches it |
| Supervisor middleware service (the Seal) | `seal/seal/server.py` (`Describe`, `EvaluateHttpRequest`) | LIVE RUN: registered with the gateway; LOCAL BUILD over gRPC | Traffic decisions through a running sandbox NOT RUN |
| Middleware registration, `on_error: fail_closed` | `openshell/policy/dogwatch.yaml`, gateway TOML written by `seal-up.sh` | LIVE RUN (admission refused an unregistered middleware) | Runtime fail-closed (P4) NOT RUN |
| Sandbox image | `openshell/sandbox/Dockerfile` | LIVE RUN (built) | |
| OpenShell sandbox, policy advisor, credential placeholders at egress | `openshell/scripts/up.sh` | NOT RUN | supervisor exits: Landlock ABI 3 needs Linux 6.2, kernel is 5.10 |
| Model route: NVIDIA API Catalog (development) | `core/dogwatch/model/routes.py`, `client.py` | LIVE RUN | probe, P6, P8, P9, P10, P12 |
| Model route: Nebius Token Factory | `core/dogwatch/model/routes.py` | NOT RUN | no key; default whenever `NEBIUS_API_KEY` exists |
| Nemotron Nano, Super, Ultra routing | `core/dogwatch/model/routing.py`, `docs/models.json` | LIVE RUN (dev route) | ids confirmed from `GET /models` plus a chat check |
| Tavily Search and Extract | `core/dogwatch/lookout/tavily.py`, `drift.py` | LIVE RUN | P9 and P10 |
| NVIDIA NemoClaw | not used | NOT USED | Not used, so not claimed |
| Hermes Agent (`nemohermes`) | skills are in `skills/` as SKILL.md folders | DESIGNED | Not run inside Hermes |
| Nebius Serverless | not used | NOT USED | Not used, so not claimed |
