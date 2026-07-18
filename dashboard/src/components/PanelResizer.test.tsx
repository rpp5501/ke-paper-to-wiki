import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import PanelResizer, { resizeFromPointer } from "./PanelResizer";

describe("PanelResizer", () => {
  it("renders an adjustable vertical separator with current bounds", () => {
    const markup = renderToStaticMarkup(
      <PanelResizer
        bounds={{ min: 240, max: 480 }}
        id="diagnostics"
        label="Resize diagnostics panel"
        onChange={() => {}}
        onReset={() => {}}
        side="left"
        value={312}
      />,
    );

    expect(markup).toContain('role="separator"');
    expect(markup).toContain('aria-orientation="vertical"');
    expect(markup).toContain('aria-valuemin="240"');
    expect(markup).toContain('aria-valuemax="480"');
    expect(markup).toContain('aria-valuenow="312"');
    expect(markup).toContain('aria-label="Resize diagnostics panel"');
  });

  it("maps pointer movement according to the panel side and clamps the result", () => {
    const bounds = { min: 240, max: 480 };

    expect(resizeFromPointer("left", 100, 132, 300, bounds)).toBe(332);
    expect(resizeFromPointer("right", 100, 132, 300, bounds)).toBe(268);
    expect(resizeFromPointer("left", 100, 400, 300, bounds)).toBe(480);
  });
});
