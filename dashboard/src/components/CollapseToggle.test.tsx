import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { CollapseTogglePresentation } from "./CollapseToggle";

const noop = () => undefined;

describe("CollapseTogglePresentation", () => {
  it("renders nothing for a leaf with no branch to fold", () => {
    const markup = renderToStaticMarkup(
      <CollapseTogglePresentation
        collapsed={false}
        count={0}
        label="Softmax"
        onToggle={noop}
      />,
    );

    expect(markup).toBe("");
  });

  it("offers to collapse a branch, showing what it would swallow", () => {
    const markup = renderToStaticMarkup(
      <CollapseTogglePresentation
        collapsed={false}
        count={3}
        label="Attention"
        onToggle={noop}
      />,
    );

    expect(markup).toContain("Collapse branch (3)");
    expect(markup).toContain('aria-pressed="false"');
    expect(markup).toContain("under Attention");
  });

  it("offers to expand once folded, reporting the hidden count", () => {
    const markup = renderToStaticMarkup(
      <CollapseTogglePresentation
        collapsed
        count={3}
        label="Attention"
        onToggle={noop}
      />,
    );

    expect(markup).toContain("Expand branch (3 hidden)");
    expect(markup).toContain('aria-pressed="true"');
  });

  it("is a real button, so the branch folds from the keyboard too", () => {
    const markup = renderToStaticMarkup(
      <CollapseTogglePresentation
        collapsed={false}
        count={2}
        label="Attention"
        onToggle={noop}
      />,
    );

    expect(markup).toContain("<button");
    expect(markup).toContain('type="button"');
  });
});
