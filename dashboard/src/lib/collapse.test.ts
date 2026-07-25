import { describe, expect, it } from "vitest";

import {
  collapseGraph,
  collapsedCount,
  hasChildren,
  hiddenByCollapse,
  partOfChildren,
} from "./collapse";
import type { KEEdge, KENode } from "../types";

// transformer ─┬─ attention ─┬─ sdpa ── eq
//              │             └─ mha
//              └─ encoder
// plus a non-tree prerequisite edge encoder → attention.
const nodes = [
  "transformer", "attention", "sdpa", "eq", "mha", "encoder",
].map((id) => ({ id, kind: "concept", label: id }) as KENode);

const edges = [
  { src: "attention", dst: "transformer", kind: "part-of" },
  { src: "encoder", dst: "transformer", kind: "part-of" },
  { src: "sdpa", dst: "attention", kind: "part-of" },
  { src: "mha", dst: "attention", kind: "part-of" },
  { src: "eq", dst: "sdpa", kind: "part-of" },
  { src: "encoder", dst: "attention", kind: "prerequisite" },
] as KEEdge[];

const idsOf = (list: { id: string }[]) => list.map((item) => item.id).sort();

describe("partOfChildren", () => {
  it("reads src --part-of--> dst as dst being the parent", () => {
    const children = partOfChildren(edges);

    expect(children.get("transformer")?.sort()).toEqual(["attention", "encoder"]);
    expect(children.get("attention")?.sort()).toEqual(["mha", "sdpa"]);
    expect(children.get("eq")).toBeUndefined();
  });

  it("ignores non part-of edges", () => {
    expect(partOfChildren([edges[5]]).size).toBe(0);
  });
});

describe("hiddenByCollapse", () => {
  it("hides the whole subtree, not just direct children", () => {
    expect([...hiddenByCollapse(new Set(["attention"]), edges)].sort())
      .toEqual(["eq", "mha", "sdpa"]);
  });

  it("keeps the collapsed node itself visible", () => {
    expect(hiddenByCollapse(new Set(["attention"]), edges).has("attention"))
      .toBe(false);
  });

  it("hides a nested collapsed node that sits inside another fold", () => {
    const hidden = hiddenByCollapse(new Set(["transformer", "attention"]), edges);

    expect(hidden.has("attention")).toBe(true);
    expect(hidden.has("transformer")).toBe(false);
  });

  it("hides nothing for a leaf", () => {
    expect(hiddenByCollapse(new Set(["eq"]), edges).size).toBe(0);
  });

  it("terminates on a malformed part-of cycle", () => {
    const cyclic = [
      { src: "a", dst: "b", kind: "part-of" },
      { src: "b", dst: "a", kind: "part-of" },
    ] as KEEdge[];

    expect([...hiddenByCollapse(new Set(["a"]), cyclic)].sort()).toEqual(["a", "b"]);
  });
});

describe("collapsedCount / hasChildren", () => {
  it("counts the whole branch for the badge", () => {
    expect(collapsedCount("attention", edges)).toBe(3);
    expect(collapsedCount("sdpa", edges)).toBe(1);
    expect(collapsedCount("eq", edges)).toBe(0);
  });

  it("knows which nodes can fold at all", () => {
    expect(hasChildren("attention", edges)).toBe(true);
    expect(hasChildren("eq", edges)).toBe(false);
  });
});

describe("collapseGraph", () => {
  it("drops the descendants of a collapsed branch", () => {
    const visible = collapseGraph(nodes, edges, new Set(["attention"]));

    expect(idsOf(visible.nodes)).toEqual(["attention", "encoder", "transformer"]);
  });

  it("preserves non-tree edges pointing at the collapsed parent", () => {
    const visible = collapseGraph(nodes, edges, new Set(["attention"]));

    expect(visible.edges).toContainEqual({
      src: "encoder", dst: "attention", kind: "prerequisite",
    });
    expect(visible.edges).toContainEqual({
      src: "attention", dst: "transformer", kind: "part-of",
    });
  });

  it("drops every edge that touches a hidden node", () => {
    const visible = collapseGraph(nodes, edges, new Set(["attention"]));

    for (const edge of visible.edges) {
      expect(["sdpa", "mha", "eq"]).not.toContain(edge.src);
      expect(["sdpa", "mha", "eq"]).not.toContain(edge.dst);
    }
  });

  it("returns the original arrays when nothing is collapsed", () => {
    const visible = collapseGraph(nodes, edges, new Set());

    // Identity, so expanding restores byte-equal layout input and the layout
    // cache key is unchanged.
    expect(visible.nodes).toBe(nodes);
    expect(visible.edges).toBe(edges);
  });

  it("restores byte-equal layout input after collapse then expand", () => {
    const before = JSON.stringify(collapseGraph(nodes, edges, new Set()));
    collapseGraph(nodes, edges, new Set(["attention"]));
    const after = JSON.stringify(collapseGraph(nodes, edges, new Set()));

    expect(after).toBe(before);
  });

  it("treats collapsing a leaf as a no-op", () => {
    const visible = collapseGraph(nodes, edges, new Set(["eq"]));

    expect(visible.nodes).toBe(nodes);
  });
});
