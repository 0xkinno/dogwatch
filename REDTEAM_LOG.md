# REDTEAM_LOG.md

Three independent reviewers (sponsor engineer, security reviewer, product and design) judged the deployed app and the public repository. Reviewers fetched pages as text; layout and mobile were not visually assessed by them (Playwright covers those).

## Round 1
Fixed:
- Footer on every page credited "Nemotron on Nebius Token Factory" while no Token Factory call exists. Now states the NVIDIA API Catalog route and that Token Factory has not been run.
- /how SDK table was stale (said gateway not started, Tavily and Nemotron no live call). Rewritten to match README and PROOF.md.
- /judge medical lane said "No administration rule is needed" next to "ask the administration" for renewal. Reworded to separate the printed-date comparison from the renewal window.
- Home Seal tile now says Seal v2 was tuned on those cases (regression check). Home boundary text says the sandbox run is not done yet.
- README setup line on WSL kernel corrected.

Accepted and disclosed, not fixable here:
- Sandbox proofs P1 (effective), P2, P4, P5, advisor: NOT RUN until sandbox-proofs.yml runs with the NVIDIA_API_KEY repository secret.
- No Token Factory calls: no key.
- Navigator 60/60 and Seal v2 results are self-built or tuned sets; already labelled on /proof.
- Rule coverage thin; Nigeria pack empty; renewal windows unsourced.
- /api/status "mode":"LIVE" is the hosted stand-in, "sandboxed":false.

Reviewer claims checked and not defects: README does not use the word the third reviewer suspected; README already states the India and Singapore packs are sourced via Tavily Extract (the reviewer saw a stale remote, pushes are blocked on credentials).

## Round 2
Three reviewers again, on the redeployed app. No exposed secrets, no fabricated numbers; counts and dates reconcile across pages.
Fixed:
- /boundary doors named only Token Factory while every result used the NVIDIA API Catalog. The door is now labelled "Model route" with both hosts, and the page states that the prover run predates the Catalog door and is repeated by the sandbox workflow.
- /watch label "Years of 365 days" was a month figure; now "Months of 365/12 days".
- README unrun list now includes P1 on the effective policy; the Seal sentence now carries the tuning caveat.
- /judge says the plan text is a labelled template when the large model is busy.
- Nav label "Open your watch" renamed "See the specimen watch".
Not changed: P-code legend and jargon glossary (listed for round 3), outbox wording on the renewal window.
## Round 3
Run on the deploy that carried the sandbox run 1 results. Three reviewers; no secrets found, numbers reconcile.
Fixed:
- The sandbox status was stale on /proof, /boundary, /how and the home page ("cannot start", "set to run"). One canonical statement now appears on all four and in README, PROOF.md and EVIDENCE.md: the build machine cannot start the sandbox; on GitHub Actions run 41009598425 it started, P1 on the effective policy found the stock NVIDIA profile too wide (narrowed, not re-proved), sandboxed P2, P4, P5 and the advisor did not execute (NOT RUN), and the no-sandbox P2 baseline leaked in 20 of 20 emails.
- /how profile row now says "narrowed and not yet re-proved".
- PROOF.md said the Nemotron comparison was NOT RUN; it is scoped to Token Factory, since it ran on the NVIDIA API Catalog.
- /judge no longer says "Run the contract check"; it says open the page and press Check.
Not changed: adding Contract and Outbox to the nav (layout risk, both reachable from the home page and /judge), the P-code and jargon glossary, the outbox renewal wording. The one banned word still appears only where the evidence file allows it.
Round 4 is pending sandbox run 2 (the sandboxed probes); until it produces results those four stay NOT RUN.

## Sandbox run 2 review (self-check before round 4)
Read the artifact from run 41012951503 and refused to count two results as passes. P2 with the sandbox showed 0 posts only because all 20 model calls were denied (the interpreter resolves to /usr/bin/python3.12, which the policy did not list); P4 failed before the Seal was stopped, so it had no baseline. Both are recorded INCONCLUSIVE, the policy and profile now list the path, the profile's extra curl binary is removed (the second P1 excess), and the probe results now carry a `valid` flag that is false when the baseline did not work. P5 and the advisor flow are recorded as passed. Round 4 follows sandbox run 3.
