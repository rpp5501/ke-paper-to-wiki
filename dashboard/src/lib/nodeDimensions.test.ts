import { describe, expect, it } from "vitest";

import { nodeCardSize } from "./nodeDimensions";

describe("nodeCardSize", () => {
  it("keeps short labels compact", () => {
    expect(nodeCardSize("Attention")).toEqual({ width: 220, height: 72 });
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
