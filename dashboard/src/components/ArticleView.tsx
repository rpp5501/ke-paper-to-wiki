import { useEffect, useMemo, useRef } from "react";

import { KE_DATA } from "../data.gen";
import {
  buildChapters,
  buildLearningChapters,
  readingTimeMinutes,
  type Chapter,
  type ChapterSection,
  type ChapterTier,
} from "../lib/article";
import { parseContent, type ContentSegment } from "../lib/contentBlocks";
import type { PanelBounds } from "../lib/panelSizing";
import { getQuiz, type QuizItem } from "../lib/quiz";
import { useApp } from "../store";
import type { KENode, LearningPath } from "../types";
import BlockRenderer from "./blocks/BlockRenderer";
import ConceptThreads, { type ConceptThreadSet } from "./ConceptThreads";
import InlineCheckpoint from "./InlineCheckpoint";
import MathReveal from "./blocks/MathReveal";
import { RichMarkdown } from "./Drawer";
import { LEARN_STEPS, switchToExplore } from "./LearnPanel";
import PanelResizer from "./PanelResizer";
import ProgressRail from "./ProgressRail";
import SelectionLookup from "./SelectionLookup";

const NODES = KE_DATA.nodes as KENode[];
const PAGES = KE_DATA.pages as Record<string, string>;
const GLOSSARY = KE_DATA.glossary as Record<string, Record<string, string>>;
// Derived from the graph in build_data, so a page cannot contradict the map.
const THREADS = ((KE_DATA as { threads?: Record<string, ConceptThreadSet> })
  .threads ?? {}) as Record<string, ConceptThreadSet>;
const SOURCE = (KE_DATA.meta as { source?: string }).source ?? "this paper";

const LEARNING_PATH = (
  KE_DATA as typeof KE_DATA & { learningPath?: LearningPath }
).learningPath;
export const CHAPTERS = LEARNING_PATH
  ? buildLearningChapters(LEARNING_PATH, NODES, PAGES)
  : buildChapters(LEARN_STEPS, NODES, PAGES);
const CHECKPOINTS = getQuiz();
// Every anchor the article actually renders: a chapter and each of its
// sections. A thread pointing outside this set is named but not linked --
// the guided path covers a subset of the graph, so most threads leave it.
const ANCHORED = new Set(CHAPTERS.flatMap(
  (chapter) => [chapter.nodeId, ...chapter.sections.map((s) => s.nodeId)],
).filter(Boolean));
// The article scrolls through every chapter at once, so a selection can land on
// a term belonging to any of them. Per-node maps already carry the paper-wide
// terms merged in, so flattening them is the whole article's vocabulary.
const ALL_TERMS = Object.assign({}, ...Object.values(GLOSSARY)) as Record<string, string>;
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
  tierId,
}: {
  expandAll: boolean;
  glossary: Record<string, string>;
  nodeId: string;
  tier: ChapterTier;
  tierId?: string;
}) {
  const segments = useMemo(() => parseContent(tier.content), [tier.content]);
  const renderMarkdown = (markdown: string) => (
    <RichMarkdown glossary={glossary} markdown={markdown} />
  );

  return (
    <section
      aria-label={`${tier.label}`}
      className={`article-tier article-tier-${tier.id}`}
      id={tierId ?? `${nodeId}--${tier.id}`}
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

function checksAt(
  chapter: Chapter,
  placement: NonNullable<QuizItem["placement"]>,
  nodeId?: string,
) {
  const ids = new Set(chapter.checkpointIds);
  return CHECKPOINTS.filter((item) => (
    ids.has(item.id)
    && (item.placement ?? "chapter-end") === placement
    && (nodeId === undefined || item.nodeId === nodeId)
  ));
}

function SectionTiers({
  chapter,
  expandAll,
  section,
}: {
  chapter: Chapter;
  expandAll: boolean;
  section: ChapterSection;
}) {
  return section.tiers.map((tier) => {
    const placement = tier.id === "intuition"
      ? "after-intuition" as const
      : tier.id === "mechanics"
        ? "after-mechanics" as const
        : null;
    const tierId = section.nodeId === chapter.nodeId
      ? `${chapter.nodeId}--${tier.id}`
      : `${chapter.nodeId}--${section.nodeId}--${tier.id}`;
    return (
      <div key={tier.id}>
        <TierSection
          expandAll={expandAll}
          glossary={GLOSSARY[section.nodeId] ?? {}}
          nodeId={section.nodeId}
          tier={tier}
          tierId={tierId}
        />
        {placement && checksAt(chapter, placement, section.nodeId).map((item) => (
          <InlineCheckpoint item={item} key={item.id} />
        ))}
      </div>
    );
  });
}

function ConceptSectionView({
  chapter,
  expandAll,
  section,
}: {
  chapter: Chapter;
  expandAll: boolean;
  section: ChapterSection;
}) {
  const body = (
    <>
      <SectionTiers chapter={chapter} expandAll={expandAll} section={section} />
      {/* Threads hang off the concept, not the chapter: a learning-path
          chapter groups several concepts and has no node of its own. */}
      <ConceptThreads reachable={ANCHORED} threads={THREADS[section.nodeId]} />
    </>
  );
  if (section.depth === "core" && section.nodeId === chapter.nodeId) return body;
  if (section.depth === "core") {
    return (
      <section className="concept-section" id={section.nodeId}>
        <h3 className="concept-section-title">{section.title}</h3>
        {body}
      </section>
    );
  }
  return (
    <details
      className={`concept-section concept-section-${section.depth}`}
      id={section.nodeId}
    >
      <summary>
        <span>{section.title}</span>
        <small>
          {section.depth === "foundation"
            ? "Foundation · open for a refresher"
            : "Advanced depth"}
        </small>
      </summary>
      <div className="concept-section-body">{body}</div>
    </details>
  );
}

type ArticleViewProps = {
  onRailOpenChange?: (open: boolean) => void;
  onRailReset: () => void;
  onRailResize: (width: number) => void;
  railBounds: PanelBounds;
  railOpen?: boolean;
  railWidth: number;
  resizable?: boolean;
};

export default function ArticleView({
  onRailOpenChange = () => {},
  onRailReset,
  onRailResize,
  railBounds,
  railOpen = true,
  railWidth,
  resizable = true,
}: ArticleViewProps) {
  const expandAllMath = useApp((state) => state.expandAllMath);
  const setLearnIdx = useApp((state) => state.setLearnIdx);
  const markReading = useApp((state) => state.markReading);
  const markStepComplete = useApp((state) => state.markStepComplete);
  const articleRef = useRef<HTMLElement>(null);
  const minutes = readingTimeMinutes(CHAPTERS);
  const fullMinutes = CHAPTERS.reduce(
    (total, chapter) => total + (chapter.estimatedFullMinutes ?? 0), 0,
  );

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return;
    const root = articleRef.current;
    if (!root) return;
    const sections = Array.from(root.querySelectorAll<HTMLElement>(
      "[data-chapter-idx], [data-chapter-end]",
    ));
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const completed = (entry.target as HTMLElement).dataset.chapterEnd;
          if (completed) {
            markStepComplete(completed);
            continue;
          }
          const index = Number(
            (entry.target as HTMLElement).dataset.chapterIdx,
          );
          if (Number.isNaN(index)) continue;
          setLearnIdx(index);
          const chapter = CHAPTERS[index];
          if (chapter) markReading(chapter.nodeId);
        }
      },
      { rootMargin: "-20% 0px -70% 0px" },
    );
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, [markReading, markStepComplete, setLearnIdx]);

  const jumpTo = (anchor: string) => {
    document.getElementById(anchor)?.scrollIntoView({ block: "start" });
  };

  return (
    <div className="article-shell">
      <SelectionLookup glossary={ALL_TERMS} onOpenConcept={jumpTo} />
      {railOpen ? (
        <ProgressRail
          chapters={CHAPTERS}
          hasClosing={Boolean(CLOSING)}
          hasNotation={Boolean(NOTATION)}
          onClose={() => onRailOpenChange(false)}
          onJump={jumpTo}
        />
      ) : (
        <button
          className="rail-reopen"
          onClick={() => onRailOpenChange(true)}
          type="button"
        >
          Show reading progress
        </button>
      )}
      {railOpen && resizable && (
        <PanelResizer
          bounds={railBounds}
          id="guided-rail"
          label="Resize guided reading panel"
          onChange={onRailResize}
          onReset={onRailReset}
          side="left"
          value={railWidth}
        />
      )}
      <div className="article-scroll">
        <article className="article" ref={articleRef}>
          <header className="article-opening">
            <p className="article-eyebrow">Guided reading</p>
            <h1 className="article-title">{SOURCE}</h1>
            <p className="article-meta">
              {CHAPTERS.length} chapters · about {minutes} min guided spine
              {fullMinutes > minutes && <> · {fullMinutes} min with full depth</>}
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
              {chapter.question && (
                <p className="chapter-question">
                  <span>Question</span>{chapter.question}
                </p>
              )}
              {chapter.sections.map((section) => (
                <ConceptSectionView
                  chapter={chapter}
                  expandAll={expandAllMath}
                  key={section.nodeId}
                  section={section}
                />
              ))}
              {checksAt(chapter, "chapter-end").map((item) => (
                <InlineCheckpoint item={item} key={item.id} />
              ))}
              <div className="chapter-end" data-chapter-end={chapter.nodeId}>
                <span>You can now</span>
                <p>{chapter.outcome ?? `Explain ${chapter.title}.`}</p>
              </div>
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
              {LEARNING_PATH?.reviewed
                ? "Want to inspect the relationships? Every guided concept also lives on the interactive map."
                : "This build uses an unreviewed fallback path. Open the map to inspect concepts the path may omit."}
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
