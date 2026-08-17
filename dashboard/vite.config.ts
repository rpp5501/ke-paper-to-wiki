import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Serve any built paper without touching the checkout:
//
//   KE_PAPER=lottery-ticket npm run dev -- --port 5174
//
// Every component imports KE_DATA from a RELATIVE "./data.gen", at three
// different depths, and dashboard/src/data.gen.ts is git-tracked -- it is the
// bundle the vitest content assertions read. Swapping papers by copying over
// it means a dirty tree and a broken suite until someone remembers to restore
// it, which has already happened twice. The regex matches the specifier at any
// depth and redirects it instead, so the working copy is never written to.
//
// Unset KE_PAPER is the old behaviour exactly, so tests and `npm run build`
// are unaffected.
const paper = process.env.KE_PAPER;
const built = paper && path.resolve(__dirname, "..", "dashboards", paper);

export default defineConfig({
  base: "./",
  plugins: [react()],
  build: { chunkSizeWarningLimit: 1500 },
  // Figures live beside the bundle that cites them; serving the default
  // public/ with another paper's bundle shows a wall of broken images.
  ...(built ? { publicDir: path.join(built, "public") } : {}),
  resolve: {
    alias: built
      ? [{ find: /^(?:\.\.?\/)+data\.gen$/,
           replacement: path.join(built, "src", "data.gen.ts") }]
      : [],
  },
});
