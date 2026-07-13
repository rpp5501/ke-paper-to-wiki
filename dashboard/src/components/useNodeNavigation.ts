import { useCallback, useEffect, useState } from "react";

import { KE_DATA } from "../data.gen";
import { viewForNode } from "../lib/navigation";
import { useApp, type View } from "../store";
import type { KENode } from "../types";
import { useCenterOn } from "./Canvas";

const KE_NODES = KE_DATA.nodes as KENode[];

type PendingNavigation = {
  nodeId: string;
  view: View;
};

export function useNodeNavigation() {
  const { view, setView, setSelected } = useApp();
  const centerOn = useCenterOn();
  const [pending, setPending] = useState<PendingNavigation | null>(null);

  useEffect(() => {
    if (!pending || view !== pending.view) return;

    let secondFrame = 0;
    const firstFrame = window.requestAnimationFrame(() => {
      secondFrame = window.requestAnimationFrame(() => {
        setSelected(pending.nodeId);
        centerOn(pending.nodeId);
        setPending(null);
      });
    });

    return () => {
      window.cancelAnimationFrame(firstFrame);
      if (secondFrame) window.cancelAnimationFrame(secondFrame);
    };
  }, [centerOn, pending, setSelected, view]);

  return useCallback((nodeId: string, requiredView?: View) => {
    const node = KE_NODES.find((candidate) => candidate.id === nodeId);
    const nextView = requiredView
      ?? (node ? viewForNode(view, node.kind) : view);
    if (nextView !== view) setView(nextView);
    setPending({ nodeId, view: nextView });
  }, [setView, view]);
}
