"use client";
import Image from "next/image";
import Link from "next/link";
import { motion, useReducedMotion, useScroll, useTransform } from "motion/react";
import { useRef } from "react";

type Strip = { k: string; v: React.ReactNode; href: string };

const ease = [0.22, 1, 0.36, 1] as const;

export function Hero({ strip }: { strip: Strip[] }) {
  const ref = useRef<HTMLElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], ["0%", reduce ? "0%" : "14%"]);
  const lines = ["Your papers", "keep watch"];

  return (
    <section ref={ref} className="hero-full" aria-labelledby="hero-title">
      <motion.div className="hero-bg" style={{ y }} initial={reduce ? false : { scale: 1.12 }} animate={{ scale: 1 }} transition={{ duration: 2.4, ease }}>
        <Image
          src="/img/hero.webp"
          alt="A merchant navy officer in a dark working jacket stands at the rail of a tanker at sunset, reading a phone, with the radar mast and satellite dome behind him."
          fill
          priority
          sizes="100vw"
        />
      </motion.div>
      <div className="hero-shade" aria-hidden="true" />
      <div className="wrap hero-content">
        <div className="hero-copy">
          <motion.span className="hero-pill" initial={reduce ? false : { opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.15, ease }}>
            <i aria-hidden="true" /> Personal AI for seafarers
          </motion.span>
          <h1 id="hero-title" className="hero-h1">
            {lines.map((l, i) => (
              <span className="line" key={l}>
                <motion.span style={{ display: "block" }} initial={reduce ? false : { y: "105%" }} animate={{ y: 0 }} transition={{ duration: 0.95, delay: 0.25 + i * 0.12, ease }}>
                  {l}
                </motion.span>
              </span>
            ))}
            <span className="line">
              <motion.span className="serif" style={{ display: "block" }} initial={reduce ? false : { y: "105%" }} animate={{ y: 0 }} transition={{ duration: 0.95, delay: 0.5, ease }}>
                while you do.
              </motion.span>
            </span>
          </h1>
          <motion.p className="hero-lede" initial={reduce ? false : { opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.75, ease }}>
            Dogwatch reads a seafarer&apos;s certificates on his own machine, computes every expiry in code, and has the renewal ready before a lapse costs him a contract.
          </motion.p>
          <motion.div className="hero-actions" initial={reduce ? false : { opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.9, ease }}>
            <a className="btn btn-paper" href="#check">See Arjun&apos;s check</a>
            <Link className="btn btn-ghost" href="/boundary">How the boundary works</Link>
          </motion.div>
        </div>
        <motion.div className="hero-strip" initial={reduce ? false : { opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9, delay: 1.05, ease }}>
          {strip.map((s) => (
            <Link key={s.k} href={s.href} className="strip-card">
              <div className="k">{s.k}</div>
              <div className="v">{s.v}</div>
            </Link>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
