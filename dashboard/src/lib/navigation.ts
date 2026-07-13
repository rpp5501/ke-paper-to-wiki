import type { View } from "../store";
import type { KENode } from "../types";

export type ArrowKey = "ArrowLeft" | "ArrowRight";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);

export type SearchResolution = {
  nodeId: string;
  view: View;
};

export function moveIndex(
  current: number,
  count: number,
  key: ArrowKey,
): number {
  if (count <= 0) return -1;
  const delta = key === "ArrowRight" ? 1 : -1;
  return (current + delta + count) % count;
}

export function viewForNode(view: View, kind: string): View {
  if (view === "bridged") return view;
  return CODE_KINDS.has(kind) ? "code" : "concepts";
}

export function resolveSearch(
  nodes: KENode[],
  query: string,
  view: View,
): SearchResolution | null {
  const normalized = query.trim().toLocaleLowerCase();
  if (!normalized) return null;
  const match = nodes.find((node) => (
    node.label.toLocaleLowerCase().includes(normalized)
  ));
  return match
    ? { nodeId: match.id, view: viewForNode(view, match.kind) }
    : null;
}
