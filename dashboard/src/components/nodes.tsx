import {
  Handle,
  Position,
  useReactFlow,
  type Node,
  type NodeProps,
  type ReactFlowInstance,
} from "@xyflow/react";

import { KE_DATA } from "../data.gen";
import { nodeAccessibleName } from "../lib/nodePresentation";
import { useApp } from "../store";

type CardData = {
  label: string;
  level?: number;
};

type ClusterData = {
  label: string;
  count: number;
  onActivate?: () => void;
};

type CardNode = Node<CardData, "concept" | "code">;
type ClusterNode = Node<ClusterData, "cluster">;

const centrality = KE_DATA.centrality as Record<string, number>;
const centralityValues = Object.values(centrality).sort((a, b) => a - b);
const p90 = centralityValues[Math.floor(centralityValues.length * 0.9)] ?? Infinity;
const hotspotRank = new Map(
  (KE_DATA.hotspots as { id: string }[]).map((hotspot, index) => [
    hotspot.id,
    index + 1,
  ]),
);

function focusNode(
  flow: ReactFlowInstance,
  positionAbsoluteX: number,
  positionAbsoluteY: number,
): void {
  const reducedMotion = typeof window !== "undefined"
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  void flow.setCenter(positionAbsoluteX + 90, positionAbsoluteY + 32, {
    zoom: flow.getZoom(),
    duration: reducedMotion ? 0 : 600,
  });
}

function Card({
  id,
  data,
  selected,
  className,
  positionAbsoluteX,
  positionAbsoluteY,
}: {
  id: string;
  data: CardData;
  selected: boolean;
  className: string;
  positionAbsoluteX: number;
  positionAbsoluteY: number;
}) {
  const setSelected = useApp((state) => state.setSelected);
  const flow = useReactFlow();
  const bridge = centrality[id] >= p90 && centralityValues.length > 1;
  const hot = hotspotRank.get(id);

  return (
    <button
      aria-label={nodeAccessibleName({
        label: data.label,
        level: data.level,
        bridge,
        hotspotRank: hot,
      })}
      aria-pressed={selected}
      className={`node-card ${className}`}
      onClick={() => setSelected(id)}
      onFocus={() => focusNode(flow, positionAbsoluteX, positionAbsoluteY)}
      title={data.label}
      type="button"
    >
      <Handle type="target" position={Position.Top} />
      <span className="node-label">{data.label}</span>
      <span className="node-badges">
        {data.level !== undefined && <span className="badge">L{data.level}</span>}
        {bridge && <span className="badge badge-bridge">bridge</span>}
        {hot && <span className="badge badge-hot">hotspot #{hot}</span>}
      </span>
      <Handle type="source" position={Position.Bottom} />
    </button>
  );
}

function ConceptNode(props: NodeProps<CardNode>) {
  return (
    <Card
      id={props.id}
      data={props.data}
      selected={props.selected}
      className="node-concept"
      positionAbsoluteX={props.positionAbsoluteX}
      positionAbsoluteY={props.positionAbsoluteY}
    />
  );
}

function CodeNode(props: NodeProps<CardNode>) {
  return (
    <Card
      id={props.id}
      data={props.data}
      selected={props.selected}
      className="node-code"
      positionAbsoluteX={props.positionAbsoluteX}
      positionAbsoluteY={props.positionAbsoluteY}
    />
  );
}

function ClusterNodeCard(props: NodeProps<ClusterNode>) {
  const flow = useReactFlow();

  return (
    <button
      aria-label={`${props.data.label}, cluster, ${props.data.count} nodes`}
      className="node-card node-cluster"
      disabled={!props.data.onActivate}
      onClick={props.data.onActivate}
      onFocus={() => focusNode(
        flow,
        props.positionAbsoluteX,
        props.positionAbsoluteY,
      )}
      title={props.data.label}
      type="button"
    >
      <Handle type="target" position={Position.Top} />
      <span className="node-label">{props.data.label}</span>
      <span className="node-badges">
        <span className="badge">{props.data.count} nodes</span>
      </span>
      <Handle type="source" position={Position.Bottom} />
    </button>
  );
}

export const nodeTypes = {
  concept: ConceptNode,
  code: CodeNode,
  cluster: ClusterNodeCard,
};
