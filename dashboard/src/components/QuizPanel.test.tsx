import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { QuizItem } from "../lib/quiz";
import QuizPanel, { QuizItemView } from "./QuizPanel";

let items: QuizItem[] = [];

vi.mock("../lib/quiz", () => ({
  getQuiz: () => items,
}));

// R16.C2 — a build with one resolvable section, so provenance chips have
// something to resolve against.
vi.mock("../lib/source", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../lib/source")>()),
  getSections: () => ({ "3.2": { title: "SDPA", text: "the passage" } }),
}));

const item: QuizItem = {
  id: "q1",
  nodeId: "scaled-dot-product-attention",
  prompt: "Why divide by sqrt(dk)?",
  options: [
    { text: "Normalize output", explain: "No — output length is unaffected." },
    { text: "Prevent softmax saturation", explain: "Yes — variance grows with dk." },
  ],
  correct: 1,
  sourceRef: "#the-math",
};

beforeEach(() => {
  items = [];
});

describe("QuizPanel", () => {
  it("renders nothing on a build without quiz items", () => {
    expect(renderToStaticMarkup(<QuizPanel />)).toBe("");
  });

  it("shows a toggle with the item count, closed by default", () => {
    items = [item];
    const html = renderToStaticMarkup(<QuizPanel />);
    expect(html).toContain("Quiz (1)");
    expect(html).toContain('aria-expanded="false"');
    expect(html).not.toContain("Why divide"); // items only when open
  });
});

describe("QuizItemView provenance chip", () => {
  const sourced: QuizItem = { ...item, sectionRef: "sec:3.2" };
  const noop = () => undefined;

  it("shows the chip once the learner has answered", () => {
    const html = renderToStaticMarkup(
      <QuizItemView answer={0} item={sourced} onAnswer={noop} onGoToNode={noop} />,
    );

    expect(html).toContain("§3.2");
  });

  it("withholds the chip until an answer is committed", () => {
    // Commit-then-reveal: seeing the source before answering gives it away.
    const html = renderToStaticMarkup(
      <QuizItemView answer={null} item={sourced} onAnswer={noop} onGoToNode={noop} />,
    );

    expect(html).not.toContain("§3.2");
  });

  it("shows no chip for an item whose ref does not resolve", () => {
    const html = renderToStaticMarkup(
      <QuizItemView answer={0} item={item} onAnswer={noop} onGoToNode={noop} />,
    );

    expect(html).not.toContain("source-chip");
  });
});

describe("QuizItemView", () => {
  const noop = () => undefined;

  it("hides explanations until answered", () => {
    const html = renderToStaticMarkup(
      <QuizItemView answer={null} item={item} onAnswer={noop} onGoToNode={noop} />,
    );
    expect(html).toContain("Why divide by sqrt(dk)?");
    expect(html).toContain("Prevent softmax saturation");
    expect(html).not.toContain("variance grows");
  });

  it("marks the picked wrong answer and reveals both explanations", () => {
    const html = renderToStaticMarkup(
      <QuizItemView answer={0} item={item} onAnswer={noop} onGoToNode={noop} />,
    );
    expect(html).toContain("wrong");
    expect(html).toContain("correct");
    expect(html).toContain("No — output length is unaffected.");
    expect(html).toContain("Yes — variance grows with dk.");
    expect(html).toContain("disabled");
  });
});
