import Link from "next/link";
import { PageHead } from "../../components/PageHead";
import { GlowCard } from "../../components/GlowCard";
import { DemoOffer } from "../../components/DemoOffer";
import { ContractRunner } from "../../components/ContractRunner";

export const metadata = { title: "For judges | Dogwatch" };

export default function Judge() {
  return (
    <>
      <PageHead
        eyebrow="For judges"
        title="Value in"
        serif="sixty seconds."
        lede="No login, no key. The page opens on Arjun's specimen profile. Every result says whether it is live, a demo of the same code path, or a recorded run."
      />
      <section className="wrap stack" style={{ paddingBottom: 64 }}>
        <div className="grid-3">
          <GlowCard className="stack">
            <h2 className="h-md display">60 seconds</h2>
            <ol style={{ paddingLeft: 18, margin: 0 }}>
              <li>Press Check below. The medical lapses on day 42 of 181 with its source quote.</li>
              <li>Run the offer flow. It uses triage, the Navigator and the plan writer; when the large model is busy the plan text is a labelled template.</li>
              <li>Open the proof page and read the misses.</li>
            </ol>
            <Link className="btn btn-ink" href="/proof">Open the proof</Link>
          </GlowCard>
          <GlowCard tone="amber" className="stack">
            <h2 className="h-md display">3 minutes</h2>
            <ol style={{ paddingLeft: 18, margin: 0 }}>
              <li>Read the boundary page: the four doors and the prover results. The sandbox cannot start on the build machine; its proofs ran on a GitHub Actions runner: 20 of 20 injected posts denied (P2), fails closed with the Seal stopped (P4), the agent sees only a placeholder (P5). The effective-policy re-proof (P1) was unsupported by the prover.</li>
              <li>Open the outbox: a draft with placeholders and its digest.</li>
              <li>Read how the model is routed and where no model is allowed.</li>
            </ol>
            <Link className="btn btn-paper" href="/boundary">Open the boundary</Link>
          </GlowCard>
          <GlowCard tone="green" className="stack">
            <h2 className="h-md display">10 minutes</h2>
            <ol style={{ paddingLeft: 18, margin: 0 }}>
              <li>Clone the repository and run the tests offline with the commands below.</li>
              <li>Open `PLATFORM_PROBE.md` and `SDK_SURFACE.md` for what is live and what is not.</li>
              <li>Reproduce a number from `docs/FACTS.json` with the run scripts.</li>
            </ol>
            <Link className="btn btn-paper" href="/how">Architecture and crew</Link>
          </GlowCard>
        </div>

        <GlowCard className="stack">
          <h2 className="h-md display">Open the contract check and press Check</h2>
          <ContractRunner />
        </GlowCard>

        <GlowCard tone="amber" className="stack">
          <h2 className="h-md display">Try an offer</h2>
          <DemoOffer />
        </GlowCard>

        <GlowCard className="stack">
          <h2 className="h-md display">Offline, no keys</h2>
          <p className="src" style={{ margin: 0 }}>Everything below runs without any key, in recorded mode.</p>
          <pre tabIndex={0}>{`git clone https://github.com/0xkinno/dogwatch && cd dogwatch
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
(cd core && python -m pytest -q)
(cd seal && python -m pytest -q)
python eval/run_seal_corpus.py   # P3
python eval/run_conventions.py   # P7
python scripts/check_facts.py`}</pre>
        </GlowCard>
      </section>
    </>
  );
}
