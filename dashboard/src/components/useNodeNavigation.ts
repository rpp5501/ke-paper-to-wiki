import { useCallback } from "react";

import { KE_DATA } from "../data.gen";
import { viewForNode } from "../lib/navigation";
import { useApp, type View } from "../store";
import type { KENode } from "../types";

const KE_NODES = KE_DATA.nodes as KENode[];

export function useNodeNavigation() {
  const { view, layoutPhase, queueNavigation } = useApp();

  return useCallback((nodeId: string, requiredView?: View) => {
    if (layoutPhase !== "ready") return;
    const node = KE_NODES.find((candidate) => candidate.id === nodeId);
    if (!node) return;
    const nextView = requiredView
      ?? viewForNode(view, node.kind);
    queueNavigation(nodeId, nextView);
  }, [layoutPhase, queueNavigation, view]);
}
