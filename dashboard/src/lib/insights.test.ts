import { describe, expect, it } from "vitest";
import { computeInsights } from "./insights";

const base = {
  meta: { kind: "code" },
  nodes: [
    { id: "a", kind: "function", label: "a" },
    { id: "b", kind: "function", label: "b" },
  ],
  edges: [{ src: "a", dst: "b", kind: "calls" }],
  notes: { a: { status: "partial", unresolved: ["why?"] } },
  provenance: { equation_fidelity: "absent" },
  centrality: { a: 0.9, b: 0.0 },
};

describe("computeInsights", () => {
  it("flags dead code (in-degree 0, code kind)", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "dead-code" && i.nodeId === "a")).toBe(true);
  });

  it("flags cycles", () => {
    const cyc = { ...base, edges: [...base.edges, { src: "b", dst: "a", kind: "calls" }] };
    expect(computeInsights(cyc as never).some((i) => i.rule === "cycle")).toBe(true);
  });

  it("flags degraded math + unresolved notes as LOW", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "degraded-math" && i.severity === "LOW")).toBe(true);
    expect(r.some((i) => i.rule === "unresolved-note" && i.nodeId === "a")).toBe(true);
  });

  it("flags bottleneck via centrality p90", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "bottleneck" && i.nodeId === "a")).toBe(true);
  });

  it("flags stale docs when code mtime is newer than its note date", () => {
    const stale = {
      ...base,
      mtimes: { a: "2026-07-08" },
      notes: { a: { status: "complete", unresolved: [], date: "2026-07-01" } },
    };
    const r = computeInsights(stale as never);
    expect(r.some((i) => i.rule === "stale-doc" && i.severity === "HIGH"
      && i.nodeId === "a")).toBe(true);
  });
});
