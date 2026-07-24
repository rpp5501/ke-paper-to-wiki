import type { KENode } from "../types";
import type { LearnStep } from "./learnPath";
import { pageMarkdownFor } from "./learnPath";
import { splitTiers, type ExplanationTier } from "./mathHtml";

export const TIER_SEQUENCE: readonly ExplanationTier[] = [
  "tldr",
  "intuition",
  "mechanics",
  "the-math",
  "go-deeper",
];

export const TIER_LABELS: Record<ExplanationTier, string> = {
  tldr: "TL;DR",
  intuition: "Intuition",
  mechanics: "Mechanics",
  "the-math": "The Math",
  "go-deeper": "Go Deeper",
};

export type ChapterTier = { id: ExplanationTier; label: string; content: string };
export type Chapter = { nodeId: string; title: string; tiers: ChapterTier[] };

/** One chapter per reading-path step that actually has a page; tiers in
 *  canonical order, missing tiers skipped. */
export function buildChapters(
  steps: LearnStep[],
  nodes: KENode[],
  pages: Record<string, string>,
): Chapter[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return steps.flatMap((step) => {
    const node = byId.get(step.nodeId);
    const markdown = node ? pageMarkdownFor(node, pages) : pages[step.nodeId];
    if (!markdown) return [];
    const tiers = splitTiers(markdown);
    const ordered = TIER_SEQUENCE.flatMap((tier) => {
      const content = tiers[tier];
      return content ? [{ id: tier, label: TIER_LABELS[tier], content }] : [];
    });
    if (ordered.length === 0) return [];
    return [{ nodeId: step.nodeId, title: step.title, tiers: ordered }];
  });
}

/** Estimated minutes at ~220 words/min over the chapters' pages. */
export function readingTimeMinutes(chapters: Chapter[]): number {
  const words = chapters
    .flatMap((chapter) => chapter.tiers)
    .map((tier) => tier.content.split(/\s+/).filter(Boolean).length)
    .reduce((total, count) => total + count, 0);
  return Math.max(1, Math.ceil(words / 220));
}
