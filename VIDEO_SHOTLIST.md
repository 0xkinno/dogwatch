# VIDEO_SHOTLIST.md

Demo video, under 3:00, public on YouTube. Label specimens, synthetic data and any synthetic voice on screen. No copyrighted music. Every result shown names its route: Route: NVIDIA API Catalog (development). Never say "Token Factory run".

| Time | What the viewer sees | Exact page or moment | Voice |
|---|---|---|---|
| 0:00 to 0:20 | The hero image, slow push in, the headline settling | https://dogwatch-eight.vercel.app/ at the top, motion on | The hook from `THESIS.md`, word for word |
| 0:20 to 0:30 | Name, then the one sentence and the X without Y line | Same page, scroll to "The moment" section | "Dogwatch. A personal assistant that handles your identity documents without ever seeing them." |
| 0:30 to 1:20 | The real flow. (1) Phone: Telegram chat with @Dogwatchdev_bot, the contract offer sent. (2) The NOT_READY reply with the day count. (3) Phone: the discharge-book SPECIMEN photo, then the ledger reply. (4) The approval message with the digest and the Approve and Reject buttons, tap Approve. (5) The inbox: the email with readiness.pdf arriving. (6) The `.ics` document in Telegram | Run `python scripts/run_live_flow.py --wait 90` while filming the phone, and tap Approve within 90 seconds so the evidence records the owner's approval. Then open the Resend inbox. Cut to https://dogwatch-eight.vercel.app/contract for the same verdict and its rule quote | "The agent offered six months. The medical lapses on day 42. It tells him inside his twenty minutes, and nothing leaves until he approves that exact digest." |
| 1:20 to 1:50 | The boundary. The doors diagram, then the prover counterexamples, then the Seal decisions. If the sandbox proofs have run: the injected email, the canary hit without the sandbox and none with it | `/boundary`; then the P2 result from `eval/results/p2_injection.json` once `sandbox-proofs.yml` has run; otherwise say it is not run yet | "The cloud model sees placeholders. A gateway outside the agent allows four doors. NVIDIA's prover finds the counterexamples. The Seal refuses a vault value even when it is encoded." |
| 1:50 to 2:20 | Sponsor proof: the OpenShell policy, the prover output, the routing table with real receipts, thinking on versus off | `/boundary` policy block; `/watch` routing and cost panel; README "NVIDIA Nemotron" table | "Nano, Super and Ultra by job. Thinking on costs ten times the tokens." |
| 2:20 to 2:45 | One proof number per set, misses first: Super alone said READY on 22 of 60; a literal guard missed 158 of 200; 39 of 40 specimens read with no identifier leaking; the counting-convention finding | `/proof` scrolling, expand "Nemotron super alone" misses | "A model alone said READY on 22 profiles that were not ready. So no model decides validity here." |
| 2:45 to 3:00 | What is next, one sentence, then the end card with the live URL | Landing page footer, the URL on screen | "Next: the sandbox proofs on a Linux 6.2 runner, and the same evidence on Token Factory when a key exists." |

## Shot notes
- Record the web at 1440 by 900. Record Telegram on the phone in portrait and cut it into a landscape frame with the web page beside it.
- Put a small on-screen label on every Telegram shot: "Route: NVIDIA API Catalog (development)".
- The Telegram offer in the committed evidence was a synthetic message injected by the driver. For the video, send the offer yourself from the phone, tap Approve yourself, and re-run the flow so the evidence file records the owner's messages.
- Do not show `.env`, a token, a key or the Resend dashboard keys.
