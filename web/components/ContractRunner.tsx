"use client";
import { useState } from "react";
import { ContractBar } from "./ContractBar";
import { Chip, ModeChip } from "./Chip";
import { R, fmtDate, type Readiness } from "../lib/data";
import { runReadiness } from "../lib/api";

export function ContractRunner({ showApproval = false }: { showApproval?: boolean }) {
  const c = R.persona.contract;
  const [start, setStart] = useState(c.start);
  const [end, setEnd] = useState(c.end);
  const [travel, setTravel] = useState(0);
  const [res, setRes] = useState<Readiness>(R.readiness);
  const [mode, setMode] = useState<"LIVE" | "DEMO" | "RECORDED">("RECORDED");
  const [note, setNote] = useState<string>("Recorded run for 1 Feb to 31 Jul. Change the dates and press Check to run the Navigator.");
  const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState(false);

  async function run() {
    setBusy(true);
    const out = await runReadiness(start, end, travel);
    setRes(out.data);
    setMode(out.mode);
    setNote(out.note ?? "Computed in code by the Navigator. No model was called.");
    setBusy(false);
  }

  const lapse = res.documents.find((d) => d.state === "LAPSES_DURING");
  return (
    <div className="stack">
      <form
        className="grid-4"
        onSubmit={(e) => {
          e.preventDefault();
          run();
        }}
        aria-label="Contract window"
      >
        <div>
          <label htmlFor="start">Joining</label>
          <input id="start" type="date" value={start} onChange={(e) => setStart(e.target.value)} required />
        </div>
        <div>
          <label htmlFor="end">Signing off</label>
          <input id="end" type="date" value={end} onChange={(e) => setEnd(e.target.value)} required />
        </div>
        <div>
          <label htmlFor="travel">Travel days after</label>
          <input id="travel" type="number" min={0} max={30} value={travel} onChange={(e) => setTravel(Number(e.target.value))} />
        </div>
        <div style={{ display: "flex", alignItems: "end" }}>
          <button className="btn btn-ink" type="submit" disabled={busy} style={{ width: "100%" }}>
            {busy ? "Checking" : "Check"}
          </button>
        </div>
      </form>
      <div className="row" aria-live="polite">
        <ModeChip mode={mode} />
        <Chip state={res.overall} />
        <span>{res.summary}</span>
      </div>
      <p className="src" style={{ margin: 0 }}>{note}</p>
      <ContractBar start={res.window_start} end={res.window_end} documents={res.documents} />
      {showApproval && (
        <div className="stack">
          <button className="btn btn-paper" onClick={() => setPreview(!preview)} aria-expanded={preview}>
            {preview ? "Hide the packet preview" : "Send to agent: show the approval preview"}
          </button>
          {preview && (
            <div className="callout">
              <strong>Approval preview (DEMO, nothing is sent from this page).</strong>
              <p style={{ margin: "8px 0 0" }}>
                The packet holds placeholders such as <span className="mono">[[COC_1]]</span> instead of identifiers. In the product, Arjun approves the packet on Telegram,
                the approval is bound to its digest, and only then does the Radio Officer fill in the real values on his machine and email the manning agent.
                {lapse ? ` The packet says: ${res.summary}` : ""}
              </p>
            </div>
          )}
        </div>
      )}
      <p className="src" style={{ margin: 0 }}>
        Window {fmtDate(res.window_start)} to {fmtDate(res.window_end)}. Rule pack hashes are in the response; the arithmetic is shown under each lane.
      </p>
    </div>
  );
}
