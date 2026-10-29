import Image from "next/image";
import Link from "next/link";
import { SmoothScroll } from "../components/SmoothScroll";
import { WatchDial } from "../components/WatchDial";
import { GlowCard } from "../components/GlowCard";
import { Reveal } from "../components/Reveal";
import { ModeChip } from "../components/Chip";
import { ContractRunner } from "../components/ContractRunner";
import { Doors } from "../components/Doors";
import { R, fact } from "../lib/data";

const src = (id: string) => R.sources.find((s) => s.id === id)!;

export default function Home() {
  const p3 = (R.proof.p3_cases ?? []) as { id: string; transform: string; literal_denied: boolean; seal_denied: boolean; seal_path: string[] }[];
  const denials = ["url_twice", "base64", "homoglyph"].map((t) => p3.find((c) => c.transform === t && c.seal_denied)).filter(Boolean) as typeof p3;
  const docs = R.readiness.documents;
  return (
    <>
      <SmoothScroll />
      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-grid">
          <div className="hero-copy">
            <span className="eyebrow">Personal AI for seafarers</span>
            <h1 id="hero-title" className="display h-xl">
              Your papers
              <br />
              keep watch
              <br />
              <span className="serif">while you do.</span>
            </h1>
            <p className="lede">
              Dogwatch reads a seafarer&apos;s certificates on his own machine, computes every expiry in code, and has the renewal ready before a lapse costs him a contract.
            </p>
            <div className="hero-actions">
              <a className="btn btn-ink" href="#check">See Arjun&apos;s check</a>
              <Link className="btn btn-paper" href="/boundary">How the boundary works</Link>
            </div>
          </div>
          <div className="hero-media">
            <Image
              src="/img/hero.webp"
              alt="A merchant navy officer in a dark working jacket stands at the rail of a tanker at sunset, reading a phone, with the radar mast and satellite dome behind him."
              fill
              priority
              sizes="(max-width: 900px) 100vw, 55vw"
            />
            <div className="hero-badge"><ModeChip mode="SPECIMEN PROFILE" /></div>
          </div>
          <div className="hero-dial">
            <GlowCard>
              <WatchDial id="hero-dial" documents={docs} label="Watch dial for Arjun's documents" />
            </GlowCard>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="moment-t">
        <div className="wrap">
          <Reveal>
            <h2 id="moment-t" className="display h-lg" style={{ maxWidth: "14em" }}>
              The moment a contract is offered, <span className="serif">the papers decide.</span>
            </h2>
          </Reveal>
          <div className="grid-3" style={{ marginTop: 36 }}>
            <GlowCard>
              <div className="stat">04:10</div>
              <h3 className="h-md" style={{ margin: "10px 0" }}>On watch</h3>
              <p>
                Arjun is Second Officer on a product tanker, on the four-to-eight watch. The world fleet runs on about{" "}
                <strong>{(src("ics-workforce-size-2021").value ?? 0).toLocaleString("en-US")}</strong> seafarers.
              </p>
              <p className="src"><a href={src("ics-workforce-size-2021").url}>Source: BIMCO and ICS Seafarer Workforce Report 2021</a></p>
            </GlowCard>
            <GlowCard tone="amber">
              <div className="stat">20 min</div>
              <h3 className="h-md" style={{ margin: "10px 0" }}>Of internet a day</h3>
              <p>
                His certificates must be carried in original form on board, and a shortfall of{" "}
                <strong data-fact="need.officer_shortfall">{fact("need.officer_shortfall")}</strong> certified officers means agents move fast when a name is not ready.
              </p>
              <p className="src"><a href={src("amsa-carry-original").url}>Source: AMSA Marine Notice 2025/05</a>, <a href={src("ics-officer-shortfall-2021").url}>BIMCO and ICS</a></p>
            </GlowCard>
            <GlowCard tone="port">
              <div className="stat">US${fact("need.contract_floor")}</div>
              <h3 className="h-md" style={{ margin: "10px 0" }}>A six month contract</h3>
              <p>
                Six months at the ILO floor of US$<span data-fact="need.ilo_wage">{fact("need.ilo_wage")}</span> a month for an able seafarer. A floor, not Arjun&apos;s wage, and the job goes to the next name.
              </p>
              <p className="src"><a href={src("ilo-wage-2027").url}>Source: ILO Joint Maritime Commission agreement</a></p>
            </GlowCard>
          </div>
        </div>
      </section>

      <section className="section" id="check" aria-labelledby="check-t">
        <div className="wrap">
          <Reveal>
            <h2 id="check-t" className="display h-lg">The check, <span className="serif">computed in code.</span></h2>
            <p className="lede" style={{ marginTop: 14 }}>
              Arjun forwards the offer. Every document is compared with the contract window by the Navigator, which never calls a model. The medical lapses mid-contract and the rule behind each answer is shown.
            </p>
          </Reveal>
          <GlowCard className="" >
            <ContractRunner />
          </GlowCard>
        </div>
      </section>

      <section className="section" aria-labelledby="boundary-t">
        <div className="wrap">
          <Reveal>
            <h2 id="boundary-t" className="display h-lg">The boundary: <span className="serif">four doors, one Seal.</span></h2>
            <p className="lede" style={{ marginTop: 14 }}>
              The assistant works inside an NVIDIA OpenShell sandbox. The cloud model sees placeholders, never a certificate number. A gateway outside the agent allows four destinations and a middleware called the Seal refuses any request that carries a vault value, even in an encoded form.
            </p>
          </Reveal>
          <div className="two-col" style={{ alignItems: "start", marginTop: 28 }}>
            <GlowCard><Doors /></GlowCard>
            <GlowCard tone="amber" className="stack">
              <div className="row"><ModeChip mode="LOCAL BUILD" /><span className="src">Seal decisions on the pre-registered corpus (P3). The injected-email run (P2) is NOT RUN yet.</span></div>
              {denials.map((c) => (
                <pre tabIndex={0} key={c.id} aria-label={`Seal decision for case ${c.id}`}>{`${c.id}  transform=${c.transform}\nliteral guard: ${c.literal_denied ? "denied" : "allowed"}\nseal: deny  path=${c.seal_path.join(">")}`}</pre>
              ))}
              <Link href="/boundary" className="btn btn-paper">Open the boundary page</Link>
            </GlowCard>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="may-t">
        <div className="wrap">
          <Reveal>
            <h2 id="may-t" className="display h-lg">What a model may, <span className="serif">and may not, do.</span></h2>
          </Reveal>
          <div className="two-col" style={{ marginTop: 28 }}>
            <GlowCard>
              <h3 className="h-md">May</h3>
              <ul style={{ paddingLeft: 18, margin: "12px 0 0" }}>
                <li>Classify an incoming message.</li>
                <li>Structure placeholder text into fields, each with a quote that code checks.</li>
                <li>Write prose around locked value tokens.</li>
                <li>Read a regulator page and quote it.</li>
              </ul>
            </GlowCard>
            <GlowCard tone="port">
              <h3 className="h-md">May not</h3>
              <ul style={{ paddingLeft: 18, margin: "12px 0 0" }}>
                <li>Decide whether a certificate is valid.</li>
                <li>Compute a date or a day count.</li>
                <li>Write a digit Arjun will act on.</li>
                <li>See a raw identifier, or change a rule pack.</li>
              </ul>
            </GlowCard>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="proof-t">
        <div className="wrap">
          <Reveal>
            <h2 id="proof-t" className="display h-lg">Proof, <span className="serif">misses included.</span></h2>
            <p className="lede" style={{ marginTop: 14 }}>Numbers come from committed result files. These sets are built by this project, so they are internal measurements, labelled as such.</p>
          </Reveal>
          <div className="grid-4" style={{ marginTop: 28 }}>
            <GlowCard>
              <div className="stat" data-fact="p3.literal.missed">{fact("p3.literal.missed")}</div>
              <p>of <span data-fact="p3.attacks">{fact("p3.attacks")}</span> encoded attacks a literal guard lets through</p>
              <Link href="/proof" className="src">See every case</Link>
            </GlowCard>
            <GlowCard tone="amber">
              <div className="stat" data-fact="p3.seal_v1.missed">{fact("p3.seal_v1.missed")}</div>
              <p>missed by the first version of the Seal, then fixed. Both runs are published.</p>
              <Link href="/proof" className="src">Misses by id</Link>
            </GlowCard>
            <GlowCard>
              <div className="stat" data-fact="p7.flips">{fact("p7.flips")}</div>
              <p>of <span data-fact="p7.histories">{fact("p7.histories")}</span> sea-service histories change verdict with the counting convention</p>
              <Link href="/proof" className="src">The finding</Link>
            </GlowCard>
            <GlowCard tone="port">
              <div className="stat" data-fact="p1.exceeds">{fact("p1.exceeds")}</div>
              <p>attack policies the prover reported as exceeding the boundary, with a counterexample</p>
              <Link href="/boundary" className="src">Prover output</Link>
            </GlowCard>
          </div>
        </div>
      </section>

      <section className="section" aria-labelledby="judges-t">
        <div className="wrap">
          <Reveal>
            <h2 id="judges-t" className="display h-lg">For judges: <span className="serif">sixty seconds.</span></h2>
          </Reveal>
          <ol className="grid-3" style={{ listStyle: "none", padding: 0, marginTop: 28 }}>
            {[
              ["1", "Run the check", "Press Check on the contract above. Watch the medical lapse on day 42 of 181 with its rule quote."],
              ["2", "Try an offer", "On the judge page, paste a contract offer and see the same code path the Telegram flow uses."],
              ["3", "Read the proof", "Open the proof page. Misses are listed first, case by case."],
            ].map(([n, t, d]) => (
              <GlowCard key={n} as="li">
                <div className="stat">{n}</div>
                <h3 className="h-md" style={{ margin: "10px 0" }}>{t}</h3>
                <p>{d}</p>
              </GlowCard>
            ))}
          </ol>
          <div className="row" style={{ marginTop: 22 }}>
            <Link className="btn btn-ink" href="/judge">Open the judge walks</Link>
            <Link className="btn btn-paper" href="/how">Architecture and crew</Link>
          </div>
        </div>
      </section>
    </>
  );
}
