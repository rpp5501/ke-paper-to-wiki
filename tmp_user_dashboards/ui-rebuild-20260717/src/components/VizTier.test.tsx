import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { VizEntry } from "../lib/viz";
import { VizTierPresentation } from "./VizTier";

const entry: VizEntry = {
  kind: "template",
  templateId: "attention-heatmap",
  title: "Scaled dot-product attention, live",
  caption: "Scrub d_k and watch softmax reweight.",
  prompt: "Which token do you bet wins?",
  srcdoc: "<!DOCTYPE html><html><body>viz</body></html>",
  stale: false,
};

describe("VizTierPresentation", () => {
  it("renders a Visualize tier with the caption, no iframe until opened", () => {
    const html = renderToStaticMarkup(
      <VizTierPresentation entry={entry} focused={false} />,
    );
    expect(html).toContain("Visualize");
    expect(html).toContain("Scrub d_k and watch softmax reweight.");
    expect(html).not.toContain("<iframe"); // lazy: unopened visuals cost nothing
    expect(html).not.toContain("open");
  });

  it("mounts the sandboxed iframe open when the gallery focused this node", () => {
    const html = renderToStaticMarkup(
      <VizTierPresentation entry={entry} focused />,
    );
    expect(html).toContain("<iframe");
    expect(html).toContain('sandbox="allow-scripts"');
    expect(html).not.toContain("allow-same-origin");
    expect(html).toContain("<details class=\"viz-tier\" open");
  });

  it("shows the staleness banner when page evidence moved on", () => {
    const html = renderToStaticMarkup(
      <VizTierPresentation entry={{ ...entry, stale: true }} focused={false} />,
    );
    expect(html).toContain("older version of the page");
  });
});
