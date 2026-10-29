import { chromium } from "@playwright/test";

const b = await chromium.launch();
for (const w of [1024, 1440]) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  await p.goto("http://localhost:3100/", { waitUntil: "networkidle" });
  const r = await p.evaluate(() => {
    const q = (s) => {
      const e = document.querySelector(s);
      const r = e.getBoundingClientRect();
      return [Math.round(r.left), Math.round(r.top + scrollY), Math.round(r.right), Math.round(r.bottom + scrollY)];
    };
    return { h1: q("#hero-title"), lede: q(".hero-copy .lede"), actions: q(".hero-actions"), dial: q(".hero-dial"), media: q(".hero-media"), grid: q(".hero-grid") };
  });
  console.log(w, JSON.stringify(r));
}
await b.close();
