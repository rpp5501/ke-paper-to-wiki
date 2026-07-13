import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import { KE_DATA } from "../data.gen";
import { useApp } from "../store";

type CardData = {
  label: string;
  level?: number;
};

type ClusterData = {
  label: string;
  count: number;
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

function Card({
  id,
  data,
  selected,
  className,
}: {
  id: string;
  data: CardData;
  selected: boolean;
  className: string;
}) {
  const setSelected = useApp((state) => state.setSelected);
  const bridge = centrality[id] >= p90 && centralityValues.length > 1;
  const hot = hotspotRank.get(id);

  return (
    <button
      aria-label={data.label}
      aria-pressed={selected}
      className={`node-card ${className}`}
      onClick={() => setSelected(id)}
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
    />
  );
}

function ClusterNodeCard(props: NodeProps<ClusterNode>) {
  const setSelected = useApp((state) => state.setSelected);

  return (
    <button
      aria-label={`${props.data.label}, ${props.data.count} nodes`}
      aria-pressed={props.selected}
      className="node-card node-cluster"
      onClick={() => setSelected(props.id)}
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
