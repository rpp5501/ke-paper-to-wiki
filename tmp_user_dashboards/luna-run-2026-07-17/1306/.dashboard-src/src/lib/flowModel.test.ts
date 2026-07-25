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
});
