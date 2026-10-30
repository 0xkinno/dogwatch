import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { ModeChip } from "../../components/Chip";
import { R } from "../../lib/data";

export const metadata = { title: "How it works | Dogwatch" };

const CREW = [
  ["Bosun", "Inside the sandbox", "OCR, placeholders, structuring with a verbatim quote per field"],
  ["Navigator", "Inside the sandbox", "Every verdict, in code, no model"],
  ["Officer of the Watch", "Inside the sandbox", "The always-on loop: triage, plan writing around locked values"],
  ["Lookout", "Inside the sandbox", "Weekly rule-drift watch on administration sites"],
  ["Radio Officer", "Host side", "Telegram, approval tokens, rehydration, email, calendar"],
  ["The Seal", "OpenShell middleware", "Refuses any outbound request carrying a vault value"],
  ["The Master", "The seafarer", "Photographs stamps, approves packets, approves or rejects new access"],
];

const SDK: [string, string, string][] = [
  ["OpenShell policy prover", "LOCAL BUILD", "Run on the build machine, version 0.1.6. Declared policy within the boundary; attack proposals reported with counterexamples."],
  ["OpenShell provider profile (NVIDIA API Catalog)", "LOCAL BUILD", "The stock NVIDIA profile was linted, imported and attached as a provider on the build machine. The Token Factory profile is written and not yet imported. The sandbox prover found its read-write access too wide; it was narrowed, and the effective-policy re-proof is unsupported by the prover."],
  ["OpenShell supervisor middleware (the Seal)", "LOCAL BUILD", "Registered with a gateway started on the build machine, and a policy naming it before registration was refused at admission. Sandbox enforcement with the Seal in the path: P4 on the Actions runner (3 of 3 refused with HTTP 403 when the Seal was stopped)."],
  ["OpenShell sandbox and policy advisor", "LIVE RUN", "Runs on a GitHub Actions ubuntu-24.04 runner. Live: P2 (20 of 20 injected posts denied, canary 0), P4 (fails closed: 403 with the Seal stopped), P5 (the agent sees only a placeholder) and the advisor flow (run 2). P1 found two excesses in the provider profile, fixed; the effective-policy re-proof is unsupported by the prover. The build machine kernel (5.10) cannot start the sandbox."],
  ["Nemotron via the NVIDIA API Catalog (development route)", "LOCAL BUILD", "Live calls with receipts that name the route. Every model result on this site came from this route."],
  ["Nemotron on Nebius Token Factory", "NOT RUN", "The submission route. No key was available, so no Token Factory call has been made. One script switches the route and re-runs the evidence."],
  ["Tavily search and extract", "LOCAL BUILD", "Live calls: the rule-drift watch, and extraction of the Singapore and India rule sources that could not be opened directly."],
  ["NemoClaw, Hermes, Nebius Serverless", "NOT USED", "Not used, so not claimed."],
];

export default function How() {
  return (
    <>
      <PageHead
        eyebrow="How it works"
        title="A crew,"
        serif="one job each."
        lede="The seafarer's machine does the reading and the deciding. The cloud model sees placeholders. A gateway outside the agent enforces the boundary."
      />
      <section className="wrap stack" style={{ paddingBottom: 64 }}>
        <GlowCard className="stack">
          <h2 className="h-md display">Architecture</h2>
          <pre tabIndex={0}>{`SEAFARER'S MACHINE (WSL2 Ubuntu or Linux, Docker)
+---------------------------------------------------------------+
| OpenShell gateway: policy, provider credentials, prover       |
|   +-- Sandbox "dogwatch" (read-only vault, no other network)  |
|   |     Bosun -> Navigator -> Officer of the Watch -> Lookout |
|   |   allowed egress: Token Factory chat, Tavily, Radio       |
|   |   Officer API, policy.local                               |
|   +-- Seal middleware (fail closed) on every allowed endpoint |
| Radio Officer (host): Telegram, email, calendar, approvals    |
| Encrypted vault: document images, identifier table            |
+---------------------------------------------------------------+
HOSTED JUDGE DOOR: the same Navigator, Bosun and Lookout code on the
specimen profile. It is not the sandboxed product.`}</pre>
        </GlowCard>
        <GlowCard tone="amber" className="stack">
          <h2 className="h-md display">The crew</h2>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <thead><tr><th scope="col">Member</th><th scope="col">Runs where</th><th scope="col">Job</th></tr></thead>
              <tbody>{CREW.map(([a, b, c]) => (<tr key={a}><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td></tr>))}</tbody>
            </table>
          </div>
        </GlowCard>
        <div className="two-col">
          <GlowCard className="stack">
            <h2 className="h-md display">Rule packs</h2>
            <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
              <table>
                <thead><tr><th scope="col">Pack</th><th scope="col">Rules</th><th scope="col">Status</th></tr></thead>
                <tbody>{Object.entries(R.packs).map(([k, p]) => (<tr key={k}><td className="mono">{k}</td><td>{p.rules}</td><td>{p.status === "unsourced" ? "no rule shipped: the source was not read" : "sourced, each quote checked against a snapshot"}</td></tr>))}</tbody>
              </table>
            </div>
            <p className="src" style={{ margin: 0 }}>A rule that could not be sourced does not exist; the engine answers Ask administration.</p>
          </GlowCard>
          <GlowCard tone="green" className="stack">
            <h2 className="h-md display">Where a model is used</h2>
            <p style={{ margin: 0 }}>Triage with Nemotron Nano, structuring with Super, plan prose with Ultra, drift reading with Nano. None of them decides validity, computes a date or writes a digit Arjun acts on.</p>
          </GlowCard>
        </div>
        <GlowCard className="stack">
          <h2 className="h-md display">SDK surface: what is live, what is not</h2>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <thead><tr><th scope="col">Feature</th><th scope="col">State</th><th scope="col">Detail</th></tr></thead>
              <tbody>{SDK.map(([f, s, d]) => (<tr key={f}><td>{f}</td><td><ModeChip mode={s} /></td><td>{d}</td></tr>))}</tbody>
            </table>
          </div>
        </GlowCard>
      </section>
    </>
  );
}
