import { describe, expect, it } from "vitest";

import canvasSource from "./Canvas.tsx?raw";

// React Flow re-adopts the node objects on every `nodes` prop change, and it
// only carries a node's measured handle bounds across an adoption when the
// object it is handed has `measured` — top-level width/height does not count
// (see parseHandles in @xyflow/system). Canvas rebuilds these objects on every
// render and never round-trips them through onNodesChange, so a node card that
// declares its size without also declaring `measured` loses its handle bounds
// on the first re-render, and every edge touching it silently stops rendering.
describe("Canvas node dimensions", () => {
  it("declares `measured` on every node card it sizes", () => {
    const sized = canvasSource.match(/^\s*\.\.\.size,$/gm) ?? [];
    const measured = canvasSource.match(/^\s*measured: size,$/gm) ?? [];

    expect(sized.length).toBeGreaterThan(0);
    expect(measured.length).toBe(sized.length);
  });
});
