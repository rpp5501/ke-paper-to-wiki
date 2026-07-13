import type { KEEdge } from "../types";

// Single source of truth mirrored from research_mcp.graph_query (python):
// part-of→dst, prerequisite→dst, builds-on→src, everything else→src.
const DEPENDENT_SIDE: Record<string, "src" | "dst"> = {
  "part-of": "dst",
  prerequisite: "dst",
  "builds-on": "src",
};

function split(e: KEEdge): { dependent: string; dependency: string } {
  const side = DEPENDENT_SIDE[e.kind] ?? "src";
  return side === "src"
    ? { dependent: e.src, dependency: e.dst }
    : { dependent: e.dst, dependency: e.src };
}

export function dependentsOf(id: string, edges: KEEdge[]): string[] {
  const out = new Set<string>();
  for (const e of edges) {
    const { dependent, dependency } = split(e);
    if (dependency === id) out.add(dependent);
  }
  return [...out];
}

export function dependencyRings(
  id: string,
  edges: KEEdge[],
  maxDepth = 2,
): Map<string, number> {
  const rings = new Map<string, number>();
  let frontier = [id];
  const seen = new Set([id]);
  for (let depth = 1; depth <= maxDepth; depth++) {
    const next: string[] = [];
    for (const cur of frontier) {
      for (const dep of dependentsOf(cur, edges)) {
        if (!seen.has(dep)) {
          seen.add(dep);
          rings.set(dep, depth);
          next.push(dep);
        }
      }
    }
    frontier = next;
  }
  return rings;
}
