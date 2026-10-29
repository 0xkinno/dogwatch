"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const LINKS = [
  { href: "/how", label: "How it works" },
  { href: "/boundary", label: "The boundary" },
  { href: "/proof", label: "Proof" },
  { href: "/judge", label: "For judges" },
];

function DialGlyph() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.2">
      <circle cx="12" cy="12" r="9.5" />
      <path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3" />
      <path d="M12 12l4.2-3.4" strokeWidth="1.6" />
      <path d="M6.2 16.6A9.5 9.5 0 0 1 4 12" stroke="#F2A93B" strokeWidth="2.2" />
    </svg>
  );
}

export function Nav() {
  const [open, setOpen] = useState(false);
  const path = usePathname();
  return (
    <header>
      <nav className={`nav${open ? " open" : ""}`} aria-label="Primary">
        <Link href="/" className="brand" onClick={() => setOpen(false)}>
          <DialGlyph />
          Dogwatch
        </Link>
        <ul id="primary-menu">
          {LINKS.map((l) => (
            <li key={l.href}>
              <Link href={l.href} aria-current={path === l.href ? "page" : undefined} onClick={() => setOpen(false)}>
                {l.label}
              </Link>
            </li>
          ))}
        </ul>
        <Link href="/watch" className="btn btn-ink cta" onClick={() => setOpen(false)}>
          Open your watch
        </Link>
        <button className="btn btn-paper menu-btn" aria-expanded={open} aria-controls="primary-menu" onClick={() => setOpen(!open)}>
          {open ? "Close" : "Menu"}
        </button>
      </nav>
    </header>
  );
}
