import { describe, expect, it } from "vitest";

describe("layoutGraph worker construction", () => {
  it("does not construct a Worker while importing the layout module", async () => {
    expect(typeof Worker).toBe("undefined");
    await expect(import("./layout")).resolves.toHaveProperty("layoutGraph");
  });

  it("rejects asynchronously and retries after Worker construction fails", async () => {
    const { layoutGraph } = await import("./layout");

    const first = layoutGraph([], []);
    expect(first).toBeInstanceOf(Promise);
    const firstError = await first.catch((error: unknown) => error);
    expect(firstError).toBeInstanceOf(ReferenceError);

    const secondError = await layoutGraph([], [])
      .catch((error: unknown) => error);
    expect(secondError).toBeInstanceOf(ReferenceError);
    expect(secondError).not.toBe(firstError);
  });
});
