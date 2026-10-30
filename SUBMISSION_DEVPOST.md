# SUBMISSION_DEVPOST.md

Draft that mirrors the live Devpost form for the Nebius x NVIDIA Global AI Hackathon. Deadline: Fri 30 Oct 2026 10:00 PT (18:00 WAT). The owner presses submit; this file is the text to paste.

## Project name
Dogwatch

## Tagline
An always-on, private assistant that keeps a seafarer's certificates under his control and has every renewal ready before a lapse costs him a contract.

## Track
Personal AI

## Route statement (put this first in the description)
Every live model result in this submission ran on the NVIDIA API Catalog (build.nvidia.com), the development route for the same Nemotron models. Nebius Token Factory could not be used: its billing requires a card and the available cards were declined, so no key was issued. The Token Factory route is built and tested in code (the client defaults to it whenever `NEBIUS_API_KEY` exists, the provider-integrity test allows exactly those two hosts, and `scripts/switch_to_tokenfactory.sh` re-runs the probe and the evidence on it; its dry run with a fake key fails only at the auth step). It has not been run, and nothing here is described as a Token Factory run.

## Inspiration
Arjun is a Second Officer on a product tanker with twenty minutes of internet a day. A manning agent offers him six months, and one certificate lapses in the middle of it. He would find out at the agency desk, not at sea. The builder is pursuing STCW certification and wanted the papers watched by something that does not need to see them.

## What it does
Dogwatch reads a seafarer's certificates on his own machine, computes every expiry and sea-service window in code, drafts the renewal packet, and sends it from Telegram after one approval bound to the packet digest. The cloud model only sees placeholders. A model never decides validity: on the same sixty profiles, Nemotron Super alone said READY on 22 that were not ready, Nemotron Ultra alone raised 8 false alarms, and the code engine matched all 60.

## How we built it
Python engine (vault, Bosun, Navigator, Officer of the Watch, Lookout), a host-side Radio Officer, an OpenShell policy whose boundary is checked by NVIDIA's own prover, a supervisor middleware called the Seal, six reusable SKILL.md skills, a pre-registered evaluation set with misses published, and a Next.js judge door. Nemotron Nano, Super and Ultra are routed by job; thinking is off for extraction. Tavily drives the weekly rule-drift watch.

## Challenges
- A model must never decide validity, so every verdict is computed from dates and rule packs, each rule carrying a quote checked against a snapshot of the source.
- OpenShell's sandbox needs Linux 6.2 or newer (Landlock ABI 3) and Docker Engine 28; the build machine had kernel 5.10 and Docker 27.1.1. The gateway, provider profile and Seal registration ran there; the sandbox could not start, so the sandbox proofs ran on a GitHub Actions ubuntu-24.04 runner instead (kernel 7.0): P2 denied 20 of 20 injected posts, P4 failed closed, P5 showed only a placeholder, and the effective-policy re-proof was unsupported by the prover.
- OCR splits identifier numbers with spaces. The first reading run leaked 12 identifiers into request bodies; the detectors were fixed and both runs are published.
- Some regulator hosts refuse the build network, so the India and Singapore rules were read through Tavily Extract and each quote is checked against its snapshot; Nigeria ships no rule rather than a guessed one.

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
Run the probe and the evidence on Token Factory when a key exists, run the sandbox proofs (P2, P4, P5) on a Linux 6.2 runner, and read the Nigeria and Paris MoU sources.

## Built with
NVIDIA Nemotron, NVIDIA OpenShell, Tavily, Python, FastAPI, gRPC, Next.js, TypeScript, Framer Motion, Playwright.

## Try it out
Repository: https://github.com/0xkinno/dogwatch. Live app: https://dogwatch-eight.vercel.app (API host: https://dogwatch-api.vercel.app/api/status, a Vercel substitute host, labelled in /api/status).

## Video
Not recorded yet.

## Testing instructions
No login. Open the live app, press Check on the contract card, run the offer flow on `/judge`. Offline commands are in `JUDGE.md`.

## New or existing
New, created in the submission period. The first commit is dated 2026-10-28.

## Feedback on Nebius Token Factory, AI Cloud and NVIDIA tools

Specific and reproducible; the long form is `FRICTION.md`.

**Which Nemotron models, with the real ids from the receipts, and why.** Triage and drift reading: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, because these are frequent short jobs over untrusted text where a wrong answer is caught by a gate (4 and 36 recorded calls). Structuring: `nvidia/nemotron-3.5-super-vl-120b-a12b`, because it followed the schema and returned quotes that code could verify (42 calls, 39 of 40 specimens exact). Plan writing: `nvidia/nemotron-3-ultra-550b-a55b`, only when a verdict needs a plan; in the recorded runs it answered HTTP 503 (busy), so a labelled template was used and zero plan calls completed. It was about 2.35 times slower than Super on the same prompts.

**Approach.** Code decides, models explain. A model structures placeholder text, code verifies each quote and parses each date, the Navigator computes verdicts, and a model writes prose around value tokens with a free-digit check that falls back to a template. A supervisor middleware (the Seal) refuses requests carrying a vault value, and NVIDIA's prover checks the policy against a boundary.

**Comparison.** Nemotron alone against the engine on 60 pre-registered profiles: Super said READY on 22 that were not ready; Ultra had none of those but 8 false alarms; the engine matched all 60 (a self-built set, so not the headline). Thinking on versus off on one real extraction: about ten times the tokens and time, 1,093 versus 113 output tokens.

**What worked on Nebius.** Nothing could be tested: Token Factory billing requires a card and the available cards were declined, so no key was issued. Onboarding rating below reflects that. What worked on the NVIDIA API Catalog, which is the route that ran: OpenAI-compatible calls, `chat_template_kwargs.enable_thinking=false`, and server-side JSON schema enforcement (3 of 3 trials). What did not: a model listed by `GET /models` that returned 404 on chat, and HTTP 503 worker limits on the largest models, which the client retries.

**Ratings, 1 to 10, with a short why** (from real use):
- Nemotron (via the NVIDIA API Catalog): 8. Strong at structuring with quotes and following a schema; loses points for 503s on Ultra and listed-but-uncallable ids.
- NVIDIA OpenShell: 7. The prover, policy schema and middleware contract are excellent and documented; loses points because an unsupported kernel or Docker version gives an error that does not name the cause (FRICTION.md items 8 and 9).
- Tavily: 9. Search plus Extract worked at runtime and also fetched two government PDFs this network could not reach; loses a point for returning no text on some PDFs.
- Nebius Token Factory onboarding: 2. A card is required and the available cards were declined, so no key was issued. Not rated on the product, which was never reached.
- Nebius AI Cloud: not used.

**Tavily runtime use.** Yes. The Lookout calls Tavily Search and Extract at runtime for the weekly rule-drift watch: 52 live requests in the recorded run, gated by domain, keyword and a verified quote, producing review items only.

**AI tools used.** AI_TOOLS: <Kinnoski fills this>

**Learning questions (drafts).**
- What surprised you? That a model alone said READY on 22 of 60 profiles, and that OCR damage, not the model, caused the identifier leaks.
- What would you do differently? Read the sandbox kernel and Docker requirements first, and pre-register the injected-inbox set before building the Seal.
- What did you learn about the tools? A literal guard misses most encodings; a decoder before the matcher fixes that. Listed models are not always callable. Thinking costs about ten times the tokens.
- What next? Run the sandbox proofs on a Linux 6.2 runner, run the evidence on Token Factory when a key exists, and read the Nigeria and Paris MoU sources.

## Open items before submitting
1. Demo video link, the AI_TOOLS line, (the sandbox proofs have run: GitHub Actions runs 41009598425, 41012951503 and 41017826733; P2 denied 20 of 20 injected posts, P4 failed closed, P5 showed a placeholder, the advisor flow is from one run via the CLI, the P1 re-proof was unsupported by the prover).
2. Confirm the repository About section shows the Apache-2.0 licence.
3. Owner approval to submit.
