import { describe, expect, it } from "vitest";
import { dependencyRings, dependentsOf, normalizeDependencies } from "./deps";

const EDGES = [
  { src: "sdpa", dst: "attention", kind: "part-of" },
  { src: "mha", dst: "sdpa", kind: "builds-on" },
  { src: "attention", dst: "transformer", kind: "part-of" },
];

describe("dependentsOf", () => {
  it("mirrors the python dependent-side map", () => {
    expect(new Set(dependentsOf("sdpa", EDGES)))
      .toEqual(new Set(["attention", "mha"]));
  });
});

describe("normalizeDependencies", () => {
  it("returns one dependent-to-dependency relationship per edge kind", () => {
    expect(normalizeDependencies(EDGES)).toEqual([
      { dependent: "attention", dependency: "sdpa" },
      { dependent: "mha", dependency: "sdpa" },
      { dependent: "transformer", dependency: "attention" },
    ]);
  });
});

describe("dependencyRings", () => {
  it("assigns hop depth per dependent", () => {
    const rings = dependencyRings("sdpa", EDGES, 3);
    expect(rings.get("attention")).toBe(1);
    expect(rings.get("mha")).toBe(1);
    expect(rings.get("transformer")).toBe(2);
    expect(rings.has("sdpa")).toBe(false);
  });
});
