export function Doors() {
  const doors = [
    { y: 70, name: "Token Factory", sub: "POST /v1/chat/completions" },
    { y: 140, name: "Tavily", sub: "POST /search, /extract" },
    { y: 210, name: "Radio Officer", sub: "drafts, questions, inbox" },
    { y: 280, name: "policy.local", sub: "advisor, built in" },
  ];
  return (
    <svg viewBox="0 0 720 360" role="img" aria-labelledby="doors-t" style={{ width: "100%", height: "auto" }}>
      <title id="doors-t">The sandbox has four allowed doors and the Seal stands at each one</title>
      <rect x="20" y="20" width="300" height="320" rx="22" fill="rgba(229,225,217,.9)" stroke="#1C1311" />
      <text x="40" y="52" fontSize="15" fontFamily="var(--font-general)" fill="#1C1311">Sandbox: dogwatch</text>
      <text x="40" y="76" fontSize="12" fill="#3B2B25">Bosun, Navigator,</text>
      <text x="40" y="92" fontSize="12" fill="#3B2B25">Officer of the Watch, Lookout</text>
      <rect x="40" y="120" width="120" height="44" rx="10" fill="rgba(255,246,224,.8)" stroke="#D9D4CA" />
      <text x="50" y="138" fontSize="11" fill="#1C1311">Vault</text>
      <text x="50" y="154" fontSize="11" fill="#3B2B25">read only mount</text>
      {doors.map((d, i) => (
        <g key={d.name}>
          <line x1="320" y1={d.y + 20} x2="470" y2={d.y + 20} stroke="#1C1311" strokeWidth="1" />
          <rect x="332" y={d.y + 6} width="40" height="28" rx="8" fill="#FFF6E0" stroke="#006B4A" />
          <text x="352" y={d.y + 24} fontSize="10" textAnchor="middle" fill="#006B4A">Seal</text>
          <rect x="470" y={d.y} width="230" height="40" rx="12" fill="rgba(255,246,224,.7)" stroke="#D9D4CA" />
          <text x="484" y={d.y + 18} fontSize="13" fill="#1C1311" fontFamily="var(--font-general)">{d.name}</text>
          <text x="484" y={d.y + 33} fontSize="11" fill="#3B2B25">{d.sub}</text>
          <circle cx="320" cy={d.y + 20} r="5" fill="#00C98B" />
          <title>{`${d.name}: allowed door ${i + 1}`}</title>
        </g>
      ))}
      <text x="40" y="320" fontSize="12" fill="#B3172A">Every other destination: denied</text>
    </svg>
  );
}
