import type { KEEdge, KENode } from "../types";

export type TourSourceStep = {
  order: number;
  title: string;
  description: string;
  nodeIds: string[];
};

export type LearnStep = { nodeId: string; title: string; blurb: string };

export function pageMarkdownFor(
  node: KENode & { page?: string },
  pages: Record<string, string>,
): string | undefined {
  if (pages[node.id]) return pages[node.id];
  if (!node.page) return undefined;
  const stem = node.page.replace(/\.md$/i, "").replace(/^\d+_/, "");
  return pages[stem];
}

export function buildLearnSteps(
  tour: TourSourceStep[],
  nodes: KENode[],
): LearnStep[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return [...tour]
    .sort((left, right) => left.order - right.order)
    .flatMap((step) => {
      const nodeId = step.nodeIds.find((candidate) => byId.has(candidate));
      if (!nodeId) return [];
      return [{ nodeId, title: step.title, blurb: step.description }];
    });
}

export function focusNodeIds(
  stepNodeId: string,
  edges: KEEdge[],
  completed: Set<string>,
): Set<string> {
  const visible = new Set([stepNodeId, ...completed]);
  edges.forEach((edge) => {
    if (edge.src === stepNodeId) visible.add(edge.dst);
    if (edge.dst === stepNodeId) visible.add(edge.src);
  });
  return visible;
}

export function learnFocus(
  mode: "learn" | "explore",
  tourIdx: number | null,
  steps: LearnStep[],
  edges: KEEdge[],
  completed: Set<string>,
): Set<string> | null {
  if (mode !== "learn" || steps.length === 0) return null;
  const bounded = Math.min(Math.max(tourIdx ?? 0, 0), steps.length - 1);
  return focusNodeIds(steps[bounded].nodeId, edges, completed);
}
