import { describe, expect, it } from "vitest";

import type { KENode } from "../types";
import * as navigation from "./navigation";
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

  it("uses vertical arrows with the same wrapping behavior", () => {
    expect(moveIndex(0, 4, "ArrowUp")).toBe(3);
    expect(moveIndex(3, 4, "ArrowDown")).toBe(0);
  });

  it("moves directly to the first or last item", () => {
    expect(moveIndex(2, 4, "Home")).toBe(0);
    expect(moveIndex(1, 4, "End")).toBe(3);
  });
});

describe("navigation coordinator decisions", () => {
  const getNavigationAction = (
    navigation as unknown as {
      getNavigationAction?: (input: {
        pending: {
          requestId: number;
          nodeId: string;
          requiredView: "code";
        } | null;
        view: "concepts" | "code";
        layoutPhase: "loading" | "ready";
        targetMounted: boolean;
      }) => string;
    }
  ).getNavigationAction;

  it("stays idle without a pending request", () => {
    expect(typeof getNavigationAction).toBe("function");
    if (!getNavigationAction) return;
    expect(getNavigationAction({
      pending: null,
      view: "concepts",
      layoutPhase: "ready",
      targetMounted: false,
    })).toBe("idle");
  });

  it("waits for readiness, the required view, and a mounted target", () => {
    expect(typeof getNavigationAction).toBe("function");
    if (!getNavigationAction) return;
    const pending = {
      requestId: 1,
      nodeId: "attention-code",
      requiredView: "code" as const,
    };
    expect(getNavigationAction({
      pending,
      view: "code",
      layoutPhase: "loading",
      targetMounted: true,
    })).toBe("wait");
    expect(getNavigationAction({
      pending,
      view: "concepts",
      layoutPhase: "ready",
      targetMounted: true,
    })).toBe("wait");
    expect(getNavigationAction({
      pending,
      view: "code",
      layoutPhase: "ready",
      targetMounted: false,
    })).toBe("wait");
  });

  it("runs only when the newest target is ready and mounted", () => {
    expect(typeof getNavigationAction).toBe("function");
    if (!getNavigationAction) return;
    expect(getNavigationAction({
      pending: {
        requestId: 2,
        nodeId: "attention-code",
        requiredView: "code",
      },
      view: "code",
      layoutPhase: "ready",
      targetMounted: true,
    })).toBe("navigate");
  });
});

describe("navigation disabled reasons", () => {
  const navigationDisabledReason = (
    navigation as unknown as {
      navigationDisabledReason?: (
        phase: "loading" | "ready" | "empty" | "error",
        targetExists: boolean,
      ) => string | null;
    }
  ).navigationDisabledReason;

  it("explains invalid targets before layout state", () => {
    expect(typeof navigationDisabledReason).toBe("function");
    if (!navigationDisabledReason) return;
    expect(navigationDisabledReason("loading", false))
      .toBe("Target node is not available in this build.");
  });

  it("explains each unavailable layout state and enables ready targets", () => {
    expect(typeof navigationDisabledReason).toBe("function");
    if (!navigationDisabledReason) return;
    expect(navigationDisabledReason("loading", true))
      .toBe("Graph layout is still loading.");
    expect(navigationDisabledReason("empty", true))
      .toBe("No graph data in this build.");
    expect(navigationDisabledReason("error", true))
      .toBe("Graph layout failed. Retry layout before navigating.");
    expect(navigationDisabledReason("ready", true)).toBeNull();
  });
});
