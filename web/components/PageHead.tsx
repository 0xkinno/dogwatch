import { ModeChip } from "./Chip";

export function PageHead({ eyebrow, title, serif, lede, mode }: { eyebrow: string; title: string; serif?: string; lede?: string; mode?: { label: string; detail?: string } }) {
  return (
    <div className="page-head">
      <div className="wrap">
        <div className="row">
          <span className="eyebrow">{eyebrow}</span>
          {mode ? <ModeChip mode={mode.label} detail={mode.detail} /> : null}
        </div>
        <h1 className="display h-lg" style={{ margin: "18px 0 12px", maxWidth: "16em" }}>
          {title} {serif ? <span className="serif">{serif}</span> : null}
        </h1>
        {lede ? <p className="lede">{lede}</p> : null}
      </div>
    </div>
  );
}
