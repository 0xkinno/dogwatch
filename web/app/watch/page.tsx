import { PageHead } from "../../components/PageHead";
import { WatchDial } from "../../components/WatchDial";
import { GlowCard } from "../../components/GlowCard";
import { Chip } from "../../components/Chip";
import { R, fmtDate } from "../../lib/data";

export const metadata = { title: "Arjun's watch | Dogwatch" };

const CONV_LABEL: Record<string, string> = {
  days_inclusive: "Days, both endpoints",
  days_exclusive: "Days, sign-off day not counted",
  calendar_months: "Calendar months",
  days_360: "Months of 30 days",
  days_365: "Years of 365 days",
};

export default function Watch() {
  const docs = R.readiness.documents;
  return (
    <>
      <PageHead
        eyebrow="Watch"
        title="Arjun's documents,"
        serif="on watch."
        lede="Every state below is computed in code from the document dates and the rule packs. The profile is a specimen."
        mode={{ label: "RECORDED", detail: `${R.run_id} ${R.recorded_at}` }}
      />
      <section className="wrap" style={{ paddingBottom: 64 }}>
        <div className="two-col" style={{ alignItems: "start" }}>
          <GlowCard>
            <div style={{ maxWidth: 380, margin: "0 auto" }}>
              <WatchDial id="watch-dial" documents={docs} label="Watch dial: documents by expiry month" />
            </div>
            <p className="src" style={{ textAlign: "center", marginBottom: 0 }}>Capsules sit at each document&apos;s expiry month. The dog watches are shaded amber.</p>
          </GlowCard>
          <GlowCard tone="amber" className="stack">
            <h2 className="h-md display">Document matrix</h2>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Document</th><th scope="col">Administration</th><th scope="col">Expiry</th><th scope="col">State</th></tr></thead>
                <tbody>
                  {docs.map((d) => (
                    <tr key={d.document_id}>
                      <td>{d.label}</td>
                      <td>{d.doc_type === "medical" ? "India" : d.label.includes("Singapore") ? "Singapore" : "India"}</td>
                      <td className="mono">{d.expiry ? fmtDate(d.expiry) : "unread"}</td>
                      <td><Chip state={d.state} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="src" style={{ margin: 0 }}>Window checked: {fmtDate(R.readiness.window_start)} to {fmtDate(R.readiness.window_end)}.</p>
          </GlowCard>
        </div>

        <div className="two-col" style={{ marginTop: 18, alignItems: "start" }}>
          <GlowCard className="stack">
            <h2 className="h-md display">Sea-service ledger</h2>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Sign on</th><th scope="col">Sign off</th><th scope="col">Vessel</th><th scope="col">Capacity</th></tr></thead>
                <tbody>
                  {R.ledger.map((e, i) => (
                    <tr key={i}><td className="mono">{fmtDate(e.sign_on)}</td><td className="mono">{fmtDate(e.sign_off)}</td><td>{e.vessel}</td><td>{e.capacity}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h3 className="h-md display" style={{ fontSize: "1.1rem" }}>Totals in the last five years, under each counting convention</h3>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Convention</th><th scope="col">Total</th></tr></thead>
                <tbody>
                  {Object.entries(R.ledger_totals).map(([k, v]) => (
                    <tr key={k}><td>{CONV_LABEL[k] ?? k}</td><td className="mono">{v.total} {v.unit}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="src" style={{ margin: 0 }}>
              Window {fmtDate(R.ledger_window[0])} to {fmtDate(R.ledger_window[1])}. Overlapping entries count once. Where conventions disagree near a threshold the answer is Ask administration.
            </p>
          </GlowCard>

          <GlowCard tone="green" className="stack">
            <h2 className="h-md display">Model routing and cost</h2>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Job</th><th scope="col">Model</th><th scope="col">Thinking</th></tr></thead>
                <tbody>
                  {R.routing.map((r) => (
                    <tr key={r.role}>
                      <td>{r.role}</td>
                      <td className="mono">{r.model}{r.confirmed ? "" : " (id not yet confirmed by a probe)"}</td>
                      <td>{r.thinking ? "on, capped" : "off"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="src" style={{ margin: 0 }}>
              Receipts recorded: {R.receipts.count}. {R.receipts.note} Cost per weekly check and the cost if the largest model handled every call appear here once real calls are recorded; no number is shown before then.
            </p>
          </GlowCard>
        </div>
      </section>
    </>
  );
}
