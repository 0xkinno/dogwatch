# TASK.md

Dogwatch build tasks, in dependency order. Mark a task `[x]` only when it is complete and verified, in the same commit that completes it. Every commit is authored by 0xkinno.

## Phase 0. Repository and safeguards
- [ ] Create public repo `0xkinno/dogwatch` with Apache-2.0 LICENSE visible in the About section
- [ ] `git config user.name 0xkinno` and the 0xkinno email; install `.githooks/commit-msg`; `core.hooksPath` set
- [ ] `.github/workflows/no-claude-attribution.yml` added and passing
- [x] `.claude/settings.json` with empty commit and PR attribution
- [x] `.gitignore` covers `reference/`, `.env*`, `vault/`, `*.age`, `node_modules`, `.venv`, `web/.next`, test-results
- [x] Reference repos cloned into `reference/` (OpenShell, NemoClaw, Hermes, proof-discipline references)
- [x] Scaffolds: `core/`, `radio/`, `seal/`, `openshell/`, `skills/`, `eval/`, `evidence/`, `web/`, `scripts/`
- [x] `scripts/check_copy.py` (no emoji, no em or en dashes, banned words) wired into CI
- [ ] First commit pushed and the attribution check is green

## Phase 1. Rules and sponsor intelligence
- [x] `RULES_EXTRACT.md`: criteria, track text, required items, video rules, deadline in WAT, Devpost form fields
- [x] `SPONSOR_INTEL.md`: OpenShell primitives with doc paths, NemoClaw and Hermes status, Token Factory models, Tavily, newest releases and preview status
- [x] Depth ladder written for OpenShell, Token Factory and Nemotron (shallow, deep, newest)

## Phase 2. Platform probe
- [x] Token Factory `GET /v1/models` output saved; exact Nemotron ids recorded (done on the NVIDIA API Catalog route; Token Factory NOT RUN, no key)
- [x] Thinking on vs off measured on one real extraction (tokens, latency, cost) (NVIDIA API Catalog route)
- [x] JSON schema enforcement tested; repair path confirmed (NVIDIA API Catalog route)
- [ ] OpenShell installed on WSL2; `openshell sandbox create` works
- [ ] `nebius-token-factory.yaml` profile linted, imported, attached; a sandboxed call to Token Factory succeeds with a placeholder key
- [ ] Content-guard middleware example smoke test runs (or the failure is recorded)
- [x] `openshell-prover` runs a boundary check and returns a counterexample on a test file
- [ ] Policy advisor enabled; one proposal submitted and rejected through the CLI
- [ ] NemoClaw install attempted; Hermes (`nemohermes`) attempted; results recorded
- [ ] Nebius AI Cloud access checked (Serverless Endpoint or VM)
- [x] `PLATFORM_PROBE.md` written from real outputs; tier decisions recorded

## Phase 3. Moment and thesis
- [ ] Every source in the instruction's source table fetched; quotes and retrieval dates in `evidence/need/sources.json`
- [x] `MOMENT.md` with the "What is true / Source" table
- [x] Money figure asserted by a test reading `sources.json`
- [x] `THESIS.md`: five-line pitch, hook, one sentence, guarantee, crew, interruption budget

## Phase 4. Core engine
- [x] Encrypted vault store and identifier registry (host side API)
- [x] Identifier detectors with check-digit tests (MRZ, passport, CoC, INDoS, CDC, CoE, email, phone)
- [x] Placeholder replacement with stable ids and overlap handling
- [ ] Local OCR in the sandbox image
- [x] Bosun structuring with Nemotron Super, thinking off, Pydantic validation, one repair retry (NVIDIA API Catalog route)
- [x] Quote verification in code; dates parsed from verified quotes only
- [x] Rule pack format, loader, SHA-256 per pack
- [ ] Rule packs: stcw-core, in-dgs, uk-mca, sg-mpa, au-amsa, ng-nimasa, every quote verified against a snapshot by test
- [x] Sea-service calculator with all counting conventions, overlaps, leap days
- [x] Readiness engine: per-document states and overall verdict; unread facts never READY
- [x] Receipts for every model call (id, model, tokens, latency, cost)

## Phase 5. Always-on loop and human actions
- [x] Officer of the Watch loop with daily and weekly timers, durable state, restart safe
- [x] Nano triage of incoming messages (no tools)
- [x] Ultra plan writer around locked value tokens; free-digit check falls back to template
- [x] Interruption budget in code (two questions per day; lapses and approvals always pass)
- [x] Radio Officer: Telegram pairing and long polling
- [x] Approval tokens bound to packet digest; single use; expiry
- [x] Recipient allowlist
- [x] Rehydration and PDF packet built host side
- [x] Email send to the test "manning agent" inbox; record in `evidence/actions/` with recipient redacted
- [x] `.ics` booking window sent to Telegram
- [x] Discharge-book photo flow updates the ledger
- [x] Lookout drift watch with Tavily Search and Extract, domain and keyword gates, review items only
- [x] Six skills with `SKILL.md` and CLI entries

## Phase 6. OpenShell integration
- [ ] Sandbox image with Python venv, OCR, Dogwatch core; vault mounted read only
- [ ] `openshell/policy/dogwatch.yaml` applied; effective policy exported
- [ ] Tavily provider profile attached
- [ ] Seal middleware implemented with all normalizations; registered fail closed
- [x] `boundary.yaml` and five attack proposals; `prove.sh` outputs committed
- [ ] Advisor flow: a denied request becomes a proposal the seafarer rejects from Telegram
- [ ] Hermes tier: skills loaded in `nemohermes` (only if the probe passed; otherwise marked designed, not run)

## Phase 7. Proof campaign
- [x] `eval/cases/prereg.json` committed and its SHA-256 recorded before any run
- [ ] P1 boundary proven
- [ ] P2 injection inbox with and without the sandbox
- [x] P3 encoding corpus: literal guard vs Seal, both directions
- [ ] P4 fail closed
- [ ] P5 credential placeholder
- [x] P6 engine vs Nemotron alone (Super and Ultra) (NVIDIA API Catalog route)
- [x] P7 counting-convention finding
- [x] P8 reading on specimen certificates; no identifier in any request body (NVIDIA API Catalog route)
- [x] P9 drift watch (NVIDIA API Catalog route)
- [x] P10 unattended daily and weekly runs recorded (NVIDIA API Catalog route)
- [x] P11 restart with a pending approval, no duplicate send
- [x] P12 cost per weekly check and per readiness run (NVIDIA API Catalog route)
- [x] `scripts/facts.py` writes `docs/FACTS.json`; `scripts/check_facts.py` in CI
- [x] `PROOF.md` and `EVIDENCE.md` with LIVE RUN / LOCAL BUILD / FIXTURE / NOT RUN states

## Phase 8. Web app and judge door
- [ ] Fonts self-hosted with license files; tokens in place
- [x] Square capsule nav with hover glow
- [x] Hero image generated or licensed; placed right with paper fade; never behind text
- [x] Watch Dial SVG component driven by real verdicts
- [x] Landing sections 1 to 9
- [x] `/watch`, `/contract`, `/outbox`, `/boundary`, `/proof`, `/judge`, `/how`
- [x] Glow cards with cursor-tracking light
- [x] API endpoints with caps and kill switch; `/api/status` measured, never hard-coded
- [x] Recorded mode labelled on every page that uses it
- [x] Vercel deploy; API host deploy; reachability script passes
- [x] Playwright across eight viewports: no overflow, no overlaps, zero console errors, axe clean, screenshots saved
- [x] Daily live probe workflow against the deployed URL

## Phase 9. Contribution and feedback
- [ ] `FRICTION.md`: reproducible notes on Token Factory, OpenShell, NemoClaw, Hermes with suggested fixes
- [ ] Nebius Token Factory provider profile prepared as an upstream PR (open only after Kinnoski approves)
- [x] `SDK_SURFACE.md`: every sponsor feature, file:line, version, live or recorded or designed, and "not used, so not claimed"

## Phase 10. Presentation and submission
- [x] README written to the required structure, numbers from FACTS only
- [x] 2x2 product screenshots and banner committed
- [x] `JUDGE.md` with 60-second, 3-minute and 10-minute paths
- [ ] Demo video under 3:00 recorded and uploaded to YouTube (public)
- [ ] `SUBMISSION_DEVPOST.md` mirrors the live form, track Personal AI, feedback section complete
- [ ] Red team: five fresh judge agents on the deployed URL; defects fixed; clean round logged in `REDTEAM_LOG.md`
- [ ] Kinnoski approves and submits
- [ ] Submitted commit tagged; deployment frozen
