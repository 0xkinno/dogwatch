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
Run after the fixes are deployed (see evidence/final/).
