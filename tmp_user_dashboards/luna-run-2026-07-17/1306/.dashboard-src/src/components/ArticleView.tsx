import { useEffect, useMemo, useRef } from "react";

import { KE_DATA } from "../data.gen";
import { buildChapters, readingTimeMinutes, type ChapterTier } from "../lib/article";
import { parseContent, type ContentSegment } from "../lib/contentBlocks";
import { useApp } from "../store";
import type { KENode } from "../types";
import BlockRenderer from "./blocks/BlockRenderer";
import MathReveal from "./blocks/MathReveal";
import { RichMarkdown } from "./Drawer";
import { LEARN_STEPS, switchToExplore } from "./LearnPanel";
import ProgressRail from "./ProgressRail";

const NODES = KE_DATA.nodes as KENode[];
const PAGES = KE_DATA.pages as Record<string, string>;
const GLOSSARY = KE_DATA.glossary as Record<string, Record<string, string>>;
const SOURCE = (KE_DATA.meta as { source?: string }).source ?? "this paper";

export const CHAPTERS = buildChapters(LEARN_STEPS, NODES, PAGES);
const NOTATION = PAGES["_notation"];
const CLOSING = PAGES["_closing"];

function segmentKey(segment: ContentSegment, index: number) {
  return `${segment.type}-${index}`;
}

function TierSection({
  expandAll,
  glossary,
  nodeId,
  tier,
}: {
  expandAll: boolean;
  glossary: Record<string, string>;
  nodeId: string;
  tier: ChapterTier;
}) {
  const segments = useMemo(() => parseContent(tier.content), [tier.content]);
  const renderMarkdown = (markdown: string) => (
    <RichMarkdown glossary={glossary} markdown={markdown} />
  );

  return (
    <section
      aria-label={`${tier.label}`}
      className={`article-tier article-tier-${tier.id}`}
      id={`${nodeId}--${tier.id}`}
    >
      <h3 className="article-tier-heading">{tier.label}</h3>
      {segments.map((segment, index) => {
        const rendered = (
          <BlockRenderer
            expandAll={expandAll}
            key={segmentKey(segment, index)}
            renderMarkdown={renderMarkdown}
            segment={segment}
          />
        );
        if (
          tier.id === "the-math"
          && segment.type === "derivation"
          && segment.shape
        ) {
          return (
            <MathReveal
              expandAll={expandAll}
              key={segmentKey(segment, index)}
              shape={segment.shape}
            >
              {rendered}
            </MathReveal>
          );
        }
        return rendered;
      })}
    </section>
  );
}

export default function ArticleView() {
  const expandAllMath = useApp((state) => state.expandAllMath);
  const setLearnIdx = useApp((state) => state.setLearnIdx);
  const markStepComplete = useApp((state) => state.markStepComplete);
  const articleRef = useRef<HTMLElement>(null);
  const minutes = readingTimeMinutes(CHAPTERS);

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return;
    const root = articleRef.current;
    if (!root) return;
    const sections = Array.from(root.querySelectorAll<HTMLElement>("[data-chapter-idx]"));
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const index = Number(
            (entry.target as HTMLElement).dataset.chapterIdx,
          );
          if (Number.isNaN(index)) continue;
          setLearnIdx(index);
          markStepComplete(CHAPTERS[index].nodeId);
        }
      },
      { rootMargin: "-20% 0px -70% 0px" },
    );
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, [markStepComplete, setLearnIdx]);

  const jumpTo = (anchor: string) => {
    document.getElementById(anchor)?.scrollIntoView({ block: "start" });
  };

  return (
    <div className="article-shell">
      <ProgressRail
        chapters={CHAPTERS}
        hasClosing={Boolean(CLOSING)}
        hasNotation={Boolean(NOTATION)}
        onJump={jumpTo}
      />
      <div className="article-scroll">
        <article className="article" ref={articleRef}>
          <header className="article-opening">
            <p className="article-eyebrow">Guided reading</p>
            <h1 className="article-title">{SOURCE}</h1>
            <p className="article-meta">
              {CHAPTERS.length} ideas · about {minutes} min
              {NOTATION && (
                <>
                  {" · "}
                  <button
                    className="article-inline-link"
                    onClick={() => jumpTo("notation")}
                    type="button"
                  >
                    notation guide
                  </button>
                </>
              )}
            </p>
          </header>

          {CHAPTERS.map((chapter, index) => (
            <section
              className="chapter"
              data-chapter-idx={index}
              id={chapter.nodeId}
              key={chapter.nodeId}
            >
              <h2 className="chapter-title">
                <span aria-hidden="true" className="chapter-number">{index + 1}</span>
                {chapter.title}
              </h2>
              {chapter.tiers.map((tier) => (
                <TierSection
                  expandAll={expandAllMath}
                  glossary={GLOSSARY[chapter.nodeId] ?? {}}
                  key={tier.id}
                  nodeId={chapter.nodeId}
                  tier={tier}
                />
              ))}
            </section>
          ))}

          {NOTATION && (
            <section className="chapter article-notation" id="notation">
              <h2 className="chapter-title">Notation guide</h2>
              <RichMarkdown glossary={{}} markdown={NOTATION} />
            </section>
          )}

          {CLOSING && (
            <section className="chapter article-closing" id="closing">
              <RichMarkdown glossary={{}} markdown={CLOSING} />
            </section>
          )}

          <aside className="article-handoff">
            <p>
              Want the full picture? Every concept in this paper — including the
              ones this path skipped — lives on the interactive map.
            </p>
            <button
              className="article-handoff-button"
              onClick={switchToExplore}
              type="button"
            >
              Open the full concept map ({NODES.length} concepts) →
            </button>
          </aside>
        </article>
      </div>
    </div>
  );
}
