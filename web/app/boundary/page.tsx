import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { Doors } from "../../components/Doors";
import { ModeChip } from "../../components/Chip";
import { R } from "../../lib/data";

export const metadata = { title: "The boundary | Dogwatch" };

const ATTACKS: Record<string, string> = {
  "01-webhook-host": "An arbitrary webhook host",
  "02-wildcard-host": "A wildcard host",
  "03-cloud-metadata": "The cloud metadata address",
  "04-telegram-direct": "Telegram reached directly from the sandbox",
  "05-vault-write": "Write access to the vault mount",
};

function firstLine(s: string, key: string) {
  const m = s.split("\n").find((l) => l.startsWith(key));
  return m ? m.replace(key, "").trim() : "";
}

export default function Boundary() {
  const names = Object.keys(R.prover).filter((k) => k.endsWith(".result.txt"));
  const declared = R.prover["dogwatch-declared.result.txt"];
  const runNote = R.prover["RUN.txt"];
  const p3 = (R.proof.p3_cases ?? []) as { id: string; transform: string; seal_denied: boolean; literal_denied: boolean; seal_path: string[] }[];
  const sample = p3.filter((c) => c.seal_denied).slice(0, 6);
  return (
    <>
      <PageHead
        eyebrow="The boundary"
        title="Four doors,"
        serif="enforced from outside."
        lede="The sandbox can reach four destinations. A gateway the agent cannot reach enforces that, an SMT prover checks the policy against a boundary, and the Seal refuses any request carrying a vault value."
        mode={{ label: "RECORDED", detail: "prover run on the build machine" }}
      />
      <section className="wrap stack" style={{ paddingBottom: 64 }}>
        <GlowCard><Doors /></GlowCard>

        <GlowCard tone="amber" className="stack">
          <div className="row"><h2 className="h-md display">Prover results</h2><ModeChip mode="LOCAL BUILD" /></div>
          <p className="src" style={{ margin: 0 }}>
            {runNote ? runNote.split("\n").filter((l) => l.startsWith("#")).join(" ") : "No prover run recorded yet."} The prover checks the declared policy; it does not model network middleware, so the Seal is tested separately. The sandbox effective export is NOT RUN yet because the gateway has not been started.
          </p>
          <div className="table-wrap" tabIndex={0} role="region" aria-label="Scrollable table">
            <table>
              <thead><tr><th scope="col">Candidate</th><th scope="col">Result</th><th scope="col">Counterexample or reason</th></tr></thead>
              <tbody>
                {declared && (
                  <tr><td>Declared Dogwatch policy</td><td className="mono">{firstLine(declared, "result:")}</td><td>Nothing beyond the boundary in the parts the prover models.</td></tr>
                )}
                {names.filter((n) => n[0] === "0").map((n) => {
                  const body = R.prover[n];
                  const key = n.replace(".result.txt", "");
                  return (
                    <tr key={n}>
                      <td>{ATTACKS[key] ?? key}</td>
                      <td className="mono">{firstLine(body, "result:")}</td>
                      <td className="mono" style={{ wordBreak: "break-word" }}>{firstLine(body, "counterexample:") || firstLine(body, "reason:") || (key === "03-cloud-metadata" ? "OpenShell never authorizes a link-local destination, so the rule adds no access." : "")}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="src" style={{ margin: 0 }}>Only within_boundary means a pass. An unsupported result is a refusal to bless the policy, not a pass.</p>
        </GlowCard>

        <div className="two-col" style={{ alignItems: "start" }}>
          <GlowCard className="stack">
            <div className="row"><h2 className="h-md display">Seal decisions</h2><ModeChip mode="LOCAL BUILD" /></div>
            <p className="src" style={{ margin: 0 }}>From the pre-registered encoding corpus (P3). No request value is shown, only the case id and the decoding path.</p>
            {sample.map((c) => (
              <pre tabIndex={0} key={c.id}>{`${c.id}  ${c.transform}\nseal: deny  path=${c.seal_path.join(">")}`}</pre>
            ))}
          </GlowCard>
          <GlowCard tone="port" className="stack">
            <div className="row"><h2 className="h-md display">Denials and advisor proposals</h2><ModeChip mode="NOT RUN" /></div>
            <p>
              The injected-inbox run with and without the sandbox (P2), the fail-closed test (P4), the credential placeholder test (P5) and the advisor flow where a denied request becomes a proposal Arjun rejects from Telegram need the OpenShell sandbox running. They are not run yet, so nothing is shown here for them.
            </p>
          </GlowCard>
        </div>

        <GlowCard className="stack">
          <h2 className="h-md display">Effective policy as written</h2>
          <pre tabIndex={0}>{R.policy}</pre>
        </GlowCard>
      </section>
    </>
  );
}
