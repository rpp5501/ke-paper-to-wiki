import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import AlgorithmWalkthrough from "./AlgorithmWalkthrough";
import AnnotatedEquation from "./AnnotatedEquation";
import BlockRenderer from "./BlockRenderer";
import DerivationSteps from "./DerivationSteps";
import FigurePlaceholder from "./FigurePlaceholder";

describe("AnnotatedEquation", () => {
  it("renders equation and one legend row per term", () => {
    render(
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
    expect(document.querySelector(".katex")).toBeTruthy();
    expect(screen.getByText("energy")).toBeTruthy();
    expect(screen.getByText("mass")).toBeTruthy();
    expect(document.querySelector(".eq-term-1")).toBeTruthy();
    expect(document.querySelector(".eq-term-2")).toBeTruthy();
  });
});

describe("DerivationSteps", () => {
  it("renders shape lead-in and each step with its why", () => {
    render(
      <DerivationSteps
        block={{
          type: "derivation",
          shape: "maps a group to a score",
          steps: [{ latex: "a = b", why: "by definition" }],
        }}
      />,
    );
    expect(screen.getByText("maps a group to a score")).toBeTruthy();
    expect(screen.getByText("by definition")).toBeTruthy();
    expect(document.querySelector(".derivation-latex .katex")).toBeTruthy();
  });
});

describe("AlgorithmWalkthrough", () => {
  const block = {
    type: "algorithm" as const,
    title: "Rank groups",
    lines: [{ code: "for g in groups:", intent: "visit each group" }],
  };

  it("hides intent until toggled", () => {
    render(<AlgorithmWalkthrough block={block} />);
    expect(screen.queryByText("visit each group")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: /why/i }));
    expect(screen.getByText("visit each group")).toBeTruthy();
  });

  it("shows every intent when expandAll", () => {
    render(<AlgorithmWalkthrough block={block} expandAll />);
    expect(screen.getByText("visit each group")).toBeTruthy();
    expect(screen.queryByRole("button")).toBeNull();
  });
});

describe("FigurePlaceholder", () => {
  it("renders caption and coming-soon copy", () => {
    render(
      <FigurePlaceholder
        block={{ type: "figure", id: "comet-plot", caption: "Confidence comets" }}
      />,
    );
    expect(screen.getByText("Interactive figure — coming soon")).toBeTruthy();
    expect(screen.getByText("Confidence comets")).toBeTruthy();
  });
});

describe("BlockRenderer", () => {
  it("dispatches markdown segments through renderMarkdown", () => {
    render(
      <BlockRenderer
        renderMarkdown={(markdown) => <p>md:{markdown}</p>}
        segment={{ type: "markdown", markdown: "hello" }}
      />,
    );
    expect(screen.getByText("md:hello")).toBeTruthy();
  });

  it("dispatches typed blocks to their components", () => {
    render(
      <BlockRenderer
        renderMarkdown={() => null}
        segment={{ type: "figure", id: "x" }}
      />,
    );
    expect(document.querySelector(".figure-placeholder")).toBeTruthy();
  });
});
