import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import ArticleView, { CHAPTERS } from "./ArticleView";
import { ProgressRailPresentation } from "./ProgressRail";

describe("ArticleView", () => {
  it("renders the article shell with opening, chapters, and explore handoff", () => {
    const markup = renderToStaticMarkup(
      <ArticleView
        onRailReset={() => {}}
        onRailResize={() => {}}
        railBounds={{ min: 220, max: 420 }}
        railWidth={288}
      />,
    );
    expect(markup).toContain('class="article-shell"');
    expect(markup).toMatch(
      /class="progress-rail"[\s\S]*aria-label="Resize guided reading panel"[\s\S]*class="article-scroll"/,
    );
    expect(markup).toContain('aria-valuenow="288"');
    expect(markup).toContain("Guided reading");
    expect(markup).toMatch(/about \d+ min/);
    expect(markup).toContain("Open the full concept map");
    for (const chapter of CHAPTERS) {
      expect(markup).toContain(`id="${chapter.nodeId}"`);
      expect(markup).toContain(`data-chapter-end="${chapter.nodeId}"`);
    }
  }, 15_000);

  it("renders every tier of every chapter vertically in the flow", () => {
    const markup = renderToStaticMarkup(
      <ArticleView
        onRailReset={() => {}}
        onRailResize={() => {}}
        railBounds={{ min: 220, max: 420 }}
        railWidth={264}
      />,
    );
    for (const chapter of CHAPTERS) {
      for (const section of chapter.sections) {
        for (const tier of section.tiers) {
          expect(markup).toContain(
            `id="${chapter.nodeId}--${section.nodeId}--${tier.id}"`,
          );
        }
      }
    }
  }, 15_000);

  it("keeps the guided rail closeable and provides a reopen control", () => {
    const markup = renderToStaticMarkup(
      <ArticleView
        onRailOpenChange={() => {}}
        onRailReset={() => {}}
        onRailResize={() => {}}
        railBounds={{ min: 220, max: 420 }}
        railOpen={false}
        railWidth={264}
      />,
    );

    expect(markup).not.toContain('class="progress-rail"');
    expect(markup).toContain("Show reading progress");
  });
});

describe("ProgressRailPresentation", () => {
  const chapters = [
    { nodeId: "alpha", title: "Alpha idea", tiers: [], sections: [], checkpointIds: [] },
    { nodeId: "beta", title: "Beta idea", tiers: [], sections: [], checkpointIds: [] },
  ];

  it("marks the current chapter and counts completed ones", () => {
    const markup = renderToStaticMarkup(
      <ProgressRailPresentation
        chapters={chapters}
        completedSteps={new Set(["alpha"])}
        mastery={{}}
        hasClosing={false}
        hasNotation
        learnIdx={1}
        onExplore={() => undefined}
        onJump={() => undefined}
      />,
    );
    expect(markup).toContain("1 of 2 read");
    expect(markup).toContain('class="rail-status">Read');
    expect(markup).toContain('class="rail-status">Reading');
    expect(markup).toContain('aria-current="step"');
    expect(markup).toContain("Notation guide");
    expect(markup).not.toContain("You can now");
    expect(markup).toContain("Full concept map");
  });
});
