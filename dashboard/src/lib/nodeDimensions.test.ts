import { describe, expect, it } from "vitest";

import { nodeCardSize } from "./nodeDimensions";

describe("nodeCardSize", () => {
  it("keeps short labels compact", () => {
    expect(nodeCardSize("Attention")).toEqual({ width: 220, height: 72 });
  });

  it("grows both dimensions with the mind-map fan-out scale", () => {
    expect(nodeCardSize("Attention", 1.25)).toEqual({ width: 275, height: 90 });
  });

  it("is byte-identical at scale 1, so layered mode is untouched", () => {
    expect(nodeCardSize("Attention", 1)).toEqual(nodeCardSize("Attention"));
  });

  it("allocates more height for a complete long concept label", () => {
    expect(nodeCardSize(
      "Disparity turns a weak attribute inference attack into a targeted threat",
    ).height).toBeGreaterThan(72);
  });

  it("accounts for unbroken identifiers without truncation", () => {
    expect(nodeCardSize("universal-post-training-backdoor-detection").height)
      .toBeGreaterThanOrEqual(90);
  });
});
