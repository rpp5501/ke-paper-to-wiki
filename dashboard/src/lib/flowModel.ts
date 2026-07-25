import type { Edge } from "@xyflow/react";

import type { KEEdge } from "../types";

function edgeStyle(kind: string) {
  if (kind === "implements") {
    return { stroke: "#4a9b5e", strokeDasharray: "6 3", strokeWidth: 2 };
  }
  if (kind === "prerequisite" || kind === "builds-on") {
    return { stroke: "#cc8855", strokeDasharray: "4 3" };
  }
  return { stroke: "#475569" };
}

// R16.B2 — the mind-map view curves its edges; the layered reading view keeps
// the default orthogonal-ish routing untouched.
export function makeFlowEdges(
  edges: KEEdge[],
  hiddenKinds: Set<string>,
  shownIds: Set<string>,
  curved = false,
): Edge[] {
  return edges
    .filter((edge) => (
      !hiddenKinds.has(edge.kind)
      && shownIds.has(edge.src)
      && shownIds.has(edge.dst)
    ))
    .map((edge, index) => ({
      id: `e${index}`,
      source: edge.src,
      target: edge.dst,
      selectable: false,
      focusable: false,
      ariaLabel: `${edge.src} ${edge.kind} ${edge.dst}`,
      ...(curved ? { type: "simplebezier" } : {}),
      style: edgeStyle(edge.kind),
    }));
}
