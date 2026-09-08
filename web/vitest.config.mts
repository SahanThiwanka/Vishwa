import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      "@": new URL("./src", import.meta.url).pathname,
      // `server-only` resolves to its browser build under Vitest and throws on
      // import. The guard it provides is a build-time concern for the Next.js
      // bundler; in a Node test process there is no client bundle to protect,
      // so it is stubbed out rather than the modules being restructured to
      // accommodate the test runner.
      "server-only": new URL("./src/test/server-only-stub.ts", import.meta.url).pathname,
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
