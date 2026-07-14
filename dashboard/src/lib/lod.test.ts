import { describe, expect, it } from "vitest";
import {
  clusterActivation,
  clusterCards,
  clusterDetailView,
  clusterZoomDuration,
  focusTargetForHiddenNode,
  selectionForCanvasNode,
  visibleAtZoom,
} from "./lod";
import { makeFlowEdges } from "./flowModel";

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

  it("explicit cluster view replaces members while preserving unclustered nodes", () => {
    const v = visibleAtZoom(
      0.8,
      0.5,
      clusters,
      ["a", "b", "solo"],
      true,
    );

    expect(v.showClusters).toBe(true);
    expect([...v.hiddenNodes].sort()).toEqual(["a", "b"]);
    expect(v.hiddenNodes.has("solo")).toBe(false);
  });

  it("builds deterministic synthetic cards from the first positioned member", () => {
    const cards = clusterCards(true, [{
      id: "c1",
      label: "Cluster one",
      nodeIds: ["missing", "b"],
    }, {
      id: "c2",
      label: "Cluster two",
      nodeIds: ["also-missing"],
    }], new Map([["b", { x: 12, y: 34 }]]));

    expect(cards).toEqual([{
      id: "cluster:c1",
      label: "Cluster one",
      count: 2,
      position: { x: 12, y: 34 },
    }, {
      id: "cluster:c2",
      label: "Cluster two",
      count: 1,
      position: { x: 220, y: 0 },
    }]);
    expect(clusterCards(false, clusters, new Map())).toEqual([]);
  });

  it("makes cluster zoom immediate under reduced motion", () => {
    expect(clusterZoomDuration(false)).toBe(500);
    expect(clusterZoomDuration(true)).toBe(0);
    expect(clusterDetailView("concept")).toBe("concepts");
    expect(clusterDetailView("code")).toBe("code");
    expect(clusterDetailView("bridged")).toBe("bridged");
  });

  it("separates synthetic cluster activation from real-node selection", () => {
    expect(clusterActivation("concept", false)).toEqual({
      duration: 500,
      view: "concepts",
      zoom: 0.9,
    });
    expect(clusterActivation("bridged", true)).toEqual({
      duration: 0,
      view: "bridged",
      zoom: 0.9,
    });
    expect(selectionForCanvasNode("cluster:attention")).toBeNull();
    expect(selectionForCanvasNode("attention")).toBe("attention");
  });

  it("moves hidden focused members to a cluster or active view control", () => {
    expect(focusTargetForHiddenNode(
      "attention",
      new Set(["cluster:attention", "solo"]),
      [{ id: "attention", label: "Attention", nodeIds: ["attention"] }],
      "clusters",
    )).toEqual({ id: "cluster:attention", kind: "cluster" });
    expect(focusTargetForHiddenNode(
      "code-node",
      new Set(["attention"]),
      [],
      "concepts",
    )).toEqual({ id: "graph-view-concepts", kind: "view" });
    expect(focusTargetForHiddenNode(
      "attention",
      new Set(["attention"]),
      clusters,
      "concepts",
    )).toBeNull();
  });

  it("feeds LOD-rendered real IDs into edge endpoint pruning", () => {
    const lod = visibleAtZoom(0.3, 0.5, clusters, ["a", "b", "solo"]);
    const cards = clusterCards(lod.showClusters, clusters, new Map());
    const shownIds = new Set([
      ...cards.map((card) => card.id),
      "solo",
    ]);

    expect(makeFlowEdges([
      { src: "a", dst: "b", kind: "calls" },
      { src: "a", dst: "solo", kind: "calls" },
    ], new Set(), shownIds)).toEqual([]);
  });
});
