import type { DocVerdict } from "../lib/data";

const CX = 100;
const CY = 100;

function pt(r: number, deg: number) {
  const a = ((deg - 90) * Math.PI) / 180;
  return [CX + r * Math.cos(a), CY + r * Math.sin(a)] as const;
}

function arc(r1: number, r2: number, a1: number, a2: number) {
  const [x1, y1] = pt(r2, a1);
  const [x2, y2] = pt(r2, a2);
  const [x3, y3] = pt(r1, a2);
  const [x4, y4] = pt(r1, a1);
  const large = a2 - a1 > 180 ? 1 : 0;
  return `M${x1} ${y1} A${r2} ${r2} 0 ${large} 1 ${x2} ${y2} L${x3} ${y3} A${r1} ${r1} 0 ${large} 0 ${x4} ${y4}Z`;
}

const SECTORS: [number, number, string][] = [
  [0, 4, "Middle"],
  [4, 8, "Morning"],
  [8, 12, "Forenoon"],
  [12, 16, "Afternoon"],
  [16, 18, "First dog"],
  [18, 20, "Last dog"],
  [20, 24, "First"],
];

const COLORS: Record<string, { fill: string; glow: string }> = {
  VALID_THROUGH: { fill: "#00C98B", glow: "rgba(0,201,139,.55)" },
  LAPSES_DURING: { fill: "#F2384A", glow: "rgba(242,56,74,.6)" },
  EXPIRED_BEFORE_START: { fill: "#F2384A", glow: "rgba(242,56,74,.6)" },
  WINDOW_NOT_OPEN: { fill: "#F2A93B", glow: "rgba(242,169,59,.6)" },
  WINDOW_OPEN: { fill: "#F2A93B", glow: "rgba(242,169,59,.6)" },
};

function monthAngle(iso: string) {
  const [, m, d] = iso.split("-").map(Number);
  return (((m - 1) + (d - 1) / 30) / 12) * 360;
}

/** The watch dial: 24 hour watch sectors inside a twelve month ring. Each document is a capsule at its expiry month. */
export function WatchDial({ documents, label = "Watch dial", id = "dial" }: { documents: Pick<DocVerdict, "label" | "state" | "expiry">[]; label?: string; id?: string }) {
  const docs = documents.filter((d) => d.expiry);
  return (
    <figure className="dial" style={{ margin: 0 }}>
      <svg viewBox="0 0 200 200" role="img" aria-labelledby={`${id}-t`} style={{ width: "100%", height: "auto", display: "block" }}>
        <title id={`${id}-t`}>{label}</title>
        <defs>
          <linearGradient id={`${id}-dog`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#F2A93B" stopOpacity=".55" />
            <stop offset="1" stopColor="#FFF6E0" stopOpacity=".7" />
          </linearGradient>
        </defs>
        <circle cx={CX} cy={CY} r="96" fill="rgba(238,235,229,.86)" stroke="#1C1311" strokeWidth=".6" />
        {SECTORS.map(([a, b], i) => {
          const dog = a === 16 || a === 18;
          return <path key={i} d={arc(48, 74, (a / 24) * 360 + 0.4, (b / 24) * 360 - 0.4)} fill={dog ? `url(#${id}-dog)` : "rgba(229,225,217,.9)"} stroke="#1C1311" strokeWidth=".5" />;
        })}
        {[16, 18].map((h, i) => {
          const [x, y] = pt(61, ((h + 1) / 24) * 360);
          return (
            <text key={h} x={x} y={y} fontSize="4.4" textAnchor="middle" dominantBaseline="middle" fill="#3B2B25" style={{ fontVariantCaps: "all-small-caps", letterSpacing: ".06em" }} transform={`rotate(${((h + 1) / 24) * 360 + (i === 0 ? 0 : 0)} ${x} ${y})`}>
              {i === 0 ? "first dog" : "last dog"}
            </text>
          );
        })}
        {[0, 4, 8, 12, 16, 18, 20].map((h) => {
          const [x1, y1] = pt(46, (h / 24) * 360);
          const [x2, y2] = pt(76, (h / 24) * 360);
          return <line key={h} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#1C1311" strokeWidth=".4" />;
        })}
        <circle cx={CX} cy={CY} r="86" fill="none" stroke="#D9D4CA" strokeWidth="9" />
        {Array.from({ length: 12 }).map((_, m) => {
          const [x1, y1] = pt(81, (m / 12) * 360);
          const [x2, y2] = pt(91, (m / 12) * 360);
          return <line key={m} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#1C1311" strokeWidth=".7" />;
        })}
        {docs.map((d, i) => {
          const a = monthAngle(d.expiry as string);
          const [x, y] = pt(86, a);
          const c = COLORS[d.state] ?? { fill: "#74675F", glow: "rgba(116,103,95,.4)" };
          return (
            <g key={i} transform={`rotate(${a} ${x} ${y})`}>
              <rect x={x - 6} y={y - 2.8} width="12" height="5.6" rx="2.2" fill={c.fill} style={{ filter: `drop-shadow(0 0 2.5px ${c.glow})` }} />
              <title>{`${d.label}: ${d.state.replaceAll("_", " ").toLowerCase()}, expires ${d.expiry}`}</title>
            </g>
          );
        })}
        <g className="dial-hand" style={{ transformBox: "view-box" }}>
          <line x1={CX} y1={CY} x2={CX} y2="30" stroke="#1C1311" strokeWidth="1.1" strokeLinecap="round" />
          <circle cx={CX} cy={CY} r="2.4" fill="#1C1311" />
        </g>
      </svg>
      <figcaption className="sr-only">
        {docs.map((d) => `${d.label}: ${d.state.replaceAll("_", " ").toLowerCase()}, expires ${d.expiry}`).join(". ")}
      </figcaption>
    </figure>
  );
}
