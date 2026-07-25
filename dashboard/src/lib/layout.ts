import ELK, { type ELK as ELKInstance } from "elkjs/lib/elk-api";
import elkWorkerUrl from "elkjs/lib/elk-worker.min.js?url";
import type { KEEdge, KENode } from "../types";
import { nodeCardSize } from "./nodeDimensions";

// Vite emits the worker as a local build asset. localhost supplies the normal
// origin required to start it; all topology calculation stays off-thread.
const LAYOUT_TIMEOUT_MS = 30_000;
let elkPromise: Promise<ELKInstance> | undefined;
let elkInstance: ELKInstance | undefined;
const layoutCache = new Map<
  string,
  Promise<Map<string, { x: number; y: number }>>
>();

function getElk(): Promise<ELKInstance> {
  if (!elkPromise) {
    elkPromise = Promise.resolve()
      .then(() => {
        elkInstance = new ELK({ workerUrl: elkWorkerUrl });
        return elkInstance;
      })
      .catch((error: unknown) => {
        elkPromise = undefined;
        throw error;
      });
  }
  return elkPromise;
}

function resetLayoutState(): void {
  const instance = elkInstance;
  layoutCache.clear();
  elkInstance = undefined;
  elkPromise = undefined;
  instance?.terminateWorker();
}

export function resetLayoutGraph(): void {
  resetLayoutState();
}

// Sizes go into the key, so the R16.B2 fan-out scaling re-layouts rather than
// reusing a cache entry laid out for different node dimensions.
function layoutKey(
  nodes: KENode[],
  edges: KEEdge[],
  scales?: Map<string, number>,
): string {
  return JSON.stringify({
    nodes: nodes.map((node) => {
      const size = nodeCardSize(node.label, scales?.get(node.id) ?? 1);
      return [node.id, size.width, size.height];
    }),
    edges: edges.map((edge) => [edge.src, edge.dst]),
  });
}

function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = globalThis.setTimeout(() => {
      reject(new Error(`Graph layout timed out after ${timeoutMs}ms.`));
    }, timeoutMs);

    promise.then(
      (value) => {
        globalThis.clearTimeout(timer);
        resolve(value);
      },
      (error: unknown) => {
        globalThis.clearTimeout(timer);
        reject(error);
      },
    );
  });
}

export type LayoutAlgorithm = "layered" | "radial";

// R15.10 mind-map view: radial arranges the part-of hierarchy around the
// root like a mind map; layered stays the default reading-order layout.
const LAYOUT_OPTIONS: Record<LayoutAlgorithm, Record<string, string>> = {
  layered: {
    "elk.algorithm": "layered",
    "elk.direction": "DOWN",
    "elk.spacing.nodeNode": "40",
  },
  radial: {
    "elk.algorithm": "radial",
    "elk.spacing.nodeNode": "60",
  },
};

export function layoutGraph(
  nodes: KENode[],
  edges: KEEdge[],
  algorithm: LayoutAlgorithm = "layered",
  scales?: Map<string, number>,
): Promise<Map<string, { x: number; y: number }>> {
  const key = `${algorithm}|${layoutKey(nodes, edges, scales)}`;
  const cached = layoutCache.get(key);
  if (cached) return cached;

  const request = getElk()
    .then((elk) => withTimeout(elk.layout({
      id: "root",
      layoutOptions: LAYOUT_OPTIONS[algorithm],
      children: nodes.map((node) => ({
        id: node.id,
        ...nodeCardSize(node.label, scales?.get(node.id) ?? 1),
      })),
      edges: edges.map((edge, index) => ({
        id: `e${index}`,
        sources: [edge.src],
        targets: [edge.dst],
      })),
    }), LAYOUT_TIMEOUT_MS))
    .then((result) => {
      const positions = new Map(
        (result.children ?? []).map((child) => [
          child.id,
          { x: child.x ?? 0, y: child.y ?? 0 },
        ]),
      );
      if (positions.size !== nodes.length) {
        throw new Error(
          `Worker returned ${positions.size} of ${nodes.length} node positions.`,
        );
      }
      return positions;
    })
    .catch((error: unknown) => {
      resetLayoutState();
      throw error;
    });
  layoutCache.set(key, request);
  return request;
}
