import type { KENode, LearningPath } from "../types";
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
export type ChapterSection = {
  nodeId: string;
  title: string;
  depth: "foundation" | "core" | "advanced";
  tiers: ChapterTier[];
};
export type Chapter = {
  nodeId: string;
  title: string;
  tiers: ChapterTier[];
  sections: ChapterSection[];
  question?: string;
  outcome?: string;
  checkpointIds: string[];
  estimatedCoreMinutes?: number;
  estimatedFullMinutes?: number;
};

function tiersFor(markdown: string): ChapterTier[] {
  const tiers = splitTiers(markdown);
  return TIER_SEQUENCE.flatMap((tier) => {
    const content = tiers[tier];
    return content ? [{ id: tier, label: TIER_LABELS[tier], content }] : [];
  });
}

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
    const ordered = tiersFor(markdown);
    if (ordered.length === 0) return [];
    return [{
      nodeId: step.nodeId,
      title: step.title,
      tiers: ordered,
      sections: [{
        nodeId: step.nodeId,
        title: node?.label ?? step.title,
        depth: "core" as const,
        tiers: ordered,
      }],
      checkpointIds: [],
    }];
  });
}

export function buildLearningChapters(
  path: LearningPath,
  nodes: KENode[],
  pages: Record<string, string>,
): Chapter[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return path.chapters.flatMap((chapter) => {
    const sections = chapter.conceptIds.flatMap((nodeId) => {
      const node = byId.get(nodeId);
      const markdown = node ? pageMarkdownFor(node, pages) : pages[nodeId];
      if (!markdown) return [];
      const tiers = tiersFor(markdown);
      if (tiers.length === 0) return [];
      const depth = chapter.foundationConceptIds.includes(nodeId)
        ? "foundation" as const
        : chapter.advancedConceptIds.includes(nodeId)
          ? "advanced" as const
          : "core" as const;
      return [{ nodeId, title: node?.label ?? nodeId, depth, tiers }];
    });
    if (sections.length === 0) return [];
    return [{
      nodeId: chapter.id,
      title: chapter.title,
      question: chapter.question,
      outcome: chapter.outcome,
      checkpointIds: chapter.checkpointIds,
      estimatedCoreMinutes: chapter.estimatedCoreMinutes,
      estimatedFullMinutes: chapter.estimatedFullMinutes,
      sections,
      tiers: sections.flatMap((section) => section.tiers),
    }];
  });
}

/** Estimated minutes at ~220 words/min over the chapters' pages. */
export function readingTimeMinutes(chapters: Chapter[]): number {
  const manifestEstimate = chapters.reduce<number | undefined>(
    (total, chapter) => chapter.estimatedCoreMinutes == null || total == null
      ? undefined
      : total + chapter.estimatedCoreMinutes,
    0,
  );
  if (manifestEstimate != null) return Math.max(1, manifestEstimate);

  const words = chapters
    .flatMap((chapter) => chapter.sections.flatMap((section) => section.tiers))
    .map((tier) => tier.content.split(/\s+/).filter(Boolean).length)
    .reduce((total, count) => total + count, 0);
  return Math.max(1, Math.ceil(words / 220));
}
