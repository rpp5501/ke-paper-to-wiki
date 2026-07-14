import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import {
  isTourDismissKey,
  orderedTourSteps,
  TourOverlayPresentation,
} from "./TourOverlay";

const steps = orderedTourSteps([
  {
    order: 1,
    title: "The Transformer",
    description: "Start with the architecture.",
    nodeIds: ["transformer"],
  },
  {
    order: 2,
    title: "Attention",
    description: "Follow the attention path.",
    nodeIds: ["attention"],
  },
], new Set(["transformer", "attention"]));

const actions = {
  onDismiss: () => undefined,
  onGo: () => undefined,
};

describe("tour state", () => {
  it("orders steps and chooses the first available node id", () => {
    expect(orderedTourSteps([
      { order: 2, title: "B", description: "second", nodeIds: ["x", "b"] },
      { order: 1, title: "A", description: "first", nodeIds: ["a"] },
    ], new Set(["a", "b"]))).toEqual([
      { order: 1, title: "A", description: "first", nodeId: "a" },
      { order: 2, title: "B", description: "second", nodeId: "b" },
    ]);
  });

  it("dismisses only for Escape", () => {
    expect(isTourDismissKey("Escape")).toBe(true);
    expect(isTourDismissKey("Enter")).toBe(false);
  });
});

describe("TourOverlay", () => {
  it("renders exact initial copy and explains why Start is disabled", () => {
    const markup = renderToStaticMarkup(
      <TourOverlayPresentation
        {...actions}
        dismissed={false}
        layoutPhase="loading"
        steps={steps}
        tourIdx={null}
      />,
    );

    expect(markup).toContain("Guided tour");
    expect(markup).toContain("Walk the 2 key concepts.");
    expect(markup).toContain(">Start</");
    expect(markup).toContain("disabled");
    expect(markup).toContain("Graph layout is still loading.");
    expect(markup).toContain('aria-label="Dismiss guided tour"');
  });

  it("renders an active semantic step and atomic progress status", () => {
    const markup = renderToStaticMarkup(
      <TourOverlayPresentation
        {...actions}
        dismissed={false}
        layoutPhase="ready"
        steps={steps}
        tourIdx={0}
      />,
    );

    expect(markup).toContain("<h3");
    expect(markup).toContain("The Transformer");
    expect(markup).toContain(">Back</");
    expect(markup).toContain(">Next</");
    expect(markup).toContain(">1/2<");
    expect(markup).toContain('aria-live="polite"');
    expect(markup).toContain('aria-atomic="true"');
  });

  it("stays hidden after session dismissal", () => {
    expect(renderToStaticMarkup(
      <TourOverlayPresentation
        {...actions}
        dismissed
        layoutPhase="ready"
        steps={steps}
        tourIdx={null}
      />,
    )).toBe("");
  });
});
