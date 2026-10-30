import Link from "next/link";
import { WatchDial } from "../components/WatchDial";
import { GlowCard } from "../components/GlowCard";
import { Reveal } from "../components/Reveal";
import { ModeChip } from "../components/Chip";
import { ContractRunner } from "../components/ContractRunner";
import { Doors } from "../components/Doors";
import { Hero } from "../components/Hero";
import { CountUp } from "../components/CountUp";
import { R, fact } from "../lib/data";

const src = (id: string) => R.sources.find((s) => s.id === id)!;
const num = (k: string) => Number(R.facts[k]?.value ?? 0);
const ROUTE = "Route: NVIDIA API Catalog (development)";
const DOCS = ["Certificate of competency", "Medical fitness", "Basic safety training", "Oil tanker endorsement", "Passport", "Discharge book", "Certificate of equivalent competency", "GMDSS operator", "Seaman's book"];

export default function Home() {
  const p3 = (R.proof.p3_cases ?? []) as { id: string; transform: string; literal_denied: boolean; seal_denied: boolean; seal_path: string[] }[];
  const denials = ["url_twice", "base64", "homoglyph"].map((t) => p3.find((c) => c.transform === t && c.seal_denied)).filter(Boolean) as typeof p3;
  const docs = R.readiness.documents;
  const med = docs.find((d) => d.state === "LAPSES_DURING");

  const strip = [
    { k: "04:10 on watch", href: "#check", v: <>Medical lapses <b className="bad">day {med?.day_x ?? "?"}</b> of {med?.day_y ?? "?"}</> },
    { k: "Encoded attacks, 200 cases", href: "/proof", v: <>Seal missed <b data-fact="p3.seal.missed">{fact("p3.seal.missed")}</b>, literal guard <b className="bad" data-fact="p3.literal.missed">{fact("p3.literal.missed")}</b> <span className="src">(Seal v2 was tuned on these cases: a regression check, not an independent score)</span></> },
    { k: "Super alone, NVIDIA API Catalog (dev)", href: "/proof", v: <><b className="bad" data-fact="p6.super.false_safe">{fact("p6.super.false_safe")}</b> false-safe, Navigator <b data-fact="p6.engine.false_safe">{fact("p6.engine.false_safe")}</b></> },
  ];

  return (
    <>
      <Hero strip={strip} />

      <div className="ribbon" aria-hidden="true">
        <div className="ribbon-track">
          {[...DOCS, ...DOCS].map((d, i) => (<span key={i}>{d}</span>))}
        </div>
      </div>

      <section className="section" aria-labelledby="moment-t">
        <div className="wrap">
          <Reveal>
            <div className="folio">No. 01 &nbsp; The moment</div>
            <h2 id="moment-t" className="display h-lg" style={{ maxWidth: "15em" }}>
              The moment a contract is offered, <span className="serif">the papers decide.</span>
            </h2>
          </Reveal>
          <div className="grid-3" style={{ marginTop: 40 }}>
            <Reveal><GlowCard>
              <div className="stat">04:10</div>
              <h3 className="h-md" style={{ margin: "12px 0" }}>On watch</h3>
              <p>
                Arjun is Second Officer on a product tanker, on the four-to-eight watch. The world fleet runs on about{" "}
                <strong>{(src("ics-workforce-size-2021").value ?? 0).toLocaleString("en-US")}</strong> seafarers.
              </p>
              <p className="src"><a href={src("ics-workforce-size-2021").url}>Source: BIMCO and ICS Seafarer Workforce Report 2021</a></p>
            </GlowCard></Reveal>
            <Reveal delay={0.08}><GlowCard tone="amber">
              <div className="stat"><CountUp value={num("need.officer_shortfall")} factKey="need.officer_shortfall" /></div>
              <h3 className="h-md" style={{ margin: "12px 0" }}>Officers short</h3>
              <p>A shortfall of certified officers means agents move fast when a name is not ready, and certificates must be carried in original form on board.</p>
              <p className="src"><a href={src("ics-officer-shortfall-2021").url}>BIMCO and ICS</a>, <a href={src("amsa-carry-original").url}>AMSA Marine Notice 2025/05</a></p>
            </GlowCard></Reveal>
            <Reveal delay={0.16}><GlowCard tone="port">
              <div className="stat">US$<CountUp value={num("need.contract_floor")} factKey="need.contract_floor" /></div>
              <h3 className="h-md" style={{ margin: "12px 0" }}>A six month contract</h3>
              <p>
                Six months at the ILO floor of US$<span data-fact="need.ilo_wage">{fact("need.ilo_wage")}</span> a month for an able seafarer. A floor, not Arjun&apos;s wage. If the papers are not ready, the job goes to the next name.
              </p>
              <p className="src"><a href={src("ilo-wage-2027").url}>Source: ILO Joint Maritime Commission agreement</a></p>
            </GlowCard></Reveal>
          </div>
        </div>
      </section>

      <section className="section" id="check" aria-labelledby="check-t" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <Reveal>
            <div className="folio">No. 02 &nbsp; The check</div>
            <h2 id="check-t" className="display h-lg">Computed in code, <span className="serif">shown with its rule.</span></h2>
            <p className="lede" style={{ marginTop: 14 }}>
              Arjun forwards the offer. The Navigator compares every document with the contract window and never calls a model. The medical lapses mid-contract, and the rule behind each answer is on the page.
            </p>
          </Reveal>
          <div className="two-col" style={{ marginTop: 36, gridTemplateColumns: "minmax(0, 5fr) minmax(0, 7fr)", alignItems: "stretch" }}>
            <Reveal><GlowCard tone="amber" className="dial-card">
              <div data-shot="home-dial" style={{ maxWidth: 420, margin: "0 auto" }}>
                <WatchDial id="check-dial" documents={docs} label="Watch dial for Arjun's documents" />
              </div>
              <p className="src" style={{ textAlign: "center", margin: "14px 0 0" }}>
                Each capsule sits at a document&apos;s expiry month. The dog watches, 16 to 20 hours, are shaded amber.
              </p>
            </GlowCard></Reveal>
            <Reveal delay={0.1}><GlowCard><ContractRunner /></GlowCard></Reveal>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="boundary-t" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <Reveal>
            <div className="folio">No. 03 &nbsp; The boundary</div>
            <h2 id="boundary-t" className="display h-lg">Four doors, <span className="serif">one Seal.</span></h2>
            <p className="lede" style={{ marginTop: 14 }}>
              The assistant is designed to work inside an NVIDIA OpenShell sandbox; the sandbox ran on a CI runner and its proofs are below. The cloud model sees placeholders, never a certificate number. A gateway outside the agent allows four destinations, and a middleware called the Seal refuses any request that carries a vault value, even in an encoded form.
            </p>
          </Reveal>
          <div className="two-col" style={{ alignItems: "start", marginTop: 32 }}>
            <Reveal><GlowCard><Doors /></GlowCard></Reveal>
            <Reveal delay={0.1}><GlowCard tone="amber" className="stack">
              <div className="row"><ModeChip mode="LOCAL BUILD" /><span className="src">Seal decisions on the pre-registered corpus (P3). The sandbox started on a GitHub Actions runner; P5 and the advisor flow passed there, P1 found two excesses that are fixed, and sandboxed P2 and P4 are inconclusive until the re-run.</span></div>
              {denials.map((c) => (
                <pre key={c.id} tabIndex={0} aria-label={`Seal decision for case ${c.id}`}>{`${c.id}  transform=${c.transform}\nliteral guard: ${c.literal_denied ? "denied" : "allowed"}\nseal: deny  path=${c.seal_path.join(">")}`}</pre>
              ))}
              <Link href="/boundary" className="btn btn-ink">Open the boundary page</Link>
            </GlowCard></Reveal>
          </div>
        </div>
      </section>

      <section className="section dark-sec" aria-labelledby="proof-t">
        <div className="wrap">
          <Reveal>
            <div className="folio">No. 04 &nbsp; Proof</div>
            <h2 id="proof-t" className="display h-lg">The model alone <span className="serif">got it wrong.</span></h2>
            <p className="lede" style={{ marginTop: 14 }}>
              Sixty synthetic seafarer profiles, expected verdicts written by an independent oracle before the run. The same Nemotron models were given the rule text and asked for the verdict. Misses stay in the denominator and are listed by id.
            </p>
            <p style={{ marginTop: 10 }}><ModeChip mode={ROUTE} /></p>
          </Reveal>
          <div className="grid-4" style={{ marginTop: 36 }}>
            <Reveal><GlowCard tone="port">
              <div className="stat"><CountUp value={num("p6.super.false_safe")} factKey="p6.super.false_safe" /></div>
              <p style={{ marginTop: 10 }}>Nemotron Super alone said READY when it was not, out of <span data-fact="p6.profiles">{fact("p6.profiles")}</span> profiles.</p>
            </GlowCard></Reveal>
            <Reveal delay={0.06}><GlowCard tone="amber">
              <div className="stat"><CountUp value={num("p6.ultra.false_alarm")} factKey="p6.ultra.false_alarm" /></div>
              <p style={{ marginTop: 10 }}>Nemotron Ultra alone raised a false alarm on a READY profile. Its false-safe count was <span data-fact="p6.ultra.false_safe">{fact("p6.ultra.false_safe")}</span>.</p>
            </GlowCard></Reveal>
            <Reveal delay={0.12}><GlowCard>
              <div className="stat"><CountUp value={num("p6.engine.correct")} factKey="p6.engine.correct" /></div>
              <p style={{ marginTop: 10 }}>profiles matched by the Navigator, which calls no model. A self-built set, so not the headline.</p>
            </GlowCard></Reveal>
            <Reveal delay={0.18}><GlowCard>
              <div className="stat"><CountUp value={num("p8.exact")} factKey="p8.exact" /></div>
              <p style={{ marginTop: 10 }}>of <span data-fact="p8.specimens">{fact("p8.specimens")}</span> specimen certificates read exactly, with <span data-fact="p8.leaks">{fact("p8.leaks")}</span> identifiers in <span data-fact="p8.bodies">{fact("p8.bodies")}</span> request bodies.</p>
            </GlowCard></Reveal>
          </div>
          <div className="grid-3" style={{ marginTop: 18 }}>
            <Reveal><GlowCard>
              <div className="stat"><CountUp value={num("p3.literal.missed")} factKey="p3.literal.missed" /></div>
              <p style={{ marginTop: 10 }}>of <span data-fact="p3.attacks">{fact("p3.attacks")}</span> encoded attacks a literal guard lets through. The first Seal missed <span data-fact="p3.seal_v1.missed">{fact("p3.seal_v1.missed")}</span>; both runs are published.</p>
            </GlowCard></Reveal>
            <Reveal delay={0.08}><GlowCard>
              <div className="stat"><CountUp value={num("p7.flips")} factKey="p7.flips" /></div>
              <p style={{ marginTop: 10 }}>of <span data-fact="p7.histories">{fact("p7.histories")}</span> sea-service histories change verdict with the counting convention. No sourced rule states one.</p>
            </GlowCard></Reveal>
            <Reveal delay={0.16}><GlowCard>
              <div className="stat"><CountUp value={num("p1.exceeds")} factKey="p1.exceeds" /></div>
              <p style={{ marginTop: 10 }}>attack policies the OpenShell prover reported as exceeding the boundary, each with a counterexample.</p>
            </GlowCard></Reveal>
          </div>
          <div className="row" style={{ marginTop: 28 }}>
            <Link className="btn btn-paper" href="/proof">Every case, misses first</Link>
            <Link className="btn btn-ghost" href="/boundary">Prover output</Link>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="may-t">
        <div className="wrap">
          <Reveal>
            <div className="folio">No. 05 &nbsp; The rule of the ship</div>
            <h2 id="may-t" className="display h-lg">What a model may, <span className="serif">and may not, do.</span></h2>
          </Reveal>
          <div className="two-col" style={{ marginTop: 32 }}>
            <Reveal><GlowCard>
              <h3 className="h-md">May</h3>
              <ul style={{ paddingLeft: 18, margin: "14px 0 0" }}>
                <li>Classify an incoming message.</li>
                <li>Structure placeholder text into fields, each with a quote that code checks.</li>
                <li>Write prose around locked value tokens.</li>
                <li>Read a regulator page and quote it.</li>
              </ul>
            </GlowCard></Reveal>
            <Reveal delay={0.1}><GlowCard tone="port">
              <h3 className="h-md">May not</h3>
              <ul style={{ paddingLeft: 18, margin: "14px 0 0" }}>
                <li>Decide whether a certificate is valid.</li>
                <li>Compute a date or a day count.</li>
                <li>Write a digit Arjun will act on.</li>
                <li>See a raw identifier, or change a rule pack.</li>
              </ul>
            </GlowCard></Reveal>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="judges-t" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <Reveal>
            <div className="folio">No. 06 &nbsp; For judges</div>
            <h2 id="judges-t" className="display h-lg">Value in <span className="serif">sixty seconds.</span></h2>
          </Reveal>
          <ol className="grid-3" style={{ listStyle: "none", padding: 0, marginTop: 32 }}>
            {[
              ["1", "Run the check", "Press Check on the contract above. Watch the medical lapse on day 42 of 181 with its rule quote."],
              ["2", "Try an offer", "On the judge page, paste a contract offer and see the same code path the Telegram flow uses."],
              ["3", "Read the proof", "Open the proof page. Misses are listed first, case by case, with the route each run used."],
            ].map(([n, t, d]) => (
              <GlowCard as="li" key={n}>
                <div className="stat">{n}</div>
                <h3 className="h-md" style={{ margin: "12px 0" }}>{t}</h3>
                <p>{d}</p>
              </GlowCard>
            ))}
          </ol>
          <div className="row" style={{ marginTop: 26 }}>
            <Link className="btn btn-ink" href="/judge">Open the judge walks</Link>
            <Link className="btn btn-paper" href="/how">Architecture and crew</Link>
          </div>
        </div>
      </section>
    </>
  );
}
