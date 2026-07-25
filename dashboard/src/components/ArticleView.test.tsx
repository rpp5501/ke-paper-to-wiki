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
    }
  });

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
      for (const tier of chapter.tiers) {
        expect(markup).toContain(`id="${chapter.nodeId}--${tier.id}"`);
      }
    }
  });
});

describe("ProgressRailPresentation", () => {
  const chapters = [
    { nodeId: "alpha", title: "Alpha idea", tiers: [] },
    { nodeId: "beta", title: "Beta idea", tiers: [] },
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
    expect(markup).toContain('aria-current="step"');
    expect(markup).toContain("Notation guide");
    expect(markup).not.toContain("You can now");
    expect(markup).toContain("Full concept map");
  });
});
