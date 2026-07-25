import { describe, expect, it } from "vitest";

import { vizAnchorTier } from "./viz";

describe("vizAnchorTier", () => {
  it("places a visual after the Intuition tier by default", () => {
    expect(vizAnchorTier(undefined)).toBe("intuition");
    expect(vizAnchorTier({ anchorTier: "after-intuition" })).toBe("intuition");
  });

  it("places a visual inside The Math when the skill chose that", () => {
    expect(vizAnchorTier({ anchorTier: "in-the-math" })).toBe("the-math");
  });

  it("falls back to Intuition for an unknown placement", () => {
    // Hand-edited manifests must not make the visual vanish.
    expect(vizAnchorTier({ anchorTier: "in-the-footnotes" })).toBe("intuition");
  });
});
