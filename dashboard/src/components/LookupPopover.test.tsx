import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import LookupPopover from "./LookupPopover";

const noop = () => undefined;

describe("LookupPopover", () => {
  it("shows a glossary definition", () => {
    const html = renderToStaticMarkup(
      <LookupPopover
        onDismiss={noop}
        phrase="d-separation"
        result={{ kind: "glossary", term: "d-separation", definition: "A criterion." }}
      />,
    );

    expect(html).toContain("d-separation");
    expect(html).toContain("A criterion.");
  });

  it("offers a concept hit as a button to navigate there", () => {
    const html = renderToStaticMarkup(
      <LookupPopover
        onDismiss={noop}
        onOpenConcept={noop}
        phrase="SID"
        result={{ kind: "concept", nodeId: "sid", label: "SID", definition: "A pre-metric." }}
      />,
    );

    expect(html).toContain("lookup-link");
  });

  it("keeps a concept hit plain when there is nowhere to navigate", () => {
    const html = renderToStaticMarkup(
      <LookupPopover
        onDismiss={noop}
        phrase="SID"
        result={{ kind: "concept", nodeId: "sid", label: "SID", definition: "A pre-metric." }}
      />,
    );

    expect(html).not.toContain("lookup-link");
  });

  it("shows a section hit with its number, for the reader to place it", () => {
    const html = renderToStaticMarkup(
      <LookupPopover
        onDismiss={noop}
        phrase="adjustment"
        result={{ kind: "section", ref: "3", title: "Algorithms", excerpt: "…text…" }}
      />,
    );

    expect(html).toContain("§3");
    expect(html).toContain("Algorithms");
  });

  it("says so plainly on a miss rather than showing something related", () => {
    const html = renderToStaticMarkup(
      <LookupPopover onDismiss={noop} phrase="quarks" result={null} />,
    );

    expect(html).toContain("No entry for");
  });

  it("is dismissable by anyone not using a mouse", () => {
    const html = renderToStaticMarkup(
      <LookupPopover onDismiss={noop} phrase="x" result={null} />,
    );

    expect(html).toContain('aria-label="Dismiss"');
    expect(html).toContain('role="dialog"');
  });
});
