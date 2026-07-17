import { describe, expect, it } from "vitest";

import { buildChapters, readingTimeMinutes } from "./article";
import type { LearnStep } from "./learnPath";
import type { KENode } from "../types";

const nodes: KENode[] = [
  { id: "alpha", kind: "concept", label: "Alpha" },
  { id: "beta", kind: "concept", label: "Beta" },
  { id: "gamma", kind: "concept", label: "Gamma" },
];

const steps: LearnStep[] = [
  { nodeId: "alpha", title: "Alpha idea", blurb: "" },
  { nodeId: "beta", title: "Beta idea", blurb: "" },
  { nodeId: "gamma", title: "Gamma idea", blurb: "" },
];

const alphaPage = [
  "# Alpha",
  "",
  "## TL;DR {#tldr}",
  "",
  "short claim",
  "",
  "## The Math {#the-math}",
  "",
  "some math",
].join("\n");

describe("buildChapters", () => {
  it("returns one chapter per step with a page, tiers in canonical order", () => {
    const chapters = buildChapters(steps, nodes, { alpha: alphaPage });
    expect(chapters).toHaveLength(1);
    expect(chapters[0].nodeId).toBe("alpha");
    expect(chapters[0].title).toBe("Alpha idea");
    expect(chapters[0].tiers.map((tier) => tier.id)).toEqual(["tldr", "the-math"]);
    expect(chapters[0].tiers[0].label).toBe("TL;DR");
    expect(chapters[0].tiers[0].content).toContain("short claim");
  });

  it("skips steps whose page is missing", () => {
    expect(buildChapters(steps, nodes, {})).toEqual([]);
  });
});

describe("readingTimeMinutes", () => {
  it("estimates ceil(words/220) with a floor of 1", () => {
    const chapters = buildChapters(steps, nodes, { alpha: alphaPage });
    expect(readingTimeMinutes(chapters)).toBe(1);
    const many = "word ".repeat(500);
    const bigPage = `## TL;DR {#tldr}\n\n${many}`;
    const big = buildChapters(steps, nodes, { alpha: bigPage });
    expect(readingTimeMinutes(big)).toBe(3);
  });
});
