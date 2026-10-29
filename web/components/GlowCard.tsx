"use client";
import { useRef } from "react";

export function GlowCard({
  tone = "green",
  children,
  className = "",
  as: Tag = "div",
}: {
  tone?: "green" | "amber" | "port";
  children: React.ReactNode;
  className?: string;
  as?: "div" | "article" | "section" | "li";
}) {
  const ref = useRef<HTMLElement | null>(null);
  const cls = `glow-card glow-${tone} ${className}`.trim();
  const onMove = (e: React.PointerEvent) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    el.style.setProperty("--x", `${e.clientX - r.left}px`);
    el.style.setProperty("--y", `${e.clientY - r.top}px`);
  };
  const Any = Tag as React.ElementType;
  return (
    <Any ref={ref} onPointerMove={onMove} className={cls}>
      {children}
    </Any>
  );
}
