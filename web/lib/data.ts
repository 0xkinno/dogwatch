import recorded from "../data/recorded.json";

export type DocVerdict = {
  document_id: string;
  doc_type: string;
  label: string;
  state: string;
  expiry: string | null;
  arithmetic: string;
  day_x: number | null;
  day_y: number | null;
  renewal: { state: string; opens_on?: string; arithmetic?: string; reason?: string } | null;
  rules: { rule_id: string; quote: string; url: string; section: string; retrieved: string; status: string; pack: string; pack_sha256: string }[];
  sea_service: unknown[];
};

export type Readiness = {
  overall: string;
  window_start: string;
  window_end: string;
  documents: DocVerdict[];
  summary: string;
  pack_hashes: Record<string, string>;
};

export type Fact = { claim: string; value: number | string; source: string; tag: string };

export const R = recorded as unknown as {
  mode: string;
  run_id: string;
  recorded_at: string;
  persona: { name: string; role: string; today: string; contract: { start: string; end: string; required_types: string[] } };
  readiness: Readiness;
  facts: Record<string, Fact>;
  proof: Record<string, any>;
  sources: { id: string; claim: string; value?: number; unit?: string; url: string; quote?: string; status: string; note?: string }[];
  packs: Record<string, { rules: number; status: string; sha256: string; administration: string; rule_list: DocVerdict["rules"] }>;
  policy: string;
  prover: Record<string, string>;
  boundary_runs: Record<string, string>;
  ledger: { sign_on: string; sign_off: string; vessel: string; flag: string; capacity: string; ship_type: string }[];
  ledger_window: string[];
  ledger_totals: Record<string, { total: number; unit: string }>;
  routing: { role: string; size: string; model: string; thinking: boolean; max_tokens: number; confirmed: boolean }[];
  receipts: { count: number; note: string };
  outbox: { packet: any; recipients: string[]; digest: string; status: string; plan_source: string; sent: unknown[] };
  live: Record<string, any>;
  probe: Record<string, any> | null;
};

export function fact(key: string): string {
  const f = R.facts[key];
  if (!f) return "n/a";
  const v = f.value;
  return typeof v === "number" && Math.abs(v) >= 10000 ? v.toLocaleString("en-US") : String(v);
}

export function fmtDate(iso: string): string {
  const d = new Date(iso + "T00:00:00Z");
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
}
