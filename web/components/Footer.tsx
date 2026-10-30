import Link from "next/link";

export function Footer() {
  return (
    <footer className="footer">
      <div className="wrap" style={{ display: "grid", gap: 14 }}>
        <p style={{ margin: 0 }}>
          Built with NVIDIA Nemotron (served from the NVIDIA API Catalog; Nebius Token Factory is the target route and has not been run), NVIDIA OpenShell, and Tavily.
        </p>
        <p className="muted" style={{ margin: 0, fontSize: 14 }}>
          Apache-2.0 licence. The profile shown is a specimen and every page says when it is showing a recorded run.
        </p>
        <div className="row" style={{ gap: 18 }}>
          <Link href="/judge">For judges</Link>
          <Link href="/proof">Proof</Link>
          <Link href="/how">How it works</Link>
          <a href="https://github.com/0xkinno/dogwatch/blob/main/DISCLOSURES.md">Disclosures</a>
          <a href="https://github.com/0xkinno/dogwatch">Source</a>
        </div>
      </div>
    </footer>
  );
}
