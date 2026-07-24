import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { VizEntry } from "../lib/viz";
import VizGallery from "./VizGallery";

let vizMap: Record<string, VizEntry> = {};

vi.mock("../lib/viz", () => ({
  getVizMap: () => vizMap,
  getViz: (id: string | null) => (id ? vizMap[id] : undefined),
}));

const entry = (title: string): VizEntry => ({
  kind: "template",
  templateId: "attention-heatmap",
  title,
  caption: "c",
  prompt: "p",
  srcdoc: "<html></html>",
  stale: false,
});

beforeEach(() => {
  vizMap = {};
});

describe("VizGallery", () => {
  it("renders nothing on a viz-free build", () => {
    expect(renderToStaticMarkup(<VizGallery />)).toBe("");
  });

  it("shows a toggle with the visual count, panel closed by default", () => {
    vizMap = { a: entry("Attention, live"), b: entry("Softmax dial") };
    const html = renderToStaticMarkup(<VizGallery />);
    expect(html).toContain("Visuals (2)");
    expect(html).toContain('aria-expanded="false"');
    expect(html).not.toContain("Attention, live"); // items only when open
  });
});
