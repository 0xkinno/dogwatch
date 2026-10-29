import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { Chip } from "../../components/Chip";
import { R } from "../../lib/data";

export const metadata = { title: "Outbox | Dogwatch" };

export default function Outbox() {
  const o = R.outbox;
  return (
    <>
      <PageHead
        eyebrow="Outbox"
        title="Nothing leaves"
        serif="without his approval."
        lede="A draft holds placeholders, never identifiers. Arjun approves a digest of exactly what will be sent. Sending recomputes the digest and refuses on any mismatch."
        mode={{ label: "RECORDED", detail: `${R.run_id} ${R.recorded_at}` }}
      />
      <section className="wrap" data-shot="outbox" style={{ paddingBottom: 64 }}>
        <div className="two-col" style={{ alignItems: "start" }}>
          <GlowCard className="stack">
            <div className="row"><h2 className="h-md display">Draft for the manning agent</h2><span className="chip chip-window">APPROVAL PENDING</span></div>
            <div className="callout">
              <div className="mono" style={{ wordBreak: "break-all" }}>digest {o.digest.slice(0, 8)} <span className="muted">({o.digest})</span></div>
              <div className="src" style={{ marginTop: 6 }}>Recipient on the allowlist: {o.recipients[0]}. A draft to any other address is refused.</div>
            </div>
            <p><strong>{o.packet.summary}</strong></p>
            <p>{o.packet.plan}</p>
            <p className="src">Plan text source: {o.plan_source === "TEMPLATE" ? "deterministic template (no model text used in this recorded draft)" : "model text with locked value tokens"}.</p>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Identifier line</th><th scope="col">In the draft</th></tr></thead>
                <tbody>
                  {Object.entries(o.packet.identifier_lines as Record<string, string>).map(([k, v]) => (
                    <tr key={k}><td>{k}</td><td className="mono">{v}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="src" style={{ margin: 0 }}>The real values are filled in only on Arjun&apos;s machine, after the approval token is verified.</p>
          </GlowCard>
          <GlowCard tone="amber" className="stack">
            <h2 className="h-md display">Document rows in the packet</h2>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Document</th><th scope="col">State</th><th scope="col">Expiry</th></tr></thead>
                <tbody>
                  {(o.packet.rows as { document: string; state: string; expiry: string | null }[]).map((r) => (
                    <tr key={r.document}><td>{r.document}</td><td><Chip state={r.state} /></td><td className="mono">{r.expiry ?? "unread"}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3 className="h-md display" style={{ fontSize: "1.1rem" }}>Sent log</h3>
            <p className="muted" style={{ margin: 0 }}>
              No packet has been sent from this build. When one is sent, the log shows the time and a redacted recipient, never the content.
            </p>
          </GlowCard>
        </div>
      </section>
    </>
  );
}
