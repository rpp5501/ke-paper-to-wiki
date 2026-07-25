// R16.B1 — mind-map branch collapse. Folding a branch hides its part-of
// subtree; the parent stays put and reports how many nodes it swallowed.
// Deferred in R15.10 v1, in scope now that real-paper graphs exist.
import type { KEEdge, KENode } from "../types";

// `src --part-of--> dst` reads "src is a part of dst", so dst is the parent.
// Same direction the python graph_query uses; see lib/deps.ts.
export function partOfChildren(edges: KEEdge[]): Map<string, string[]> {
  const children = new Map<string, string[]>();

  for (const edge of edges) {
    if (edge.kind !== "part-of") continue;
    children.set(edge.dst, [...(children.get(edge.dst) ?? []), edge.src]);
  }
  return children;
}

/** Every part-of descendant of the collapsed nodes. Collapsed nodes stay
 *  visible themselves — unless they sit inside another folded branch. */
export function hiddenByCollapse(
  collapsed: Set<string>,
  edges: KEEdge[],
): Set<string> {
  const children = partOfChildren(edges);
  const hidden = new Set<string>();

  const walk = (id: string): void => {
    for (const child of children.get(id) ?? []) {
      // Also the cycle guard: malformed part-of loops terminate here rather
      // than recursing forever.
      if (hidden.has(child)) continue;
      hidden.add(child);
      walk(child);
    }
  };
  for (const id of collapsed) walk(id);

  return hidden;
}

/** How many nodes a given branch would swallow — the badge number. */
export function collapsedCount(nodeId: string, edges: KEEdge[]): number {
  return hiddenByCollapse(new Set([nodeId]), edges).size;
}

export function hasChildren(nodeId: string, edges: KEEdge[]): boolean {
  return (partOfChildren(edges).get(nodeId)?.length ?? 0) > 0;
}

export type VisibleGraph = { nodes: KENode[]; edges: KEEdge[] };

// Edges are dropped only when they touch a hidden node, so non-tree edges
// pointing at a collapsed parent survive the fold.
export function collapseGraph(
  nodes: KENode[],
  edges: KEEdge[],
  collapsed: Set<string>,
): VisibleGraph {
  const hidden = collapsed.size === 0
    ? new Set<string>()
    : hiddenByCollapse(collapsed, edges);

  // Identity when nothing folds: the layout cache key is derived from these
  // arrays, so expanding everything restores the original layout input.
  if (hidden.size === 0) return { nodes, edges };

  return {
    nodes: nodes.filter((node) => !hidden.has(node.id)),
    edges: edges.filter(
      (edge) => !hidden.has(edge.src) && !hidden.has(edge.dst),
    ),
  };
}
