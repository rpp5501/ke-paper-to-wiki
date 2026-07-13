import ELK, { type ELK as ELKInstance } from "elkjs/lib/elk-api";
import elkWorkerUrl from "elkjs/lib/elk-worker.min.js?url";
import type { KEEdge, KENode } from "../types";

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

function layoutKey(nodes: KENode[], edges: KEEdge[]): string {
  return JSON.stringify({
    nodes: nodes.map((node) => node.id),
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

export function layoutGraph(
  nodes: KENode[],
  edges: KEEdge[],
): Promise<Map<string, { x: number; y: number }>> {
  const key = layoutKey(nodes, edges);
  const cached = layoutCache.get(key);
  if (cached) return cached;

  const request = getElk()
    .then((elk) => withTimeout(elk.layout({
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
