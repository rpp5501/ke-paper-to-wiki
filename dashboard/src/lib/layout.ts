import ELK from "elkjs/lib/elk-api";
import elkWorkerUrl from "elkjs/lib/elk-worker.min.js?url";
import type { KEEdge, KENode } from "../types";

// Vite emits the worker as a local build asset. localhost supplies the normal
// origin required to start it; all topology calculation stays off-thread.
const elk = new ELK({ workerUrl: elkWorkerUrl });

export async function layoutGraph(
  nodes: KENode[],
  edges: KEEdge[],
): Promise<Map<string, { x: number; y: number }>> {
  const result = await elk.layout({
    id: "root",
    layoutOptions: {
      "elk.algorithm": "layered",
      "elk.direction": "DOWN",
      "elk.spacing.nodeNode": "40",
    },
    children: nodes.map((node) => ({ id: node.id, width: 180, height: 64 })),
    edges: edges.map((edge, index) => ({
      id: `e${index}`,
      sources: [edge.src],
      targets: [edge.dst],
    })),
  });
  return new Map(
    (result.children ?? []).map((child) => [
      child.id,
      { x: child.x ?? 0, y: child.y ?? 0 },
    ]),
  );
}
