import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const ROUTES = ["/", "/watch", "/contract", "/outbox", "/boundary", "/proof", "/judge", "/how"];
const VIEWPORTS = [
  { name: "360x780", width: 360, height: 780 },
  { name: "390x844", width: 390, height: 844 },
  { name: "430x932", width: 430, height: 932 },
  { name: "768x1024", width: 768, height: 1024 },
  { name: "1024x768", width: 1024, height: 768 },
  { name: "1366x768", width: 1366, height: 768 },
  { name: "1440x900", width: 1440, height: 900 },
  { name: "1920x1080", width: 1920, height: 1080 },
];
const SHOTS = path.join(__dirname, "..", "test-results", "screens", "nav");

for (const vp of VIEWPORTS) {
  test.describe(`nav ${vp.name}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } });
    for (const route of ROUTES) {
      test(route, async ({ page }) => {
        await page.goto(route, { waitUntil: "networkidle" });
        const total = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
        for (const frac of [0, 0.25, 0.5, 0.75, 1]) {
          await page.evaluate((y) => window.scrollTo(0, y), Math.round(total * frac));
          await page.waitForTimeout(450);
          const r = await page.evaluate(() => {
            const nav = document.querySelector("nav.nav") as HTMLElement;
            const nb = nav.getBoundingClientRect();
            const visible = (el: Element) => (el as HTMLElement).offsetParent !== null || getComputedStyle(el).position === "fixed";
            const targets = [...nav.querySelectorAll("a, button")].filter(visible) as HTMLElement[];
            const misses: string[] = [];
            const heights: number[] = [];
            for (const el of targets) {
              const b = el.getBoundingClientRect();
              if (b.width === 0) continue;
              const hit = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
              if (!hit || !nav.contains(hit)) misses.push(`${el.textContent?.trim()} hit ${hit?.tagName}.${(hit as HTMLElement | null)?.className?.toString().slice(0, 30)}`);
              if (el.tagName === "A" && el.closest(".nav-links")) heights.push(b.height);
            }
            const bg = getComputedStyle(nav).backgroundColor;
            const m = bg.match(/rgba?\(([^)]+)\)/);
            const parts = m ? m[1].split(",").map((x) => parseFloat(x)) : [0, 0, 0, 0];
            const alpha = parts.length === 4 ? parts[3] : 1;
            const overlaps: string[] = [];
            document.querySelectorAll("h1, h2, p").forEach((el) => {
              const b = el.getBoundingClientRect();
              if (b.width === 0 || b.height === 0) return;
              const inside = b.top >= 0 && b.bottom <= window.innerHeight && b.left >= 0 && b.right <= window.innerWidth;
              if (!inside || nav.contains(el)) return;
              const hit = !(b.right <= nb.left || b.left >= nb.right || b.bottom <= nb.top || b.top >= nb.bottom);
              if (hit) overlaps.push(`${el.tagName} ${(el.textContent || "").slice(0, 30)}`);
            });
            return { misses, alpha, scrollY: window.scrollY, overlaps, maxLinkH: Math.max(0, ...heights), navH: nb.height };
          });
          const where = `${route} ${vp.name} at ${Math.round(frac * 100)}%`;
          expect(r.misses, `nav targets covered: ${where}`).toEqual([]);
          if (r.scrollY > 8) expect(r.alpha, `nav background alpha: ${where}`).toBeGreaterThanOrEqual(0.9);
          if (r.alpha < 0.9) expect(r.overlaps, `text under a transparent nav: ${where}`).toEqual([]);
          expect(r.maxLinkH, `link wraps: ${where}`).toBeLessThanOrEqual(48);
          if (frac === 0.5 && (vp.width === 390 || vp.width === 1440)) {
            fs.mkdirSync(SHOTS, { recursive: true });
            await page.screenshot({ path: path.join(SHOTS, `${route === "/" ? "home" : route.slice(1)}-${vp.name}.png`) });
          }
        }
      });
    }
  });
}

test("menu sheet: opens, traps focus, Escape closes", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/", { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Menu" }).click();
  await expect(page.locator("#nav-sheet")).toBeVisible();
  for (let i = 0; i < 8; i++) {
    await page.keyboard.press("Tab");
    const inside = await page.evaluate(() => !!document.activeElement?.closest("#nav-sheet, nav.nav"));
    expect(inside).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(page.locator("#nav-sheet")).toBeHidden();
});

test("reduced motion: background still switches, with no transition", async ({ browser }) => {
  const ctx = await browser.newContext({ reducedMotion: "reduce", viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto("/", { waitUntil: "networkidle" });
  await page.evaluate(() => window.scrollTo(0, 600));
  await page.waitForTimeout(500);
  const s = await page.evaluate(() => {
    const n = document.querySelector("nav.nav") as HTMLElement;
    return { bg: getComputedStyle(n).backgroundColor, dur: getComputedStyle(n).transitionDuration };
  });
  expect(s.dur.split(",").every((d) => parseFloat(d) === 0)).toBe(true);
  expect(s.bg).toContain("238, 235, 229");
  await ctx.close();
});
