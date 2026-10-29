"use client";
import { useState } from "react";
import { Chip, ModeChip } from "./Chip";
import { runOffer } from "../lib/api";
import type { Readiness } from "../lib/data";

export function DemoOffer() {
  const [text, setText] = useState("New contract offer for you, joining 1 Feb to 31 Jul. Can you make it?");
  const [out, setOut] = useState<{ reply: string; result: Readiness | null; mode: string; note?: string; error?: string } | null>(null);
  const [busy, setBusy] = useState(false);

  async function go() {
    setBusy(true);
    const r = await runOffer(text);
    setOut({ reply: r.data.reply, result: r.data.result, mode: r.mode, note: r.note, error: r.error });
    setBusy(false);
  }

  return (
    <div className="stack">
      <div>
        <label htmlFor="offer">Message from the manning agent (forwarded on Telegram)</label>
        <textarea id="offer" rows={3} value={text} onChange={(e) => setText(e.target.value)} />
      </div>
      <button className="btn btn-ink" onClick={go} disabled={busy}>{busy ? "Working" : "Run the offer flow"}</button>
      <p className="src" style={{ margin: 0 }}>
        Runs triage, then the Navigator, then the plan writer. Caps: one live run at a time per browser, 8 an hour per address, 60 a day overall. Past a cap you get the recorded run.
      </p>
      {out && (
        <div className="callout" aria-live="polite">
          <div className="row" style={{ marginBottom: 8 }}>
            <ModeChip mode={out.mode} />
            {out.result && <Chip state={out.result.overall} />}
          </div>
          <div>{out.reply}</div>
          {out.error && <p className="src" style={{ margin: "8px 0 0" }}>{out.error}</p>}
          {out.note && <p className="src" style={{ margin: "8px 0 0" }}>{out.note}</p>}
        </div>
      )}
    </div>
  );
}
