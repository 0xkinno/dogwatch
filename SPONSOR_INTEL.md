# SPONSOR_INTEL.md

Read from clones in `reference/` on 28 Oct 2026. OpenShell HEAD fdce6ef (2026-10-28), NemoClaw f568a3f (2026-10-28), Hermes agent 82096747 (2026-10-28). Docs move quickly; re-read the cited path before building on it.

## OpenShell

| Primitive | Path | Status | Use in Dogwatch |
|---|---|---|---|
| Sandbox with filesystem, process and network policy | `docs/how-it-works/policies/overview.mdx`, `schema.mdx` | released | Sandbox "dogwatch": read-only vault, no other network |
| Provider profiles and credential placeholders | `providers/nvidia.yaml`, `docs/how-it-works/inference.mdx` | released | Our own Token Factory profile (no such profile ships) |
| L7 REST rules, `deny_rules`, per-binary matching | `docs/how-it-works/policies/network-rules.mdx` | released | Method and path allowlist per door |
| Supervisor middleware (research preview, `fail_closed` default) | `proto/supervisor_middleware.proto`, `docs/how-it-works/policies/schema.mdx` (Network Middleware) | research preview | The Seal |
| Content guard example | `examples/supervisor-middleware-content-guard/` | example, "not a complete or reliable content guard" | Baseline for the encoding corpus |
| Policy prover (SMT) | `crates/openshell-prover*`, `docs/how-it-works/policies/prover.mdx` | released | Boundary proof and attack proposals |
| Policy advisor | `docs/how-it-works/policies/advisor.mdx`, `examples/policy-advisor/` | released, off by default | Denied request becomes a proposal the seafarer rejects |
| Policy export | `openshell sandbox get <name> --policy-only` | released | Effective policy for the prover |
| Platforms | `WINDOWS.md` | Linux, macOS arm64, Windows WSL 2 experimental | WSL2 Ubuntu 24.04 |

Middleware facts from the proto: it sees the buffered request body (up to 4 MiB), headers before credential injection, and the target; it returns allow, deny or mutation. Registration carries the timeout and `on_error`. The Seal reads `HttpRequestEvaluation.body`.

## NemoClaw and Hermes

- NemoClaw is an open source reference stack that runs OpenClaw, Hermes or LangChain Deep Agents Code inside an OpenShell sandbox, with guided onboarding, managed inference and network policy (`NemoClaw/README.md`). Alpha.
- Express install on WSL is supported. Prerequisites: Docker, 8 GB RAM minimum.
- Hermes is the Nous Research agent with skills and memory; `nemohermes` is the NemoClaw alias with Hermes preselected.
- No mention of Nebius Token Factory was found in the NemoClaw or OpenShell docs (grep of `docs/`), so Token Factory is wired through the generic OpenAI-compatible endpoint path plus our profile.

## Nebius Token Factory

- OpenAI-compatible API at `https://api.tokenfactory.nebius.com/v1/`.
- Exact Nemotron model ids, pricing and the thinking flag are measured in Phase 2 with a real key. Until then no id in this repository is claimed as confirmed.
- Builder Program credits cover Token Factory and Tavily.

## Tavily

- Search with `include_domains` and Extract; the Best Use of Tavily prize ($3,000) is in scope for the drift watch.

## Depth ladder

| Sponsor | Shallow (not enough) | Deep (the build) | Newest (reach for it) |
|---|---|---|---|
| OpenShell | Run an agent in a sandbox | Custom provider profile, L7 rules per binary, policy export, prover with five rejected attack proposals, advisor flow | Supervisor middleware (research preview) as the Seal, fail closed, tested against an encoding corpus |
| Token Factory | One chat call | Routed by job (Nano triage, Super structure, Ultra plan), thinking off for extraction, schema validation with repair, receipts and cost per call | Nemotron 3 Ultra with a capped reasoning budget, only where a verdict needs a plan |
| Nemotron | One model for everything | Three sizes with a cost counterfactual against Ultra-for-everything | Nemotron model measured against the rule engine on the same cases, with false-safe counts |

Anything not reached in Phase 2 is recorded as designed, not run, in `PLATFORM_PROBE.md` and `SDK_SURFACE.md`.
