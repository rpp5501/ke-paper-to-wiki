import { describe, expect, it } from "vitest";

import type { KENode } from "../types";
import { moveIndex, resolveSearch } from "./navigation";

const nodes: KENode[] = [
  { id: "attention", kind: "concept", label: "Attention" },
  { id: "attention-code", kind: "function", label: "Compute Attention" },
  { id: "encoder", kind: "concept", label: "Attention Encoder" },
];

describe("resolveSearch", () => {
  it("returns the first case-insensitive label match", () => {
    expect(resolveSearch(nodes, "  ATTENTION  ", "concepts")).toEqual({
      nodeId: "attention",
      view: "concepts",
    });
  });

  it("reveals a code match from a view that hides detailed code nodes", () => {
    expect(resolveSearch(nodes, "compute", "clusters")).toEqual({
      nodeId: "attention-code",
      view: "code",
    });
  });

  it("reveals a concept match from the code-only view", () => {
    expect(resolveSearch(nodes, "encoder", "code")).toEqual({
      nodeId: "encoder",
      view: "concepts",
    });
  });

  it("keeps the bridged view because it already shows both node kinds", () => {
    expect(resolveSearch(nodes, "compute", "bridged")).toEqual({
      nodeId: "attention-code",
      view: "bridged",
    });
  });

  it("returns null when no label matches", () => {
    expect(resolveSearch(nodes, "missing", "concepts")).toBeNull();
  });
});

describe("moveIndex", () => {
  it("wraps right-arrow movement at the end", () => {
    expect(moveIndex(3, 4, "ArrowRight")).toBe(0);
  });

  it("wraps left-arrow movement at the beginning", () => {
    expect(moveIndex(0, 4, "ArrowLeft")).toBe(3);
  });

  it("returns no index for an empty group", () => {
    expect(moveIndex(0, 0, "ArrowRight")).toBe(-1);
  });
});
