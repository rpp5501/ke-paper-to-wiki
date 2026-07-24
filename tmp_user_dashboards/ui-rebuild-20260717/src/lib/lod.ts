export function visibleAtZoom(
  zoom: number,
  threshold: number,
  clusters: { id: string; nodeIds: string[] }[],
  nodeIds: string[],
  forceClusters = false,
): { showClusters: boolean; hiddenNodes: Set<string> } {
  const showClusters = (forceClusters || zoom < threshold) && clusters.length > 0;
  if (!showClusters) return { showClusters, hiddenNodes: new Set() };
  const clustered = new Set(clusters.flatMap((cluster) => cluster.nodeIds));
  return {
    showClusters,
    hiddenNodes: new Set(nodeIds.filter((id) => clustered.has(id))),
  };
}

type Position = { x: number; y: number };
type Cluster = { id: string; label: string; nodeIds: string[] };

export type ClusterCard = {
  id: string;
  label: string;
  count: number;
  position: Position;
};

export function clusterCards(
  showClusters: boolean,
  clusters: Cluster[],
  positions: Map<string, Position>,
): ClusterCard[] {
  if (!showClusters) return [];
  return clusters.map((cluster, index) => ({
    id: `cluster:${cluster.id}`,
    label: cluster.label,
    count: cluster.nodeIds.length,
    position: cluster.nodeIds
      .map((nodeId) => positions.get(nodeId))
      .find((position): position is Position => position !== undefined)
      ?? { x: index * 220, y: 0 },
  }));
}

export function clusterZoomDuration(reducedMotion: boolean) {
  return reducedMotion ? 0 : 500;
}

export function clusterDetailView(kind: "concept" | "code" | "bridged") {
  if (kind === "concept") return "concepts" as const;
  return kind;
}

export function clusterActivation(
  kind: "concept" | "code" | "bridged",
  reducedMotion: boolean,
) {
  return {
    duration: clusterZoomDuration(reducedMotion),
    view: clusterDetailView(kind),
    zoom: 0.9,
  };
}

export function selectionForCanvasNode(nodeId: string) {
  return nodeId.startsWith("cluster:") ? null : nodeId;
}

export type HiddenFocusTarget = {
  id: string;
  kind: "cluster" | "view";
};

export function focusTargetForHiddenNode(
  focusedNodeId: string | null,
  shownIds: Set<string>,
  visibleClusters: Cluster[],
  view: "concepts" | "clusters" | "code" | "bridged",
): HiddenFocusTarget | null {
  if (!focusedNodeId || shownIds.has(focusedNodeId)) return null;
  const cluster = visibleClusters.find((candidate) => (
    candidate.nodeIds.includes(focusedNodeId)
    && shownIds.has(`cluster:${candidate.id}`)
  ));
  return cluster
    ? { id: `cluster:${cluster.id}`, kind: "cluster" }
    : { id: `graph-view-${view}`, kind: "view" };
}
