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
  it("flags code with no normalized dependents", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "dead-code" && i.nodeId === "a")).toBe(true);
  });

  it("flags cycles", () => {
    const cyc = { ...base, edges: [...base.edges, { src: "b", dst: "a", kind: "calls" }] };
    expect(computeInsights(cyc as never).some((i) => i.rule === "cycle")).toBe(true);
  });

  it("does not mistake equivalent mixed-kind dependencies for a cycle", () => {
    const mixed = {
      ...base,
      edges: [
        { src: "a", dst: "b", kind: "prerequisite" },
        { src: "b", dst: "a", kind: "builds-on" },
      ],
    };
    expect(computeInsights(mixed as never).some((i) => i.rule === "cycle")).toBe(false);
  });

  it("flags a cycle after normalizing mixed edge kinds", () => {
    const cycle = {
      ...base,
      edges: [
        { src: "a", dst: "b", kind: "prerequisite" },
        { src: "a", dst: "b", kind: "builds-on" },
      ],
    };
    expect(computeInsights(cycle as never).some((i) => i.rule === "cycle")).toBe(true);
  });

  it("flags dead code by normalized dependents, regardless of raw indegree", () => {
    const dependency = {
      ...base,
      edges: [{ src: "a", dst: "b", kind: "prerequisite" }],
    };
    const dead = computeInsights(dependency as never)
      .filter((i) => i.rule === "dead-code")
      .map((i) => i.nodeId);
    expect(dead).toEqual(["b"]);
  });

  it("excludes routes and clear main entry identifiers or labels from dead code", () => {
    const entries = {
      ...base,
      nodes: [
        { id: "route", kind: "route", label: "GET /health" },
        { id: "app.py::main", kind: "function", label: "entry" },
        { id: "module", kind: "file", label: "__main__" },
        { id: "helper", kind: "function", label: "helper" },
      ],
      edges: [],
      notes: {},
      provenance: { equation_fidelity: "exact" },
      centrality: {},
    };
    const dead = computeInsights(entries as never)
      .filter((i) => i.rule === "dead-code")
      .map((i) => i.nodeId);
    expect(dead).toEqual(["helper"]);
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
