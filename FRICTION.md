# FRICTION.md

Notes on Nebius Token Factory, OpenShell, NemoClaw and Hermes, written to be reproducible. Each item says what was done, what happened, and a suggested fix. Items are added as the platform probe reaches each primitive.

## OpenShell

1. **Prover returns `unsupported` for REST endpoints without `enforcement: enforce`.**
   Reproduce: write a policy with `protocol: rest` and no `enforcement`, run `openshell-prover check candidate.yaml --boundary boundary.yaml`. Result: `unsupported`, reason `boundary policy rule 'radio-officer' uses REST without enforced inspection`.
   Suggestion: name the missing field in the reason (`add enforcement: enforce to endpoint host:port`), since the default is `audit`.

2. **Prover cannot check a policy that has `network_middlewares`.**
   Reproduce: add a `network_middlewares` block to a candidate. Result: `unsupported`, reason `candidate policy uses network middleware controls`. The Seal, a supervisor middleware, is therefore outside the boundary proof.
   Suggestion: model `fail_closed` middleware as an additional constraint, or document how to prove a boundary for a policy that uses it.

3. **Path comparison returns `unsupported` instead of `exceeds_boundary` for new write paths.**
   Reproduce: boundary writable `/sandbox` and `/tmp`, candidate writable `/etc` or `/vault`. Result: `unsupported`, `depends on sandbox path resolution; use matching paths`. It is documented, but an operator who wants "no new writable path" has to build a focused boundary.
   Suggestion: a `--strict-paths` mode that treats any candidate write path absent from the boundary as exceeding.

4. **Wildcard host `*.com` is `unsupported`** with `overlapping exact and wildcard endpoints with different implicit destination IP modes`. A broad wildcard is the case an operator most wants flagged as exceeding.

5. **Installer on WSL2 as root cannot restart the gateway.** `Failed to connect to bus` and `could not reach the user systemd manager for root`. The message gives the follow-up commands, which also need a user systemd session. Suggestion: print a systemd-free command to start the gateway in the foreground for WSL.

6. **Installed release is older than the repository HEAD the docs describe.** `openshell --version` printed 0.1.6 while the cloned HEAD documents newer behaviour. Suggestion: show the doc version in the site header and the minimum release for each feature.

7. **No Nebius Token Factory provider profile ships**, although the profile format makes one a short file. A profile is in `openshell/profiles/nebius-token-factory.yaml` and is prepared for an upstream contribution.

## Nebius Token Factory

Not yet reached with a key. Items to be added from the probe: model ids returned by `GET /v1/models`, behaviour of `enable_thinking`, schema enforcement.

## Tooling met on the way

- Devpost refuses plain HTTP fetches (HTTP 403), so the rules page was read in a browser.
- Next.js 15.5 refuses TypeScript 7 (`The TypeScript 7 native compiler does not provide the JavaScript compiler API`); the project pins TypeScript 6.
- Fontshare's licence page is script rendered, so its text cannot be fetched without a browser; the font files come from the public CSS API.

## Reading sources from a blocked network

16. **Tavily Extract fetched official government PDFs that this network could not reach** (MPA Shipping Circular 3 of 2026, the DG Shipping TEAP manual). It returned no text for some other PDFs (the DG Shipping revalidation PDF, an IRClass order), so a "no text" result must not be read as "empty document". Suggestion: return an extraction status and the byte length fetched.

17. **WSL on Windows build 21996 cannot run a 6.x kernel.** `wsl --update` to WSL 2.9.13 failed with HCS_E_INVALID_JSON and was rolled back to the inbox WSL (kernel 5.10). OpenShell then cannot start a sandbox locally. Suggestion: a preflight that prints the kernel and Landlock ABI and says which Windows builds are supported.
