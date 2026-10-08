import type { NextConfig } from "next";
import { loadEnvConfig } from "@next/env";

// One .env at the repo root, shared with the pipeline. forceReload: Next has already
// loaded (and cached) env for web/ by the time this runs.
loadEnvConfig("..", undefined, undefined, true);

const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
