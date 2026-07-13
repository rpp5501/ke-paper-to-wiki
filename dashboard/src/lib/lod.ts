export function visibleAtZoom(
  zoom: number,
  threshold: number,
  clusters: { id: string; nodeIds: string[] }[],
  nodeIds: string[],
): { showClusters: boolean; hiddenNodes: Set<string> } {
  const showClusters = zoom < threshold && clusters.length > 0;
  if (!showClusters) return { showClusters, hiddenNodes: new Set() };
  const clustered = new Set(clusters.flatMap((cluster) => cluster.nodeIds));
  return {
    showClusters,
    hiddenNodes: new Set(nodeIds.filter((id) => clustered.has(id))),
  };
}
