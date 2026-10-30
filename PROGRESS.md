# PROGRESS.md

Last updated 2026-10-28. State words: LIVE RUN, LOCAL BUILD, FIXTURE, NOT RUN.

| Phase | State | Notes |
|---|---|---|
| 0 Repository and safeguards | done | Pushed to https://github.com/0xkinno/dogwatch, both workflows green |
| 1 Rules and sponsor intel | done | |
| 2 Platform probe | partial | NVIDIA API Catalog route probed live; OpenShell installed, gateway, provider and Seal registration live; sandbox blocked by kernel 5.10 locally and run on a GitHub Actions runner; Token Factory NOT RUN (no key) |
| 3 Moment and thesis | done | India and Singapore sources read through Tavily Extract; Paris MoU table not fetched |
| 4 Core engine | LOCAL BUILD, live Bosun on dev route | |
| 5 Always-on loop and human actions | LOCAL BUILD; Tavily and unattended runs live | Telegram and Resend live flow run (offer synthetic, approval by the driver, both labelled); P11 live |
| 6 OpenShell integration | partial | gateway, profile, Seal registration live; sandbox proofs wait for `sandbox-proofs.yml` on a Linux 6.2 runner (needs the NVIDIA_API_KEY repo secret) |
| 7 Proof campaign | partial | P3, P6 (engine and Nemotron), P7, P8, P9, P10, P11, P12 run; P1, P2, P4, P5 and the advisor flow run on a GitHub Actions runner (P1 re-proof unsupported by the prover) |
| 8 Web app and judge door | deployed | Vercel web and Vercel Python API (substitute host); reachability script passes; Playwright passes locally (64) and against the live URL (15 of 16 first run, the failure passed on rerun) |
| 9 Contribution and feedback | partial | `FRICTION.md`, `SDK_SURFACE.md`; upstream PR waits for the owner |
| 10 Presentation and submission | partial | README, JUDGE.md, Devpost draft complete; video, deploy link, red team, submission pending |

The task checklist is kept outside the repository; only verified items are ticked there.

Remaining unticked items in the task checklist, and why: the ng-nimasa rule pack (no Nigerian source was read); the sandbox items that need the seafarer's own machine (the proofs ran on a CI runner); the Token Factory items (no key); the submission item (an owner step); the demo video is published at https://youtu.be/GOJ-oNZSZw4 and the red team rounds are logged; the font licence text (the Fontshare licence page is script rendered); the OpenShell Nebius profile lint and attach (needs a gateway and is part of `switch_to_tokenfactory.sh`); the upstream profile PR (needs the owner's approval).
