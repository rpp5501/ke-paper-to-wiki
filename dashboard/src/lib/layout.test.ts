import { beforeEach, describe, expect, it, vi } from "vitest";

const workerHarness = vi.hoisted(() => ({
  created: 0,
  layoutCalls: 0,
  terminated: 0,
  behaviors: [] as Array<() => Promise<{
    children?: Array<{ id: string; x?: number; y?: number }>;
  }>>,
}));

vi.mock("elkjs/lib/elk-api", () => ({
  default: class FakeElk {
    constructor() {
      workerHarness.created += 1;
    }

    layout() {
      workerHarness.layoutCalls += 1;
      const behavior = workerHarness.behaviors.shift();
      return behavior
        ? behavior()
        : Promise.resolve({ children: [{ id: "node", x: 12, y: 16 }] });
    }

    terminateWorker() {
      workerHarness.terminated += 1;
    }
  },
}));

const nodes = [{ id: "node", kind: "concept", label: "Node" }];
const edges: [] = [];

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

beforeEach(() => {
  vi.resetModules();
  vi.useRealTimers();
  workerHarness.created = 0;
  workerHarness.layoutCalls = 0;
  workerHarness.terminated = 0;
  workerHarness.behaviors = [];
});

describe("layoutGraph worker lifecycle", () => {
  it("does not construct a worker while importing the layout module", async () => {
    await expect(import("./layout")).resolves.toHaveProperty("layoutGraph");
    expect(workerHarness.created).toBe(0);
  });

  it("deduplicates the same in-flight logical layout attempt", async () => {
    const pending = deferred<{
      children: Array<{ id: string; x: number; y: number }>;
    }>();
    workerHarness.behaviors.push(() => pending.promise);
    const { layoutGraph } = await import("./layout");

    const first = layoutGraph(nodes, edges);
    const second = layoutGraph(nodes, edges);

    expect(second).toBe(first);
    await vi.waitFor(() => expect(workerHarness.layoutCalls).toBe(1));

    pending.resolve({ children: [{ id: "node", x: 20, y: 24 }] });
    await expect(first).resolves.toEqual(new Map([
      ["node", { x: 20, y: 24 }],
    ]));
  });

  it("terminates the worker and clears cached layout state after rejection", async () => {
    workerHarness.behaviors.push(
      () => Promise.reject(new Error("worker failed")),
      () => Promise.resolve({ children: [{ id: "node", x: 28, y: 32 }] }),
    );
    const { layoutGraph } = await import("./layout");

    await expect(layoutGraph(nodes, edges)).rejects.toThrow("worker failed");
    expect(workerHarness.terminated).toBe(1);

    await expect(layoutGraph(nodes, edges)).resolves.toEqual(new Map([
      ["node", { x: 28, y: 32 }],
    ]));
    expect(workerHarness.created).toBe(2);
    expect(workerHarness.layoutCalls).toBe(2);
  });

  it("times out a stalled layout and terminates its worker", async () => {
    vi.useFakeTimers();
    const stalled = deferred<{
      children: Array<{ id: string; x: number; y: number }>;
    }>();
    workerHarness.behaviors.push(() => stalled.promise);
    const { layoutGraph } = await import("./layout");

    const request = layoutGraph(nodes, edges);
    const outcome = request.catch((error: unknown) => error);
    await vi.advanceTimersByTimeAsync(0);

    expect(workerHarness.layoutCalls).toBe(1);
    expect(vi.getTimerCount()).toBe(1);
    await vi.advanceTimersByTimeAsync(30_000);
    const error = await outcome;
    expect(error).toBeInstanceOf(Error);
    expect((error as Error).message).toBe("Graph layout timed out after 30000ms.");
    expect(workerHarness.terminated).toBe(1);
  });

  it("explicit reset terminates cached state so Retry uses a fresh worker", async () => {
    workerHarness.behaviors.push(
      () => Promise.resolve({ children: [{ id: "node", x: 12, y: 16 }] }),
      () => Promise.resolve({ children: [{ id: "node", x: 36, y: 40 }] }),
    );
    const layoutModule = await import("./layout") as typeof import("./layout") & {
      resetLayoutGraph: () => void;
    };

    await expect(layoutModule.layoutGraph(nodes, edges)).resolves.toEqual(new Map([
      ["node", { x: 12, y: 16 }],
    ]));
    layoutModule.resetLayoutGraph();
    expect(workerHarness.terminated).toBe(1);

    await expect(layoutModule.layoutGraph(nodes, edges)).resolves.toEqual(new Map([
      ["node", { x: 36, y: 40 }],
    ]));
    expect(workerHarness.created).toBe(2);
    expect(workerHarness.layoutCalls).toBe(2);
  });

  it("treats incomplete worker output as a reset-worthy layout rejection", async () => {
    workerHarness.behaviors.push(() => Promise.resolve({ children: [] }));
    const { layoutGraph } = await import("./layout");

    await expect(layoutGraph(nodes, edges)).rejects.toThrow(
      "Worker returned 0 of 1 node positions.",
    );
    expect(workerHarness.terminated).toBe(1);
  });
});
