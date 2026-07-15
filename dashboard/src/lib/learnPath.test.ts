import { describe, expect, it } from "vitest";
import { buildLearnSteps, focusNodeIds, pageMarkdownFor } from "./learnPath";

const NODES = [
  { id: "a", kind: "concept", label: "Alpha", page: "01_a.md" },
  { id: "b", kind: "concept", label: "Beta" },
];
const PAGES = {
  a: "## TL;DR {#tldr}\nAlpha is the core idea. It has $x^2$ math.\n\n## The Math {#the-math}\n$$x$$",
};
const TOUR = [
  { order: 2, title: "Beta", description: "fallback blurb", nodeIds: ["b"] },
  { order: 1, title: "Alpha", description: "generic", nodeIds: ["a"] },
];

describe("buildLearnSteps", () => {
  it("orders by tour order and prefers the TL;DR first sentence as blurb", () => {
    const steps = buildLearnSteps(TOUR, NODES, PAGES);
    expect(steps.map((s) => s.nodeId)).toEqual(["a", "b"]);
    expect(steps[0].blurb).toBe("Alpha is the core idea.");
  });

  it("falls back to the tour description when no page exists", () => {
    const steps = buildLearnSteps(TOUR, NODES, PAGES);
    expect(steps[1].blurb).toBe("fallback blurb");
  });

  it("skips steps whose node is missing", () => {
    const steps = buildLearnSteps(
      [{ order: 1, title: "Ghost", description: "", nodeIds: ["ghost"] }],
      NODES,
      PAGES,
    );
    expect(steps).toEqual([]);
  });
});

describe("pageMarkdownFor", () => {
  it("resolves by id, then by numbered-filename stem", () => {
    expect(pageMarkdownFor(NODES[0], PAGES)).toContain("Alpha is the core idea");
    expect(
      pageMarkdownFor({ id: "zzz", kind: "concept", label: "Z", page: "07_a.md" }, PAGES),
    ).toContain("Alpha is the core idea");
  });
});

describe("focusNodeIds", () => {
  const EDGES = [
    { src: "a", dst: "b", kind: "prerequisite" },
    { src: "c", dst: "a", kind: "builds-on" },
    { src: "d", dst: "e", kind: "prerequisite" },
  ];
  it("returns the step node, its 1-hop neighbors, and completed steps", () => {
    expect(focusNodeIds("a", EDGES, new Set(["e"]))).toEqual(new Set(["a", "b", "c", "e"]));
  });
  it("works with no edges", () => {
    expect(focusNodeIds("a", [], new Set())).toEqual(new Set(["a"]));
  });
});
