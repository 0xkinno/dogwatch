# PLATFORM_PROBE.md

Written from real outputs on 2026-10-28. Anything not run says NOT RUN and why. This file is updated as each primitive is reached.

## Build machine

| Item | Observed |
|---|---|
| Host | Windows 10 Pro, WSL2 Ubuntu 24.04 (default distribution, runs as root) |
| Docker in WSL | 27.1.1 |
| Memory visible in WSL | about 7 GB, 8 logical CPUs (under the 8 GB minimum NemoClaw lists) |
| Python | 3.12.10 (Windows) |
| Node | v24.14.1 |

## OpenShell

| Step | State | Output or reason |
|---|---|---|
| Installer read before running | done | `install.sh` from the cloned repository, which installs the Debian package from a GitHub release and checks it against the release checksums file |
| Install | LIVE RUN | `openshell 0.1.6` installed as package `openshell_0.1.6-1_amd64.deb`; binaries `openshell`, `openshell-gateway`, `openshell-prover` on the path. The cloned repository HEAD is newer than this release (the docs read for the build come from HEAD) |
| Gateway start | NOT RUN | The installer printed `Failed to connect to bus: No such file or directory` and `could not reach the user systemd manager for root`. WSL has no user systemd session for root, so `systemctl --user` is unavailable. A manual gateway start is the next step |
| `openshell sandbox create` | NOT RUN | needs the gateway |
| Provider profile lint and import | NOT RUN | needs the gateway; the profile file is written in `openshell/profiles/` |
| Content-guard example smoke test | NOT RUN | its script builds Rust crates and needs `mise`, `cargo`, `uv`; not attempted yet |
| Policy advisor | NOT RUN | needs a running sandbox |
| Boundary prover | LIVE RUN | `openshell-prover check`, results below |

### Prover results (real output, `evidence/prover/`)

| Candidate | Result | Detail |
|---|---|---|
| Declared Dogwatch policy | within_boundary | candidate is `dogwatch.yaml` without the `network_middlewares` block |
| Webhook host | exceeds_boundary | counterexample host `webhook.site:443`, POST |
| Wildcard host `*.com` | unsupported | `overlapping exact and wildcard endpoints with different implicit destination IP modes` |
| Cloud metadata address | within_boundary | the docs state that network policy never authorizes a link-local destination, so the rule adds no access |
| Telegram API from the sandbox | exceeds_boundary | counterexample host `api.telegram.org:443`, POST |
| Write to `/vault` | exceeds_boundary | `filesystem write /vault`, against a focused boundary that grants no write access |

Findings from getting there, each reproducible:

1. A REST endpoint without `enforcement: enforce` makes the prover return `unsupported` (`uses REST without enforced inspection`). The first run of every file returned that until the field was added.
2. A candidate that contains `network_middlewares` returns `unsupported` (`uses network middleware controls`). The prover cannot check the Seal's registration, so the Seal is tested separately.
3. A candidate path under a different path than the boundary (for example `/etc` written when the boundary lists writable `/sandbox` and `/tmp`) returns `unsupported`, not `exceeds_boundary`. The docs describe this (path by path comparison); a focused boundary was used for the vault write case.
4. The sandbox effective export (`openshell sandbox get dogwatch --policy-only`) was not available, so the declared policy was checked. The claim "the running sandbox is within the boundary" is therefore NOT RUN.

## Nebius Token Factory

| Step | State | Reason |
|---|---|---|
| `GET /v1/models`, exact Nemotron ids | NOT RUN | no `NEBIUS_API_KEY` yet. Model ids in `core/dogwatch/model/routing.py` are marked unconfirmed until this runs |
| Thinking on versus off, one real extraction | NOT RUN | needs the key |
| JSON schema enforcement and the repair path | NOT RUN against the live API | the repair path is tested against a fake client |
| Sandboxed call with a placeholder key | NOT RUN | needs the gateway and the key |

## Tavily

NOT RUN: no `TAVILY_API_KEY` yet. The client and gates are tested against a fake transport.

## NemoClaw, Hermes, Nebius AI Cloud

| Item | State |
|---|---|
| NemoClaw install | NOT RUN. Memory visible to WSL is under the stated minimum, and it depends on the gateway |
| Hermes (`nemohermes`) | NOT RUN. Marked designed, not run |
| Nebius AI Cloud (Serverless Endpoint or VM) | NOT CHECKED. Needs console access |

## Tier decisions

| Tier | Decision |
|---|---|
| OpenShell policy and prover | in the build, LOCAL BUILD |
| Seal as supervisor middleware | built against the proto and tested over gRPC; registered in a running gateway: pending the gateway |
| OpenShell sandbox for the product | pending the gateway start |
| Hermes, NemoClaw, Nebius Serverless | designed, not run, not claimed |
| Hosted judge door host | substitute host, labelled in `/api/status` and the README; the product runs on the seafarer's machine |
