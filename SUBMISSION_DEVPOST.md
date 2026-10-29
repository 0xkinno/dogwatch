# SUBMISSION_DEVPOST.md

Draft that mirrors the live Devpost form for the Nebius x NVIDIA Global AI Hackathon. Deadline: Fri 30 Oct 2026 10:00 PT (18:00 WAT). The owner presses submit; this file is the text to paste.

## Project name
Dogwatch

## Tagline
An always-on, private assistant that keeps a seafarer's certificates under his control and has every renewal ready before a lapse costs him a contract.

## Track
Personal AI

## Route statement (put this first in the description)
Every live model result in this submission ran on the NVIDIA API Catalog (build.nvidia.com), the development route for the same Nemotron models, because a Nebius Token Factory key could not be obtained (the promotional credit could not be claimed because of card restrictions). Token Factory is the intended target: the client defaults to it whenever `NEBIUS_API_KEY` exists, and `scripts/switch_to_tokenfactory.sh` re-runs the probe and the evidence on it. Nothing in this submission is described as a Token Factory run.

## Inspiration
Arjun is a Second Officer on a product tanker with twenty minutes of internet a day. A manning agent offers him six months, and one certificate lapses in the middle of it. He would find out at the agency desk, not at sea. The builder is pursuing STCW certification and wanted the papers watched by something that does not need to see them.

## What it does
Dogwatch reads a seafarer's certificates on his own machine, computes every expiry and sea-service window in code, drafts the renewal packet, and sends it from Telegram after one approval bound to the packet digest. The cloud model only sees placeholders. A model never decides validity: on the same sixty profiles, Nemotron Super alone said READY on 22 that were not ready, Nemotron Ultra alone raised 8 false alarms, and the code engine matched all 60.

## How we built it
Python engine (vault, Bosun, Navigator, Officer of the Watch, Lookout), a host-side Radio Officer, an OpenShell policy whose boundary is checked by NVIDIA's own prover, a supervisor middleware called the Seal, six reusable SKILL.md skills, a pre-registered evaluation set with misses published, and a Next.js judge door. Nemotron Nano, Super and Ultra are routed by job; thinking is off for extraction. Tavily drives the weekly rule-drift watch.

## Challenges
- A model must never decide validity, so every verdict is computed from dates and rule packs, each rule carrying a quote checked against a snapshot of the source.
- OpenShell's sandbox needs Linux 6.2 or newer (Landlock ABI 3) and Docker Engine 28; the build machine had kernel 5.10 and Docker 27.1.1. The gateway, provider profile and Seal registration ran; the sandbox could not start, so P2, P4 and P5 are NOT RUN.
- OCR splits identifier numbers with spaces. The first reading run leaked 12 identifiers into request bodies; the detectors were fixed and both runs are published.
- Some regulator pages could not be read from the build machine, so those rule packs ship no rules rather than guessed ones.

## Accomplishments
- Nemotron alone against an independent oracle (60 profiles): Super 30 correct with 22 false-safe, Ultra 47 correct with 8 false alarms, Navigator 60 correct.
- 39 of 40 specimen certificates read exactly, 0 wrong without a flag, 0 identifiers in 40 outgoing request bodies.
- A literal-only guard let 158 of 200 encoded attacks through; the first Seal missed 8, the second missed 0 with 0 false blocks (a regression check, labelled so).
- The OpenShell prover reports counterexamples for three attack policies.
- An unattended loop ran one daily and one weekly check with live Tavily and Nemotron.
- Restart with a pending approval produces one send and no duplicate.

## What we learned
Sourced rules do not state a counting convention for sea service, and 7 of 60 histories near the thresholds flip verdict with it. A literal guard misses most encodings. Thinking on used about ten times the tokens and time of thinking off on one real extraction. Listed models are not always callable: one Nemotron id in the catalog list returned 404.

## What's next
Run the probe and the evidence on Token Factory when a key exists, run the sandbox proofs (P2, P4, P5) on a Linux 6.2 host, read the India and Singapore sources, and send the first live Telegram and email packet.

## Built with
NVIDIA Nemotron, NVIDIA OpenShell, Tavily, Python, FastAPI, gRPC, Next.js, TypeScript, Framer Motion, Playwright.

## Try it out
Repository: https://github.com/0xkinno/dogwatch. Live app: https://dogwatch-eight.vercel.app (API host: https://dogwatch-api.vercel.app, a Vercel substitute host, labelled in /api/status).

## Video
Not recorded yet.

## Testing instructions
No login. Open the live app, press Check on the contract card, run the offer flow on `/judge`. Offline commands are in `JUDGE.md`.

## New or existing
New, created in the submission period. The first commit is dated 2026-10-28.

## Feedback on Nebius Token Factory, AI Cloud and NVIDIA tools

Written to be specific and reproducible; the long form is `FRICTION.md`.

**Which Nemotron models and why.** Nano (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`) for triage and drift reading, because those are frequent, short, untrusted-text jobs where latency and cost matter and a wrong answer is caught by a gate. Super (`nvidia/nemotron-3.5-super-vl-120b-a12b`) for structuring documents into fields with quotes, because it followed the schema and returned verifiable quotes (39 of 40 specimens exact). Ultra (`nvidia/nemotron-3-ultra-550b-a55b`) only when a verdict needs a plan written around locked values, because it was about 2.35 times slower than Super on the same prompts and is not needed for extraction.

**Approach.** Code decides, models explain. A model structures placeholder text, code verifies each quote and parses each date, the Navigator computes verdicts, and a model writes prose around value tokens with a free-digit check that falls back to a template. A supervisor middleware (the Seal) refuses any request carrying a vault value, and the OpenShell prover checks the policy against a boundary.

**Comparison.** Nemotron alone against the engine on 60 pre-registered profiles: Super said READY on 22 that were not ready; Ultra had none of those but 8 false alarms; the engine matched all 60. Thinking on versus off: about ten times the tokens and time. The Navigator's score is on a self-built set and is not the headline.

**What worked on Nebius.** Not tested live. The Token Factory key could not be obtained (promotional credit blocked by card restrictions), so every live run used the NVIDIA API Catalog. What worked there: `chat_template_kwargs.enable_thinking=false`, server-side JSON schema enforcement (3 of 3 trials), and OpenAI-compatible calls. What did not: a model listed by `GET /models` that returned 404 on chat, and HTTP 503 worker limits on the largest models, which the client retries.

**Ratings, 1 to 10, with reasons** (for what was actually used):
- NVIDIA API Catalog and Nemotron: 8. Fast, OpenAI-compatible, schema enforced; loses points for listed-but-uncallable ids and 503s on the largest models.
- NVIDIA OpenShell: 7. The prover, policy schema and supervisor middleware contract are excellent and well documented; loses points because a sandbox failure on an unsupported kernel or Docker version gives a message that does not name the cause (see FRICTION.md items 8 and 9).
- Nebius Token Factory: not rated, not used live.
- Nebius AI Cloud: not rated, not used.

**Tavily runtime use.** Yes. The Lookout calls Tavily Search and Extract at runtime for the weekly rule-drift watch: 52 live requests in the recorded run, gated by domain, keyword and a verified quote, producing review items only.

**AI tools used.** An AI coding assistant (a large language model agent run in the terminal) helped write code and documents under the owner's direction and review; the owner approved every commit. Models used in the product: NVIDIA Nemotron (Nano, Super, Ultra). Third-party services: Tavily. Image: the hero image was generated by the owner with an image generator.

## Open items before submitting
1. Demo video link.
2. Confirm the repository About section shows the Apache-2.0 licence.
3. Owner approval to submit.
