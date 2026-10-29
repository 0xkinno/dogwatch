# SDK_SURFACE.md

Every sponsor feature, where it is used, its version, and whether it is live, recorded, designed, or not used. Versions: OpenShell release 0.1.6 installed on the build machine (docs read from the repository HEAD of 2026-10-28). Line numbers are in this repository.

| Feature | Where | State | Note |
|---|---|---|---|
| OpenShell policy prover (`openshell-prover check`) | `openshell/scripts/prove.sh`, `evidence/prover/` | LIVE RUN on the build machine | Candidate is the declared policy; the sandbox effective export is NOT RUN |
| OpenShell policy schema (filesystem, network_policies, L7 rules) | `openshell/policy/dogwatch.yaml`, `openshell/policy/boundary.yaml` | LOCAL BUILD | Checked by the prover; not applied to a running sandbox |
| OpenShell provider profile format | `openshell/profiles/nebius-token-factory.yaml:9`, `openshell/profiles/tavily.yaml:2` | WRITTEN | Lint and import NOT RUN (needs the gateway) |
| OpenShell supervisor middleware service (`SupervisorMiddleware`) | `seal/seal/server.py:49` (`Describe`), `seal/seal/server.py:66` (`EvaluateHttpRequest`) | LOCAL BUILD | Implemented against `seal/proto/supervisor_middleware.proto`, exercised over gRPC in `seal/tests/test_seal.py`. Registered in a running gateway: NOT RUN |
| Middleware registration with `on_error: fail_closed` | `openshell/policy/dogwatch.yaml:12` | WRITTEN | Fail-closed behaviour (P4) NOT RUN |
| 4.5 MiB gRPC message limit | `seal/seal/server.py:84` | LOCAL BUILD | A 3 MB body is handled in the Seal tests |
| OpenShell policy advisor (`policy.local`) | doors diagram on `/boundary` | NOT RUN | Designed |
| OpenShell sandbox and credential placeholders | `openshell/scripts/up.sh` | NOT RUN | Needs the gateway |
| Nebius Token Factory chat completions | `core/dogwatch/model/client.py:80` (thinking flag), `:99` (`structured`) | NOT RUN against the live API | Tested against a fake client including the repair retry |
| Nemotron Nano, Super, Ultra routing | `core/dogwatch/model/routing.py` | NOT RUN | Ids unconfirmed until the probe writes `docs/models.json` |
| Tavily Search and Extract | `core/dogwatch/lookout/tavily.py`, `core/dogwatch/lookout/drift.py:67` | NOT RUN against the live API | Tested against a fake transport |
| NVIDIA NemoClaw | not used | NOT USED | Not used, so not claimed |
| Hermes Agent (`nemohermes`) | skills are in `skills/` as SKILL.md folders | DESIGNED | Not run inside Hermes, so reuse by Hermes is not claimed |
| Nebius Serverless | not used | NOT USED | Not used, so not claimed |
