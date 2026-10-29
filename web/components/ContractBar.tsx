import { Chip } from "./Chip";
import { fmtDate, type DocVerdict } from "../lib/data";

function days(a: string, b: string) {
  return (Date.parse(b) - Date.parse(a)) / 86400000;
}

/** One lane per document across the contract window. A lapse turns the rest of the lane port red, with the rule quote shown. */
export function ContractBar({ start, end, documents }: { start: string; end: string; documents: DocVerdict[] }) {
  const total = Math.max(1, days(start, end));
  return (
    <div className="lanes" role="list" aria-label={`Documents across the contract from ${fmtDate(start)} to ${fmtDate(end)}`}>
      <div className="lane" aria-hidden="true">
        <div className="muted" style={{ fontSize: 13 }}>Contract window</div>
        <div className="row" style={{ justifyContent: "space-between", fontSize: 13 }}>
          <span className="mono">{fmtDate(start)}</span>
          <span className="mono">{fmtDate(end)}</span>
        </div>
      </div>
      {documents.map((d) => {
        const lapse = d.state === "LAPSES_DURING";
        const frac = d.expiry && lapse ? Math.min(1, Math.max(0, days(start, d.expiry) / total)) : 1;
        const ok = d.state === "VALID_THROUGH";
        const unknown = !d.expiry || d.state === "UNREAD" || d.state === "MISSING";
        return (
          <div className="lane" role="listitem" key={d.document_id}>
            <div className="lane-label">
              <div style={{ fontWeight: 500 }}>{d.label}</div>
              <div style={{ marginTop: 4 }}>
                <Chip state={d.state} />
              </div>
            </div>
            <div>
              <div className="lane-track">
                {!unknown && (
                  <div className={`lane-fill ${ok ? "valid" : "lapse"}`} style={{ width: `${frac * 100}%`, animation: "grow .9s ease-out both" }} />
                )}
                {lapse && <div className="lane-gap" style={{ left: `${frac * 100}%` }} />}
                {lapse && <div className="lane-mark" style={{ left: `${frac * 100}%` }} />}
              </div>
              {lapse && d.day_x && (
                <div style={{ marginTop: 6, fontSize: 14 }}>
                  <span className="mono">{fmtDate(d.expiry as string)}</span>, day {d.day_x} of {d.day_y}.
                  {d.rules[0] ? <div className="quote" style={{ marginTop: 6 }}>{d.rules[0].quote} <span className="src">({d.rules[0].rule_id})</span></div> : null}
                  {d.renewal?.state === "ASK_ADMINISTRATION" ? <div className="src" style={{ marginTop: 4 }}>Renewal window: ask the administration. No sourced rule for it is shipped yet.</div> : null}
                </div>
              )}
              {unknown && <div style={{ marginTop: 6, fontSize: 14 }} className="muted">{d.arithmetic}</div>}
            </div>
          </div>
        );
      })}
      <style>{`@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } } @media (prefers-reduced-motion: reduce) { .lane-fill { animation: none !important; } }`}</style>
    </div>
  );
}
