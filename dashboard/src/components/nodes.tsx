import {
  Handle,
  Position,
  useReactFlow,
  type Node,
  type NodeProps,
  type ReactFlowInstance,
} from "@xyflow/react";

import { KE_DATA } from "../data.gen";
import { nodeCardSize } from "../lib/nodeDimensions";
import { recordFor } from "../lib/mastery";
import { levelBadgeLabel, nodeAccessibleName } from "../lib/nodePresentation";
import { useApp } from "../store";

type CardData = {
  label: string;
  level?: number;
  /** Descendants folded into this node, when its branch is collapsed. */
  hidden?: number;
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
  width: number,
  height: number,
): void {
  const reducedMotion = typeof window !== "undefined"
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  void flow.setCenter(positionAbsoluteX + width / 2, positionAbsoluteY + height / 2, {
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
  const mastery = useApp((state) => recordFor(state.mastery, id).level);
  const flow = useReactFlow();
  const bridge = centrality[id] >= p90 && centralityValues.length > 1;
  const hot = hotspotRank.get(id);
  const levelBadge = levelBadgeLabel(data.level);
  const size = nodeCardSize(data.label);

  return (
    <button
      aria-label={nodeAccessibleName({
        label: data.label,
        level: data.level,
        bridge,
        hotspotRank: hot,
        mastery,
        hidden: data.hidden,
      })}
      aria-pressed={selected}
      className={`node-card ${className}${mastery === "unseen" ? "" : ` is-${mastery}`}`}
      data-node-id={id}
      onClick={() => setSelected(id)}
      onFocus={() => focusNode(
        flow,
        positionAbsoluteX,
        positionAbsoluteY,
        size.width,
        size.height,
      )}
      title={data.label}
      type="button"
    >
      <Handle type="target" position={Position.Top} />
      <span className="node-label">{data.label}</span>
      <span className="node-badges">
        {levelBadge && <span className="badge">{levelBadge}</span>}
        {bridge && <span className="badge badge-bridge">bridge</span>}
        {hot && <span className="badge badge-hot">hotspot #{hot}</span>}
        {mastery === "mastered" && (
          <span className="badge badge-mastered">mastered</span>
        )}
        {data.hidden !== undefined && data.hidden > 0 && (
          <span className="badge badge-collapsed">+{data.hidden}</span>
        )}
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
  const size = nodeCardSize(props.data.label);

  return (
    <button
      aria-label={`${props.data.label}, cluster, ${props.data.count} nodes`}
      className="node-card node-cluster"
      data-node-id={props.id}
      disabled={!props.data.onActivate}
      onClick={props.data.onActivate}
      onFocus={() => focusNode(
        flow,
        props.positionAbsoluteX,
        props.positionAbsoluteY,
        size.width,
        size.height,
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
