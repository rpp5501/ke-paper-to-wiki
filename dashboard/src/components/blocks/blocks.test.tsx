import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import AlgorithmWalkthrough from "./AlgorithmWalkthrough";
import AnnotatedEquation from "./AnnotatedEquation";
import BlockRenderer from "./BlockRenderer";
import DerivationSteps from "./DerivationSteps";
import FigurePlaceholder from "./FigurePlaceholder";

describe("AnnotatedEquation", () => {
  it("renders equation and one legend row per term", () => {
    const html = renderToStaticMarkup(
      <AnnotatedEquation
        block={{
          type: "annotated-eq",
          latex: "E = mc^2",
          terms: [
            { tex: "E", role: 1, words: "energy" },
            { tex: "m", role: 2, words: "mass" },
          ],
        }}
      />,
    );
    expect(html).toContain("katex");
    expect(html).toContain("energy");
    expect(html).toContain("mass");
    expect(html).toContain("eq-term-1");
    expect(html).toContain("eq-term-2");
  });
});

describe("DerivationSteps", () => {
  it("renders shape lead-in and each step with its why", () => {
    const html = renderToStaticMarkup(
      <DerivationSteps
        block={{
          type: "derivation",
          shape: "maps a group to a score",
          steps: [{ latex: "a = b", why: "by definition" }],
        }}
      />,
    );
    expect(html).toContain("maps a group to a score");
    expect(html).toContain("by definition");
    expect(html).toContain("derivation-latex");
    expect(html).toContain("katex");
  });
});

describe("AlgorithmWalkthrough", () => {
  const block = {
    type: "algorithm" as const,
    title: "Rank groups",
    lines: [{ code: "for g in groups:", intent: "visit each group" }],
  };

  it("hides intent by default behind a collapsed toggle", () => {
    const html = renderToStaticMarkup(<AlgorithmWalkthrough block={block} />);
    expect(html).not.toContain("visit each group");
    expect(html).toContain('aria-expanded="false"');
    expect(html).toContain("Rank groups");
  });

  it("shows every intent and no toggles when expandAll", () => {
    const html = renderToStaticMarkup(<AlgorithmWalkthrough block={block} expandAll />);
    expect(html).toContain("visit each group");
    expect(html).not.toContain("aria-expanded");
  });
});

describe("FigurePlaceholder", () => {
  it("renders caption and coming-soon copy", () => {
    const html = renderToStaticMarkup(
      <FigurePlaceholder
        block={{ type: "figure", id: "comet-plot", caption: "Confidence comets" }}
      />,
    );
    expect(html).toContain("Interactive figure — coming soon");
    expect(html).toContain("Confidence comets");
    expect(html).toContain('data-figure-id="comet-plot"');
  });
});

describe("BlockRenderer", () => {
  it("dispatches markdown segments through renderMarkdown", () => {
    const html = renderToStaticMarkup(
      <BlockRenderer
        renderMarkdown={(markdown) => <p>md:{markdown}</p>}
        segment={{ type: "markdown", markdown: "hello" }}
      />,
    );
    expect(html).toContain("md:hello");
  });

  it("dispatches typed blocks to their components", () => {
    const html = renderToStaticMarkup(
      <BlockRenderer renderMarkdown={() => null} segment={{ type: "figure", id: "x" }} />,
    );
    expect(html).toContain("figure-placeholder");
  });
});
