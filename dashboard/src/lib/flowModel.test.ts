import { describe, expect, it } from "vitest";

import { makeFlowEdges } from "./flowModel";

describe("makeFlowEdges", () => {
  it("keeps every rendered edge outside React Flow selection state", () => {
    const edges = makeFlowEdges(
      [
        { src: "a", dst: "b", kind: "implements" },
        { src: "b", dst: "c", kind: "prerequisite" },
      ],
      new Set(),
      new Set(["a", "b", "c"]),
    );

    expect(edges).toHaveLength(2);
    expect(edges.every((edge) => edge.selectable === false)).toBe(true);
    expect(edges.every((edge) => edge.focusable === false)).toBe(true);
  });

  it("removes hidden kinds and edges whose endpoint is not shown", () => {
    const edges = makeFlowEdges(
      [
        { src: "a", dst: "b", kind: "implements" },
        { src: "b", dst: "c", kind: "prerequisite" },
      ],
      new Set(["implements"]),
      new Set(["a", "b"]),
    );

    expect(edges).toEqual([]);
  });

  it("curves edges for the mind map", () => {
    const [edge] = makeFlowEdges(
      [{ src: "a", dst: "b", kind: "part-of" }],
      new Set(),
      new Set(["a", "b"]),
      true,
    );

    expect(edge.type).toBe("simplebezier");
  });

  it("leaves layered-mode edges untouched", () => {
    const [edge] = makeFlowEdges(
      [{ src: "a", dst: "b", kind: "part-of" }],
      new Set(),
      new Set(["a", "b"]),
    );

    // No `type` key at all, so React Flow keeps its default routing.
    expect(edge).not.toHaveProperty("type");
  });
});
