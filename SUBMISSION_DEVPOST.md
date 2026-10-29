# SUBMISSION_DEVPOST.md

Draft that mirrors the live Devpost form for the Nebius x NVIDIA Global AI Hackathon. Deadline: Fri 30 Oct 2026 10:00 PT (18:00 WAT). Do not submit until the open items at the end are closed and the owner approves.

## Project name
Dogwatch

## Tagline
An always-on, private assistant that keeps a seafarer's certificates under his control and has every renewal ready before a lapse costs him a contract.

## Track
Personal AI

## Inspiration
Arjun is a Second Officer on a product tanker with twenty minutes of internet a day. A manning agent offers him six months, and one certificate lapses in the middle of it. He would find out at the agency desk, not at sea. The builder is pursuing STCW certification and wanted the papers watched by something that does not need to see them.

## What it does
Dogwatch reads a seafarer's certificates on his own machine, computes every expiry and sea-service window in code, drafts the renewal packet, and sends it from Telegram after one approval bound to the packet digest. The cloud model only sees placeholders. See the README for what is live and what is not.

## How we built it
Python engine (vault, Bosun, Navigator, Officer of the Watch, Lookout), a host-side Radio Officer, an OpenShell policy with a prover-checked boundary, a supervisor middleware called the Seal, six reusable SKILL.md skills, a pre-registered evaluation set, and a Next.js judge door. Nemotron Nano, Super and Ultra are routed by job through Token Factory; thinking is off for extraction. Tavily powers the weekly rule-drift watch.

## Challenges
- A model must never decide validity: every verdict is computed from dates and rule packs, each rule carrying a quote checked against a snapshot.
- The prover and the middleware are research-grade; the friction is written up in `FRICTION.md`.
- Some regulator pages could not be read from the build machine, so those rule packs ship no rules rather than guessed ones.

## Accomplishments
- Seal tested over gRPC against a 200 attack and 200 legitimate encoding corpus; both versions of the run are published with misses by id.
- The prover reports counterexamples for three attack policies.
- Restart with a pending approval produces one send and no duplicate.

## What we learned
Sourced rules do not state a counting convention for sea service, and near the thresholds the verdict flips with it. A literal-only guard misses most encodings. (Thinking-off cost: pending the live probe.)

## What's next
Run the live probe and the injected-inbox comparison with and without the sandbox, register the Seal in a running gateway, and read the India and Singapore sources.

## Built with
Nebius Token Factory, NVIDIA Nemotron, NVIDIA OpenShell, Tavily, Python, FastAPI, gRPC, Next.js, TypeScript.

## Try it out
Repository: https://github.com/0xkinno/dogwatch (to be confirmed). Live app: not deployed yet.

## Video
Not recorded yet.

## Testing instructions
No login. Open the live app, press Check on the contract card, run the offer flow on `/judge`. Offline commands are in `JUDGE.md`.

## Feedback on Token Factory, AI Cloud and NVIDIA tools
See `FRICTION.md`. Token Factory items are pending the live probe.

## New or existing
New, created in the submission period. The first commit is dated 2026-10-28.

## Open items before submitting
1. Live Token Factory and Tavily probes (keys needed).
2. Deploy the web app and the API host; record the demo video; upload it to YouTube.
3. Confirm the repository is public with the licence visible in the About section.
4. Owner approval to submit.
