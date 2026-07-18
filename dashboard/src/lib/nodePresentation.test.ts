import { describe, expect, it } from "vitest";

import { levelBadgeLabel, nodeAccessibleName } from "./nodePresentation";

describe("levelBadgeLabel", () => {
  it.each([
    [undefined, null],
    [0, "core idea"],
    [1, "core idea"],
    [2, "mechanism"],
    [3, "deep dive"],
    [5, "deep dive"],
  ])("level %s → %s", (level, expected) => {
    expect(levelBadgeLabel(level as number | undefined)).toBe(expected);
  });
});

describe("nodeAccessibleName", () => {
  it("expands every visible badge into meaningful accessible copy", () => {
    expect(nodeAccessibleName({
      label: "Attention",
      level: 2,
      bridge: true,
      hotspotRank: 3,
    })).toBe("Attention, mechanism, bridge, hotspot rank 3");
  });

  it("uses the node label alone when no badges are visible", () => {
    expect(nodeAccessibleName({ label: "Attention" })).toBe("Attention");
  });
});
