import { describe, expect, it } from "vitest";

import { nodeAccessibleName } from "./nodePresentation";

describe("nodeAccessibleName", () => {
  it("expands every visible badge into meaningful accessible copy", () => {
    expect(nodeAccessibleName({
      label: "Attention",
      level: 2,
      bridge: true,
      hotspotRank: 3,
    })).toBe("Attention, level 2, bridge, hotspot rank 3");
  });

  it("uses the node label alone when no badges are visible", () => {
    expect(nodeAccessibleName({ label: "Attention" })).toBe("Attention");
  });
});
