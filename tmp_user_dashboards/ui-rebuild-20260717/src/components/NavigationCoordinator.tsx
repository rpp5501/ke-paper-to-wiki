import { useEffect, useState } from "react";
import { useNodes, useReactFlow, useStore } from "@xyflow/react";

import { getNavigationAction } from "../lib/navigation";
import { useApp } from "../store";

function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function NavigationCoordinator() {
  const pending = useApp((state) => state.pendingNavigation);
  const view = useApp((state) => state.view);
  const layoutPhase = useApp((state) => state.layoutPhase);
  const setSelected = useApp((state) => state.setSelected);
  const clearNavigation = useApp((state) => state.clearNavigation);
  const flow = useReactFlow();
  const mountedNodes = useNodes();
  const viewportMounted = useStore((state) => state.panZoom !== null);
  const [snappedRequestId, setSnappedRequestId] = useState<number | null>(null);
  const target = pending
    ? mountedNodes.find((node) => node.id === pending.nodeId)
    : undefined;
  const targetX = target?.position.x;
  const targetY = target?.position.y;
  const action = getNavigationAction({
    pending,
    view,
    layoutPhase,
    targetMounted: viewportMounted && target !== undefined,
  });

  useEffect(() => {
    if (!pending) {
      setSnappedRequestId(null);
      return;
    }

    const requestId = pending.requestId;
    let cancelled = false;
    const isCurrent = () => (
      useApp.getState().pendingNavigation?.requestId === requestId
    );

    setSnappedRequestId(null);
    void flow.setViewport(flow.getViewport(), { duration: 0 }).then(() => {
      if (!cancelled && isCurrent()) setSnappedRequestId(requestId);
    });

    return () => {
      cancelled = true;
    };
  }, [flow, pending]);

  useEffect(() => {
    if (
      action !== "navigate"
      || !pending
      || snappedRequestId !== pending.requestId
      || targetX === undefined
      || targetY === undefined
    ) return;

    const requestId = pending.requestId;
    let cancelled = false;

    setSelected(pending.nodeId);
    void flow.setCenter(targetX + 90, targetY + 32, {
      zoom: 1.2,
      duration: prefersReducedMotion() ? 0 : 600,
    }).then(() => {
      if (!cancelled) clearNavigation(requestId);
    });

    return () => {
      cancelled = true;
    };
  }, [
    action,
    clearNavigation,
    flow,
    pending,
    setSelected,
    snappedRequestId,
    targetX,
    targetY,
  ]);

  return null;
}
