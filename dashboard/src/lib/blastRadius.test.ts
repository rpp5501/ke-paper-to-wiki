import { describe, expect, it } from "vitest";
import { ghostStyles } from "./blastRadius";

describe("ghostStyles", () => {
  it("selected=0, ring1, ring2, others ghosted", () => {
    const rings = new Map([["x", 1], ["y", 2]]);
    const s = ghostStyles(rings, ["sel", "x", "y", "z"], "sel");
    expect(s.get("sel")).toEqual({ opacity: 1, ring: 0 });
    expect(s.get("x")!.ring).toBe(1);
    expect(s.get("y")!.ring).toBe(2);
    expect(s.get("z")!.opacity).toBeLessThanOrEqual(0.15);
  });
});
