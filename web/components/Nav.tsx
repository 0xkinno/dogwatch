"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const LINKS = [
  { href: "/how", label: "How it works", overflow: false },
  { href: "/boundary", label: "The boundary", overflow: false },
  { href: "/proof", label: "Proof", overflow: false },
  { href: "/judge", label: "For judges", overflow: true },
];

function DialGlyph() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.2" style={{ flex: "none" }}>
      <circle cx="12" cy="12" r="9.5" />
      <path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3" />
      <path d="M12 12l4.2-3.4" strokeWidth="1.6" />
      <path d="M6.2 16.6A9.5 9.5 0 0 1 4 12" stroke="#F2A93B" strokeWidth="2.4" />
    </svg>
  );
}

export function Nav() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const path = usePathname();
  const navRef = useRef<HTMLElement>(null);
  const sentinel = useRef<HTMLDivElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const sheetRef = useRef<HTMLDivElement>(null);

  // One observer on a sentinel at the top of the page flips the state once scrollY passes 8px.
  useEffect(() => {
    const el = sentinel.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setScrolled(!e.isIntersecting), { threshold: 0 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  // Expose the nav height so sections can leave room for it.
  useEffect(() => {
    const el = navRef.current;
    if (!el) return;
    const set = () => document.documentElement.style.setProperty("--nav-h", `${Math.ceil(el.getBoundingClientRect().bottom)}px`);
    set();
    const ro = new ResizeObserver(set);
    ro.observe(el);
    window.addEventListener("resize", set);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", set);
    };
  }, []);

  useEffect(() => setOpen(false), [path]);

  // Menu sheet: Escape closes, Tab stays inside the sheet and the button.
  useEffect(() => {
    if (!open) return;
    const items = () => [btnRef.current, ...(sheetRef.current?.querySelectorAll<HTMLElement>("a") ?? [])].filter(Boolean) as HTMLElement[];
    (sheetRef.current?.querySelector("a") as HTMLElement | null)?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOpen(false);
        btnRef.current?.focus();
      } else if (e.key === "Tab") {
        const list = items().filter((x) => x.offsetParent !== null);
        if (!list.length) return;
        const first = list[0];
        const last = list[list.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  const hero = path === "/" && !scrolled;
  const tone = scrolled ? "scrolled" : hero ? "hero" : "top";
  return (
    <header>
      <div ref={sentinel} aria-hidden="true" style={{ position: "absolute", top: 0, left: 0, width: 1, height: 8, pointerEvents: "none" }} />
      <nav ref={navRef} className={`nav${open ? " open" : ""}`} data-tone={tone} aria-label="Primary">
        <Link href="/" className="brand" onClick={() => setOpen(false)}>
          <DialGlyph />
          <span>Dogwatch</span>
        </Link>
        <ul id="primary-menu" className="nav-links">
          {LINKS.map((l) => (
            <li key={l.href} className={l.overflow ? "overflow" : undefined}>
              <Link href={l.href} aria-current={path === l.href ? "page" : undefined}>
                {l.label}
              </Link>
            </li>
          ))}
        </ul>
        <Link href="/watch" className="btn btn-ink cta" style={{ minHeight: 44, padding: "0 22px" }}>
          Open your watch
        </Link>
        <button ref={btnRef} className="menu-btn" aria-expanded={open} aria-controls="nav-sheet" onClick={() => setOpen(!open)}>
          {open ? "Close" : "Menu"}
        </button>
      </nav>
      <div id="nav-sheet" ref={sheetRef} className={`nav-sheet${open ? " open" : ""}`} hidden={!open}>
        <ul>
          {LINKS.map((l) => (
            <li key={l.href} className={l.overflow ? "overflow" : "small-only"}>
              <Link href={l.href} aria-current={path === l.href ? "page" : undefined}>{l.label}</Link>
            </li>
          ))}
          <li className="small-only">
            <Link href="/watch">Open your watch</Link>
          </li>
        </ul>
      </div>
    </header>
  );
}
