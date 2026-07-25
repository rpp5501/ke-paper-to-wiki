import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { SourceSection } from "../lib/source";
import SourceChip from "./SourceChip";

const sections: Record<string, SourceSection> = {
  "3.2": { title: "Scaled Dot-Product Attention", text: "the passage" },
};

const noop = () => undefined;

describe("SourceChip", () => {
  it("renders the section number when the ref resolves", () => {
    const html = renderToStaticMarkup(
      <SourceChip onOpen={noop} sections={sections} sourceRef="sec:3.2" />,
    );

    expect(html).toContain("§3.2");
  });

  it("names the section for anyone reading the chip out of context", () => {
    const html = renderToStaticMarkup(
      <SourceChip onOpen={noop} sections={sections} sourceRef="sec:3.2" />,
    );

    expect(html).toContain("Scaled Dot-Product Attention");
  });

  it("renders nothing when the ref matches no section", () => {
    const html = renderToStaticMarkup(
      <SourceChip onOpen={noop} sections={sections} sourceRef="sec:9.9" />,
    );

    expect(html).toBe("");
  });

  it("renders nothing without a ref at all", () => {
    for (const ref of ["", null, undefined]) {
      expect(renderToStaticMarkup(
        <SourceChip onOpen={noop} sections={sections} sourceRef={ref} />,
      )).toBe("");
    }
  });

  it("renders nothing when the build carries no sections", () => {
    expect(renderToStaticMarkup(
      <SourceChip onOpen={noop} sections={{}} sourceRef="sec:3.2" />,
    )).toBe("");
  });

  it("is a static label when there is nothing to navigate to", () => {
    // In the drawer the source panel is already on screen for this node, so a
    // button would be a control that does nothing.
    const html = renderToStaticMarkup(
      <SourceChip sections={sections} sourceRef="sec:3.2" />,
    );

    expect(html).toContain("§3.2");
    expect(html).not.toContain("<button");
  });

  it("is a button, so the chip can open the source from the keyboard", () => {
    const html = renderToStaticMarkup(
      <SourceChip onOpen={noop} sections={sections} sourceRef="sec:3.2" />,
    );

    expect(html).toContain("<button");
    expect(html).toContain('type="button"');
  });
});
