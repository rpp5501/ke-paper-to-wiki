import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it } from "vitest";

import { useApp } from "../store";
import LearnPanel, {
  LEARN_STEPS,
  LearnPanelPresentation,
  stepActivation,
} from "./LearnPanel";

beforeEach(() => {
  useApp.setState({
    mode: "learn",
    tourIdx: 0,
    completedSteps: new Set(),
    selected: null,
    layoutPhase: "ready",
  } as never);
});

describe("LearnPanel", () => {
  it("renders one numbered step per tour entry with title and blurb", () => {
    const markup = renderToStaticMarkup(<LearnPanel onCloseSheet={() => {}} />);
    LEARN_STEPS.forEach((step) => {
      expect(markup).toContain(step.title);
    });
    expect(markup).toContain(LEARN_STEPS[0].blurb);
    expect(markup).toContain(`The ${LEARN_STEPS.length} ideas that matter`);
  });

  // Store-wired render cannot see setState here: zustand v5 serves
  // getInitialState() to server rendering, so state-dependent markup is
  // asserted through the props-driven presentation (Drawer.test.tsx idiom).
  it("marks the current step and completed steps", () => {
    const markup = renderToStaticMarkup(
      <LearnPanelPresentation
        completedSteps={new Set([LEARN_STEPS[0].nodeId])}
        onCloseSheet={() => {}}
        onExplore={() => {}}
        onStep={() => {}}
        tourIdx={1}
      />,
    );
    expect(markup).toContain('aria-current="step"');
    expect(markup).toContain("is-done");
    expect(markup).toContain("✓");
    expect(markup).toContain(`1 of ${LEARN_STEPS.length} visited`);
  });

  it("computes step activation only when layout is ready and the step exists", () => {
    expect(stepActivation(LEARN_STEPS, 2, "ready")).toEqual({
      index: 2,
      nodeId: LEARN_STEPS[2].nodeId,
    });
    expect(stepActivation(LEARN_STEPS, 2, "loading")).toBeNull();
    expect(stepActivation(LEARN_STEPS, 99, "ready")).toBeNull();
  });

  it("renders the full-map escape hatch with the node count", () => {
    const markup = renderToStaticMarkup(<LearnPanel onCloseSheet={() => {}} />);
    expect(markup).toContain("Show the full map");
  });
});
