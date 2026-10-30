import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { ModeChip } from "../../components/Chip";
import { R, fact } from "../../lib/data";

export const metadata = { title: "Proof | Dogwatch" };

type P3Case = { id: string; transform: string; literal_denied: boolean; seal_denied: boolean };

export default function Proof() {
  const live = R.live as Record<string, any>;
  const p3 = R.proof.p3 as Record<string, any>;
  const v1 = R.proof.p3_v1 as Record<string, any>;
  const p7 = R.proof.p7 as Record<string, any>;
  const p7cases = (R.proof.p7_cases ?? []) as { id: string; rule: string; flip: boolean; verdict: string }[];
  const p6 = R.proof.p6 as Record<string, any>;
  const p11 = R.proof.p11 as Record<string, any>;
  const p3cases = (R.proof.p3_cases ?? []) as P3Case[];
  const literalMissed = p3cases.filter((c) => !c.literal_denied);
  const flips = p7cases.filter((c) => c.flip);
  return (
    <>
      <PageHead
        eyebrow="Proof"
        title="Every set,"
        serif="misses first."
        lede="Each set was pre-registered: case files and expected outcomes committed, and their SHA-256 recorded, before the run. These are internal measurements on sets this project built, labelled that way."
        mode={{ label: "RECORDED", detail: `${R.run_id} ${R.recorded_at}` }}
      />
      <section className="wrap stack" data-shot="proof" style={{ paddingBottom: 64 }}>
        <GlowCard>
          <div className="row"><h2 className="h-md display">Pre-registration</h2></div>
          <p className="mono" style={{ wordBreak: "break-all", marginBottom: 0 }}>prereg SHA-256 <span data-fact="proof.prereg_sha256">{fact("proof.prereg_sha256")}</span></p>
        </GlowCard>

        <GlowCard tone="amber" className="stack">
          <div className="row"><h2 className="h-md display">P3 Encoding corpus: literal guard and the Seal</h2><ModeChip mode="LOCAL BUILD" /></div>
          <div className="grid-4">
            <div><div className="stat" data-fact="p3.literal.missed">{fact("p3.literal.missed")}</div><div className="src">of {p3.attacks} attacks missed by the literal guard</div></div>
            <div><div className="stat" data-fact="p3.literal.false_blocks">{fact("p3.literal.false_blocks")}</div><div className="src">legitimate bodies it blocked</div></div>
            <div><div className="stat" data-fact="p3.seal_v1.missed">{fact("p3.seal_v1.missed")}</div><div className="src">missed by Seal v1</div></div>
            <div><div className="stat" data-fact="p3.seal.missed">{fact("p3.seal.missed")}</div><div className="src">missed by Seal v2, <span data-fact="p3.seal.false_blocks">{fact("p3.seal.false_blocks")}</span> false blocks</div></div>
          </div>
          <div className="callout">
            Seal v1 missed {v1.seal.missed} attacks: ids {v1.seal.missed_ids.join(", ")}. Each was a base64 token shorter than the 12 character minimum, so the decoder skipped it. The minimum was lowered to 8 after seeing these misses, on the same cases. The v2 result is a regression check, not an independent score. A fresh corpus is the next test.
          </div>
          <h3 className="h-md display" style={{ fontSize: "1.1rem" }}>By transform</h3>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <thead><tr><th scope="col">Transform</th><th scope="col">Cases</th><th scope="col">Literal guard missed</th><th scope="col">Seal v2 missed</th></tr></thead>
              <tbody>
                {Object.entries(p3.by_transform as Record<string, { n: number; literal_missed: number; seal_missed: number }>)
                  .sort((a, b) => b[1].literal_missed - a[1].literal_missed)
                  .map(([t, v]) => (
                    <tr key={t}><td className="mono">{t}</td><td>{v.n}</td><td>{v.literal_missed}</td><td>{v.seal_missed}</td></tr>
                  ))}
              </tbody>
            </table>
          </div>
          <p className="src" style={{ margin: 0 }}>Literal guard misses by case id (first 40 of {literalMissed.length}): {literalMissed.slice(0, 40).map((c) => c.id).join(", ")}.</p>
        </GlowCard>

        <GlowCard className="stack">
          <div className="row"><h2 className="h-md display">P7 Counting conventions</h2><ModeChip mode="LOCAL BUILD" /></div>
          <div className="row"><div className="stat" data-fact="p7.flips">{fact("p7.flips")}</div><div>of <span data-fact="p7.histories">{fact("p7.histories")}</span> histories near a threshold change verdict depending on how the days are counted.</div></div>
          <p>
            Sourced rules that state a counting convention: <span data-fact="p7.rules_stating_convention">{fact("p7.rules_stating_convention")}</span>. So near a boundary the engine answers Ask administration instead of guessing. Flipping cases:
          </p>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <thead><tr><th scope="col">Case</th><th scope="col">Rule</th><th scope="col">Engine verdict</th></tr></thead>
              <tbody>{flips.map((c) => (<tr key={c.id}><td className="mono">{c.id}</td><td className="mono">{c.rule}</td><td>{c.verdict.replaceAll("_", " ")}</td></tr>))}</tbody>
            </table>
          </div>
          <p className="src" style={{ margin: 0 }}>Rules per administration: {Object.entries(p7.per_rule as Record<string, { histories: number; flips: number }>).map(([r, v]) => `${r}: ${v.flips} of ${v.histories}`).join("; ")}.</p>
        </GlowCard>

        <GlowCard className="stack">
          <div className="row"><h2 className="h-md display">P6 Navigator against the oracle</h2><ModeChip mode="LOCAL BUILD" /></div>
          <p>
            <span data-fact="p6.engine.correct">{fact("p6.engine.correct")}</span> of <span data-fact="p6.profiles">{fact("p6.profiles")}</span> synthetic profiles matched the verdict written by an independent oracle before the run; false-safe <span data-fact="p6.engine.false_safe">{fact("p6.engine.false_safe")}</span>. This is a self-built set, so it is not the headline.
          </p>
          <div className="callout">
            <div className="row" style={{ marginBottom: 8 }}><ModeChip mode={String(live.p6_model.route_label)} /><span className="src">Thinking off, rule text supplied, one verdict per profile.</span></div>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Contestant</th><th scope="col">Correct</th><th scope="col">False-safe</th><th scope="col">False alarm</th></tr></thead>
                <tbody>
                  <tr><td>Navigator (code)</td><td>{fact("p6.engine.correct")} of {fact("p6.profiles")}</td><td>{fact("p6.engine.false_safe")}</td><td>0</td></tr>
                  {Object.entries(live.p6_model.contestants as Record<string, any>).map(([k, c]) => (
                    <tr key={k}><td>Nemotron {k}<div className="src mono">{c.model}</div></td><td>{c.correct} of {live.p6_model.profiles}</td><td>{c.false_safe}</td><td>{c.false_alarm}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="src" style={{ margin: "8px 0 0" }}>
              Super missed profiles: {(live.p6_model.contestants.super.miss_ids as string[]).join(", ")}. Ultra missed: {(live.p6_model.contestants.ultra.miss_ids as string[]).join(", ")}.
            </p>
          </div>
        </GlowCard>

        <GlowCard className="stack">
          <div className="row"><h2 className="h-md display">P11 Restart with a pending approval</h2><ModeChip mode="FIXTURE" /></div>
          <p>
            After a kill with one approved packet pending and a restart: <span data-fact="p11.sends">{fact("p11.sends")}</span> send, <span data-fact="p11.duplicates">{fact("p11.duplicates")}</span> duplicates. The mail transport is a local capture, so this proves the state machine and the idempotency key, not a mail provider.
          </p>
          <p className="src" style={{ margin: 0 }}>{p11.transport}</p>
        </GlowCard>

        <GlowCard className="stack">
          <div className="row"><h2 className="h-md display">Every miss, case by case</h2><ModeChip mode={String(live.p6_model.route_label)} /></div>
          {Object.entries(live.p6_model.contestants as Record<string, any>).map(([k, c]) => (
            <details key={k}>
              <summary>Nemotron {k} alone: {(c.miss_ids as string[]).length} missed profiles</summary>
              <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table" style={{ marginTop: 10 }}>
                <table>
                  <thead><tr><th scope="col">Profile</th><th scope="col">Category</th><th scope="col">Expected</th><th scope="col">Said</th></tr></thead>
                  <tbody>{(c.cases as any[]).filter((x) => !x.ok).map((x) => (<tr key={x.id}><td className="mono">{x.id}</td><td>{x.category}</td><td>{x.expected}</td><td>{x.got}</td></tr>))}</tbody>
                </table>
              </div>
            </details>
          ))}
          <details>
            <summary>Reading: the specimen that was left UNREAD</summary>
            <p className="src" style={{ marginTop: 10 }}>{(live.p8.miss_ids as string[]).join(", ") || "none"}: rotated and blurred, so no quote could be verified and the field stayed UNREAD instead of being guessed.</p>
          </details>
        </GlowCard>

        <GlowCard className="stack">
          <div className="row"><h2 className="h-md display">P8 Reading specimen certificates</h2><ModeChip mode={String(live.p8.route_label)} /></div>
          <p>
            <span data-fact="p8.exact">{fact("p8.exact")}</span> of <span data-fact="p8.specimens">{fact("p8.specimens")}</span> specimens read with the exact expiry date; <span data-fact="p8.unread">{fact("p8.unread")}</span> left UNREAD; <span data-fact="p8.wrong_confident">{fact("p8.wrong_confident")}</span> read wrongly without a flag. OCR runs locally with Tesseract; only placeholder text reaches the model.
          </p>
          <div className="callout">
            The first run found <strong data-fact="p8.v1_leaks">{fact("p8.v1_leaks")}</strong> identifier leaks in the outgoing request bodies: OCR split numbers with spaces and the holder&apos;s name has no pattern, so the detectors missed them. The detectors were made OCR tolerant and the name is matched from the vault&apos;s own table. The second run scanned <span data-fact="p8.bodies">{fact("p8.bodies")}</span> bodies and found <span data-fact="p8.leaks">{fact("p8.leaks")}</span>. Both result files are committed.
          </div>
          <p className="src" style={{ margin: 0 }}>By variant: {Object.entries(live.p8.by_variant as Record<string, { n: number; exact: number }>).map(([k, v]) => `${k} ${v.exact} of ${v.n}`).join("; ")}. Missed: {(live.p8.miss_ids as string[]).join(", ") || "none"}.</p>
        </GlowCard>

        <GlowCard tone="amber" className="stack">
          <div className="row"><h2 className="h-md display">P9 Drift watch, P10 unattended, P12 cost</h2><ModeChip mode={String(live.p9.route_label)} /></div>
          <p>
            P9: the Lookout searched five administration domains with live Tavily ({live.p9.tavily_requests_by_path["/search"]} searches, {live.p9.tavily_requests_by_path["/extract"]} extracts). <span data-fact="p9.searched">{fact("p9.searched")}</span> pages returned, {live.p9.gates.keyword_miss} rejected by the keyword gate, {live.p9.gates.already_seen} already seen, <span data-fact="p9.classified">{fact("p9.classified")}</span> classified by Nemotron Nano, <span data-fact="p9.items">{fact("p9.items")}</span> raised as review items. There is no ground truth for new rule text, so this reports behaviour, not accuracy; the high count shows the classifier is eager and a person reviews every item.
          </p>
          <p>
            P10: the service loop woke four times; it ran <span data-fact="p10.daily">{fact("p10.daily")}</span> daily and <span data-fact="p10.weekly">{fact("p10.weekly")}</span> weekly run, once each, and raised the medical lapse alert. Trace: <span className="mono">evidence/unattended/trace.json</span>.
          </p>
          <p style={{ margin: 0 }}>
            P12: one weekly drift check across all administrations used <span data-fact="p12.weekly_tokens">{fact("p12.weekly_tokens")}</span> tokens. A readiness run uses 0 tokens because the Navigator calls no model. Ultra answered the same prompts about <span data-fact="p12.latency_ratio">{fact("p12.latency_ratio")}</span> times slower than Super. No dollar figure is shown: this route has no list price.
          </p>
        </GlowCard>

        <GlowCard tone="port" className="stack">
          <div className="row"><h2 className="h-md display">OpenShell sandbox proofs</h2><ModeChip mode="NOT RUN" /></div>
          <p style={{ margin: 0 }}>On the build machine (WSL kernel 5.10, no Landlock ABI 3) the sandbox cannot start. On a GitHub Actions ubuntu-24.04 runner (runs 41009598425 and 41012951503, not the seafarer's machine) it did. P5 passed live: inside the sandbox the agent saw an opaque placeholder (57 characters, not an API key), and the canary received 0 real keys from the sandbox against 1 without it. The advisor flow worked: a denied model request became a pending proposal annotated by the prover and was rejected from the command line (Telegram was not wired to the runner). P1 on the effective policy found two excesses, the stock profile's read-write access and its extra curl binary; both are fixed and not yet re-proved. P2 with the sandbox and P4 are inconclusive: the sandbox denied the model host because the interpreter resolves to /usr/bin/python3.12, which the policy did not list, so all 20 sandboxed model calls errored and 0 posts is not evidence of a defence, and P4's calls failed before the Seal was stopped. The policy now lists that path and the re-run is pending. The same run without a sandbox: 20 of 20 injected emails made the agent post and 20 of 20 canary requests carried a vault value.</p>
        </GlowCard>
      </section>
    </>
  );
}
