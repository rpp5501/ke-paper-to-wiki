import type {
  LayoutPhase,
  PendingNavigation,
  View,
} from "../store";
import type { KENode } from "../types";

export type ArrowKey = "ArrowLeft" | "ArrowRight";
export type IndexNavigationKey = ArrowKey
  | "ArrowUp"
  | "ArrowDown"
  | "Home"
  | "End";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);

export type SearchResolution = {
  nodeId: string;
  view: View;
};

export function moveIndex(
  current: number,
  count: number,
  key: IndexNavigationKey,
): number {
  if (count <= 0) return -1;
  if (key === "Home") return 0;
  if (key === "End") return count - 1;
  const delta = key === "ArrowRight" || key === "ArrowDown" ? 1 : -1;
  return (current + delta + count) % count;
}

export type NavigationAction = "idle" | "wait" | "navigate";

export function getNavigationAction({
  pending,
  view,
  layoutPhase,
  targetMounted,
}: {
  pending: PendingNavigation | null;
  view: View;
  layoutPhase: LayoutPhase;
  targetMounted: boolean;
}): NavigationAction {
  if (!pending) return "idle";
  if (
    layoutPhase !== "ready"
    || view !== pending.requiredView
    || !targetMounted
  ) return "wait";
  return "navigate";
}

export function navigationDisabledReason(
  layoutPhase: LayoutPhase,
  targetExists: boolean,
): string | null {
  if (!targetExists) return "Target node is not available in this build.";
  if (layoutPhase === "loading") return "Graph layout is still loading.";
  if (layoutPhase === "empty") return "No graph data in this build.";
  if (layoutPhase === "error") {
    return "Graph layout failed. Retry layout before navigating.";
  }
  return null;
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
