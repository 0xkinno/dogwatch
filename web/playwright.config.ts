import { defineConfig } from "@playwright/test";

const port = Number(process.env.PORT ?? 3100);

export default defineConfig({
  testDir: "./tests",
  timeout: 90_000,
  fullyParallel: false,
  workers: 1,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${port}`, browserName: "chromium", reducedMotion: "reduce" },
  webServer: {
    command: `npx next start -p ${port}`,
    url: `http://localhost:${port}`,
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
