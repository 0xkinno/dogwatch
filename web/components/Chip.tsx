const MAP: Record<string, { label: string; cls: string; icon: "check" | "cross" | "clock" | "question" }> = {
  VALID_THROUGH: { label: "VALID THROUGH", cls: "chip-valid", icon: "check" },
  LAPSES_DURING: { label: "LAPSES", cls: "chip-lapse", icon: "cross" },
  EXPIRED_BEFORE_START: { label: "EXPIRED", cls: "chip-lapse", icon: "cross" },
  WINDOW_NOT_OPEN: { label: "WINDOW OPENS", cls: "chip-window", icon: "clock" },
  WINDOW_OPEN: { label: "WINDOW OPEN", cls: "chip-window", icon: "clock" },
  UNREAD: { label: "UNREAD", cls: "chip-unknown", icon: "question" },
  MISSING: { label: "MISSING", cls: "chip-unknown", icon: "question" },
  ASK_ADMINISTRATION: { label: "ASK ADMINISTRATION", cls: "chip-unknown", icon: "question" },
  READY: { label: "READY", cls: "chip-valid", icon: "check" },
  NOT_READY: { label: "NOT READY", cls: "chip-lapse", icon: "cross" },
  CANNOT_VERIFY: { label: "CANNOT VERIFY", cls: "chip-unknown", icon: "question" },
};

function Icon({ k }: { k: "check" | "cross" | "clock" | "question" }) {
  const p = { fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  return (
    <svg viewBox="0 0 12 12" aria-hidden="true">
      {k === "check" && <path d="M2 6.5l2.5 2.5L10 3.5" {...p} />}
      {k === "cross" && <path d="M3 3l6 6M9 3l-6 6" {...p} />}
      {k === "clock" && (
        <g {...p}>
          <circle cx="6" cy="6" r="4.2" />
          <path d="M6 3.6V6l1.6 1" />
        </g>
      )}
      {k === "question" && <path d="M4.2 4.4a1.9 1.9 0 1 1 2.7 1.7c-.6.3-.9.7-.9 1.3M6 9.4v.1" {...p} />}
    </svg>
  );
}

export function Chip({ state }: { state: string }) {
  const m = MAP[state] ?? { label: state.replaceAll("_", " "), cls: "chip-unknown", icon: "question" as const };
  return (
    <span className={`chip ${m.cls}`}>
      <Icon k={m.icon} />
      {m.label}
    </span>
  );
}

export function ModeChip({ mode, detail }: { mode: string; detail?: string }) {
  return (
    <span className="chip chip-mode" title={detail}>
      {mode}
      {detail ? <span style={{ opacity: 0.7 }}>{detail}</span> : null}
    </span>
  );
}
