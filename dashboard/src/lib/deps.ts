import type { KEEdge } from "../types";

// Single source of truth mirrored from research_mcp.graph_query (python):
// part-of→dst, prerequisite→dst, builds-on→src, everything else→src.
const DEPENDENT_SIDE: Record<string, "src" | "dst"> = {
  "part-of": "dst",
  prerequisite: "dst",
  "builds-on": "src",
};

export type NormalizedDependency = {
  dependent: string;
  dependency: string;
};

export function normalizeDependencies(edges: KEEdge[]): NormalizedDependency[] {
  return edges.map((edge) => {
    const side = DEPENDENT_SIDE[edge.kind] ?? "src";
    return side === "src"
      ? { dependent: edge.src, dependency: edge.dst }
      : { dependent: edge.dst, dependency: edge.src };
  });
}

function dependentsFrom(
  id: string,
  relations: NormalizedDependency[],
): string[] {
  return [...new Set(
    relations
      .filter(({ dependency }) => dependency === id)
      .map(({ dependent }) => dependent),
  )];
}

export function dependentsOf(id: string, edges: KEEdge[]): string[] {
  return dependentsFrom(id, normalizeDependencies(edges));
}

// R16.B3 — a node plus everything one edge away, ignoring direction and kind.
// Used for the hover halo, where "related to what I'm pointing at" is the
// question, not "what depends on what".
export function neighborhood(id: string, edges: KEEdge[]): Set<string> {
  const halo = new Set([id]);

  for (const edge of edges) {
    if (edge.src === id) halo.add(edge.dst);
    if (edge.dst === id) halo.add(edge.src);
  }
  return halo;
}

export function dependencyRings(
  id: string,
  edges: KEEdge[],
  maxDepth = 2,
): Map<string, number> {
  const relations = normalizeDependencies(edges);
  const rings = new Map<string, number>();
  let frontier = [id];
  const seen = new Set([id]);
  for (let depth = 1; depth <= maxDepth; depth++) {
    const next: string[] = [];
    for (const cur of frontier) {
      for (const dep of dependentsFrom(cur, relations)) {
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
