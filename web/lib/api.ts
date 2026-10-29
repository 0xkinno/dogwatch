import { R, type Readiness } from "./data";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export type Labelled<T> = { mode: "LIVE" | "DEMO" | "RECORDED"; data: T; note?: string };

function browserId(): string {
  try {
    let id = localStorage.getItem("dw-browser");
    if (!id) {
      id = Math.random().toString(36).slice(2);
      localStorage.setItem("dw-browser", id);
    }
    return id;
  } catch {
    return "anon";
  }
}

/** Calls the judge door. When it cannot be reached the page shows the recorded run, labelled RECORDED. */
export async function runReadiness(start: string, end: string, travelAfter = 0): Promise<Labelled<Readiness>> {
  if (API_BASE) {
    try {
      const r = await fetch(`${API_BASE}/api/readiness`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ start, end, travel_after: travelAfter }),
      });
      if (r.ok) return { mode: "LIVE", data: (await r.json()).result };
    } catch {
      /* fall through to the recorded run */
    }
  }
  return {
    mode: "RECORDED",
    data: R.readiness,
    note: API_BASE
      ? "The API host did not answer, so this is the recorded run for 1 Feb to 31 Jul."
      : "No API host is configured in this build, so this is the recorded run for 1 Feb to 31 Jul.",
  };
}

export async function runOffer(text: string): Promise<Labelled<{ reply: string; result: Readiness | null }> & { error?: string }> {
  if (API_BASE) {
    try {
      const r = await fetch(`${API_BASE}/api/demo/offer`, {
        method: "POST",
        headers: { "content-type": "application/json", "x-browser-id": browserId() },
        body: JSON.stringify({ text }),
      });
      if (r.status === 429) {
        const j = await r.json();
        return { mode: "RECORDED", data: { reply: R.readiness.summary, result: R.readiness }, error: j.detail };
      }
      if (r.ok) {
        const j = await r.json();
        return { mode: "DEMO", data: { reply: j.reply, result: j.result } };
      }
    } catch {
      /* fall through */
    }
  }
  return {
    mode: "RECORDED",
    data: { reply: `${R.readiness.summary} Approve the packet to send it to your agent.`, result: R.readiness },
    note: "Recorded run: the API host is not reachable from this page.",
  };
}

export async function fetchStatus(): Promise<Record<string, any> | null> {
  if (!API_BASE) return null;
  try {
    const r = await fetch(`${API_BASE}/api/status`, { cache: "no-store" });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}
