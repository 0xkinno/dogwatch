import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { ModeChip } from "../../components/Chip";
import { R, fact } from "../../lib/data";

export const metadata = { title: "Proof | Dogwatch" };

type P3Case = { id: string; transform: string; literal_denied: boolean; seal_denied: boolean };

export default function Proof() {
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
      <section className="wrap stack" style={{ paddingBottom: 64 }}>
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
          <div className="callout">The same profiles against Nemotron Super and Ultra: <strong>NOT RUN</strong>. It needs a Token Factory key. The counterfactual is the headline result and will appear here, with its false-safe count, as soon as it runs.</div>
        </GlowCard>

        <GlowCard className="stack">
          <div className="row"><h2 className="h-md display">P11 Restart with a pending approval</h2><ModeChip mode="FIXTURE" /></div>
          <p>
            After a kill with one approved packet pending and a restart: <span data-fact="p11.sends">{fact("p11.sends")}</span> send, <span data-fact="p11.duplicates">{fact("p11.duplicates")}</span> duplicates. The mail transport is a local capture, so this proves the state machine and the idempotency key, not a mail provider.
          </p>
          <p className="src" style={{ margin: 0 }}>{p11.transport}</p>
        </GlowCard>

        <GlowCard tone="port" className="stack">
          <div className="row"><h2 className="h-md display">Not run yet</h2><ModeChip mode="NOT RUN" /></div>
          <p style={{ margin: 0 }}>P1 prover on the sandbox effective policy, P2 injection inbox with and without the sandbox, P4 fail closed, P5 credential placeholder, P6 against Nemotron, P8 reading on specimen images, P9 drift watch, P10 unattended runs, P12 cost. Each needs a key or the running OpenShell stack.</p>
        </GlowCard>
      </section>
    </>
  );
}
