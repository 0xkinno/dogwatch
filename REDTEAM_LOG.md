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
Pending: run after this deploy.
