import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { KEEdge } from "../types";
import {
  advancePlayback,
  blastTraceSteps,
  PlayerBarPresentation,
  readingPathSteps,
} from "./PlayerBar";

const actions = {
  onClose: () => undefined,
  onMove: () => undefined,
  onStart: () => undefined,
  onTogglePlaying: () => undefined,
};

describe("PlayerBar ordering", () => {
  it("uses tour order and the first available node in each concept step", () => {
    const steps = readingPathSteps([
      { order: 2, nodeIds: ["missing", "attention"] },
      { order: 1, nodeIds: ["transformer"] },
    ], new Set(["attention", "transformer"]));

    expect(steps).toEqual(["transformer", "attention"]);
  });

  it("orders blast dependents by depth and then stable node id", () => {
    const edges: KEEdge[] = [
      { src: "beta", dst: "root", kind: "calls" },
      { src: "alpha", dst: "root", kind: "calls" },
      { src: "zeta", dst: "alpha", kind: "calls" },
      { src: "gamma", dst: "beta", kind: "calls" },
    ];

    expect(blastTraceSteps("root", edges)).toEqual([
      "root",
      "alpha",
      "beta",
      "gamma",
      "zeta",
    ]);
  });

  it("advances once and stops playback at the final step", () => {
    expect(advancePlayback(0, 3)).toEqual({ idx: 1, playing: true });
    expect(advancePlayback(1, 3)).toEqual({ idx: 2, playing: false });
    expect(advancePlayback(2, 3)).toEqual({ idx: 2, playing: false });
  });
});

describe("PlayerBar", () => {
  it("shows only the concept reading action with a layout reason", () => {
    const markup = renderToStaticMarkup(
      <PlayerBarPresentation
        {...actions}
        firstStep="graph-comparison-problem"
        isConcept
        layoutPhase="loading"
        player={null}
        reducedMotion={false}
      />,
    );

    expect(markup).toContain("▶ reading path");
    expect(markup).not.toContain("trace blast radius");
    expect(markup).toContain("disabled");
    expect(markup).toMatch(/aria-describedby="[^"]+"/);
    expect(markup).toContain("Graph layout is still loading.");
  });

  it("renders active boundaries, play, close, and one atomic status", () => {
    const markup = renderToStaticMarkup(
      <PlayerBarPresentation
        {...actions}
        firstStep="transformer"
        isConcept
        layoutPhase="ready"
        player={{
          idx: 0,
          label: "Reading path",
          playing: false,
          steps: ["transformer", "attention"],
        }}
        reducedMotion={false}
      />,
    );

    expect(markup).toContain("Reading path");
    expect(markup).toContain("step 1 / 2");
    expect(markup).toContain('aria-label="Previous step"');
    expect(markup).toContain('aria-label="Play reading path"');
    expect(markup).toContain('aria-label="Close player"');
    expect(markup).toContain('aria-live="polite"');
    expect(markup).toContain('aria-atomic="true"');
  });
});
