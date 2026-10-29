import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
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
const SHOTS = path.join(__dirname, "..", "test-results", "screens");

type Box = { x: number; y: number; w: number; h: number };

async function box(page: Page, selector: string): Promise<Box | null> {
  const el = page.locator(selector).first();
  if ((await el.count()) === 0) return null;
  const b = await el.boundingBox();
  return b ? { x: b.x, y: b.y + (await page.evaluate(() => window.scrollY)), w: b.width, h: b.height } : null;
}

const overlap = (a: Box, b: Box) => a.x < b.x + b.w - 1 && b.x < a.x + a.w - 1 && a.y < b.y + b.h - 1 && b.y < a.y + a.h - 1;

for (const vp of VIEWPORTS) {
  test.describe(`viewport ${vp.name}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } });
    for (const route of ROUTES) {
      test(`${route}`, async ({ page }) => {
        const errors: string[] = [];
        page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
        page.on("pageerror", (e) => errors.push(String(e)));
        await page.goto(route, { waitUntil: "networkidle" });
        await page.waitForTimeout(400);

        // no horizontal scroll
        const scrollW = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        expect(scrollW, "horizontal overflow in px").toBeLessThanOrEqual(1);

        if (route === "/") {
          // full-bleed hero: headline and calls to action are visible and inside the viewport width
          const h1 = await box(page, "#hero-title");
          const strip = await box(page, ".hero-strip");
          const actions = await box(page, ".hero-actions");
          expect(h1 && strip && actions).toBeTruthy();
          expect(h1!.x + h1!.w, "headline inside viewport").toBeLessThanOrEqual(vp.width + 1);
          expect(overlap(actions!, strip!), "buttons overlap the fact strip").toBe(false);
          expect(overlap(h1!, strip!), "headline overlaps the fact strip").toBe(false);
          await expect(page.locator(".hero-pill")).toBeVisible();
          // the specimen badge is not part of the hero image
          expect(await page.locator(".hero-full").getByText("SPECIMEN PROFILE").count()).toBe(0);
        }

        // mobile nav collapses below 768
        if (vp.width < 768) {
          await expect(page.locator(".nav .menu-btn")).toBeVisible();
          await expect(page.locator(".nav .cta")).toBeHidden();
        } else {
          await expect(page.locator(".nav .menu-btn")).toBeHidden();
        }

        const axe = await new AxeBuilder({ page }).analyze();
        const bad = axe.violations.filter((v) => v.impact === "serious" || v.impact === "critical");
        expect(bad.map((v) => `${v.id}: ${v.nodes.slice(0, 2).map((n) => n.target.join(" ")).join(" | ")}`), "axe serious or critical").toEqual([]);
        expect(errors, "console errors").toEqual([]);

        fs.mkdirSync(SHOTS, { recursive: true });
        await page.screenshot({ path: path.join(SHOTS, `${route === "/" ? "home" : route.slice(1)}-${vp.name}.png`), fullPage: false });
      });
    }
  });
}
