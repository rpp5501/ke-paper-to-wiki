import {
  Background,
  Controls,
  ReactFlow,
  useReactFlow,
  useStore,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useRef, useState } from "react";

import { KE_DATA } from "../data.gen";
import { ghostStyles } from "../lib/blastRadius";
import { dependencyRings } from "../lib/deps";
import { makeFlowEdges } from "../lib/flowModel";
import { layoutGraph, resetLayoutGraph } from "../lib/layout";
import { nodeCardSize } from "../lib/nodeDimensions";
import { learnFocus } from "../lib/learnPath";
import {
  clusterActivation,
  clusterCards,
  focusTargetForHiddenNode,
  selectionForCanvasNode,
  visibleAtZoom,
} from "../lib/lod";
import { useApp } from "../store";
import type { KEEdge, KENode } from "../types";
import { LEARN_STEPS } from "./LearnPanel";
import { nodeTypes } from "./nodes";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);
const RING_COLOR = ["#ef4444", "#f97316", "#eab308"];
const KE_NODES = KE_DATA.nodes as KENode[];
const KE_EDGES = KE_DATA.edges as KEEdge[];
const GRAPH_KIND = (KE_DATA.meta as {
  kind: "concept" | "code" | "bridged";
}).kind;
const CLUSTERS = KE_DATA.clusters as {
  id: string;
  label: string;
  nodeIds: string[];
}[];

type Position = { x: number; y: number };
type LayoutState =
  | { phase: "loading" }
  | { phase: "empty" }
  | { phase: "ready"; positions: Map<string, Position> }
  | { phase: "error"; diagnostic: string };

function diagnosticFor(error: unknown): string {
  if (error instanceof Error) return `${error.name}: ${error.message}`;
  return `Unknown worker error: ${String(error)}`;
}

export default function Canvas() {
  const {
    selected,
    setSelected,
    view,
    setView,
    hiddenKinds,
    blastOn,
    hoverEq,
    setLayoutPhase,
    mode,
    learnIdx,
    completedSteps,
  } = useApp();
  const [attempt, setAttempt] = useState(0);
  const [layout, setLayout] = useState<LayoutState>(
    KE_NODES.length === 0 ? { phase: "empty" } : { phase: "loading" },
  );
  const [visibilityStatus, setVisibilityStatus] = useState({
    message: "",
    revision: 0,
  });
  const flow = useReactFlow();
  const zoomedOut = useStore((state) => state.transform[2] < 0.5);
  const fittedAttempt = useRef<number | null>(null);
  const focusedNodeId = useRef<string | null>(null);

  useEffect(() => {
    if (KE_NODES.length === 0) {
      setLayout({ phase: "empty" });
      setLayoutPhase("empty");
      return;
    }

    let cancelled = false;
    setLayout({ phase: "loading" });
    setLayoutPhase("loading");
    void layoutGraph(KE_NODES, KE_EDGES)
      .then((positions) => {
        if (!cancelled) {
          setLayout({ phase: "ready", positions });
          setLayoutPhase("ready");
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLayout({ phase: "error", diagnostic: diagnosticFor(error) });
          setLayoutPhase("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [attempt, setLayoutPhase]);

  const rings = useMemo(
    () => (blastOn && selected ? dependencyRings(selected, KE_EDGES) : new Map()),
    [blastOn, selected],
  );
  const ghost = useMemo(
    () => ghostStyles(
      rings as Map<string, number>,
      KE_NODES.map((node) => node.id),
      selected ?? undefined,
    ),
    [rings, selected],
  );
  const equationHits = useMemo(
    () => new Set(
      hoverEq
        ? (KE_DATA.eqIndex as Record<string, string[]>)[hoverEq] ?? []
        : [],
    ),
    [hoverEq],
  );

  const viewNodeIds = useMemo(() => new Set(
    KE_NODES
      .filter((node) => view !== "concepts" || !CODE_KINDS.has(node.kind))
      .filter((node) => view !== "code" || CODE_KINDS.has(node.kind))
      .map((node) => node.id),
  ), [view]);
  const viewClusters = useMemo(() => CLUSTERS
    .map((cluster) => ({
      ...cluster,
      nodeIds: cluster.nodeIds.filter((nodeId) => viewNodeIds.has(nodeId)),
    }))
    .filter((cluster) => cluster.nodeIds.length > 0), [viewNodeIds]);
  const focus = useMemo(
    () => learnFocus(mode, learnIdx, LEARN_STEPS, KE_EDGES, completedSteps),
    [completedSteps, mode, learnIdx],
  );
  const lod = useMemo(() => (
    focus
      ? { showClusters: false, hiddenNodes: new Set<string>() }
      : visibleAtZoom(
        zoomedOut ? 0 : 1,
        0.5,
        viewClusters,
        [...viewNodeIds],
        view === "clusters",
      )
  ), [focus, view, viewClusters, viewNodeIds, zoomedOut]);

  const nodes = useMemo<Node[]>(() => {
    if (layout.phase !== "ready") return [];

    const memberNodes = KE_NODES
      .filter((node) => viewNodeIds.has(node.id))
      .filter((node) => !lod.hiddenNodes.has(node.id))
      .filter((node) => !focus || focus.has(node.id))
      .flatMap<Node>((node) => {
        const position = layout.positions.get(node.id);
        if (!position) return [];

        const ghostStyle = blastOn && selected ? ghost.get(node.id) : undefined;
        const ringColor = ghostStyle && ghostStyle.ring >= 0
          ? RING_COLOR[ghostStyle.ring]
          : undefined;
        const size = nodeCardSize(node.label);
        return [{
          id: node.id,
          type: CODE_KINDS.has(node.kind) ? "code" : "concept",
          position,
          ...size,
          data: { label: node.label, level: node.level },
          selected: node.id === selected,
          focusable: false,
          draggable: false,
          connectable: false,
          style: {
            opacity: ghostStyle?.opacity ?? 1,
            outline: equationHits.has(node.id)
              ? "3px solid #7aa2f7"
              : ringColor
                ? `3px solid ${ringColor}`
                : undefined,
            outlineOffset: 3,
            borderRadius: 8,
          },
        } satisfies Node];
      });
    const syntheticClusters = clusterCards(
      lod.showClusters,
      viewClusters,
      layout.positions,
    ).map<Node>((cluster) => {
      const size = nodeCardSize(cluster.label);
      return {
        id: cluster.id,
        type: "cluster",
        position: cluster.position,
        ...size,
        data: {
          label: cluster.label,
          count: cluster.count,
          onActivate: () => {
            const reducedMotion = window.matchMedia(
              "(prefers-reduced-motion: reduce)",
            ).matches;
            const activation = clusterActivation(GRAPH_KIND, reducedMotion);
            void flow.zoomTo(activation.zoom, {
              duration: activation.duration,
            });
            if (view === "clusters") setView(activation.view);
          },
        },
        focusable: false,
        draggable: false,
        connectable: false,
      };
    });
    return [...syntheticClusters, ...memberNodes];
  }, [
    blastOn,
    equationHits,
    flow,
    focus,
    ghost,
    layout,
    lod,
    selected,
    setView,
    view,
    viewClusters,
    viewNodeIds,
  ]);

  const shownIds = useMemo(() => new Set(nodes.map((node) => node.id)), [nodes]);
  const edges = useMemo(
    () => makeFlowEdges(KE_EDGES, hiddenKinds, shownIds),
    [hiddenKinds, shownIds],
  );

  useEffect(() => {
    const trackFocusedNode = (event: FocusEvent) => {
      const target = event.target;
      focusedNodeId.current = target instanceof HTMLElement
        ? target.closest<HTMLElement>("[data-node-id]")?.dataset.nodeId ?? null
        : null;
    };
    document.addEventListener("focusin", trackFocusedNode);
    return () => document.removeEventListener("focusin", trackFocusedNode);
  }, []);

  useEffect(() => {
    const focusTarget = focusTargetForHiddenNode(
      focusedNodeId.current,
      shownIds,
      lod.showClusters ? viewClusters : [],
      view,
    );
    if (!focusTarget) return;
    const frame = window.requestAnimationFrame(() => {
      const target = focusTarget.kind === "cluster"
        ? Array.from(document.querySelectorAll<HTMLElement>("[data-node-id]"))
          .find((element) => element.dataset.nodeId === focusTarget.id)
        : document.getElementById(focusTarget.id);
      if (!target) return;
      target.focus();
      const message = focusTarget.kind === "cluster"
        ? "Focused graph node hidden by semantic zoom; focus moved to its cluster."
        : "Focused graph node hidden by the active view; focus moved to the view control.";
      setVisibilityStatus((current) => ({
        message,
        revision: current.revision + 1,
      }));
    });
    return () => window.cancelAnimationFrame(frame);
  }, [lod.showClusters, shownIds, view, viewClusters]);

  useEffect(() => {
    if (
      layout.phase !== "ready"
      || nodes.length === 0
      || fittedAttempt.current === attempt
    ) return;
    const frame = window.requestAnimationFrame(() => {
      fittedAttempt.current = attempt;
      void flow.fitView({ padding: 0.16 });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [attempt, flow, layout.phase, nodes.length]);

  useEffect(() => {
    if (!focus || layout.phase !== "ready") return;
    const frame = window.requestAnimationFrame(() => {
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      void flow.fitView({ padding: 0.3, duration: reducedMotion ? 0 : 400 });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [flow, layout.phase, focus]);

  const ready = layout.phase === "ready";
  const statusMessage = layout.phase === "loading"
    ? `Laying out ${KE_NODES.length} nodes…`
    : layout.phase === "ready"
      ? `Graph layout ready. ${KE_NODES.length} nodes positioned.`
      : layout.phase === "empty"
        ? "No graph data in this build."
        : "Graph layout failed. Retry layout is available.";

  return (
    <div className="canvas" aria-busy={layout.phase === "loading"}>
      <ReactFlow
        aria-label="Knowledge dependency graph"
        colorMode="dark"
        deleteKeyCode={null}
        edges={edges}
        edgesFocusable={false}
        elementsSelectable={false}
        multiSelectionKeyCode={null}
        nodes={nodes}
        nodesConnectable={false}
        nodesDraggable={false}
        nodesFocusable={false}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => {
          const selectedNodeId = selectionForCanvasNode(node.id);
          if (ready && selectedNodeId) setSelected(selectedNodeId);
        }}
        onPaneClick={() => setSelected(null)}
        selectionKeyCode={null}
        selectionOnDrag={false}
        selectNodesOnDrag={false}
      >
        <Background color="#333846" gap={24} />
        <Controls
          aria-label="Graph viewport controls"
          position="top-right"
          showInteractive={false}
        />
      </ReactFlow>

      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {statusMessage}
      </div>
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        <span key={visibilityStatus.revision}>{visibilityStatus.message}</span>
      </div>

      {layout.phase === "loading" && (
        <div className="canvas-state canvas-loading">{statusMessage}</div>
      )}
      {layout.phase === "empty" && (
        <div className="canvas-state canvas-empty">
          <strong>No graph data in this build.</strong>
          <span>Run the local data bundler, then rebuild the dashboard.</span>
        </div>
      )}
      {layout.phase === "error" && (
        <div className="canvas-state canvas-error">
          <strong>Graph layout failed.</strong>
          <span className="layout-diagnostic">{layout.diagnostic}</span>
          <button
            className="retry-layout"
            onClick={() => {
              setLayout({ phase: "loading" });
              setLayoutPhase("loading");
              resetLayoutGraph();
              setAttempt((value) => value + 1);
            }}
            type="button"
          >
            Retry layout
          </button>
        </div>
      )}
    </div>
  );
}
