import type { KEEdge, KENode } from "../types";
import { splitTiers } from "./mathHtml";

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

const MAX_BLURB = 180;

function firstSentence(markdown: string): string {
  const body = markdown
    .replace(/\$\$[\s\S]*?\$\$/g, "")
    .replace(/\\\([\s\S]*?\\\)/g, "")
    .replace(/[#*_`>[\]]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (!body) return "";
  const sentence = body.split(/(?<=[.!?])\s/)[0] ?? "";
  return sentence.length > MAX_BLURB
    ? `${sentence.slice(0, MAX_BLURB - 1).trimEnd()}…`
    : sentence;
}

export function buildLearnSteps(
  tour: TourSourceStep[],
  nodes: KENode[],
  pages: Record<string, string>,
): LearnStep[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return [...tour]
    .sort((left, right) => left.order - right.order)
    .flatMap((step) => {
      const nodeId = step.nodeIds.find((candidate) => byId.has(candidate));
      if (!nodeId) return [];
      const node = byId.get(nodeId) as KENode & { page?: string };
      const markdown = pageMarkdownFor(node, pages);
      const tldr = markdown ? splitTiers(markdown).tldr : undefined;
      const blurb = (tldr && firstSentence(tldr)) || step.description;
      return [{ nodeId, title: step.title, blurb }];
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
