import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { MapTogglePresentation } from "./MapToggle";

const noop = () => undefined;

describe("MapTogglePresentation", () => {
  it("renders nothing outside explore mode", () => {
    expect(
      renderToStaticMarkup(
        <MapTogglePresentation active={false} onToggle={noop} visible={false} />,
      ),
    ).toBe("");
  });

  it("shows an inactive pill in explore mode", () => {
    const html = renderToStaticMarkup(
      <MapTogglePresentation active={false} onToggle={noop} visible />,
    );
    expect(html).toContain("Mind map");
    expect(html).toContain('aria-pressed="false"');
  });

  it("marks the pill active when radial layout is on", () => {
    const html = renderToStaticMarkup(
      <MapTogglePresentation active onToggle={noop} visible />,
    );
    expect(html).toContain('aria-pressed="true"');
  });
});
