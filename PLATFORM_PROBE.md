# PLATFORM_PROBE.md

Written from real outputs on 2026-10-28 and 2026-10-29. Anything not run says NOT RUN and why. Raw outputs are in `evidence/probe/` and `evidence/prover/`.

## Build machine

| Item | Observed |
|---|---|
| Host | Windows 10 Pro (build 21996), WSL2 Ubuntu 24.04, default user root |
| WSL | inbox WSL, `wsl --version` unsupported, kernel 5.10.102.1-microsoft-standard-WSL2, systemd not PID 1 even with `systemd=true` in `/etc/wsl.conf` after `wsl --shutdown` |
| Docker in WSL | Engine 27.1.1 (API 1.46); a second Engine 28.0.4 ran on its own socket for OpenShell |
| Memory visible in WSL | about 7.6 GB, 8 logical CPUs |
| Python / Node | 3.12.10 / 24.14.1 |

## Model routes

Nebius Token Factory is the submission target. No Token Factory key exists (the promotional credit could not be claimed, card restrictions), so everything below ran on the NVIDIA API Catalog development route and says so. `bash scripts/switch_to_tokenfactory.sh` repeats the probe, P6, P8 and P12 on Token Factory.

### Route: NVIDIA API Catalog (development), `https://integrate.api.nvidia.com/v1`

| Step | State | Output |
|---|---|---|
| `GET /v1/models` | LIVE RUN | 84 models, 18 with "nemotron" in the id |
| Chat check of each Nemotron id | LIVE RUN | 200: `nemotron-3-nano-omni-30b-a3b-reasoning` (HTTP 503 worker limit when busy, retried), `nemotron-3.5-super-vl-120b-a12b`, `nemotron-3-ultra-550b-a55b` (503 when busy, 200 on retry), `nemotron-3.5-lightning-30b-a3b`, `nemotron-3.5-bolt-e4b`. 404 despite being listed: `nemotron-3-super-120b-a12b`, `nemotron-nano-3-30b-a3b`, `llama-3.1-nemotron-ultra-253b-v1`, `nemotron-4-340b-instruct` |
| Ids chosen | LIVE RUN | nano `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, super `nvidia/nemotron-3.5-super-vl-120b-a12b`, ultra `nvidia/nemotron-3-ultra-550b-a55b` (`docs/models.json`) |
| Thinking off versus on, one real Bosun extraction | LIVE RUN | off: 113 output tokens, about 1.7 s; on: 1,093 output tokens (925 reasoning), about 16.5 s |
| JSON schema enforcement | LIVE RUN | a prose-only instruction with a schema attached still returned schema-valid JSON in 3 of 3 trials, so the schema is enforced server side on this route; the client still validates with Pydantic |
| Repair path | LIVE RUN | the schema-driven call needed no repair; the repair retry is tested against a fake client |
| Price | not available | the route publishes no list price, so no dollar figure is computed |

### Route: Nebius Token Factory

NOT RUN. No key. Model ids in `routes.py` for this route are the ones named in the build notes and remain marked unconfirmed until the probe runs.

## OpenShell (release 0.1.6)

| Step | State | Output or reason |
|---|---|---|
| Install | LIVE RUN | `openshell 0.1.6`, `openshell-gateway`, `openshell-prover` from the official Debian package |
| Gateway start | LIVE RUN | by hand with `openshell/scripts/wsl-start.sh` and `seal-up.sh`; the packaged systemd user unit cannot run (no systemd) |
| Seal registered with the gateway | LIVE RUN | the gateway log reads `external middleware registration 'dogwatch-seal' uses dynamic binding discovery`; before registration, creating a sandbox with a policy that named the Seal failed with `middleware dogwatch-seal is not registered` |
| NVIDIA provider profile | LIVE RUN | `provider profile lint` passed, `import` imported 1, `provider create --name nvidia --type nvidia --credential NVIDIA_API_KEY` created it |
| Nebius Token Factory profile | WRITTEN | file is ready and unattached, as specified; lint and import need no key and are done by `switch_to_tokenfactory.sh` |
| Sandbox image | LIVE RUN | `openshell/sandbox/Dockerfile`, 285 MB, Python venv, Tesseract, Dogwatch core |
| `openshell sandbox create` | NOT RUN to completion | with Docker 27.1.1: `Docker responded with status code 500: getent unable to find entry "1000:1000" in passwd database` (Docker 28 is required). With Docker 28.0.4: container created, then `ControlSupervisorStartFailed: Docker sandbox exited before supervisor became ready` |
| Why the supervisor exits | diagnosed | the support matrix requires the Landlock LSM at ABI 3 or newer, introduced in Linux 6.2; this kernel is 5.10.102 |
| Content-guard example smoke test | NOT RUN | it needs the sandbox |
| Policy advisor | NOT RUN | needs a running sandbox |
| Sandboxed call, P2, P4, P5 | NOT RUN | need the sandbox |
| Boundary prover | LIVE RUN | results below |

### Prover results (`evidence/prover/`, re-run after the NVIDIA door and the sandbox user were added to the policy)

See `evidence/prover/*.result.txt`. The declared Dogwatch policy is within the boundary. The webhook, direct-Telegram and vault-write proposals exceed it with counterexamples; the wildcard proposal is refused as unsupported; the cloud-metadata proposal is within the boundary because the docs state that network policy never authorizes a link-local destination.

Findings, each reproducible and in `FRICTION.md`: REST endpoints need `enforcement: enforce` or the prover returns unsupported; a candidate with `network_middlewares` is unsupported; path comparison is path by path; the effective export needs a running sandbox, so the declared policy was checked.

## Tavily

LIVE RUN. The drift watch made 52 requests (10 searches, 42 extracts) across five administration domains (`eval/results/p9_drift.json`).

## NemoClaw, Hermes, Nebius AI Cloud

| Item | State |
|---|---|
| NemoClaw | NOT RUN. It sits on the OpenShell sandbox, which cannot start on this kernel |
| Hermes (`nemohermes`) | NOT RUN, designed |
| Nebius AI Cloud (Serverless Endpoint or VM) | NOT CHECKED. A Linux VM with a 6.2 or newer kernel and Docker is the host the sandbox needs |

## Tier decisions

| Tier | Decision |
|---|---|
| OpenShell policy, prover, provider profiles, gateway, Seal registration | in the build, LIVE RUN |
| OpenShell sandbox for the product | blocked by the host kernel; needs a Linux 6.2 or newer host |
| Hermes, NemoClaw, Nebius Serverless | designed, not run, not claimed |
| Model route | development route live; Token Factory pending a key |
| Hosted judge door host | substitute host, labelled in `/api/status` and the README; the product runs on the seafarer's machine |
