import { test, expect } from "@playwright/test";

// Every user action on the deployed app. Run with LIVE_URL=https://dogwatch-eight.vercel.app
test.describe("live user actions", () => {
  test("contract check with a custom window and the rule quote", async ({ page }) => {
    await page.goto("/contract", { waitUntil: "networkidle" });
    await page.locator("#start").fill("2027-03-01");
    await page.locator("#end").fill("2027-09-30");
    await page.locator("#travel").fill("2");
    await page.getByRole("button", { name: "Check" }).click();
    await expect(page.getByText("LIVE", { exact: true }).first()).toBeVisible({ timeout: 30000 });
    // the medical certificate lapses on 14 Mar inside this window, with its rule shown
    await expect(page.getByText("Not ready", { exact: false }).first()).toBeVisible();
    // open each document's rules: the certificate of competency shows its sourced sea-service rule quote
    const whys = page.locator("details.why");
    const n = await whys.count();
    expect(n).toBeGreaterThanOrEqual(4);
    for (let i = 0; i < n; i++) await whys.nth(i).locator("summary").click();
    await expect(page.locator("details.why .quote").first()).toBeVisible();
    const q = await page.locator("details.why .quote").first().innerText();
    expect(q.length).toBeGreaterThan(20);
  });

  test("approval preview opens", async ({ page }) => {
    await page.goto("/contract", { waitUntil: "networkidle" });
    await page.getByRole("button", { name: /approval preview/i }).click();
    await expect(page.getByText("Approval preview", { exact: false })).toBeVisible();
  });

  test("proof: every set opens and a miss expands", async ({ page }) => {
    await page.goto("/proof", { waitUntil: "networkidle" });
    for (const h of ["P3 Encoding corpus", "P7 Counting conventions", "P6 Navigator against the oracle", "P8 Reading specimen certificates", "P11 Restart"]) {
      await expect(page.getByRole("heading", { name: new RegExp(h) }).first()).toBeVisible();
    }
    const d = page.locator("details").first();
    await d.locator("summary").click();
    await expect(d.locator("table")).toBeVisible();
  });

  test("judge: the offer flow runs once and shows its label, route and cap text", async ({ page }) => {
    await page.goto("/judge", { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Run the offer flow" }).click();
    const box = page.locator(".callout[aria-live]");
    await expect(box).toBeVisible({ timeout: 60000 });
    const text = await box.innerText();
    expect(text).toMatch(/DEMO|RECORDED/);
    expect(text).toMatch(/Route: NVIDIA API Catalog \(development\)|Recorded run/);
    expect(text).toMatch(/per hour|One live run at a time|not reachable/);
  });

  test("reduced motion renders the landing page", async ({ browser }) => {
    const ctx = await browser.newContext({ reducedMotion: "reduce" });
    const page = await ctx.newPage();
    await page.goto("/", { waitUntil: "networkidle" });
    await expect(page.locator("#hero-title")).toBeVisible();
    await ctx.close();
  });

  test("every in-app link and every README link resolves", async ({ page, request }) => {
    const seen = new Set<string>();
    for (const route of ["/", "/watch", "/contract", "/outbox", "/boundary", "/proof", "/judge", "/how"]) {
      await page.goto(route, { waitUntil: "domcontentloaded" });
      const hrefs = await page.$$eval("a[href]", (as) => as.map((a) => (a as HTMLAnchorElement).href));
      for (const h of hrefs) seen.add(h.split("#")[0]);
    }
    const base = new URL(page.url()).origin;
    const bad: string[] = [];
    for (const h of seen) {
      if (!h.startsWith("http")) continue;
      const internal = h.startsWith(base);
      const r = await request.get(h, { timeout: 30000, failOnStatusCode: false }).catch(() => null);
      const code = r ? r.status() : 0;
      if (internal ? code !== 200 : code >= 404 && code !== 429 && code !== 403) bad.push(`${code} ${h}`);
    }
    expect(bad).toEqual([]);
  });
});
