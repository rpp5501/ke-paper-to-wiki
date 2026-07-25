import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { NextStep } from "../lib/nextSteps";
import ContinuePanel from "./ContinuePanel";

let steps: NextStep[] = [];

vi.mock("../lib/nextSteps", () => ({
  getNextSteps: () => steps,
}));

const step = (title: string, confirmed = false): NextStep => ({
  title,
  rationale: "why this matters",
  kind: "paper-limitation",
  nodes: ["attention"],
  sources: ["§sec:3.2"],
  confirmed,
});

beforeEach(() => {
  steps = [];
});

describe("ContinuePanel", () => {
  it("renders nothing on a build without next steps", () => {
    expect(renderToStaticMarkup(<ContinuePanel />)).toBe("");
  });

  it("shows a toggle with the count, list closed by default", () => {
    steps = [step("Profile attention cost", true), step("Try learned PE")];
    const html = renderToStaticMarkup(<ContinuePanel />);
    expect(html).toContain("Continue (2)");
    expect(html).toContain('aria-expanded="false"');
    expect(html).not.toContain("Profile attention cost"); // items only when open
  });
});
