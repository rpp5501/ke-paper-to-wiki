import { describe, expect, it } from "vitest";

import {
  buildChapters,
  buildLearningChapters,
  readingTimeMinutes,
} from "./article";
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

describe("buildLearningChapters", () => {
  it("groups every authored concept under its macro chapter", () => {
    const betaPage = alphaPage.replaceAll("Alpha", "Beta").replaceAll("alpha", "beta");
    const chapters = buildLearningChapters({
      version: 1,
      reviewed: true,
      chapters: [{
        id: "why",
        title: "Why graph distance is not enough",
        question: "Why does edit distance miss causal error?",
        outcome: "Distinguish structural and interventional mistakes.",
        conceptIds: ["alpha", "beta"],
        foundationConceptIds: ["alpha"],
        advancedConceptIds: ["beta"],
        checkpointIds: ["check-why"],
        estimatedCoreMinutes: 6,
        estimatedFullMinutes: 12,
      }],
    }, nodes, { alpha: alphaPage, beta: betaPage });

    expect(chapters).toHaveLength(1);
    expect(chapters[0].nodeId).toBe("why");
    expect(chapters[0].question).toContain("edit distance");
    expect(chapters[0].sections.map((section) => section.nodeId)).toEqual([
      "alpha", "beta",
    ]);
    expect(chapters[0].sections[0].depth).toBe("foundation");
    expect(chapters[0].sections[1].depth).toBe("advanced");
    expect(chapters[0].checkpointIds).toEqual(["check-why"]);
  });
});

describe("readingTimeMinutes", () => {
  it("uses reviewed manifest core estimates for the guided spine", () => {
    const chapters = buildLearningChapters({
      version: 1,
      reviewed: true,
      chapters: [{
        id: "why",
        title: "Why graph distance is not enough",
        question: "Why does edit distance miss causal error?",
        outcome: "Distinguish structural and interventional mistakes.",
        conceptIds: ["alpha"],
        foundationConceptIds: [],
        advancedConceptIds: [],
        checkpointIds: [],
        estimatedCoreMinutes: 6,
        estimatedFullMinutes: 12,
      }],
    }, nodes, { alpha: `## TL;DR {#tldr}\n\n${"word ".repeat(500)}` });

    expect(readingTimeMinutes(chapters)).toBe(6);
  });

  it("estimates ceil(words/220) with a floor of 1", () => {
    const chapters = buildChapters(steps, nodes, { alpha: alphaPage });
    expect(readingTimeMinutes(chapters)).toBe(1);
    const many = "word ".repeat(500);
    const bigPage = `## TL;DR {#tldr}\n\n${many}`;
    const big = buildChapters(steps, nodes, { alpha: bigPage });
    expect(readingTimeMinutes(big)).toBe(3);
  });
});
