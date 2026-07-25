import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import ReviewPanel, { ReviewPanelPresentation } from "./ReviewPanel";

const noop = () => undefined;

describe("ReviewPanelPresentation", () => {
  it("renders nothing when there is nothing to review", () => {
    const markup = renderToStaticMarkup(
      <ReviewPanelPresentation onPick={noop} onToggle={noop} open queue={[]} />,
    );

    expect(markup).toBe("");
  });

  it("shows the queue size on the closed pill without listing nodes", () => {
    const markup = renderToStaticMarkup(
      <ReviewPanelPresentation
        onPick={noop}
        onToggle={noop}
        open={false}
        queue={["sdpa", "softmax"]}
      />,
    );

    expect(markup).toContain("Review (2)");
    expect(markup).toContain('aria-expanded="false"');
    expect(markup).not.toContain("sdpa");
  });

  it("lists each queued node once opened", () => {
    const markup = renderToStaticMarkup(
      <ReviewPanelPresentation
        onPick={noop}
        onToggle={noop}
        open
        queue={["sdpa", "softmax"]}
      />,
    );

    expect(markup).toContain('aria-expanded="true"');
    expect(markup).toContain('aria-label="Nodes to review"');
    expect(markup).toContain("sdpa");
    expect(markup).toContain("softmax");
  });
});

describe("ReviewPanel", () => {
  it("stays out of the toolbar on a fresh ledger", () => {
    expect(renderToStaticMarkup(<ReviewPanel />)).toBe("");
  });
});
