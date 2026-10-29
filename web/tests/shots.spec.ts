import { test } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

// README screenshots: every one is a 1440x900 desktop landscape viewport capture, so they are all the same size.
const OUT = path.join(__dirname, "..", "..", "docs", "img");
const SHOTS: { file: string; route: string; anchor?: string; offset?: number }[] = [
  { file: "banner.png", route: "/" },
  { file: "check.png", route: "/", anchor: "#check" },
  { file: "watch.png", route: "/watch", anchor: "[data-shot=watch]", offset: 470 },
  { file: "contract.png", route: "/contract", anchor: "[data-shot=contract]", offset: 470 },
  { file: "boundary.png", route: "/boundary", anchor: "[data-shot=boundary]", offset: 470 },
  { file: "proof.png", route: "/proof", anchor: "[data-shot=proof]", offset: 470 },
  { file: "outbox.png", route: "/outbox", anchor: "[data-shot=outbox]", offset: 470 },
];

test.use({ viewport: { width: 1440, height: 900 }, reducedMotion: "no-preference" });

for (const s of SHOTS) {
  test(`screenshot ${s.file}`, async ({ page }) => {
    await page.goto(s.route, { waitUntil: "networkidle" });
    if (s.anchor) {
      await page.evaluate(([sel, off]) => {
        const el = document.querySelector(sel as string) as HTMLElement | null;
        if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - (off as number));
      }, [s.anchor, s.offset ?? 110]);
    }
    await page.waitForTimeout(s.anchor ? 1600 : 3200);
    fs.mkdirSync(OUT, { recursive: true });
    await page.screenshot({ path: path.join(OUT, s.file), fullPage: false });
  });
}
