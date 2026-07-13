import { describe, expect, it } from "vitest";
import { visibleAtZoom } from "./lod";

const clusters = [{ id: "c1", label: "C1", nodeIds: ["a", "b"] }];

describe("visibleAtZoom", () => {
  it("zoomed out shows clusters, hides members", () => {
    const v = visibleAtZoom(0.3, 0.5, clusters, ["a", "b", "solo"]);
    expect(v.showClusters).toBe(true);
    expect(v.hiddenNodes.has("a")).toBe(true);
    expect(v.hiddenNodes.has("solo")).toBe(false);
  });

  it("zoomed in shows members", () => {
    const v = visibleAtZoom(0.8, 0.5, clusters, ["a", "b"]);
    expect(v.showClusters).toBe(false);
    expect(v.hiddenNodes.size).toBe(0);
  });
});
