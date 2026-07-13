import {
  Background,
  Controls,
  ReactFlow,
  useReactFlow,
  type Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useState } from "react";

import { KE_DATA } from "../data.gen";
import { ghostStyles } from "../lib/blastRadius";
import { dependencyRings } from "../lib/deps";
import { makeFlowEdges } from "../lib/flowModel";
import { layoutGraph, resetLayoutGraph } from "../lib/layout";
import { useApp } from "../store";
import type { KEEdge, KENode } from "../types";
import { nodeTypes } from "./nodes";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);
const RING_COLOR = ["#ef4444", "#f97316", "#eab308"];
const KE_NODES = KE_DATA.nodes as KENode[];
const KE_EDGES = KE_DATA.edges as KEEdge[];

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

function prefersReducedMotion(): boolean {
  return typeof window !== "undefined"
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export default function Canvas() {
  const { selected, setSelected, view, hiddenKinds, blastOn, hoverEq } = useApp();
  const [attempt, setAttempt] = useState(0);
  const [layout, setLayout] = useState<LayoutState>(
    KE_NODES.length === 0 ? { phase: "empty" } : { phase: "loading" },
  );
  const flow = useReactFlow();

  useEffect(() => {
    if (KE_NODES.length === 0) {
      setLayout({ phase: "empty" });
      return;
    }

    let cancelled = false;
    setLayout({ phase: "loading" });
    void layoutGraph(KE_NODES, KE_EDGES)
      .then((positions) => {
        if (!cancelled) setLayout({ phase: "ready", positions });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLayout({ phase: "error", diagnostic: diagnosticFor(error) });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [attempt]);

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

  const nodes = useMemo<Node[]>(() => {
    if (layout.phase !== "ready") return [];

    return KE_NODES
      .filter((node) => view !== "concepts" || !CODE_KINDS.has(node.kind))
      .filter((node) => view !== "code" || CODE_KINDS.has(node.kind))
      .flatMap<Node>((node) => {
        const position = layout.positions.get(node.id);
        if (!position) return [];

        const ghostStyle = blastOn && selected ? ghost.get(node.id) : undefined;
        const ringColor = ghostStyle && ghostStyle.ring >= 0
          ? RING_COLOR[ghostStyle.ring]
          : undefined;
        return [{
          id: node.id,
          type: CODE_KINDS.has(node.kind) ? "code" : "concept",
          position,
          width: 180,
          height: 64,
          data: { label: node.label, level: node.level },
          selected: node.id === selected,
          focusable: false,
          draggable: false,
          connectable: false,
          style: {
            opacity: ghostStyle?.opacity ?? 1,
            outline: equationHits.has(node.id)
              ? "3px solid #4a7ebb"
              : ringColor
                ? `3px solid ${ringColor}`
                : undefined,
            outlineOffset: 3,
            borderRadius: 8,
          },
        } satisfies Node];
      });
  }, [blastOn, equationHits, ghost, layout, selected, view]);

  const shownIds = useMemo(() => new Set(nodes.map((node) => node.id)), [nodes]);
  const edges = useMemo(
    () => makeFlowEdges(KE_EDGES, hiddenKinds, shownIds),
    [hiddenKinds, shownIds],
  );

  useEffect(() => {
    if (layout.phase !== "ready" || nodes.length === 0) return;
    const frame = window.requestAnimationFrame(() => {
      void flow.fitView({ padding: 0.16 });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [flow, layout, nodes.length]);

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
          if (ready) setSelected(node.id);
        }}
        onPaneClick={() => setSelected(null)}
        selectionKeyCode={null}
        selectionOnDrag={false}
        selectNodesOnDrag={false}
      >
        <Background color="#1e293b" gap={24} />
        <Controls
          aria-label="Graph viewport controls"
          position="top-right"
          showInteractive={false}
        />
      </ReactFlow>

      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {statusMessage}
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

export function useCenterOn() {
  const flow = useReactFlow();

  return (id: string) => {
    const node = flow.getNode(id);
    if (!node) return;
    void flow.setCenter(node.position.x + 90, node.position.y + 32, {
      zoom: 1.2,
      duration: prefersReducedMotion() ? 0 : 600,
    });
  };
}
